"""Gate power study: size and power of the pre-holdout information gate.

The v2/v3 gate required a feature to beat a date-blocked permutation null in at
least 80% of dates. This script simulates panels with a known signal and
measures:

- false-positive rate under the null (beta = 0);
- power at realistic signal strengths;
- how power changes with assets (50/72/150) and dates (60/179);
- whether a pooled MI gate or a decile-spread gate is more powerful.

The simulation is synthetic and does not touch the 2025-2026 holdout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"


def _mi(values: np.ndarray, target: np.ndarray) -> float:
    return float(
        mutual_info_regression(
            values.reshape(-1, 1), target, n_neighbors=5, random_state=0
        )[0]
    )


def _mi_gate(
    features: np.ndarray,
    target: np.ndarray,
    *,
    n_permutations: int = 30,
    alpha: float = 0.05,
    pass_threshold: float = 0.80,
    seed: int = 0,
) -> tuple[float, bool]:
    """Date-blocked MI gate; returns pass rate and gate decision."""
    rng = np.random.default_rng(seed)
    passes = []
    for date in range(features.shape[0]):
        x = features[date]
        y = target[date]
        actual = _mi(x, y)
        null = np.array([_mi(x, rng.permutation(y)) for _ in range(n_permutations)])
        pvalue = (1.0 + float((null >= actual).sum())) / (n_permutations + 1.0)
        passes.append(pvalue < alpha)
    pass_rate = float(np.mean(passes))
    return pass_rate, pass_rate >= pass_threshold


def _pooled_gate(
    features: np.ndarray,
    target: np.ndarray,
    *,
    n_permutations: int = 30,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, bool]:
    """Pooled MI gate on within-date-centered data."""
    x = features - features.mean(axis=1, keepdims=True)
    y = target - target.mean(axis=1, keepdims=True)
    rng = np.random.default_rng(seed)
    actual = _mi(x.ravel(), y.ravel())
    null = np.empty(n_permutations)
    for permutation in range(n_permutations):
        shuffled = np.vstack([rng.permutation(row) for row in y])
        null[permutation] = _mi(x.ravel(), shuffled.ravel())
    pvalue = (1.0 + float((null >= actual).sum())) / (n_permutations + 1.0)
    return pvalue, pvalue < alpha


def _decile_gate(
    features: np.ndarray,
    target: np.ndarray,
    *,
    n_permutations: int = 30,
    alpha: float = 0.05,
    pass_threshold: float = 0.80,
    seed: int = 0,
) -> tuple[float, bool]:
    """Per-date top-minus-bottom decile spread gate."""
    rng = np.random.default_rng(seed)
    passes = []
    for date in range(features.shape[0]):
        x = features[date]
        y = target[date]
        order = np.argsort(x)
        k = max(1, len(x) // 10)
        actual = float(y[order[-k:]].mean() - y[order[:k]].mean())
        null = np.empty(n_permutations)
        for permutation in range(n_permutations):
            shuffled = rng.permutation(y)
            null[permutation] = float(
                shuffled[order[-k:]].mean() - shuffled[order[:k]].mean()
            )
        pvalue = (1.0 + float((np.abs(null) >= abs(actual)).sum())) / (
            n_permutations + 1.0
        )
        passes.append(pvalue < alpha)
    pass_rate = float(np.mean(passes))
    return pass_rate, pass_rate >= pass_threshold


def _simulate(
    n_assets: int,
    n_dates: int,
    beta: float,
    signal: str,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    features = rng.normal(size=(n_dates, n_assets))
    noise = rng.normal(size=(n_dates, n_assets))
    if signal == "linear":
        target = beta * features + noise
    elif signal == "quadratic":
        target = beta * (features**2 - 1.0) + noise
    else:
        raise ValueError(f"unknown signal: {signal}")
    return features, target


def main() -> None:
    parser = argparse.ArgumentParser(description="Gate power study.")
    parser.add_argument("--quick", action="store_true", help="One pilot scenario.")
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--assets", default="50,72,150")
    parser.add_argument("--dates", default="60,179")
    parser.add_argument("--betas", default="0.0,0.1,0.2,0.3,0.5")
    parser.add_argument("--signals", default="linear,quadratic")
    args = parser.parse_args()

    assets = [int(value) for value in args.assets.split(",")]
    dates = [int(value) for value in args.dates.split(",")]
    betas = [float(value) for value in args.betas.split(",")]
    signals = args.signals.split(",")

    if args.quick:
        assets, dates, betas, signals, args.seeds = [72], [179], [0.0, 0.2, 0.5], ["linear"], 1

    rows: list[dict] = []
    for n_assets in assets:
        for n_dates in dates:
            for beta in betas:
                for signal in signals:
                    for seed in range(args.seeds):
                        features, target = _simulate(n_assets, n_dates, beta, signal, seed)
                        mi_pass, mi_decision = _mi_gate(features, target, seed=seed)
                        pooled_p, pooled_decision = _pooled_gate(features, target, seed=seed)
                        decile_pass, decile_decision = _decile_gate(
                            features, target, seed=seed
                        )
                        rows.append(
                            {
                                "n_assets": n_assets,
                                "n_dates": n_dates,
                                "beta": beta,
                                "signal": signal,
                                "seed": seed,
                                "mi_pass_rate": mi_pass,
                                "mi_gate": mi_decision,
                                "pooled_pvalue": pooled_p,
                                "pooled_gate": pooled_decision,
                                "decile_pass_rate": decile_pass,
                                "decile_gate": decile_decision,
                            }
                        )
                        print(
                            f"assets={n_assets} dates={n_dates} beta={beta} "
                            f"signal={signal} seed={seed} "
                            f"mi_pass={mi_pass:.3f} gate={mi_decision} "
                            f"pooled={pooled_p:.3f} decile={decile_pass:.3f}"
                        )

    results = pd.DataFrame(rows)
    TABLES.mkdir(parents=True, exist_ok=True)
    results.to_csv(TABLES / "gate_power_study.csv", index=False)

    summary = (
        results.groupby(["n_assets", "n_dates", "beta", "signal"])
        .agg(
            mi_power=("mi_gate", "mean"),
            mi_pass_rate=("mi_pass_rate", "mean"),
            pooled_power=("pooled_gate", "mean"),
            decile_power=("decile_gate", "mean"),
            decile_pass_rate=("decile_pass_rate", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(TABLES / "gate_power_summary.csv", index=False)
    (TABLES / "gate_power_study.json").write_text(
        json.dumps(
            {
                "design": {
                    "assets": assets,
                    "dates": dates,
                    "betas": betas,
                    "signals": signals,
                    "seeds": args.seeds,
                },
                "rows": summary.to_dict(orient="records"),
                "note": (
                    "Synthetic study. mi_power is the fraction of seeds where the "
                    "80% date-level MI gate passes. beta is the signal coefficient; "
                    "noise is standard normal."
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(summary.to_string(index=False))
    print(f"wrote {TABLES / 'gate_power_summary.csv'}")


if __name__ == "__main__":
    main()
