"""Re-evaluate the actual development signals with a pooled MI gate.

The original v1/v2/v3 gates used an 80% date-level pass rule. The simulation
shows that rule has near-zero power at realistic effect sizes. This script asks
the narrower question: would the actual development features/sigma pass a
pooled, date-blocked MI test?

Development only. The 2025-2026 holdout is not used.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression

from epistemic_dro.data import load_panel
from epistemic_dro.features import FeatureSpec, build_features, build_targets

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
PUBLISHED = ROOT / "paper" / "published-results"


def _mi(x: np.ndarray, y: np.ndarray) -> float:
    return float(
        mutual_info_regression(x.reshape(-1, 1), y, n_neighbors=5, random_state=0)[0]
    )


def _pooled_pvalue_long(
    x: np.ndarray,
    y: np.ndarray,
    dates: pd.Series,
    *,
    n_permutations: int = 30,
    seed: int = 0,
) -> tuple[float, float]:
    """Pooled MI on within-date-centered long data, date-blocked null."""
    codes, uniques = pd.factorize(dates, sort=True)
    n_groups = len(uniques)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    counts = np.bincount(codes, minlength=n_groups)
    x_centered = x - (np.bincount(codes, weights=x, minlength=n_groups) / counts)[codes]
    y_centered = y - (np.bincount(codes, weights=y, minlength=n_groups) / counts)[codes]

    actual = _mi(x_centered, y_centered)
    rng = np.random.default_rng(seed)
    null = np.empty(n_permutations)
    for permutation in range(n_permutations):
        shuffled = y_centered.copy()
        for code in range(n_groups):
            mask = codes == code
            shuffled[mask] = rng.permutation(shuffled[mask])
        null[permutation] = _mi(x_centered, shuffled)
    pvalue = (1.0 + float((null >= actual).sum())) / (n_permutations + 1.0)
    return actual, pvalue


def _bh(pvalues: list[float]) -> list[float]:
    values = np.array(pvalues)
    order = np.argsort(values)
    ranked = values[order]
    m = len(values)
    q = ranked * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty_like(q)
    out[order] = np.clip(q, 0.0, 1.0)
    return out.tolist()


def main() -> None:
    v1 = load_panel(ROOT / "data" / "raw")
    features = build_features(
        v1.prices, v1.metadata, v1.universe, v1.factors, FeatureSpec()
    )
    targets = build_targets(v1.returns)
    frame = features.join(targets, how="inner")
    target = targets.columns[0]
    dates = pd.Series(frame.index.get_level_values("date"))

    feature_rows = []
    raw_pvalues = []
    for feature in features.columns:
        actual, pvalue = _pooled_pvalue_long(
            frame[feature].to_numpy(dtype=float),
            frame[target].to_numpy(dtype=float),
            dates,
        )
        feature_rows.append({"feature": feature, "pooled_mi": actual, "pvalue": pvalue})
        raw_pvalues.append(pvalue)
    qvalues = _bh(raw_pvalues)
    for row, qvalue in zip(feature_rows, qvalues, strict=True):
        row["bh_q"] = qvalue
        row["passes"] = qvalue < 0.05

    v2 = pd.read_parquet(PUBLISHED / "v2_uncertainty_dev.parquet")
    v2_targets = build_targets(load_panel(ROOT / "data" / "raw_v2").returns).reset_index()
    v2_targets = v2_targets.rename(columns={v2_targets.columns[-1]: "target"})
    v2 = v2.merge(v2_targets, on=["date", "ticker"], how="inner")
    v2["abs_target"] = v2["target"].abs()
    v2_mi, v2_p = _pooled_pvalue_long(
        v2["sigma"].to_numpy(dtype=float),
        v2["abs_target"].to_numpy(dtype=float),
        pd.Series(v2["date"]),
    )

    v3 = pd.read_parquet(PUBLISHED / "v3_sigma_dev.parquet")
    v3_mi, v3_p = _pooled_pvalue_long(
        v3["sigma"].to_numpy(dtype=float),
        v3["realized_abs"].to_numpy(dtype=float),
        pd.Series(v3["date"]),
    )

    output = {
        "v1_features": feature_rows,
        "v2_sigma": {"pooled_mi": v2_mi, "pvalue": v2_p, "passes": v2_p < 0.05},
        "v3_sigma": {"pooled_mi": v3_mi, "pvalue": v3_p, "passes": v3_p < 0.05},
        "note": (
            "Development only. The original 80% date-level gate is not the same "
            "test as this pooled gate; a pass here does not retroactively promote "
            "v2/v3 to the holdout. It measures whether the development signal was "
            "detectable at all."
        ),
    }
    out = TABLES / "gate_reevaluation.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
