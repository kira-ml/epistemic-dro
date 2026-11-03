"""Block-aware pooled MI gate.

The iid within-date permutation null can be anti-conservative when features and
targets are autocorrelated across dates. This script compares the actual pooled
MI against:

1. the iid within-date permutation null;
2. block-permutation nulls that preserve contiguous date blocks.

If the actual signal only passes the iid null and disappears under block
permutation, the pooled pass was a time-series artifact, not cross-sectional
information.

Development only. The 2025-2026 holdout is untouched.
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


def _center_rows(matrix: np.ndarray) -> np.ndarray:
    return matrix - matrix.mean(axis=1, keepdims=True)


def _iid_pvalue(
    x: np.ndarray,
    y: np.ndarray,
    *,
    n_permutations: int,
    seed: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    actual = _mi(x.ravel(), y.ravel())
    null = np.empty(n_permutations)
    for permutation in range(n_permutations):
        shuffled = np.vstack([rng.permutation(row) for row in y])
        null[permutation] = _mi(x.ravel(), shuffled.ravel())
    pvalue = (1.0 + float((null >= actual).sum())) / (n_permutations + 1.0)
    return actual, pvalue


def _block_permute(matrix: np.ndarray, block: int, rng: np.random.Generator) -> np.ndarray:
    blocks = [matrix[start:start + block] for start in range(0, len(matrix), block)]
    order = rng.permutation(len(blocks))
    return np.vstack([blocks[index] for index in order])


def _block_pvalue(
    x: np.ndarray,
    y: np.ndarray,
    *,
    block: int,
    n_permutations: int,
    seed: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    actual = _mi(x.ravel(), y.ravel())
    null = np.empty(n_permutations)
    for permutation in range(n_permutations):
        shuffled = _block_permute(y, block, rng)
        null[permutation] = _mi(x.ravel(), shuffled.ravel())
    pvalue = (1.0 + float((null >= actual).sum())) / (n_permutations + 1.0)
    return actual, pvalue


def _evaluate(
    name: str,
    x: np.ndarray,
    y: np.ndarray,
    *,
    n_permutations: int = 100,
    blocks: tuple[int, ...] = (6, 12, 24),
    seed: int = 42,
) -> dict:
    x_centered = _center_rows(x)
    y_centered = _center_rows(y)
    actual, iid_p = _iid_pvalue(
        x_centered, y_centered, n_permutations=n_permutations, seed=seed
    )
    block_results = {}
    for block in blocks:
        _, block_p = _block_pvalue(
            x_centered,
            y_centered,
            block=block,
            n_permutations=n_permutations,
            seed=seed + block,
        )
        block_results[str(block)] = block_p
    return {
        "signal": name,
        "pooled_mi": actual,
        "iid_pvalue": iid_p,
        "block_pvalues": block_results,
        "passes_iid": iid_p < 0.05,
        "passes_all_blocks": all(value < 0.05 for value in block_results.values()),
    }


def main() -> None:
    v1 = load_panel(ROOT / "data" / "raw")
    features = build_features(
        v1.prices, v1.metadata, v1.universe, v1.factors, FeatureSpec()
    )
    targets = build_targets(v1.returns)
    frame = features.join(targets, how="inner")
    target = targets.columns[0]
    dates = sorted(frame.index.get_level_values("date").unique())

    results = []
    for feature in features.columns:
        x = frame[feature].unstack("ticker").reindex(dates).to_numpy(dtype=float)
        y = frame[target].unstack("ticker").reindex(dates).to_numpy(dtype=float)
        mask = np.isfinite(x).all(axis=1) & np.isfinite(y).all(axis=1)
        results.append(_evaluate(f"v1:{feature}", x[mask], y[mask]))

    v2 = pd.read_parquet(PUBLISHED / "v2_uncertainty_dev.parquet")
    v2_targets = build_targets(load_panel(ROOT / "data" / "raw_v2").returns).reset_index()
    v2_targets = v2_targets.rename(columns={v2_targets.columns[-1]: "target"})
    v2 = v2.merge(v2_targets, on=["date", "ticker"], how="inner")
    v2["abs_target"] = v2["target"].abs()
    v2_x = v2.pivot(index="date", columns="ticker", values="sigma").sort_index()
    v2_y = v2.pivot(index="date", columns="ticker", values="abs_target").sort_index()
    v2_x, v2_y = v2_x.align(v2_y, join="inner")
    mask = v2_x.notna().all(axis=1) & v2_y.notna().all(axis=1)
    results.append(
        _evaluate(
            "v2:sigma",
            v2_x[mask].to_numpy(dtype=float),
            v2_y[mask].to_numpy(dtype=float),
        )
    )

    v3 = pd.read_parquet(PUBLISHED / "v3_sigma_dev.parquet")
    v3_x = v3.pivot(index="date", columns="ticker", values="sigma").sort_index()
    v3_y = v3.pivot(index="date", columns="ticker", values="realized_abs").sort_index()
    v3_x, v3_y = v3_x.align(v3_y, join="inner")
    mask = v3_x.notna().all(axis=1) & v3_y.notna().all(axis=1)
    results.append(
        _evaluate(
            "v3:sigma",
            v3_x[mask].to_numpy(dtype=float),
            v3_y[mask].to_numpy(dtype=float),
        )
    )

    output = {
        "permutations": 100,
        "blocks": [6, 12, 24],
        "results": results,
        "summary": {
            "iid_passes": sum(1 for row in results if row["passes_iid"]),
            "block_passes": sum(1 for row in results if row["passes_all_blocks"]),
            "total": len(results),
        },
        "note": (
            "Development only. A pooled signal that passes iid but not block "
            "permutation is a time-series artifact. Do not touch the holdout."
        ),
    }
    out = TABLES / "block_gate_study.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    for row in results:
        print(
            f"{row['signal']:24s} MI={row['pooled_mi']:.4f} "
            f"iid_p={row['iid_pvalue']:.3f} "
            f"block_p={row['block_pvalues']} "
            f"all_blocks={row['passes_all_blocks']}"
        )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
