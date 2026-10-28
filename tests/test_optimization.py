from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from epistemic_dro.optimization import solve_box_dro_cvar


@pytest.fixture()
def toy_panel() -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    rng = np.random.default_rng(42)
    n_assets = 10
    n_months = 120
    dates = pd.date_range("2010-01-31", periods=n_months, freq="ME")
    assets = [f"A{i:02d}" for i in range(n_assets)]
    returns = pd.DataFrame(
        rng.normal(0.005, 0.05, size=(n_months, n_assets)),
        index=dates,
        columns=assets,
    )
    mu = returns.mean()
    sigma = returns.std(ddof=1) / np.sqrt(12.0) + 1e-6
    return mu, sigma, returns


def test_solution_satisfies_constraints(toy_panel) -> None:
    mu, sigma, returns = toy_panel
    solution = solve_box_dro_cvar(
        mu,
        sigma,
        returns,
        kappa=1.0,
        cvar_level=0.95,
        cvar_penalty=1.0,
        max_weight=0.20,
        cost_bps=10.0,
    )
    assert solution.weights.sum() == pytest.approx(1.0, abs=1e-6)
    assert (solution.weights >= -1e-8).all()
    assert (solution.weights <= 0.20 + 1e-6).all()
    assert np.isfinite(solution.objective)
    assert solution.turnover == pytest.approx(1.0, abs=1e-6)


def test_second_solve_uses_previous_weights(toy_panel) -> None:
    mu, sigma, returns = toy_panel
    first = solve_box_dro_cvar(
        mu, sigma, returns, kappa=1.0, max_weight=0.20, cost_bps=10.0
    )
    second = solve_box_dro_cvar(
        mu,
        sigma,
        returns,
        kappa=1.0,
        max_weight=0.20,
        cost_bps=10.0,
        prev_weights=first.weights,
    )
    assert 0.0 <= second.turnover <= 2.0
    assert second.weights.sum() == pytest.approx(1.0, abs=1e-6)


def test_infeasible_max_weight_raises(toy_panel) -> None:
    mu, sigma, returns = toy_panel
    with pytest.raises(ValueError):
        solve_box_dro_cvar(mu, sigma, returns, max_weight=0.05)


def test_negative_sigma_raises(toy_panel) -> None:
    mu, sigma, returns = toy_panel
    bad_sigma = sigma.copy()
    bad_sigma.iloc[0] = -1.0
    with pytest.raises(ValueError):
        solve_box_dro_cvar(mu, bad_sigma, returns, max_weight=0.20)


def test_misaligned_assets_raise(toy_panel) -> None:
    mu, sigma, returns = toy_panel
    with pytest.raises(ValueError):
        solve_box_dro_cvar(mu, sigma[sigma.index[::-1]], returns, max_weight=0.20)


def test_zero_kappa_still_solves(toy_panel) -> None:
    mu, sigma, returns = toy_panel
    solution = solve_box_dro_cvar(
        mu,
        sigma,
        returns,
        kappa=0.0,
        max_weight=0.20,
        cvar_penalty=1.0,
    )
    assert solution.weights.sum() == pytest.approx(1.0, abs=1e-6)
    assert np.isfinite(solution.cvar)
