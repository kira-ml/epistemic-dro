from __future__ import annotations

from epistemic_dro.backtest import walk_forward_splits


def test_walk_forward_splits_are_ordered_and_disjoint() -> None:
    splits = walk_forward_splits(
        120,
        train_min=60,
        validation=12,
        test=12,
        purge=1,
        embargo=1,
    )
    assert len(splits) >= 1
    for split in splits:
        assert split.train.max() < split.validation.min()
        assert split.validation.max() < split.test.min()
        assert len(set(split.train) & set(split.validation)) == 0
        assert len(set(split.train) & set(split.test)) == 0
        assert len(set(split.validation) & set(split.test)) == 0


def test_walk_forward_respects_purge() -> None:
    splits = walk_forward_splits(100, train_min=40, validation=10, test=10, purge=2)
    first = splits[0]
    assert first.validation.min() - first.train.max() == 3  # one gap + purge=2
    assert first.test.min() - first.validation.max() == 3


def test_walk_forward_stops_when_not_enough_data() -> None:
    assert walk_forward_splits(50, train_min=60, validation=12, test=12) == []
