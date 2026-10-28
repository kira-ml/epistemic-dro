from __future__ import annotations

import pandas as pd
import pytest

from epistemic_dro.leakage import (
    assert_no_group_overlap,
    assert_no_lookahead,
    assert_unique_keys,
)


def test_lookahead_accepts_same_or_earlier_timestamps() -> None:
    features = pd.Series(pd.to_datetime(["2020-01-31", "2020-02-29"]))
    decisions = pd.Series(pd.to_datetime(["2020-01-31", "2020-02-29"]))
    assert_no_lookahead(features, decisions)


def test_lookahead_rejects_future_feature() -> None:
    features = pd.Series(pd.to_datetime(["2020-02-29"]))
    decisions = pd.Series(pd.to_datetime(["2020-01-31"]))
    with pytest.raises(ValueError, match="after the decision date"):
        assert_no_lookahead(features, decisions)


def test_lookahead_rejects_length_mismatch() -> None:
    features = pd.Series(pd.to_datetime(["2020-01-31"]))
    decisions = pd.Series(pd.to_datetime(["2020-01-31", "2020-02-29"]))
    with pytest.raises(ValueError, match="equal length"):
        assert_no_lookahead(features, decisions)


def test_group_overlap_raises() -> None:
    train = pd.DataFrame({"ticker": ["A", "B"]})
    test = pd.DataFrame({"ticker": ["B", "C"]})
    with pytest.raises(ValueError, match="overlap"):
        assert_no_group_overlap(train, test, "ticker")


def test_group_overlap_accepts_disjoint() -> None:
    train = pd.DataFrame({"ticker": ["A", "B"]})
    test = pd.DataFrame({"ticker": ["C", "D"]})
    assert_no_group_overlap(train, test, "ticker")


def test_unique_keys_raises_on_duplicate() -> None:
    frame = pd.DataFrame({"date": ["2020-01-31", "2020-01-31"], "ticker": ["A", "A"]})
    with pytest.raises(ValueError, match="duplicate"):
        assert_unique_keys(frame, ["date", "ticker"])
