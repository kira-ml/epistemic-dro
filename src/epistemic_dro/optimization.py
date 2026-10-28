"""Distributionally robust mean-CVaR optimization.

The v1 ambiguity set is a box around the predicted mean:

    U = {mu : |mu_i - mu_hat_i| <= kappa * sigma_i}

For long-only weights, the worst-case expected return is

    mu_hat @ w - kappa * sum_i sigma_i * w_i

which keeps the problem convex. The CVaR term uses historical scenario returns
and the Rockafellar-Uryasev formulation:

    CVaR_alpha = min_t [ t + 1/((1-alpha)T) * sum_t max(0, -r_t @ w - t) ]

A solver failure is fatal. There is no equal-weight fallback: silently replacing
a failed solve would hide the failure inside the results.
"""

from __future__ import annotations

from dataclasses import dataclass

import cvxpy as cp
import numpy as np
import pandas as pd

__all__ = ["DROSolution", "SolverFailure", "solve_box_dro_cvar"]


class SolverFailure(RuntimeError):
    """Raised when the optimizer does not return an accepted solution."""


@dataclass(frozen=True)
class DROSolution:
    """A weight vector plus the diagnostics needed to audit it."""

    weights: pd.Series
    objective: float
    status: str
    worst_case_mean: float
    cvar: float
    turnover: float
    solver: str


def _validate_inputs(
    mu: pd.Series,
    sigma: pd.Series,
    scenarios: pd.DataFrame,
    max_weight: float,
    cvar_level: float,
    kappa: float,
) -> list[str]:
    if not isinstance(mu, pd.Series):
        raise TypeError("mu must be a pandas Series")
    if not isinstance(sigma, pd.Series):
        raise TypeError("sigma must be a pandas Series")
    if not isinstance(scenarios, pd.DataFrame):
        raise TypeError("scenarios must be a pandas DataFrame")

    assets = list(mu.index)
    if not assets:
        raise ValueError("mu is empty")
    if list(sigma.index) != assets:
        raise ValueError("sigma index must match mu index exactly")
    if list(scenarios.columns) != assets:
        raise ValueError("scenario columns must match mu index exactly")
    if len(scenarios) < 2:
        raise ValueError("need at least two scenario rows")
    if scenarios.isna().any().any():
        raise ValueError("scenarios contain missing values")
    if not np.isfinite(mu.to_numpy(dtype=float)).all():
        raise ValueError("mu contains non-finite values")
    if not np.isfinite(sigma.to_numpy(dtype=float)).all():
        raise ValueError("sigma contains non-finite values")
    if (sigma.to_numpy(dtype=float) < 0.0).any():
        raise ValueError("sigma must be non-negative")
    if not (0.0 < max_weight <= 1.0):
        raise ValueError("max_weight must lie in (0, 1]")
    if len(assets) * max_weight < 1.0 - 1e-12:
        raise ValueError(
            f"infeasible max_weight: {len(assets)} assets * {max_weight} < 1"
        )
    if not (0.0 < cvar_level < 1.0):
        raise ValueError("cvar_level must lie strictly between 0 and 1")
    if kappa < 0.0:
        raise ValueError("kappa must be non-negative")
    if len(scenarios) < 1.0 / (1.0 - cvar_level):
        raise ValueError(
            "not enough scenario rows for the requested CVaR tail; "
            "need at least 1/(1-level) observations"
        )
    return assets


def solve_box_dro_cvar(
    mu: pd.Series,
    sigma: pd.Series,
    scenarios: pd.DataFrame,
    *,
    kappa: float = 1.0,
    cvar_level: float = 0.95,
    cvar_penalty: float = 1.0,
    max_weight: float = 0.05,
    prev_weights: pd.Series | None = None,
    turnover_penalty: float = 0.0,
    cost_bps: float = 10.0,
    solver: str = "CLARABEL",
) -> DROSolution:
    """Solve the box-DRO mean-CVaR problem.

    Args:
        mu: Predicted mean returns, one per asset.
        sigma: Uncertainty (standard deviation of the mean forecast), one per
            asset. Must be non-negative.
        scenarios: Historical monthly returns, rows are scenarios, columns are
            assets in the same order as ``mu``.
        kappa: Ambiguity radius. ``0`` reduces to mean-CVaR with no DRO.
        cvar_level: Confidence level, e.g. ``0.95`` for the worst 5%.
        cvar_penalty: Weight on the CVaR term. Larger values penalize tail risk.
        max_weight: Per-asset cap.
        prev_weights: Previous post-rebalance weights. ``None`` means an initial
            allocation from cash.
        turnover_penalty: Additional penalty on one-way turnover.
        cost_bps: One-way transaction cost in basis points.
        solver: cvxpy solver name.

    Returns:
        A :class:`DROSolution`.

    Raises:
        SolverFailure: If the solve is not optimal or the solution violates a
            constraint beyond numerical tolerance.
    """
    assets = _validate_inputs(mu, sigma, scenarios, max_weight, cvar_level, kappa)
    n_assets = len(assets)
    n_scenarios = len(scenarios)

    mu_vector = mu.to_numpy(dtype=float)
    sigma_vector = sigma.to_numpy(dtype=float)
    returns = scenarios.to_numpy(dtype=float)

    if prev_weights is None:
        previous = np.zeros(n_assets, dtype=float)
    else:
        if not isinstance(prev_weights, pd.Series):
            raise TypeError("prev_weights must be a pandas Series or None")
        previous = prev_weights.reindex(assets).fillna(0.0).to_numpy(dtype=float)
        if (previous < 0.0).any():
            raise ValueError("prev_weights must be non-negative")

    weights = cp.Variable(n_assets, nonneg=True)
    value_at_risk = cp.Variable()
    excess = cp.Variable(n_scenarios, nonneg=True)
    turnover = cp.Variable(n_assets, nonneg=True)

    worst_case_mean = mu_vector @ weights - kappa * (sigma_vector @ weights)
    cvar_expression = value_at_risk + (
        1.0 / ((1.0 - cvar_level) * n_scenarios)
    ) * cp.sum(excess)

    constraints = [
        cp.sum(weights) == 1.0,
        weights <= max_weight,
        excess >= -returns @ weights - value_at_risk,
    ]

    constraints.extend(
        [
            turnover >= weights - previous,
            turnover >= previous - weights,
        ]
    )

    transaction_cost = (cost_bps / 10_000.0) * cp.sum(turnover)
    objective = cp.Maximize(
        worst_case_mean
        - cvar_penalty * cvar_expression
        - turnover_penalty * cp.sum(turnover)
        - transaction_cost
    )

    problem = cp.Problem(objective, constraints)
    try:
        problem.solve(solver=solver)
    except Exception as exc:  # cvxpy raises solver-specific exceptions
        raise SolverFailure(f"solver {solver!r} raised: {exc}") from exc

    if problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
        raise SolverFailure(
            f"solver {solver!r} returned status {problem.status!r}; "
            "no fallback portfolio is substituted"
        )

    raw_weights = np.asarray(weights.value, dtype=float).ravel()
    if not np.isfinite(raw_weights).all():
        raise SolverFailure("solver returned non-finite weights")

    tolerance = 1e-6
    if abs(raw_weights.sum() - 1.0) > tolerance:
        raise SolverFailure(f"weights sum to {raw_weights.sum():.8f}, not 1")
    if (raw_weights < -tolerance).any():
        raise SolverFailure("solver returned negative weights")
    if (raw_weights > max_weight + tolerance).any():
        raise SolverFailure("solver returned a weight above max_weight")

    cleaned = np.clip(raw_weights, 0.0, None)
    cleaned = cleaned / cleaned.sum()
    weight_series = pd.Series(cleaned, index=assets, dtype=float)

    realized_scenarios = returns @ cleaned
    tail = max(1, int(np.ceil((1.0 - cvar_level) * n_scenarios)))
    realized_cvar = float(np.sort(realized_scenarios)[:tail].mean())
    realized_turnover = float(np.abs(cleaned - previous).sum())

    return DROSolution(
        weights=weight_series,
        objective=float(problem.value),
        status=str(problem.status),
        worst_case_mean=float(mu_vector @ cleaned - kappa * (sigma_vector @ cleaned)),
        cvar=realized_cvar,
        turnover=realized_turnover,
        solver=solver,
    )
