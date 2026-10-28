"""Walk-forward split construction.

No random splits. The test window is always after the validation window, with a
purge gap to reduce label overlap and an embargo before the next training window.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["Split", "walk_forward_splits"]


@dataclass(frozen=True)
class Split:
    """Integer positions for one walk-forward fold."""

    train: np.ndarray
    validation: np.ndarray
    test: np.ndarray


def walk_forward_splits(
    n_periods: int,
    *,
    train_min: int = 60,
    validation: int = 12,
    test: int = 12,
    purge: int = 1,
    embargo: int = 1,
) -> list[Split]:
    """Build expanding-window walk-forward splits.

    Args:
        n_periods: Number of monthly observations.
        train_min: Minimum training length.
        validation: Validation length used for tuning.
        test: Test length.
        purge: Observations dropped between train/validation and validation/test.
        embargo: Observations dropped after a test window before the next fold.

    Returns:
        A list of :class:`Split` objects with integer positions.
    """
    if min(train_min, validation, test) <= 0:
        raise ValueError("train_min, validation, and test must be positive")
    if purge < 0 or embargo < 0:
        raise ValueError("purge and embargo must be non-negative")

    splits: list[Split] = []
    start = 0
    while True:
        train_end = start + train_min
        validation_start = train_end + purge
        validation_end = validation_start + validation
        test_start = validation_end + purge
        test_end = test_start + test
        if test_end > n_periods:
            break
        splits.append(
            Split(
                train=np.arange(start, train_end),
                validation=np.arange(validation_start, validation_end),
                test=np.arange(test_start, test_end),
            )
        )
        start += test + embargo

    return splits
