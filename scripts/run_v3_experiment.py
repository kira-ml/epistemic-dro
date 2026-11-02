"""v3 experiment: conditional tail-risk forecast as DRO sigma.

This is not epistemic uncertainty. The model predicts |next-month excess
return| with LightGBM L1 regression; the forecast is calibrated on a 12-month
validation window and used as sigma. The comparator is each asset's trailing
36-month realized volatility.

Development period: 2010-01 .. 2024-11. Holdout: 2025-01 .. 2026-08, touched
only after the G-R4v3 gate passes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from epistemic_dro.baselines import fit_ridge_baseline
from epistemic_dro.data import load_panel
from epistemic_dro.evaluation import metric_basket
from epistemic_dro.features import FeatureSpec, build_features, build_targets
from epistemic_dro.optimization import DROSolution, solve_box_dro_cvar

ROOT = Path(__file__).resolve().parents[1]
STRATEGIES = ("M1_v3", "B5_uncond_sigma", "B3_CVaR", "B1_equal_weight")


def _predict_tail(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test_features: pd.DataFrame,
    feature_columns: list[str],
    abs_column: str,
    *,
    seeds: int,
    n_estimators: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    validation_predictions = []
    test_predictions = []
    for seed in range(seeds):
        model = lgb.LGBMRegressor(
            objective="regression_l1",
            n_estimators=n_estimators,
            learning_rate=0.03,
            num_leaves=15,
            max_depth=4,
            min_child_samples=50,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=seed,
            n_jobs=1,
            verbosity=-1,
        )
        model.fit(train[feature_columns], train[abs_column])
        validation_predictions.append(model.predict(validation[feature_columns]))
        test_predictions.append(model.predict(test_features[feature_columns]))

    val_pred = np.mean(np.vstack(validation_predictions), axis=0)
    test_pred = np.mean(np.vstack(test_predictions), axis=0)
    realized = validation[abs_column].to_numpy(dtype=float)
    scale = float(np.mean(realized) / max(np.mean(val_pred), 1e-12))
    scale = float(np.clip(scale, 0.5, 2.0))
    return val_pred, test_pred, scale


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
    parser = argparse.ArgumentParser(description="v3 conditional tail-risk experiment.")
    parser.add_argument("--period", choices=("dev", "holdout"), required=True)
    parser.add_argument("--raw", type=Path, default=ROOT / "data" / "raw_v2")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "tables")
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--n-estimators", type=int, default=200)
    args = parser.parse_args()

    panel = load_panel(args.raw)
    features = build_features(
        panel.prices, panel.metadata, panel.universe, panel.factors, FeatureSpec()
    )
    targets = build_targets(panel.returns)
    target_column = targets.columns[0]
    data = features.join(targets, how="inner").sort_index()
    data["abs_target"] = data[target_column].abs()
    feature_columns = list(features.columns)

    returns_pivot = (
        panel.returns.pivot(index="date", columns="ticker", values="ret").sort_index()
    )
    rf = panel.risk_free.set_index("date")["rf"].sort_index()
    all_dates = sorted(data.index.get_level_values("date").unique())
    date_position = {date: index for index, date in enumerate(all_dates)}
    if args.period == "dev":
        start, end = pd.Timestamp("2010-01-01"), pd.Timestamp("2024-11-30")
    else:
        start, end = pd.Timestamp("2025-01-01"), pd.Timestamp("2026-08-31")
    rebalance_dates = [date for date in all_dates if start <= date <= end]

    previous: dict[str, pd.Series | None] = {name: None for name in STRATEGIES}
    rows: list[dict] = []
    weight_rows: list[dict] = []
    sigma_rows: list[dict] = []

    for date in rebalance_dates:
        position = date_position[date]
        if position < 73:
            continue
        train_dates = all_dates[position - 73:position - 13]
        validation_dates = all_dates[position - 12:position]
        if len(train_dates) != 60 or len(validation_dates) != 12:
            continue
        train = data[data.index.get_level_values("date").isin(train_dates)]
        validation = data[data.index.get_level_values("date").isin(validation_dates)]
        if len(train) < 100 or len(validation) < 20:
            continue
        test = data.loc[date]
        test_features = features.loc[date]
        if test.empty or test_features.empty:
            continue

        try:
            _val_pred, test_pred, scale = _predict_tail(
                train,
                validation,
                test_features,
                feature_columns,
                "abs_target",
                seeds=args.seeds,
                n_estimators=args.n_estimators,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"skip {date.date()}: tail fit failed: {exc}")
            continue

        assets = list(test_features.index)
        sigma = pd.Series(np.maximum(scale * test_pred, 1e-6), index=assets)
        ridge = fit_ridge_baseline(
            train[feature_columns], train[target_column], alpha=1.0
        )
        mu = ridge.predict(test_features[feature_columns])

        scenario_window = returns_pivot.loc[:date].tail(60)
        scenario_window = scenario_window.reindex(columns=assets)
        scenario_window = scenario_window.dropna(axis=1, how="any").dropna(axis=0, how="any")
        if len(scenario_window) < 36 or scenario_window.shape[1] < 20:
            print(f"skip {date.date()}: insufficient scenario panel")
            continue
        assets = list(scenario_window.columns)
        mu = mu.reindex(assets)
        sigma = sigma.reindex(assets)
        next_returns = returns_pivot.shift(-1).loc[date].reindex(assets)
        valid = next_returns.notna()
        assets = [asset for asset in assets if valid[asset]]
        if len(assets) < 20:
            print(f"skip {date.date()}: insufficient assets")
            continue
        scenarios = scenario_window[assets]
        mu = mu.reindex(assets)
        sigma = sigma.reindex(assets)
        next_returns = next_returns.reindex(assets)
        if mu.isna().any() or sigma.isna().any():
            print(f"skip {date.date()}: missing forecast")
            continue

        realized_abs = (
            data.loc[date]["abs_target"].reindex(assets).to_numpy(dtype=float)
        )
        sigma_rows.extend(
            {
                "date": date,
                "ticker": ticker,
                "mu": float(mu[ticker]),
                "sigma": float(sigma[ticker]),
                "realized_abs": float(realized_abs[index]),
                "scale": scale,
            }
            for index, ticker in enumerate(assets)
        )

        for name in STRATEGIES:
            if name == "M1_v3":
                kappa, strategy_sigma = 1.0, sigma
            elif name == "B5_uncond_sigma":
                kappa = 1.0
                uncond = (returns_pivot.loc[:date].tail(36).std()).reindex(assets)
                strategy_sigma = uncond.fillna(float(sigma.median())).clip(lower=1e-6)
            else:
                kappa = 0.0
                strategy_sigma = pd.Series(1e-6, index=assets)

            weights, turnover, cost = _run_strategy(
                name, mu, strategy_sigma, scenarios, previous[name],
                kappa=kappa, cost_bps=args.cost_bps,
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
                    "mean_mu": float(mu.mean()),
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
        print(
            f"{date.date()}: {len(assets)} assets; "
            f"sigma {sigma.mean():.5f}; scale {scale:.3f}"
        )

    if not rows:
        raise SystemExit("no portfolio rows produced")

    results = pd.DataFrame(rows).sort_values(["strategy", "date"])
    weights_frame = pd.DataFrame(weight_rows)
    rf_series = rf.reindex(sorted(results["date"].unique()))
    if rf_series.isna().any():
        raise SystemExit("risk-free missing for a rebalance date")

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
            "mean_n_assets": float(results[results["strategy"] == name]["n_assets"].mean()),
            "mean_sigma": float(results[results["strategy"] == name]["mean_sigma"].mean()),
            "mean_mu": float(results[results["strategy"] == name]["mean_mu"].mean()),
        }

    args.out.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.period}"
    results.to_csv(args.out / f"v3_returns{suffix}.csv", index=False)
    weights_frame.to_parquet(args.out / f"v3_weights{suffix}.parquet", index=False)
    pd.DataFrame(sigma_rows).to_parquet(
        args.out / f"v3_sigma{suffix}.parquet", index=False
    )
    (args.out / f"v3_summary{suffix}.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print("\nv3 summary")
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out / f'v3_summary{suffix}.json'}")


if __name__ == "__main__":
    main()
