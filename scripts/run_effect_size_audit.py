"""Effect-size audit of the block-aware survivors.

The gate study leaves three v1 features that survive a block-aware null:
mom_6m, vol_12m, downside_vol_12m. This script asks whether any of them has an
economically meaningful cross-sectional rank IC, and does the same for the v2
and v3 sigma.

This is a development-only diagnostic. It does not touch the holdout.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from epistemic_dro.data import load_panel
from epistemic_dro.features import FeatureSpec, build_features, build_targets

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
PUBLISHED = ROOT / "paper" / "published-results"
SURVIVORS = ("mom_6m", "vol_12m", "downside_vol_12m")


def _rank_ic(feature: np.ndarray, target: np.ndarray) -> float:
    frame = pd.DataFrame({"feature": feature, "target": target}).dropna()
    if len(frame) < 10:
        return float("nan")
    if frame["feature"].nunique() < 3 or frame["target"].nunique() < 3:
        return float("nan")
    return float(frame["feature"].corr(frame["target"], method="spearman"))


def _ic_series(x: np.ndarray, y: np.ndarray) -> pd.Series:
    values = [_rank_ic(x[index], y[index]) for index in range(len(x))]
    return pd.Series(values).dropna()


def _block_bootstrap_ci(
    values: np.ndarray,
    *,
    block: int = 12,
    reps: int = 2000,
    seed: int = 42,
) -> list[float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    n_blocks = math.ceil(n / block)
    means = np.empty(reps)
    for repeat in range(reps):
        starts = rng.integers(0, max(1, n - block + 1), size=n_blocks)
        indices = np.concatenate(
            [np.arange(start, min(start + block, n)) for start in starts]
        )[:n]
        means[repeat] = values[indices].mean()
    return [float(np.percentile(means, 5)), float(np.percentile(means, 95))]


def _summarize(name: str, ic: pd.Series) -> dict:
    mean = float(ic.mean())
    std = float(ic.std(ddof=1))
    tstat = mean / (std / math.sqrt(len(ic))) if std > 0 else float("nan")
    ci = _block_bootstrap_ci(ic.to_numpy(dtype=float))
    return {
        "signal": name,
        "months": int(len(ic)),
        "mean_ic": mean,
        "ic_std": std,
        "icir": mean / std if std > 0 else float("nan"),
        "t_stat": tstat,
        "block_ci90": ci,
        "clears_002": abs(mean) >= 0.02,
        "clears_002_and_ci": abs(mean) >= 0.02 and (ci[0] > 0.0 or ci[1] < 0.0),
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
        ic = _ic_series(x[mask], y[mask])
        results.append(_summarize(f"v1:{feature}", ic))

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
        _summarize(
            "v2:sigma",
            _ic_series(v2_x[mask].to_numpy(dtype=float), v2_y[mask].to_numpy(dtype=float)),
        )
    )

    v2_panel = load_panel(ROOT / "data" / "raw_v2")
    trailing = v2_panel.returns.pivot(index="date", columns="ticker", values="ret")
    trailing = trailing.rolling(36).std().stack().rename("trailing_vol").reset_index()
    trailing.columns = ["date", "ticker", "trailing_vol"]
    v2_vol = v2.merge(trailing, on=["date", "ticker"], how="inner")
    v2_vol_x = v2_vol.pivot(index="date", columns="ticker", values="trailing_vol").sort_index()
    v2_vol_y = v2_vol.pivot(index="date", columns="ticker", values="abs_target").sort_index()
    v2_vol_x, v2_vol_y = v2_vol_x.align(v2_vol_y, join="inner")
    mask = v2_vol_x.notna().all(axis=1) & v2_vol_y.notna().all(axis=1)
    results.append(
        _summarize(
            "v2:trailing_vol",
            _ic_series(v2_vol_x[mask].to_numpy(dtype=float), v2_vol_y[mask].to_numpy(dtype=float)),
        )
    )

    v3 = pd.read_parquet(PUBLISHED / "v3_sigma_dev.parquet")
    v3_x = v3.pivot(index="date", columns="ticker", values="sigma").sort_index()
    v3_y = v3.pivot(index="date", columns="ticker", values="realized_abs").sort_index()
    v3_x, v3_y = v3_x.align(v3_y, join="inner")
    mask = v3_x.notna().all(axis=1) & v3_y.notna().all(axis=1)
    results.append(
        _summarize(
            "v3:sigma",
            _ic_series(v3_x[mask].to_numpy(dtype=float), v3_y[mask].to_numpy(dtype=float)),
        )
    )

    v3_vol = v3.merge(trailing, on=["date", "ticker"], how="inner")
    v3_vol_x = v3_vol.pivot(index="date", columns="ticker", values="trailing_vol").sort_index()
    v3_vol_y = v3_vol.pivot(index="date", columns="ticker", values="realized_abs").sort_index()
    v3_vol_x, v3_vol_y = v3_vol_x.align(v3_vol_y, join="inner")
    mask = v3_vol_x.notna().all(axis=1) & v3_vol_y.notna().all(axis=1)
    results.append(
        _summarize(
            "v3:trailing_vol",
            _ic_series(v3_vol_x[mask].to_numpy(dtype=float), v3_vol_y[mask].to_numpy(dtype=float)),
        )
    )

    output = {
        "survivors": list(SURVIVORS),
        "results": results,
        "summary": {
            "survivor_mean_ics": {
                name: next(row["mean_ic"] for row in results if row["signal"] == f"v1:{name}")
                for name in SURVIVORS
            },
            "any_survivor_clears_002": any(
                row["clears_002"]
                for row in results
                if row["signal"].split(":", 1)[1] in SURVIVORS
            ),
            "any_survivor_clears_002_and_ci": any(
                row["clears_002_and_ci"]
                for row in results
                if row["signal"].split(":", 1)[1] in SURVIVORS
            ),
            "v2_sigma_mean_ic": next(
                row["mean_ic"] for row in results if row["signal"] == "v2:sigma"
            ),
            "v3_sigma_mean_ic": next(
                row["mean_ic"] for row in results if row["signal"] == "v3:sigma"
            ),
            "v2_trailing_vol_mean_ic": next(
                row["mean_ic"] for row in results if row["signal"] == "v2:trailing_vol"
            ),
            "v3_trailing_vol_mean_ic": next(
                row["mean_ic"] for row in results if row["signal"] == "v3:trailing_vol"
            ),
        },
        "note": (
            "Development-only rank IC. The 0.02 bar is a diagnostic for whether "
            "a v4 is worth designing, not a pre-registered v1/v2/v3 decision."
        ),
    }
    out = TABLES / "effect_size_audit.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    for row in sorted(results, key=lambda item: item["mean_ic"], reverse=True):
        print(
            f"{row['signal']:24s} IC={row['mean_ic']:+.4f} "
            f"t={row['t_stat']:+.2f} CI={row['block_ci90']} clears={row['clears_002']}"
        )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
