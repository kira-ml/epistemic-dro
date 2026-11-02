"""Data loading and synthetic smoke-test panels.

``load_panel`` reads the frozen ETF snapshot written by
``scripts/build_snapshot.py``. It validates schema, key uniqueness, date
alignment, and finite values before returning a typed :class:`Panel`.

The synthetic panel remains for smoke tests only. It is not market data and
must never be used for an empirical claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = ["Panel", "SyntheticPanel", "load_panel", "make_synthetic_panel"]


@dataclass(frozen=True)
class SyntheticPanel:
    """A synthetic monthly panel used only for smoke tests."""

    returns: pd.DataFrame
    mu: pd.Series
    sigma: pd.Series


@dataclass(frozen=True)
class Panel:
    """The frozen ETF snapshot, validated and ready for feature construction."""

    prices: pd.DataFrame
    returns: pd.DataFrame
    metadata: pd.DataFrame
    universe: pd.DataFrame
    factors: pd.DataFrame
    risk_free: pd.DataFrame
    benchmark: pd.DataFrame


REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "prices": ("date", "ticker", "close", "adj_close", "volume", "dollar_volume"),
    "returns": ("date", "ticker", "ret", "excess_ret", "rf"),
    "metadata": (
        "ticker",
        "name",
        "inception_date",
        "category",
        "role",
        "expense_ratio",
        "distribution_yield",
    ),
    "universe": ("date", "ticker", "eligible"),
    "factors": ("date", "mkt_rf", "smb", "hml", "mom", "rf"),
    "risk_free": ("date", "rf"),
    "benchmark": ("date", "benchmark_ret"),
}


def make_synthetic_panel(
    n_assets: int = 20,
    n_months: int = 120,
    seed: int = 42,
) -> SyntheticPanel:
    """Create a synthetic monthly return panel.

    The data are **not** a market simulation. They are a deterministic fixture
    for unit tests and the smoke script.
    """
    if n_assets < 2:
        raise ValueError("n_assets must be at least 2")
    if n_months < 24:
        raise ValueError("n_months must be at least 24")

    rng = np.random.default_rng(seed)
    dates = pd.date_range("2010-01-31", periods=n_months, freq="ME")
    assets = [f"A{i:02d}" for i in range(n_assets)]

    market = rng.normal(0.005, 0.04, size=(n_months, 1))
    idiosyncratic = rng.normal(0.0, 0.05, size=(n_months, n_assets))
    returns = market + idiosyncratic
    frame = pd.DataFrame(returns, index=dates, columns=assets)

    mu = frame.mean()
    sigma = frame.std(ddof=1) / np.sqrt(12.0)
    sigma = sigma.clip(lower=1e-6)

    return SyntheticPanel(returns=frame, mu=mu, sigma=sigma)


def _read_table(root: Path, name: str) -> pd.DataFrame:
    path = root / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"snapshot table missing: {path}")
    return pd.read_parquet(path)


def _require_columns(frame: pd.DataFrame, name: str) -> None:
    missing = [column for column in REQUIRED_COLUMNS[name] if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def _require_unique_keys(frame: pd.DataFrame, name: str, keys: list[str]) -> None:
    if frame.duplicated(keys).any():
        raise ValueError(f"{name} contains duplicate keys {keys}")


def _require_finite(frame: pd.DataFrame, name: str, columns: list[str]) -> None:
    values = frame[columns].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{name} contains non-finite values in {columns}")


def _validate(panel: Panel) -> Panel:
    for name, frame in panel.__dict__.items():
        if frame.empty:
            raise ValueError(f"{name} table is empty")

    for name, frame in panel.__dict__.items():
        if name in REQUIRED_COLUMNS:
            _require_columns(frame, name)

    for name in ("prices", "returns", "universe", "factors", "risk_free", "benchmark"):
        frame = getattr(panel, name)
        if "date" in frame.columns:
            if frame["date"].isna().any():
                raise ValueError(f"{name} contains a missing date")
            if not pd.api.types.is_datetime64_any_dtype(frame["date"]):
                raise ValueError(f"{name}.date must be datetime64")

    for name in ("prices", "returns", "universe"):
        frame = getattr(panel, name)
        if frame["ticker"].isna().any():
            raise ValueError(f"{name} contains a missing ticker")
        _require_unique_keys(frame, name, ["date", "ticker"])

    _require_unique_keys(panel.metadata, "etf_metadata", ["ticker"])
    _require_unique_keys(panel.factors, "factors", ["date"])
    _require_unique_keys(panel.risk_free, "risk_free", ["date"])
    _require_unique_keys(panel.benchmark, "benchmark", ["date"])

    _require_finite(panel.prices, "prices", ["close", "adj_close", "volume", "dollar_volume"])
    _require_finite(panel.returns, "returns", ["ret", "excess_ret", "rf"])
    _require_finite(panel.factors, "factors", ["mkt_rf", "smb", "hml", "mom", "rf"])
    _require_finite(panel.risk_free, "risk_free", ["rf"])
    _require_finite(panel.benchmark, "benchmark", ["benchmark_ret"])

    price_dates = set(panel.prices["date"])
    if not set(panel.returns["date"]).issubset(price_dates):
        raise ValueError("returns contain dates not present in prices")
    if set(panel.universe["date"]) != price_dates:
        raise ValueError("universe dates must match prices dates")
    if not set(panel.factors["date"]).issubset(price_dates):
        raise ValueError("factors contain dates not present in prices")
    if not set(panel.risk_free["date"]).issubset(price_dates):
        raise ValueError("risk_free contains dates not present in prices")
    if not set(panel.benchmark["date"]).issubset(price_dates):
        raise ValueError("benchmark contains dates not present in prices")

    metadata_tickers = set(panel.metadata["ticker"])
    for name in ("prices", "returns", "universe"):
        extra = set(getattr(panel, name)["ticker"]) - metadata_tickers
        if extra:
            raise ValueError(f"{name} contains tickers absent from metadata: {sorted(extra)}")

    if panel.metadata["inception_date"].isna().any():
        raise ValueError("metadata contains a missing inception_date")
    if not pd.api.types.is_datetime64_any_dtype(panel.metadata["inception_date"]):
        raise ValueError("metadata.inception_date must be datetime64")
    if panel.universe["eligible"].dtype != bool:
        raise ValueError("universe.eligible must be boolean")

    return panel


def load_panel(path: str | Path) -> Panel:
    """Load and validate the frozen ETF snapshot.

    Args:
        path: Directory containing ``prices.parquet``, ``returns.parquet``,
            ``etf_metadata.parquet``, ``universe.parquet``, ``factors.parquet``,
            ``risk_free.parquet``, and ``benchmark.parquet``.

    Returns:
        A validated :class:`Panel`.

    Raises:
        FileNotFoundError: If a required table is missing.
        ValueError: If schema, keys, dates, or values fail validation.
    """
    root = Path(path)
    panel = Panel(
        prices=_read_table(root, "prices"),
        returns=_read_table(root, "returns"),
        metadata=_read_table(root, "etf_metadata"),
        universe=_read_table(root, "universe"),
        factors=_read_table(root, "factors"),
        risk_free=_read_table(root, "risk_free"),
        benchmark=_read_table(root, "benchmark"),
    )
    return _validate(panel)
