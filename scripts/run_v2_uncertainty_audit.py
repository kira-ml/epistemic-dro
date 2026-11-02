"""G-R4v2: does conformal sigma carry information about future tail outcomes?

Development period only. Uses date-blocked permutation nulls and a BH-FDR
screen. If sigma does not pass the 80% date-level rule, the v2 pre-registration
forbids touching the 2025-2026 holdout.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression

from epistemic_dro.data import load_panel
from epistemic_dro.features import build_targets

ROOT = Path(__file__).resolve().parents[1]


def _bh(pvalues: np.ndarray) -> np.ndarray:
    order = np.argsort(pvalues)
    ranked = pvalues[order]
    m = len(pvalues)
    q = ranked * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty_like(q)
    out[order] = np.clip(q, 0.0, 1.0)
    return out


def main() -> None:
    uncertainty = pd.read_parquet(ROOT / "results" / "tables" / "v2_uncertainty_dev.parquet")
    panel = load_panel(ROOT / "data" / "raw_v2")
    targets = build_targets(panel.returns).reset_index()
    targets = targets.rename(columns={targets.columns[-1]: "target"})
    frame = uncertainty.merge(targets, on=["date", "ticker"], how="inner")
    frame["abs_target"] = frame["target"].abs()
    frame["downside"] = (frame["target"] < 0.0).astype(float)

    dates = [date for date, group in frame.groupby("date") if len(group) >= 20]
    rng = np.random.default_rng(42)
    n_permutations = 30
    actual_rows = []
    null_rows = []
    p_rows = []

    for date in dates:
        group = frame[frame["date"] == date]
        x = group[["sigma", "interval_width"]].to_numpy(dtype=float)
        y = group["abs_target"].to_numpy(dtype=float)
        actual = mutual_info_regression(x, y, n_neighbors=5, random_state=0)
        null = np.empty((n_permutations, x.shape[1]))
        for permutation in range(n_permutations):
            shuffled = rng.permutation(y)
            null[permutation] = mutual_info_regression(
                x, shuffled, n_neighbors=5, random_state=0
            )
        pvalues = (1.0 + (null >= actual).sum(axis=0)) / (n_permutations + 1.0)
        actual_rows.append(actual)
        null_rows.append(null)
        p_rows.append(_bh(pvalues))

    actual_matrix = np.vstack(actual_rows)
    null_matrix = np.vstack(null_rows)
    q_matrix = np.vstack(p_rows)
    features = ["sigma", "interval_width"]
    summary = []
    for index, name in enumerate(features):
        pass_rate = float((q_matrix[:, index] < 0.05).mean())
        summary.append(
            {
                "feature": name,
                "mean_mi": float(actual_matrix[:, index].mean()),
                "mean_null_95": float(np.percentile(null_matrix[:, index], 95)),
                "median_qvalue": float(np.median(q_matrix[:, index])),
                "pass_rate": pass_rate,
                "survives": pass_rate >= 0.80,
            }
        )

    coverage = {
        "mean_validation_coverage": float(
            pd.read_csv(ROOT / "results" / "tables" / "v2_returns_dev.csv")
            .groupby("strategy")["validation_coverage"]
            .mean()
            .mean()
        ),
        "mean_test_coverage": float(
            pd.read_csv(ROOT / "results" / "tables" / "v2_returns_dev.csv")
            .groupby("strategy")["test_coverage"]
            .mean()
            .mean()
        ),
    }
    output = {
        "dates": len(dates),
        "permutations": n_permutations,
        "fdr": "BH q<0.05",
        "survival_rule": "pass_rate>=0.80",
        "features": summary,
        "coverage": coverage,
        "holdout_allowed": any(item["survives"] for item in summary),
        "note": (
            "Development-only audit. If no uncertainty feature survives, v2 stops "
            "before the 2025-2026 holdout."
        ),
    }
    out = ROOT / "results" / "tables" / "v2_uncertainty_audit.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
