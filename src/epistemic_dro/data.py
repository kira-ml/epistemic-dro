"""Data loading and synthetic smoke-test panels.

Real vendor loaders are intentionally not implemented until the data source is
selected. The synthetic panel exists only to prove that the optimizer, metrics,
and tests run end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = ["SyntheticPanel", "load_panel", "make_synthetic_panel"]


@dataclass(frozen=True)
class SyntheticPanel:
    """A synthetic monthly panel used only for smoke tests."""

    returns: pd.DataFrame
    mu: pd.Series
    sigma: pd.Series


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


def load_panel(path: str | Path) -> pd.DataFrame:
    """Load a real vendor panel.

    Not implemented until the data source is selected. Keeping this explicit
    prevents a silent fallback to synthetic data in a research run.
    """
    raise NotImplementedError(
        "Real data loading is blocked on the G1 data-source decision. "
        "Use make_synthetic_panel for smoke tests only."
    )
