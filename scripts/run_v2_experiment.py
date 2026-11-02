"""v2 experiment: conformalized quantile LightGBM + constant-sigma DRO.

Development period: 2010-01 .. 2024-11.
Holdout period: 2025-01 .. 2026-08 (run only after docs-freeze-v2).

The model predicts q05/q50/q95 of next-month excess returns with LightGBM
quantile regression, averages 3 seeds, and calibrates the quantiles on a
12-month validation window with split conformal residual quantiles.

Uncertainty for DRO: sigma = (q95 - q05) / (2 * 1.645), floored.
Comparator: B5_const_sigma uses the cross-sectional median sigma (constant
across assets), so it has a real ambiguity radius but no asset-specific
uncertainty information.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from epistemic_dro.data import load_panel
from epistemic_dro.evaluation import metric_basket
from epistemic_dro.features import FeatureSpec, build_features, build_targets
from epistemic_dro.optimization import DROSolution, solve_box_dro_cvar

ROOT = Path(__file__).resolve().parents[1]
STRATEGIES = ("M1_v2", "B5_uncond_sigma", "B3_CVaR", "B1_equal_weight")
QUANTILES = (0.05, 0.50, 0.95)
Z90 = 1.6448536269514722


def _fit_predict_quantiles(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test_features: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    *,
    seeds: int,
    n_estimators: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Fit quantile ensemble, calibrate on validation, return test quantiles."""
    val_predictions = {q: [] for q in QUANTILES}
    test_predictions = {q: [] for q in QUANTILES}
    for seed in range(seeds):
        for quantile in QUANTILES:
            model = lgb.LGBMRegressor(
                objective="quantile",
                alpha=quantile,
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
            model.fit(train[feature_columns], train[target_column])
            val_predictions[quantile].append(model.predict(validation[feature_columns]))
            test_predictions[quantile].append(model.predict(test_features[feature_columns]))

    validation_target = validation[target_column].to_numpy(dtype=float)
    calibrated_test: list[np.ndarray] = []
    calibrated_val: list[np.ndarray] = []
    for quantile in QUANTILES:
        val_mean = np.mean(np.vstack(val_predictions[quantile]), axis=0)
        test_mean = np.mean(np.vstack(test_predictions[quantile]), axis=0)
        correction = float(np.quantile(validation_target - val_mean, quantile))
        calibrated_val.append(val_mean + correction)
        calibrated_test.append(test_mean + correction)

    val_matrix = np.column_stack(calibrated_val)
    test_matrix = np.column_stack(calibrated_test)
    test_matrix[:, 0] = np.minimum(test_matrix[:, 0], test_matrix[:, 1])
    test_matrix[:, 2] = np.maximum(test_matrix[:, 2], test_matrix[:, 1])
    val_matrix[:, 0] = np.minimum(val_matrix[:, 0], val_matrix[:, 1])
    val_matrix[:, 2] = np.maximum(val_matrix[:, 2], val_matrix[:, 1])
    return val_matrix, test_matrix, validation_target, test_features.index.to_numpy()


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
    parser = argparse.ArgumentParser(description="v2 conformal quantile DRO experiment.")
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
    data = features.join(targets, how="inner").sort_index()
    target_column = targets.columns[0]
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
    uncertainty_rows: list[dict] = []

    for date in rebalance_dates:
        position = date_position[date]
        if position < 73:
            continue
        validation_dates = all_dates[position - 12:position]
        train_dates = all_dates[position - 73:position - 13]
        if len(train_dates) != 60 or len(validation_dates) != 12:
            continue
        train = data[data.index.get_level_values("date").isin(train_dates)]
        validation = data[data.index.get_level_values("date").isin(validation_dates)]
        if len(train) < 100 or len(validation) < 20:
            continue

        test = data.loc[date] if date in data.index.get_level_values("date") else None
        if test is None or test.empty:
            continue
        test_features = features.loc[date]
        try:
            val_matrix, test_matrix, val_target, test_index = _fit_predict_quantiles(
                train,
                validation,
                test_features,
                feature_columns,
                target_column,
                seeds=args.seeds,
                n_estimators=args.n_estimators,
            )
        except Exception as exc:  # noqa: BLE001 - fatal for this date
            print(f"skip {date.date()}: quantile fit failed: {exc}")
            continue

        assets = list(test_features.index)
        mu = pd.Series(test_matrix[:, 1], index=assets, name="mu")
        lower = pd.Series(test_matrix[:, 0], index=assets)
        upper = pd.Series(test_matrix[:, 2], index=assets)
        sigma = ((upper - lower) / (2.0 * Z90)).clip(lower=1e-6)

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

        validation_coverage = float(
            np.mean(
                (val_target >= val_matrix[:, 0]) & (val_target <= val_matrix[:, 2])
            )
        )
        test_target = test[target_column].reindex(assets).to_numpy(dtype=float)
        test_coverage = float(
            np.mean(
                (test_target >= lower.reindex(assets))
                & (test_target <= upper.reindex(assets))
            )
        )
        uncertainty_rows.extend(
            {
                "date": date,
                "ticker": ticker,
                "mu": float(mu[ticker]),
                "sigma": float(sigma[ticker]),
                "lower": float(lower.reindex(assets)[ticker]),
                "upper": float(upper.reindex(assets)[ticker]),
                "interval_width": float(
                    upper.reindex(assets)[ticker] - lower.reindex(assets)[ticker]
                ),
            }
            for ticker in assets
        )

        for name in STRATEGIES:
            if name == "M1_v2":
                kappa, strategy_sigma = 1.0, sigma
            elif name == "B5_uncond_sigma":
                kappa = 1.0
                uncond = (
                    returns_pivot.loc[:date].tail(36).std()
                ).reindex(assets)
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
                    "validation_coverage": validation_coverage,
                    "test_coverage": test_coverage,
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
            f"sigma {sigma.mean():.6f}; val cov {validation_coverage:.3f}"
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
            "mean_validation_coverage": float(
                results[results["strategy"] == name]["validation_coverage"].mean()
            ),
            "mean_test_coverage": float(
                results[results["strategy"] == name]["test_coverage"].mean()
            ),
        }

    args.out.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.period}"
    results.to_csv(args.out / f"v2_returns{suffix}.csv", index=False)
    weights_frame.to_parquet(args.out / f"v2_weights{suffix}.parquet", index=False)
    pd.DataFrame(uncertainty_rows).to_parquet(
        args.out / f"v2_uncertainty{suffix}.parquet", index=False
    )
    (args.out / f"v2_summary{suffix}.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print("\nv2 summary")
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out / f'v2_summary{suffix}.json'}")


if __name__ == "__main__":
    main()
