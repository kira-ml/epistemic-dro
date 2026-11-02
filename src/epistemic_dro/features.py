"""Feature construction.

The real feature builder is implemented after the ETF data card is signed off.
The interface is fixed here so the rest of the pipeline can be written against
it. v1 features are ETF-appropriate: no stock fundamentals.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

__all__ = ["FeatureSpec", "build_features"]


@dataclass(frozen=True)
class FeatureSpec:
    """Declarative description of the v1 ETF feature set."""

    momentum_windows: tuple[int, ...] = (1, 3, 6, 12)
    volatility_windows: tuple[int, ...] = (3, 12)
    drawdown_window: int = 12
    liquidity_window: int = 12
    beta_window: int = 36
    metadata_fields: tuple[str, ...] = ("expense_ratio", "distribution_yield")
    factor_exposures: tuple[str, ...] = ("mkt_rf", "smb", "hml", "mom")
    winsorize: float = 0.01


def build_features(
    prices: pd.DataFrame,
    metadata: pd.DataFrame,
    universe: pd.DataFrame,
    factors: pd.DataFrame,
    spec: FeatureSpec,
) -> pd.DataFrame:
    """Build lagged cross-sectional ETF features.

    Not implemented until the G1 ETF snapshot and schema are validated. The
    output must be indexed by ``(date, ticker)`` and every feature must be
    available at the decision date. Metadata fields are used only if a
    historical series exists; otherwise they are excluded or disclosed as
    current-snapshot fields.
    """
    raise NotImplementedError(
        "Feature construction is blocked on the G1 ETF data card. "
        "Implement only after the snapshot, listing dates, and universe rules are verified."
    )
