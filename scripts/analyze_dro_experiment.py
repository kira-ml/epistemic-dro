"""Paired bootstrap analysis of the reduced DRO experiment.

Compares M1_reduced against B5_DRO_point (uncertainty ablation), B3_CVaR, and
B1_equal_weight. Reports 90% bootstrap intervals for Sharpe, max drawdown,
CVaR95, and relative tail improvement.

H1 requires a 20% relative max-drawdown improvement and a CVaR95 interval that
excludes zero. H2 is the 0.20 Sharpe non-inferiority margin. H3 is the
uncertainty ablation separation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _metrics(net: np.ndarray, rf: np.ndarray) -> dict[str, float]:
    excess = net - rf
    std = float(np.std(excess, ddof=1))
    sharpe = float(np.mean(excess) / std * math.sqrt(12.0)) if std > 0 else float("nan")
    wealth = np.cumprod(1.0 + net)
    drawdown = wealth / np.maximum.accumulate(wealth) - 1.0
    mdd = float(np.min(drawdown))
    tail = max(1, int(math.ceil(0.05 * len(net))))
    cvar = float(np.mean(np.sort(net)[:tail]))
    return {"net_sharpe": sharpe, "max_drawdown": mdd, "cvar95": cvar}


def _ci(values: np.ndarray) -> list[float]:
    return [float(np.nanpercentile(values, 5)), float(np.nanpercentile(values, 95))]


def _bootstrap_diff(
    a: np.ndarray,
    b: np.ndarray,
    rf: np.ndarray,
    *,
    reps: int = 2000,
    seed: int = 42,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    n = len(a)
    sharpe_diff = np.empty(reps)
    mdd_diff = np.empty(reps)
    cvar_diff = np.empty(reps)
    relative_mdd = np.empty(reps)
    relative_cvar = np.empty(reps)
    for repeat in range(reps):
        index = rng.integers(0, n, size=n)
        metrics_a = _metrics(a[index], rf[index])
        metrics_b = _metrics(b[index], rf[index])
        sharpe_diff[repeat] = metrics_a["net_sharpe"] - metrics_b["net_sharpe"]
        mdd_diff[repeat] = metrics_a["max_drawdown"] - metrics_b["max_drawdown"]
        cvar_diff[repeat] = metrics_a["cvar95"] - metrics_b["cvar95"]
        relative_mdd[repeat] = (
            (metrics_b["max_drawdown"] - metrics_a["max_drawdown"])
            / abs(metrics_b["max_drawdown"])
            if metrics_b["max_drawdown"] != 0.0
            else float("nan")
        )
        relative_cvar[repeat] = (
            (metrics_b["cvar95"] - metrics_a["cvar95"]) / abs(metrics_b["cvar95"])
            if metrics_b["cvar95"] != 0.0
            else float("nan")
        )
    return {
        "sharpe_diff_mean": float(sharpe_diff.mean()),
        "sharpe_diff_ci90": _ci(sharpe_diff),
        "sharpe_diff_positive_share": float((sharpe_diff > 0).mean()),
        "mdd_diff_mean": float(mdd_diff.mean()),
        "mdd_diff_ci90": _ci(mdd_diff),
        "relative_mdd_mean": float(np.nanmean(relative_mdd)),
        "relative_mdd_ci90": _ci(relative_mdd),
        "cvar_diff_mean": float(cvar_diff.mean()),
        "cvar_diff_ci90": _ci(cvar_diff),
        "relative_cvar_mean": float(np.nanmean(relative_cvar)),
        "relative_cvar_ci90": _ci(relative_cvar),
    }


def main() -> None:
    results = pd.read_csv(ROOT / "results" / "tables" / "dro_experiment_returns.csv")
    risk_free = pd.read_parquet(ROOT / "data" / "raw" / "risk_free.parquet")
    risk_free = risk_free.set_index("date")["rf"].sort_index()
    pivot = results.pivot(index="date", columns="strategy", values="net_return").sort_index()
    frames = pivot.dropna()
    rf = risk_free.reindex(pd.to_datetime(frames.index))
    if rf.isna().any():
        raise SystemExit("risk-free missing for some experiment dates")

    strategies = list(frames.columns)
    point = {name: _metrics(frames[name].to_numpy(), rf.to_numpy()) for name in strategies}
    comparisons = {}
    for baseline in ("B5_DRO_point", "B3_CVaR", "B1_equal_weight"):
        if baseline not in frames:
            continue
        comparisons[baseline] = _bootstrap_diff(
            frames["M1_reduced"].to_numpy(),
            frames[baseline].to_numpy(),
            rf.to_numpy(),
        )

    best_baseline = max(
        ("B5_DRO_point", "B3_CVaR", "B1_equal_weight"),
        key=lambda name: point[name]["net_sharpe"],
    )
    h2_comparison = comparisons[best_baseline]
    h1 = comparisons["B5_DRO_point"]
    h3 = comparisons["B5_DRO_point"]

    verdict = {
        "H1_tail_improvement": {
            "mdd_improvement_observed": point["B5_DRO_point"]["max_drawdown"]
            - point["M1_reduced"]["max_drawdown"],
            "relative_mdd_ci90": h1["relative_mdd_ci90"],
            "cvar_diff_ci90": h1["cvar_diff_ci90"],
            "passes_20pct_mdd": h1["relative_mdd_ci90"][0] >= 0.20,
            "passes_cvar_excludes_zero": h1["cvar_diff_ci90"][0] > 0.0,
            "verdict": (
                "PASS"
                if h1["relative_mdd_ci90"][0] >= 0.20
                and h1["cvar_diff_ci90"][0] > 0.0
                else "FAIL"
            ),
        },
        "H2_sharpe_non_inferiority": {
            "best_baseline": best_baseline,
            "sharpe_diff": point["M1_reduced"]["net_sharpe"] - point[best_baseline]["net_sharpe"],
            "sharpe_diff_ci90": h2_comparison["sharpe_diff_ci90"],
            "margin": -0.20,
            "verdict": (
                "PASS"
                if h2_comparison["sharpe_diff_ci90"][0] >= -0.20
                else "FAIL"
            ),
        },
        "H3_uncertainty_ablation": {
            "mdd_diff_ci90": h3["mdd_diff_ci90"],
            "cvar_diff_ci90": h3["cvar_diff_ci90"],
            "passes_mdd_separation": h3["mdd_diff_ci90"][0] > 0.0,
            "passes_cvar_separation": h3["cvar_diff_ci90"][0] > 0.0,
            "verdict": (
                "PASS"
                if h3["mdd_diff_ci90"][0] > 0.0
                and h3["cvar_diff_ci90"][0] > 0.0
                else "FAIL"
            ),
        },
    }

    output = {
        "months": int(len(frames)),
        "point_estimates": point,
        "comparisons": comparisons,
        "verdict": verdict,
        "note": (
            "Reduced M1 uses Ridge B0 mean + bootstrap ensemble sigma. "
            "It is not the original LightGBM M1. H1/H3 failure is a negative "
            "result, not a reason to add capacity."
        ),
    }
    out = ROOT / "results" / "tables" / "dro_experiment_analysis.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
