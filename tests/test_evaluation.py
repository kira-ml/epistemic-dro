from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from epistemic_dro.evaluation import (
    GateFailure,
    GateRule,
    evaluate_counter_metric_gate,
    metric_basket,
)


def _returns() -> pd.Series:
    return pd.Series([0.01, -0.02, 0.03, -0.01, 0.02, -0.005, 0.015, -0.03, 0.01, 0.005])


def test_metric_basket_contains_primary_and_counter_metrics() -> None:
    basket = metric_basket(_returns())
    assert set(basket) == {"net_sharpe", "max_drawdown", "cvar95", "sortino", "calmar"}
    assert all(np.isfinite(value) for value in basket.values())
    assert basket["max_drawdown"] <= 0.0
    assert basket["cvar95"] <= 0.0


def test_gate_accepts_a_basket_that_meets_every_bound() -> None:
    basket = metric_basket(_returns())
    rules = [
        GateRule("net_sharpe", ">=", -10.0),
        GateRule("max_drawdown", ">=", -1.0),
        GateRule("cvar95", ">=", -1.0),
    ]
    result = evaluate_counter_metric_gate(basket, rules)
    assert result == basket


def test_gate_rejects_a_basket_with_a_tail_breach() -> None:
    basket = metric_basket(_returns())
    rules = [
        GateRule("net_sharpe", ">=", -10.0),
        GateRule("max_drawdown", ">=", -0.0001),
        GateRule("cvar95", ">=", -1.0),
    ]
    with pytest.raises(GateFailure, match="max_drawdown"):
        evaluate_counter_metric_gate(basket, rules)


def test_gate_rejects_missing_metric() -> None:
    with pytest.raises(GateFailure, match="missing"):
        evaluate_counter_metric_gate({"net_sharpe": 1.0}, [GateRule("cvar95", ">=", -0.05)])


def test_gate_rejects_non_finite_metric() -> None:
    with pytest.raises(GateFailure, match="non-finite"):
        evaluate_counter_metric_gate(
            {"net_sharpe": float("nan")}, [GateRule("net_sharpe", ">=", 0.0)]
        )


def test_gate_requires_at_least_one_rule() -> None:
    with pytest.raises(ValueError, match="at least one"):
        evaluate_counter_metric_gate(metric_basket(_returns()), [])


def test_metric_basket_requires_complete_risk_free_series() -> None:
    returns = _returns()
    rf = pd.Series(0.0, index=returns.index[:-1])
    with pytest.raises(ValueError, match="risk-free"):
        metric_basket(returns, rf=rf)
