"""Run the mandatory Ridge B0 walk-forward baseline (G-R6 / G-R1).

The baseline is deliberately simple and is fitted only on each training window.
It reports forecast quality, not portfolio performance:

- pooled out-of-sample R^2;
- mean monthly cross-sectional rank IC and ICIR;
- hit rate;
- fold-level metrics.

It does not tune alpha. Alpha is the frozen baseline value (1.0). No test data
is used for fitting or feature selection.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from epistemic_dro.backtest import walk_forward_splits
from epistemic_dro.baselines import fit_ridge_baseline
from epistemic_dro.data import load_panel
from epistemic_dro.features import FeatureSpec, build_features, build_targets

ROOT = Path(__file__).resolve().parents[1]


def _rank_ic(group: pd.DataFrame, target: str, prediction: str) -> float:
    if len(group) < 5:
        return float("nan")
    if group[target].std() == 0.0 or group[prediction].std() == 0.0:
        return float("nan")
    return float(group[target].corr(group[prediction], method="spearman"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk-forward Ridge B0 baseline.")
    parser.add_argument("--raw", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "tables")
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--report-start", default="2010-01-01")
    parser.add_argument(
        "--shuffle-target",
        action="store_true",
        help="Shuffle the target within each date as a leakage falsification test.",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    panel = load_panel(args.raw)
    features = build_features(
        panel.prices, panel.metadata, panel.universe, panel.factors, FeatureSpec()
    )
    targets = build_targets(panel.returns)
    data = features.join(targets, how="inner").sort_index()
    target_column = targets.columns[0]
    if args.shuffle_target:
        rng = np.random.default_rng(args.seed)
        data[target_column] = data.groupby(level="date")[target_column].transform(
            lambda values: rng.permutation(values.to_numpy())
        )
        print(f"shuffled target within each date (seed={args.seed})")

    dates = sorted(data.index.get_level_values("date").unique())
    splits = walk_forward_splits(
        len(dates),
        train_min=60,
        validation=12,
        test=12,
        purge=1,
        embargo=1,
    )
    if not splits:
        raise SystemExit("no walk-forward splits; not enough history")

    predictions: list[pd.DataFrame] = []
    fold_rows: list[dict] = []
    for fold, split in enumerate(splits, start=1):
        train_dates = [dates[i] for i in split.train]
        test_dates = [dates[i] for i in split.test]
        train = data[data.index.get_level_values("date").isin(train_dates)].copy()
        test = data[data.index.get_level_values("date").isin(test_dates)].copy()
        if len(train) < 100 or len(test) == 0:
            continue

        baseline = fit_ridge_baseline(
            train[features.columns], train[target_column], alpha=args.alpha
        )
        test["prediction"] = baseline.predict(test[features.columns])
        predictions.append(
            test.reset_index()[["date", "ticker", target_column, "prediction"]]
        )

        fold_ic = pd.Series(
            {
                date: _rank_ic(group, target_column, "prediction")
                for date, group in test.reset_index().groupby("date")
            }
        ).dropna()
        fold_rows.append(
            {
                "fold": fold,
                "train_start": str(train_dates[0].date()),
                "train_end": str(train_dates[-1].date()),
                "test_start": str(test_dates[0].date()),
                "test_end": str(test_dates[-1].date()),
                "train_rows": int(len(train)),
                "test_rows": int(len(test)),
                "mean_ic": float(fold_ic.mean()) if len(fold_ic) else float("nan"),
            }
        )

    if not predictions:
        raise SystemExit("no baseline predictions were produced")

    oos = pd.concat(predictions, ignore_index=True).sort_values(["date", "ticker"])
    oos = oos[oos["date"] >= pd.Timestamp(args.report_start)].copy()
    if oos.empty:
        raise SystemExit(f"no OOS rows on or after {args.report_start}")

    residuals = oos[target_column] - oos["prediction"]
    total_variance = ((oos[target_column] - oos[target_column].mean()) ** 2).sum()
    r2 = 1.0 - float((residuals**2).sum() / total_variance)
    ic_series = pd.Series(
        {
            date: _rank_ic(group, target_column, "prediction")
            for date, group in oos.groupby("date")
        }
    ).dropna()
    mean_ic = float(ic_series.mean())
    std_ic = float(ic_series.std(ddof=1))
    icir = mean_ic / std_ic if std_ic > 0 else float("nan")
    ic_t_stat = mean_ic / (std_ic / np.sqrt(len(ic_series))) if std_ic > 0 else float("nan")
    hit_rate = float((np.sign(oos[target_column]) == np.sign(oos["prediction"])).mean())

    summary = {
        "baseline": "B0 Ridge",
        "alpha": args.alpha,
        "report_start": args.report_start,
        "folds": len(fold_rows),
        "oos_rows": int(len(oos)),
        "oos_months": int(oos["date"].nunique()),
        "oos_tickers": int(oos["ticker"].nunique()),
        "pooled_oos_r2": r2,
        "mean_rank_ic": mean_ic,
        "ic_std": std_ic,
        "ic_t_stat": ic_t_stat,
        "icir_monthly": icir,
        "icir_annualized": icir * np.sqrt(12.0),
        "hit_rate": hit_rate,
        "shuffled_target": bool(args.shuffle_target),
        "shuffle_seed": args.seed if args.shuffle_target else None,
        "fold_metrics": fold_rows,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    suffix = "_shuffled" if args.shuffle_target else ""
    predictions_path = args.out / f"ridge_b0_oos_predictions{suffix}.parquet"
    summary_path = args.out / f"ridge_b0_summary{suffix}.json"
    oos.to_parquet(predictions_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print("Ridge B0 walk-forward baseline")
    for key in ("folds", "oos_rows", "oos_months", "oos_tickers", "pooled_oos_r2",
                "mean_rank_ic", "ic_std", "ic_t_stat", "icir_monthly",
                "icir_annualized", "hit_rate"):
        print(f"  {key}: {summary[key]}")
    print(f"wrote {summary_path}")
    print(f"wrote {predictions_path}")


if __name__ == "__main__":
    main()
