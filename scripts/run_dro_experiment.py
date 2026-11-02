"""Reduced uncertainty-aware DRO experiment (post-G-R4 null).

Because no feature passed the G-R4 information rule, LightGBM is not fitted.
The reduced M1 uses the Ridge B0 mean and a 5-model bootstrap Ridge ensemble
standard deviation as an explicitly labelled epistemic-uncertainty proxy.

Strategies:
- M1_reduced: Ridge mean + bootstrap sigma, box DRO + CVaR.
- B5_DRO_point: Ridge mean + zero sigma, box DRO + CVaR.
- B3_CVaR: Ridge mean, kappa=0, CVaR only.
- B1_equal_weight: 1/N across eligible ETFs.

All strategies use the same monthly rebalance dates, universe, 5% cap,
long-only/sum=1 constraints, 10 bps one-way costs, and rolling 60-month
training window. This is a reduced methods experiment, not the original
LightGBM M1.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from epistemic_dro.baselines import fit_ridge_baseline
from epistemic_dro.data import load_panel
from epistemic_dro.evaluation import metric_basket
from epistemic_dro.features import FeatureSpec, build_features, build_targets
from epistemic_dro.optimization import DROSolution, solve_box_dro_cvar

ROOT = Path(__file__).resolve().parents[1]
STRATEGIES = ("M1_reduced", "B5_DRO_point", "B3_CVaR", "B1_equal_weight")


def _bootstrap_sigma(
    train: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    features_at_t: pd.DataFrame,
    seeds: tuple[int, ...],
) -> tuple[pd.Series, pd.Series]:
    """Fit bootstrap Ridge models and return mean + cross-model sigma."""
    train_dates = sorted(train.index.get_level_values("date").unique())
    predictions = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        sampled = rng.choice(train_dates, size=len(train_dates), replace=True)
        sample = train[train.index.get_level_values("date").isin(sampled)]
        baseline = fit_ridge_baseline(
            sample[feature_columns], sample[target_column], alpha=1.0
        )
        predictions.append(baseline.predict(features_at_t[feature_columns]))
    matrix = np.vstack([prediction.to_numpy() for prediction in predictions])
    mean = pd.Series(matrix.mean(axis=0), index=features_at_t.index, dtype=float)
    sigma = pd.Series(matrix.std(axis=0, ddof=1), index=features_at_t.index, dtype=float)
    sigma = sigma.clip(lower=1e-6)
    return mean, sigma


def _run_strategy(
    name: str,
    mu: pd.Series,
    sigma: pd.Series,
    scenarios: pd.DataFrame,
    prev_weights: pd.Series | None,
    *,
    kappa: float,
    cost_bps: float,
) -> tuple[pd.Series, float, float]:
    if name == "B1_equal_weight":
        weights = pd.Series(1.0 / len(scenarios.columns), index=scenarios.columns)
        previous = (
            pd.Series(0.0, index=weights.index)
            if prev_weights is None
            else prev_weights.reindex(weights.index).fillna(0.0)
        )
        turnover = float((weights - previous).abs().sum())
        cost = cost_bps / 10_000.0 * turnover
        return weights, turnover, cost

    solution: DROSolution = solve_box_dro_cvar(
        mu,
        sigma,
        scenarios,
        kappa=kappa,
        cvar_level=0.95,
        cvar_penalty=1.0,
        max_weight=0.05,
        prev_weights=prev_weights,
        turnover_penalty=0.0,
        cost_bps=cost_bps,
        solver="CLARABEL",
    )
    cost = cost_bps / 10_000.0 * solution.turnover
    return solution.weights, solution.turnover, cost


def main() -> None:
    parser = argparse.ArgumentParser(description="Reduced DRO uncertainty experiment.")
    parser.add_argument("--raw", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "tables")
    parser.add_argument("--start", default="2010-01-01")
    parser.add_argument("--end", default="2024-11-30")
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--train-months", type=int, default=60)
    parser.add_argument("--scenario-months", type=int, default=60)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument(
        "--suffix",
        default="",
        help="Suffix for output filenames, e.g. _5bp or _20bp.",
    )
    args = parser.parse_args()

    panel = load_panel(args.raw)
    features = build_features(
        panel.prices, panel.metadata, panel.universe, panel.factors, FeatureSpec()
    )
    targets = build_targets(panel.returns)
    data = features.join(targets, how="inner").sort_index()
    target_column = targets.columns[0]
    feature_columns = list(features.columns)

    returns_pivot = (
        panel.returns.pivot(index="date", columns="ticker", values="ret").sort_index()
    )
    rf = panel.risk_free.set_index("date")["rf"].sort_index()
    rebalance_dates = [
        date
        for date in sorted(features.index.get_level_values("date").unique())
        if pd.Timestamp(args.start) <= date <= pd.Timestamp(args.end)
    ]
    all_dates = sorted(features.index.get_level_values("date").unique())
    if len(all_dates) <= args.train_months:
        raise SystemExit("not enough history for the training window")

    date_position = {date: index for index, date in enumerate(all_dates)}
    seeds = tuple(range(args.seeds))
    previous: dict[str, pd.Series | None] = {name: None for name in STRATEGIES}
    rows: list[dict] = []
    weight_rows: list[dict] = []

    for date in rebalance_dates:
        position = date_position[date]
        train_dates = all_dates[max(0, position - args.train_months):position]
        if len(train_dates) < args.train_months:
            continue
        train = data[data.index.get_level_values("date").isin(train_dates)]
        if len(train) < 100:
            continue

        features_at_t = features.loc[date]
        if features_at_t.empty:
            continue
        mean, sigma = _bootstrap_sigma(
            train, feature_columns, target_column, features_at_t, seeds
        )

        scenario_window = returns_pivot.loc[:date].tail(args.scenario_months)
        scenario_window = scenario_window.reindex(columns=mean.index)
        scenario_window = scenario_window.dropna(axis=1, how="any")
        scenario_window = scenario_window.dropna(axis=0, how="any")
        if len(scenario_window) < 36 or scenario_window.shape[1] < 20:
            print(f"skip {date.date()}: insufficient scenario panel")
            continue
        assets = list(scenario_window.columns)
        mean = mean.reindex(assets)
        sigma = sigma.reindex(assets)
        next_returns = returns_pivot.shift(-1).loc[date].reindex(assets)
        valid = next_returns.notna()
        assets = [asset for asset in assets if valid[asset]]
        if len(assets) < 20:
            print(f"skip {date.date()}: insufficient assets")
            continue
        scenarios = scenario_window[assets]
        mean = mean.reindex(assets)
        sigma = sigma.reindex(assets)
        next_returns = next_returns.reindex(assets)
        if mean.isna().any() or sigma.isna().any():
            print(f"skip {date.date()}: missing forecast")
            continue

        for name in STRATEGIES:
            if name == "M1_reduced":
                kappa = 1.0
                strategy_sigma = sigma
            elif name == "B5_DRO_point":
                kappa = 1.0
                strategy_sigma = pd.Series(1e-6, index=assets)
            elif name == "B3_CVaR":
                kappa = 0.0
                strategy_sigma = pd.Series(1e-6, index=assets)
            else:
                kappa = 0.0
                strategy_sigma = pd.Series(1e-6, index=assets)

            weights, turnover, cost = _run_strategy(
                name,
                mean,
                strategy_sigma,
                scenarios,
                previous[name],
                kappa=kappa,
                cost_bps=args.cost_bps,
            )
            weights = weights.reindex(assets).fillna(0.0)
            weights = weights / weights.sum()
            previous[name] = weights
            net_return = float(weights @ next_returns) - cost
            rows.append(
                {
                    "date": date,
                    "strategy": name,
                    "net_return": net_return,
                    "gross_return": float(weights @ next_returns),
                    "turnover": turnover,
                    "cost": cost,
                    "n_assets": len(assets),
                    "mean_sigma": float(strategy_sigma.mean()),
                    "mean_mu": float(mean.mean()),
                }
            )
            weight_rows.extend(
                {
                    "date": date,
                    "strategy": name,
                    "ticker": ticker,
                    "weight": float(weight),
                }
                for ticker, weight in weights.items()
            )
        print(f"{date.date()}: {len(assets)} assets; M1 sigma mean {sigma.mean():.6f}")

    if not rows:
        raise SystemExit("no portfolio rows were produced")

    results = pd.DataFrame(rows).sort_values(["strategy", "date"])
    weights_frame = pd.DataFrame(weight_rows)
    rf_series = rf.reindex(sorted(results["date"].unique()))
    if rf_series.isna().any():
        raise SystemExit("risk-free series does not cover every rebalance date")

    summary = {}
    for name in STRATEGIES:
        series = results[results["strategy"] == name].set_index("date")["net_return"]
        if series.empty:
            continue
        basket = metric_basket(series, rf=rf_series.reindex(series.index))
        gross = results[results["strategy"] == name].set_index("date")["gross_return"]
        turnover = results[results["strategy"] == name].set_index("date")["turnover"]
        summary[name] = {
            **basket,
            "months": int(len(series)),
            "mean_net_return": float(series.mean()),
            "annualized_net_return": float((1.0 + series).prod() ** (12.0 / len(series)) - 1.0),
            "annualized_turnover": float(turnover.mean() * 12.0),
            "annualized_cost_drag": float((gross.mean() - series.mean()) * 12.0),
            "mean_n_assets": float(
                results[results["strategy"] == name]["n_assets"].mean()
            ),
            "mean_sigma": float(
                results[results["strategy"] == name]["mean_sigma"].mean()
            ),
            "mean_mu": float(results[results["strategy"] == name]["mean_mu"].mean()),
        }

    args.out.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.out / f"dro_experiment_returns{args.suffix}.csv", index=False)
    weights_frame.to_parquet(
        args.out / f"dro_experiment_weights{args.suffix}.parquet", index=False
    )
    (args.out / f"dro_experiment_summary{args.suffix}.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    print("\nReduced DRO experiment summary")
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out / f'dro_experiment_summary{args.suffix}.json'}")


if __name__ == "__main__":
    main()
