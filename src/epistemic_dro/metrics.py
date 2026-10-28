"""Performance and risk metrics.

Definitions are deliberately explicit because silent second definitions are a
common source of irreproducible backtests.

All functions accept a pandas Series of monthly returns unless stated otherwise.
Returns are decimal (0.01 = 1%), not percentages.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

__all__ = [
    "PERIODS_PER_YEAR",
    "annualized_turnover",
    "calmar",
    "cvar",
    "max_drawdown",
    "sharpe",
    "sortino",
]

PERIODS_PER_YEAR = 12


def _clean_returns(returns: pd.Series | np.ndarray) -> pd.Series:
    series = pd.Series(returns, dtype="float64").dropna()
    if series.empty:
        raise ValueError("returns series is empty after dropping missing values")
    if not np.isfinite(series.to_numpy()).all():
        raise ValueError("returns contain non-finite values")
    return series


def sharpe(
    returns: pd.Series | np.ndarray,
    rf: pd.Series | np.ndarray | None = None,
    periods_per_year: int = PERIODS_PER_YEAR,
) -> float:
    """Annualized Sharpe ratio.

    Args:
        returns: Monthly decimal returns.
        rf: Optional monthly risk-free returns aligned by index. A missing
            risk-free observation is an error, not a silent zero.
        periods_per_year: Annualization factor.

    Returns:
        Annualized Sharpe ratio, or NaN when volatility is zero.
    """
    series = _clean_returns(returns)
    if rf is not None:
        rf_series = pd.Series(rf, dtype="float64").reindex(series.index)
        if rf_series.isna().any():
            raise ValueError("risk-free series does not cover every return observation")
        series = series - rf_series

    volatility = float(series.std(ddof=1))
    if not np.isfinite(volatility) or abs(volatility) < 1e-12:
        return float("nan")
    return float(series.mean() / volatility * math.sqrt(periods_per_year))


def max_drawdown(returns: pd.Series | np.ndarray) -> float:
    """Maximum drawdown of a compounded return series.

    Returns:
        The minimum peak-to-trough return, e.g. ``-0.20`` for a 20% drawdown.
    """
    series = pd.Series(returns, dtype="float64").fillna(0.0)
    if series.empty:
        raise ValueError("returns series is empty")
    wealth = (1.0 + series).cumprod()
    peak = wealth.cummax()
    drawdown = wealth / peak - 1.0
    return float(drawdown.min())


def cvar(
    returns: pd.Series | np.ndarray,
    level: float = 0.05,
) -> float:
    """Conditional Value-at-Risk (expected shortfall) of a return series.

    Args:
        returns: Monthly decimal returns.
        level: Tail probability, e.g. ``0.05`` for the worst 5%.

    Returns:
        Mean of the worst ``ceil(level * n)`` returns. This is a negative
        number when the tail is a loss.
    """
    if not 0.0 < level < 1.0:
        raise ValueError("level must lie strictly between 0 and 1")
    series = _clean_returns(returns).sort_values()
    k = max(1, int(math.ceil(level * len(series))))
    return float(series.iloc[:k].mean())


def annualized_turnover(
    weights: pd.DataFrame,
    periods_per_year: int = PERIODS_PER_YEAR,
) -> float:
    """Annualized one-way turnover from a post-rebalance weight panel.

    Args:
        weights: DataFrame indexed by rebalance date, columns are assets.
            The first row is treated as an initial allocation from cash.
        periods_per_year: Annualization factor.

    Returns:
        Annualized mean of ``sum_i |w_i(t) - w_i(t-1)|``.
    """
    if not isinstance(weights, pd.DataFrame):
        raise TypeError("weights must be a pandas DataFrame")
    if weights.empty:
        raise ValueError("weights frame is empty")
    frame = weights.sort_index().astype("float64")
    if frame.isna().any().any():
        raise ValueError("weights contain missing values")
    changes = frame.diff().abs().sum(axis=1)
    changes.iloc[0] = frame.iloc[0].abs().sum()
    return float(periods_per_year * changes.mean())


def sortino(
    returns: pd.Series | np.ndarray,
    rf: pd.Series | np.ndarray | None = None,
    periods_per_year: int = PERIODS_PER_YEAR,
) -> float:
    """Annualized Sortino ratio using downside deviation.

    Returns NaN when there are fewer than two downside observations or the
    downside deviation is zero.
    """
    series = _clean_returns(returns)
    if rf is not None:
        rf_series = pd.Series(rf, dtype="float64").reindex(series.index)
        if rf_series.isna().any():
            raise ValueError("risk-free series does not cover every return observation")
        series = series - rf_series

    downside = series[series < 0.0]
    if len(downside) < 2:
        return float("nan")
    downside_deviation = float(downside.std(ddof=1))
    if not np.isfinite(downside_deviation) or abs(downside_deviation) < 1e-12:
        return float("nan")
    return float(series.mean() / downside_deviation * math.sqrt(periods_per_year))


def calmar(
    returns: pd.Series | np.ndarray,
    periods_per_year: int = PERIODS_PER_YEAR,
) -> float:
    """Calmar ratio: annualized compound return divided by absolute max drawdown."""
    series = _clean_returns(returns)
    years = len(series) / periods_per_year
    if years <= 0:
        return float("nan")
    wealth = (1.0 + series).cumprod()
    cagr = float(wealth.iloc[-1] ** (1.0 / years) - 1.0)
    drawdown = max_drawdown(series)
    if drawdown == 0.0:
        return float("nan")
    return float(cagr / abs(drawdown))
