"""Data-leakage guards.

These functions are intentionally small and testable. They are not a substitute
for a data card and a domain review; they catch the mistakes that are easy to
automate.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["assert_no_group_overlap", "assert_no_lookahead", "assert_unique_keys"]


def assert_no_lookahead(
    feature_dates: pd.Series,
    decision_dates: pd.Series,
) -> None:
    """Raise if any feature timestamp is after its decision timestamp.

    Both series must be aligned row-wise: row ``i`` is the feature used for
    decision ``i``.
    """
    features = pd.to_datetime(pd.Series(feature_dates), errors="raise")
    decisions = pd.to_datetime(pd.Series(decision_dates), errors="raise")
    if len(features) != len(decisions):
        raise ValueError("feature_dates and decision_dates must have equal length")
    bad = features > decisions
    if bad.any():
        count = int(bad.sum())
        first = int(bad.to_numpy().nonzero()[0][0])
        raise ValueError(
            f"{count} feature timestamps are after the decision date; "
            f"first offending row: {first} ({features.iloc[first]} > {decisions.iloc[first]})"
        )


def assert_unique_keys(frame: pd.DataFrame, keys: list[str]) -> None:
    """Raise if the given key columns are not unique."""
    missing = [key for key in keys if key not in frame.columns]
    if missing:
        raise KeyError(f"missing key columns: {missing}")
    duplicated = frame.duplicated(subset=keys)
    if duplicated.any():
        raise ValueError(f"{int(duplicated.sum())} duplicate keys for {keys}")


def assert_no_group_overlap(
    train: pd.DataFrame,
    test: pd.DataFrame,
    group_column: str,
) -> None:
    """Raise if any group appears in both train and test."""
    if group_column not in train.columns or group_column not in test.columns:
        raise KeyError(f"group column {group_column!r} missing from one frame")
    overlap = set(train[group_column].dropna()) & set(test[group_column].dropna())
    if overlap:
        examples = sorted(map(str, list(overlap)[:5]))
        raise ValueError(
            f"{len(overlap)} groups overlap between train and test; examples: {examples}"
        )
