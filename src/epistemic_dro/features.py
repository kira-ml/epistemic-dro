"""Feature construction.

The v1 feature set is ETF-appropriate. Every feature at month-end ``t`` uses
prices, volumes, and factor returns timestamped at or before ``t``. The builder
never sees the next-month target.

The output is indexed by ``(date, ticker)`` and contains only rows that were
eligible in the point-in-time universe at that date.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = ["FeatureSpec", "build_features", "build_targets"]


@dataclass(frozen=True)
class FeatureSpec:
    """Declarative description of the v1 ETF feature set."""

    momentum_windows: tuple[int, ...] = (1, 3, 6, 12)
    volatility_windows: tuple[int, ...] = (3, 12)
    drawdown_window: int = 12
    liquidity_window: int = 12
    beta_window: int = 36
    skew_window: int = 12
    downside_window: int = 12
    volume_shock_window: int = 12
    corr_window: int = 36
    metadata_fields: tuple[str, ...] = ("expense_ratio", "distribution_yield")
    factor_exposures: tuple[str, ...] = ("mkt_rf", "smb", "hml", "mom")
    winsorize: float = 0.01
    cross_sectional_rank: bool = True


def _check_columns(frame: pd.DataFrame, name: str, columns: set[str]) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing columns: {missing}")


def _max_drawdown(window: np.ndarray) -> float:
    if not np.isfinite(window).all():
        return float("nan")
    wealth = np.cumprod(1.0 + window)
    peak = np.maximum.accumulate(wealth)
    return float(np.min(wealth / peak - 1.0))


def _factor_exposures(
    excess: pd.Series,
    factors: pd.DataFrame,
    columns: tuple[str, ...],
    window: int,
) -> pd.DataFrame:
    """Rolling multivariate factor loadings; uses only data up to each date."""
    output = pd.DataFrame(index=excess.index, columns=[f"exp_{c}" for c in columns], dtype=float)
    factor_frame = factors.loc[:, list(columns)]
    mask = excess.notna() & factor_frame.notna().all(axis=1)
    values = excess.to_numpy(dtype=float)
    design_values = factor_frame.to_numpy(dtype=float)

    for position in range(window - 1, len(excess)):
        window_slice = slice(position - window + 1, position + 1)
        if not mask.iloc[window_slice].all():
            continue
        y_window = values[window_slice]
        x_window = design_values[window_slice]
        design = np.column_stack([np.ones(len(x_window)), x_window])
        coefficients, *_ = np.linalg.lstsq(design, y_window, rcond=None)
        output.iloc[position] = coefficients[1:]
    return output


def _rolling_beta(excess: pd.DataFrame, market: pd.Series, window: int) -> pd.DataFrame:
    """Rolling univariate beta using only observations up to each date."""
    mean_y = excess.rolling(window).mean()
    mean_x = market.rolling(window).mean()
    covariance = (
        excess.mul(market, axis=0).rolling(window).mean()
        - mean_y.mul(mean_x, axis=0)
    )
    variance = market.pow(2).rolling(window).mean() - mean_x.pow(2)
    return covariance.div(variance, axis=0)


def build_features(
    prices: pd.DataFrame,
    metadata: pd.DataFrame,
    universe: pd.DataFrame,
    factors: pd.DataFrame,
    spec: FeatureSpec,
) -> pd.DataFrame:
    """Build lagged cross-sectional ETF features.

    Args:
        prices: Long monthly prices with ``date, ticker, adj_close, dollar_volume``.
        metadata: One row per ticker. Metadata fields are used only when a
            historical series exists; current snapshots are ignored.
        universe: Long ``date, ticker, eligible`` eligibility panel.
        factors: Monthly factor returns with ``date`` plus the configured
            factor columns and ``rf``.
        spec: Feature specification.

    Returns:
        A DataFrame indexed by ``(date, ticker)`` with one column per feature.
        Only eligible rows are returned.

    Raises:
        ValueError: If required columns are missing or the panel is empty.
    """
    _check_columns(
        prices,
        "prices",
        {"date", "ticker", "adj_close", "dollar_volume"},
    )
    _check_columns(universe, "universe", {"date", "ticker", "eligible"})
    _check_columns(metadata, "metadata", {"ticker"})
    _check_columns(factors, "factors", {"date", "rf", *spec.factor_exposures})

    if prices.empty or universe.empty or factors.empty:
        raise ValueError("prices, universe, and factors must be non-empty")
    if prices.duplicated(["date", "ticker"]).any():
        raise ValueError("prices contain duplicate (date, ticker) rows")

    adj = prices.pivot(index="date", columns="ticker", values="adj_close").sort_index()
    dollar = prices.pivot(index="date", columns="ticker", values="dollar_volume").sort_index()
    adj = adj.apply(pd.to_numeric, errors="coerce")
    dollar = dollar.apply(pd.to_numeric, errors="coerce")

    returns = adj.pct_change()
    factors = factors.set_index("date").sort_index()
    factors = factors.reindex(adj.index)
    if factors["rf"].isna().any():
        raise ValueError("risk-free series does not cover every price date")

    excess = returns.sub(factors["rf"], axis=0)
    feature_frames: dict[str, pd.DataFrame] = {}

    for window in spec.momentum_windows:
        feature_frames[f"mom_{window}m"] = adj.pct_change(window)
    for window in spec.volatility_windows:
        feature_frames[f"vol_{window}m"] = returns.rolling(window).std() * np.sqrt(12.0)

    downside = returns.clip(upper=0.0)
    feature_frames[f"downside_vol_{spec.downside_window}m"] = (
        np.sqrt((downside**2).rolling(spec.downside_window).mean()) * np.sqrt(12.0)
    )
    feature_frames[f"skew_{spec.skew_window}m"] = returns.rolling(spec.skew_window).skew()
    feature_frames[f"worst_1m_{spec.downside_window}m"] = returns.rolling(
        spec.downside_window
    ).min()
    if "vol_3m" in feature_frames and "vol_12m" in feature_frames:
        feature_frames["vol_ratio_3_12"] = (
            feature_frames["vol_3m"] / feature_frames["vol_12m"]
        )
    feature_frames["volume_shock_1m"] = dollar / dollar.rolling(
        spec.volume_shock_window
    ).mean()
    feature_frames[f"corr_market_{spec.corr_window}m"] = returns.rolling(
        spec.corr_window
    ).corr(factors["mkt_rf"])

    feature_frames[f"mdd_{spec.drawdown_window}m"] = returns.rolling(
        spec.drawdown_window
    ).apply(_max_drawdown, raw=True)
    feature_frames[f"dollar_vol_{spec.liquidity_window}m"] = dollar.rolling(
        spec.liquidity_window
    ).mean()

    beta = _rolling_beta(excess, factors["mkt_rf"], spec.beta_window)
    feature_frames["beta_36m"] = beta

    exposures = {
        ticker: _factor_exposures(
            excess[ticker], factors, spec.factor_exposures, spec.beta_window
        )
        for ticker in excess.columns
    }
    for column in [f"exp_{name}" for name in spec.factor_exposures]:
        feature_frames[column] = pd.concat(
            {ticker: frame[column] for ticker, frame in exposures.items()}, axis=1
        ).reindex(adj.index)

    for field in spec.metadata_fields:
        if field not in metadata.columns or not metadata[field].notna().any():
            continue
        vintage = metadata.get("metadata_vintage", pd.Series("", index=metadata.index))
        is_pit = vintage.astype(str).str.contains("pit", case=False, na=False).any()
        if not is_pit:
            continue
        mapping = metadata.set_index("ticker")[field]
        feature_frames[field] = pd.DataFrame(
            {ticker: mapping.get(ticker, np.nan) for ticker in adj.columns},
            index=adj.index,
        )

    long = None
    for name, frame in feature_frames.items():
        frame = frame.replace([np.inf, -np.inf], np.nan)
        series = frame.stack(future_stack=True).rename(name)
        series.index.names = ["date", "ticker"]
        long = (
            series.to_frame()
            if long is None
            else long.join(series, how="outer", sort=False)
        )
    if long is None:
        raise ValueError("no features were constructed")
    long.index.names = ["date", "ticker"]
    long = long.reset_index()

    eligible = universe.loc[universe["eligible"].astype(bool), ["date", "ticker"]]
    long = long.merge(eligible, on=["date", "ticker"], how="inner")
    if long.empty:
        raise ValueError("no eligible feature rows; check the universe panel")

    feature_columns = list(feature_frames)
    long = long.dropna(subset=feature_columns)
    if long.empty:
        raise ValueError("no complete feature rows; check the snapshot history")
    if spec.winsorize > 0.0:
        lower = spec.winsorize
        upper = 1.0 - spec.winsorize
        for column in feature_columns:
            long[column] = long.groupby("date")[column].transform(
                lambda values: values.clip(
                    lower=values.quantile(lower), upper=values.quantile(upper)
                )
            )
    if spec.cross_sectional_rank:
        for column in feature_columns:
            long[column] = long.groupby("date")[column].rank(pct=True) - 0.5

    return long.sort_values(["date", "ticker"]).set_index(["date", "ticker"])


def build_targets(returns: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    """Build next-horizon excess returns without using future information in features.

    Args:
        returns: Long monthly returns with ``date, ticker, excess_ret``.
        horizon: Forward horizon in months.

    Returns:
        A DataFrame indexed by ``(date, ticker)`` with column
        ``forward_excess_return_{horizon}m``. The final ``horizon`` month per
        ticker has a missing target and is dropped.
    """
    _check_columns(returns, "returns", {"date", "ticker", "excess_ret"})
    if horizon < 1:
        raise ValueError("horizon must be at least 1")
    frame = returns.sort_values(["ticker", "date"]).copy()
    column = f"forward_excess_return_{horizon}m"
    frame[column] = frame.groupby("ticker")["excess_ret"].shift(-horizon)
    frame = frame.dropna(subset=[column])
    return frame.set_index(["date", "ticker"])[[column]].sort_index()
