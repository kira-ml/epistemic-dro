"""Synthetic-data smoke test.

This proves the optimizer and metrics run end-to-end. It says nothing about
real-world performance and must not be cited as a result.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from epistemic_dro.data import make_synthetic_panel  # noqa: E402
from epistemic_dro.metrics import cvar, max_drawdown, sharpe  # noqa: E402
from epistemic_dro.optimization import solve_box_dro_cvar  # noqa: E402


def main() -> None:
    panel = make_synthetic_panel(n_assets=20, n_months=120, seed=42)
    rows = []
    previous = None

    for kappa in (0.0, 1.0):
        solution = solve_box_dro_cvar(
            panel.mu,
            panel.sigma,
            panel.returns,
            kappa=kappa,
            cvar_level=0.95,
            cvar_penalty=1.0,
            max_weight=0.20,
            prev_weights=previous,
            cost_bps=10.0,
        )
        portfolio = panel.returns @ solution.weights
        rows.append(
            {
                "kappa": kappa,
                "max_weight": float(solution.weights.max()),
                "turnover": solution.turnover,
                "sharpe": sharpe(portfolio),
                "max_drawdown": max_drawdown(portfolio),
                "cvar95": cvar(portfolio, level=0.05),
                "solver": solution.solver,
            }
        )
        previous = solution.weights

    print("Synthetic smoke test only -- not an empirical result.")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
