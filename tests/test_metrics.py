from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from epistemic_dro.metrics import (
    annualized_turnover,
    calmar,
    cvar,
    max_drawdown,
    sharpe,
    sortino,
)


def test_max_drawdown_known_path() -> None:
    returns = pd.Series([0.10, -0.10, 0.20])
    assert max_drawdown(returns) == pytest.approx(-0.10)


def test_cvar_is_mean_of_worst_tail() -> None:
    returns = pd.Series([-0.20, -0.10, 0.00, 0.10, 0.20])
    assert cvar(returns, level=0.40) == pytest.approx(-0.15)


def test_sharpe_zero_volatility_is_nan() -> None:
    returns = pd.Series([0.01] * 12)
    assert np.isnan(sharpe(returns))


def test_sharpe_uses_supplied_risk_free() -> None:
    returns = pd.Series([0.02, 0.01, 0.03, 0.00])
    rf = pd.Series([0.01, 0.01, 0.01, 0.01])
    assert sharpe(returns, rf=rf) < sharpe(returns)


def test_sharpe_rejects_missing_risk_free() -> None:
    returns = pd.Series([0.02, 0.01, 0.03], index=[0, 1, 2])
    rf = pd.Series([0.01, 0.01], index=[0, 1])
    with pytest.raises(ValueError):
        sharpe(returns, rf=rf)


def test_annualized_turnover_includes_initial_allocation() -> None:
    weights = pd.DataFrame(
        [[1.0, 0.0], [0.5, 0.5]],
        index=pd.date_range("2020-01-31", periods=2, freq="ME"),
        columns=["A", "B"],
    )
    assert annualized_turnover(weights) == pytest.approx(12.0)


def test_sortino_requires_downside_observations() -> None:
    returns = pd.Series([0.01, 0.02, 0.03])
    assert np.isnan(sortino(returns))


def test_calmar_zero_drawdown_is_nan() -> None:
    returns = pd.Series([0.01, 0.02, 0.03])
    assert np.isnan(calmar(returns))


def test_cvar_rejects_invalid_level() -> None:
    with pytest.raises(ValueError):
        cvar(pd.Series([0.01, -0.01]), level=0.0)
