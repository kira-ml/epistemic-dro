"""G-R1 / G-R7 diagnostics: noise floor, factor variance share, tail risk.

Writes a JSON report to ``results/tables/diagnostics.json``. The numbers are
descriptive properties of the frozen snapshot, not a model result.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from epistemic_dro.data import load_panel
from epistemic_dro.features import build_targets

ROOT = Path(__file__).resolve().parents[1]


def _hill_tail_index(losses: np.ndarray, fraction: float = 0.10) -> float | None:
    values = np.sort(losses[losses > 0.0])[::-1]
    if len(values) < 20:
        return None
    k = max(10, int(fraction * len(values)))
    if k >= len(values):
        return None
    threshold = values[k]
    if threshold <= 0.0:
        return None
    return float(k / np.sum(np.log(values[:k] / threshold)))


def main() -> None:
    panel = load_panel(ROOT / "data" / "raw")
    targets = build_targets(panel.returns)
    target_column = targets.columns[0]
    returns = panel.returns.merge(panel.factors, on="date", how="inner")

    target = targets[target_column].to_numpy(dtype=float)
    losses = -target[target < 0.0]

    cross_sectional_variance = targets.groupby(level="date")[target_column].var()
    breadth = targets.groupby(level="date")[target_column].size()

    y = returns["excess_ret"].to_numpy(dtype=float)
    factor_columns = ["mkt_rf", "smb", "hml", "mom"]
    x = returns[factor_columns].to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    residuals = y - design @ coefficients
    factor_r2 = 1.0 - float((residuals**2).sum() / ((y - y.mean()) ** 2).sum())

    report = {
        "snapshot": "data/raw",
        "target": target_column,
        "rows": int(len(target)),
        "months": int(targets.index.get_level_values("date").nunique()),
        "tickers": int(targets.index.get_level_values("ticker").nunique()),
        "target_mean": float(np.mean(target)),
        "target_std": float(np.std(target, ddof=1)),
        "target_skew": float(pd.Series(target).skew()),
        "target_kurtosis_excess": float(pd.Series(target).kurt()),
        "target_min": float(np.min(target)),
        "target_max": float(np.max(target)),
        "cross_sectional_variance_mean": float(cross_sectional_variance.mean()),
        "cross_sectional_variance_median": float(cross_sectional_variance.median()),
        "breadth_min": int(breadth.min()),
        "breadth_median": int(breadth.median()),
        "breadth_max": int(breadth.max()),
        "factor_regression_r2": factor_r2,
        "factor_regression_coefficients": dict(
            zip(["intercept", *factor_columns], map(float, coefficients), strict=True)
        ),
        "hill_tail_index_losses_10pct": _hill_tail_index(losses),
        "tail_loss_count": int(len(losses)),
        "note": (
            "factor_regression_r2 is the contemporaneous factor variance share, "
            "not predictive R^2; the linear predictive upper bound is the Ridge "
            "B0 OOS R^2 in ridge_b0_summary.json."
        ),
    }

    out = ROOT / "results" / "tables" / "diagnostics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
