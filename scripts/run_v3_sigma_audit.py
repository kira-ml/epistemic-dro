"""G-R4v3: does the conditional tail forecast carry information about realized tail risk?

Development only. If the pass rate is below 0.80, the v3 pre-registration
forbids touching the 2025-2026 holdout.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression

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
    frame = pd.read_parquet(ROOT / "results" / "tables" / "v3_sigma_dev.parquet")
    frame = frame.dropna(subset=["sigma", "realized_abs"])
    dates = [date for date, group in frame.groupby("date") if len(group) >= 20]
    rng = np.random.default_rng(42)
    n_permutations = 30
    actual_rows = []
    null_rows = []
    p_rows = []

    for date in dates:
        group = frame[frame["date"] == date]
        x = group[["sigma"]].to_numpy(dtype=float)
        y = group["realized_abs"].to_numpy(dtype=float)
        actual = mutual_info_regression(x, y, n_neighbors=5, random_state=0)
        null = np.empty((n_permutations, 1))
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
    pass_rate = float((q_matrix[:, 0] < 0.05).mean())

    correlation = float(frame["sigma"].corr(frame["realized_abs"]))
    top = frame[frame["sigma"] >= frame["sigma"].quantile(0.9)]["realized_abs"].mean()
    bottom = frame[frame["sigma"] <= frame["sigma"].quantile(0.1)]["realized_abs"].mean()
    calibration = {
        "mean_sigma": float(frame["sigma"].mean()),
        "mean_realized_abs": float(frame["realized_abs"].mean()),
        "correlation": correlation,
        "top_decile_realized_abs": float(top),
        "bottom_decile_realized_abs": float(bottom),
        "decile_spread": float(top - bottom),
    }

    output = {
        "dates": len(dates),
        "permutations": n_permutations,
        "fdr": "BH q<0.05",
        "survival_rule": "pass_rate>=0.80",
        "sigma": {
            "mean_mi": float(actual_matrix[:, 0].mean()),
            "mean_null_95": float(np.percentile(null_matrix[:, 0], 95)),
            "median_qvalue": float(np.median(q_matrix[:, 0])),
            "pass_rate": pass_rate,
            "survives": pass_rate >= 0.80,
        },
        "calibration": calibration,
        "holdout_allowed": pass_rate >= 0.80,
        "note": (
            "Development-only tail-forecast information audit. If the gate fails, "
            "the 2025-2026 holdout remains untouched."
        ),
    }
    out = ROOT / "results" / "tables" / "v3_sigma_audit.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
