"""Counter-metric evaluation gate (G-R10: Goodhart-Campbell alignment).

Net Sharpe is the pre-registered primary metric, but it is never evaluated
alone. A result is accepted only when the primary metric and the tail-risk
counter-metrics pass their bounds simultaneously.

This module intentionally has no default thresholds: the bounds belong to the
frozen protocol and must be passed in by the caller. A hardcoded threshold would
be a silent second protocol.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from .metrics import calmar, cvar, max_drawdown, sharpe, sortino

__all__ = [
    "GateFailure",
    "GateRule",
    "evaluate_counter_metric_gate",
    "metric_basket",
]

Operator = Literal[">=", "<="]


class GateFailure(RuntimeError):
    """Raised when a metric basket violates at least one pre-registered bound."""


@dataclass(frozen=True)
class GateRule:
    """One bound in the counter-metric gate.

    ``threshold`` uses the metric's native sign. Drawdown and CVaR are negative
    numbers, so a rule such as ``GateRule("max_drawdown", ">=", -0.18)`` means
    "the drawdown may not be worse than -18%".
    """

    metric: str
    op: Operator
    threshold: float


def metric_basket(
    returns: pd.Series | np.ndarray,
    rf: pd.Series | np.ndarray | None = None,
) -> dict[str, float]:
    """Compute the primary metric and its counter-metrics.

    Args:
        returns: Monthly decimal returns.
        rf: Optional monthly risk-free returns. If provided, it must cover every
            return observation; a missing value is an error, not zero.

    Returns:
        A dictionary with net Sharpe, max drawdown, CVaR95, Sortino, and Calmar.
    """
    series = pd.Series(returns, dtype="float64").dropna()
    return {
        "net_sharpe": sharpe(series, rf=rf),
        "max_drawdown": max_drawdown(series),
        "cvar95": cvar(series, level=0.05),
        "sortino": sortino(series, rf=rf),
        "calmar": calmar(series),
    }


def evaluate_counter_metric_gate(
    metrics: Mapping[str, float],
    rules: Sequence[GateRule],
) -> dict[str, float]:
    """Check every rule and raise :class:`GateFailure` on the first basket that fails.

    Args:
        metrics: Output of :func:`metric_basket` or an equivalent mapping.
        rules: Pre-registered bounds. All are evaluated; the error message lists
            every failure, not just the first one.

    Returns:
        The input metrics, unchanged, when every rule passes.

    Raises:
        GateFailure: If any metric is missing, non-finite, or outside its bound.
    """
    if not rules:
        raise ValueError("at least one gate rule is required")

    failures: list[str] = []
    for rule in rules:
        if rule.metric not in metrics:
            failures.append(f"{rule.metric}: missing from metric basket")
            continue
        value = float(metrics[rule.metric])
        if not np.isfinite(value):
            failures.append(f"{rule.metric}: non-finite value {value!r}")
            continue
        if rule.op == ">=" and value < rule.threshold:
            failures.append(f"{rule.metric}={value:.6f} < {rule.threshold:.6f}")
        elif rule.op == "<=" and value > rule.threshold:
            failures.append(f"{rule.metric}={value:.6f} > {rule.threshold:.6f}")
        elif rule.op not in (">=", "<="):
            failures.append(f"{rule.metric}: unsupported operator {rule.op!r}")

    if failures:
        raise GateFailure("counter-metric gate rejected: " + "; ".join(failures))
    return dict(metrics)
