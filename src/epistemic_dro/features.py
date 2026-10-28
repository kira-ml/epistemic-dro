"""Feature construction.

The real feature builder is implemented after the data card is signed off. The
interface is fixed here so the rest of the pipeline can be written against it.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

__all__ = ["FeatureSpec", "build_features"]


@dataclass(frozen=True)
class FeatureSpec:
    """Declarative description of a feature set."""

    momentum_windows: tuple[int, ...] = (1, 6, 12)
    volatility_window: int = 12
    value_fields: tuple[str, ...] = ("book_to_market", "earnings_yield")
    quality_fields: tuple[str, ...] = ("roe", "gross_profitability")
    size_field: str = "market_cap"
    liquidity_window: int = 12
    winsorize: float = 0.01


def build_features(
    prices: pd.DataFrame,
    fundamentals: pd.DataFrame,
    universe: pd.DataFrame,
    spec: FeatureSpec,
) -> pd.DataFrame:
    """Build lagged cross-sectional features.

    Not implemented until the data source and schema are fixed. The output must
    be indexed by ``(date, ticker)`` and every feature must be available at the
    decision date.
    """
    raise NotImplementedError(
        "Feature construction is blocked on the G1 data card. "
        "Implement only after PIT timestamps and universe rules are verified."
    )
