"""Final reporting: cost sensitivity, stress windows, deflated Sharpe.

Reads the reduced DRO outputs and writes ``results/tables/final_report.json``.
No new model or feature is introduced.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, norm, skew

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
STRATEGIES = ("M1_reduced", "B5_DRO_point", "B3_CVaR", "B1_equal_weight")


def _metrics(net: np.ndarray, rf: np.ndarray) -> dict[str, float]:
    excess = net - rf
    std = float(np.std(excess, ddof=1))
    sharpe = float(np.mean(excess) / std * math.sqrt(12.0)) if std > 0 else float("nan")
    wealth = np.cumprod(1.0 + net)
    drawdown = wealth / np.maximum.accumulate(wealth) - 1.0
    tail = max(1, int(math.ceil(0.05 * len(net))))
    return {
        "net_sharpe": sharpe,
        "max_drawdown": float(np.min(drawdown)),
        "cvar95": float(np.mean(np.sort(net)[:tail])),
        "months": int(len(net)),
    }


def _deflated_sharpe(
    returns: np.ndarray,
    rf: np.ndarray,
    trial_sharpes: np.ndarray,
    n_trials: int,
) -> dict[str, float]:
    """Bailey-Lopez de Prado deflated Sharpe ratio (monthly excess returns)."""
    excess = returns - rf
    sr = float(np.mean(excess) / np.std(excess, ddof=1))
    t = len(returns)
    g3 = float(skew(returns, bias=False))
    g4 = float(kurtosis(returns, fisher=False, bias=False))
    variance_sr = float(np.var(trial_sharpes, ddof=1))
    euler = 0.5772156649015329
    sr0 = math.sqrt(variance_sr) * (
        (1.0 - euler) * norm.ppf(1.0 - 1.0 / n_trials)
        + euler * norm.ppf(1.0 - 1.0 / (n_trials * math.e))
    )
    denominator = math.sqrt(max(1e-12, 1.0 - g3 * sr + (g4 - 1.0) / 4.0 * sr**2))
    dsr = float(norm.cdf((sr - sr0) * math.sqrt(t - 1.0) / denominator))
    psr = float(norm.cdf(sr * math.sqrt(t - 1.0) / denominator))
    return {
        "sharpe_monthly": sr,
        "sharpe_annualized": sr * math.sqrt(12.0),
        "expected_max_sharpe_monthly": sr0,
        "deflated_sharpe_probability": dsr,
        "probabilistic_sharpe_probability": psr,
        "skew": g3,
        "kurtosis": g4,
        "months": t,
        "trials": n_trials,
    }


def main() -> None:
    risk_free = pd.read_parquet(ROOT / "data" / "raw" / "risk_free.parquet")
    rf = risk_free.set_index("date")["rf"].sort_index()

    cost_sensitivity: dict[str, dict] = {}
    for bps, suffix in ((5, "_5bp"), (10, ""), (20, "_20bp"), (50, "_50bp")):
        summary = json.loads(
            (TABLES / f"dro_experiment_summary{suffix}.json").read_text(encoding="utf-8")
        )
        cost_sensitivity[str(bps)] = {
            name: {
                key: summary[name][key]
                for key in ("net_sharpe", "max_drawdown", "cvar95", "annualized_turnover")
            }
            for name in STRATEGIES
        }

    returns = pd.read_csv(TABLES / "dro_experiment_returns.csv")
    pivot = returns.pivot(index="date", columns="strategy", values="net_return").sort_index()
    pivot.index = pd.to_datetime(pivot.index)
    rf_aligned = rf.reindex(pivot.index)
    if rf_aligned.isna().any():
        raise SystemExit("risk-free missing for some experiment dates")

    windows = {
        "2010_2019": ("2010-01-01", "2019-12-31"),
        "2020": ("2020-01-01", "2020-12-31"),
        "2022": ("2022-01-01", "2022-12-31"),
        "2020_2024": ("2020-01-01", "2024-12-31"),
    }
    stress: dict[str, dict] = {}
    for label, (start, end) in windows.items():
        mask = (pivot.index >= pd.Timestamp(start)) & (pivot.index <= pd.Timestamp(end))
        frame = pivot.loc[mask]
        rf_window = rf_aligned.loc[mask]
        if frame.empty:
            continue
        stress[label] = {
            name: _metrics(frame[name].to_numpy(), rf_window.to_numpy())
            for name in STRATEGIES
        }

    trial_sharpes = np.array(
        [
            _metrics(pivot[name].to_numpy(), rf_aligned.to_numpy())["net_sharpe"]
            for name in STRATEGIES
        ]
    ) / math.sqrt(12.0)
    deflated = {
        name: _deflated_sharpe(
            pivot[name].to_numpy(), rf_aligned.to_numpy(), trial_sharpes, len(STRATEGIES)
        )
        for name in STRATEGIES
    }

    report = {
        "cost_sensitivity": cost_sensitivity,
        "stress_windows": stress,
        "deflated_sharpe": deflated,
        "verdict": {
            "H1": "FAIL",
            "H2": "PASS",
            "H3": "FAIL",
            "note": (
                "Reduced M1; not the original LightGBM M1. "
                "Negative result for the uncertainty layer."
            ),
        },
    }
    out = TABLES / "final_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Cost sensitivity (net Sharpe / MDD / CVaR95)")
    for bps in ("5", "10", "20", "50"):
        row = cost_sensitivity[bps]
        print(
            f"  {bps:>2} bps: "
            f"M1 {row['M1_reduced']['net_sharpe']:.3f}/"
            f"{row['M1_reduced']['max_drawdown']:.3%}/"
            f"{row['M1_reduced']['cvar95']:.3%}; "
            f"B5 {row['B5_DRO_point']['net_sharpe']:.3f}/"
            f"{row['B5_DRO_point']['max_drawdown']:.3%}/"
            f"{row['B5_DRO_point']['cvar95']:.3%}; "
            f"B1 {row['B1_equal_weight']['net_sharpe']:.3f}/"
            f"{row['B1_equal_weight']['max_drawdown']:.3%}/"
            f"{row['B1_equal_weight']['cvar95']:.3%}"
        )

    print("\nStress windows (net Sharpe / MDD / CVaR95)")
    for label, row in stress.items():
        print(
            f"  {label}: M1 {row['M1_reduced']['net_sharpe']:.3f}/"
            f"{row['M1_reduced']['max_drawdown']:.3%}/"
            f"{row['M1_reduced']['cvar95']:.3%}; "
            f"B5 {row['B5_DRO_point']['net_sharpe']:.3f}/"
            f"{row['B5_DRO_point']['max_drawdown']:.3%}/"
            f"{row['B5_DRO_point']['cvar95']:.3%}"
        )

    print("\nDeflated Sharpe (10 bps)")
    for name, row in deflated.items():
        print(
            f"  {name}: SR {row['sharpe_annualized']:.3f}; "
            f"DSR {row['deflated_sharpe_probability']:.3f}; "
            f"PSR {row['probabilistic_sharpe_probability']:.3f}"
        )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
