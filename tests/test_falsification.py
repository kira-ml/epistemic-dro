from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from epistemic_dro.falsification import assert_target_shuffling_collapses, pearson_score


def _panel() -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(11)
    features = pd.DataFrame({"x1": rng.normal(size=200), "x2": rng.normal(size=200)})
    target = pd.Series(1.5 * features["x1"] - 0.75 * features["x2"], index=features.index)
    return features, target


def test_pearson_score_is_zero_for_constant_series() -> None:
    actual = pd.Series(np.zeros(5))
    predicted = pd.Series(np.arange(5.0))
    assert pearson_score(actual, predicted) == 0.0


def test_target_shuffling_catches_a_leaky_model() -> None:
    features, target = _panel()

    def leaky_fit_predict(
        training_features: pd.DataFrame, training_target: pd.Series
    ) -> pd.Series:
        # A model that returns its training labels is the canonical leak.
        return training_target.copy()

    with pytest.raises(AssertionError, match="leakage detected"):
        assert_target_shuffling_collapses(leaky_fit_predict, features, target)


def test_target_shuffling_passes_an_honest_model() -> None:
    features, target = _panel()

    def honest_fit_predict(
        training_features: pd.DataFrame, training_target: pd.Series
    ) -> pd.Series:
        # A constant forecast cannot learn shuffled noise.
        return pd.Series(np.zeros(len(training_features)), index=training_features.index)

    score = assert_target_shuffling_collapses(honest_fit_predict, features, target)
    assert score == pytest.approx(0.0)


def test_target_shuffling_requires_aligned_target() -> None:
    features, _ = _panel()
    misaligned = pd.Series(np.zeros(len(features)), index=range(1000, 1000 + len(features)))

    def honest_fit_predict(
        training_features: pd.DataFrame, training_target: pd.Series
    ) -> pd.Series:
        return pd.Series(np.zeros(len(training_features)), index=training_features.index)

    with pytest.raises(ValueError, match="cover every feature row"):
        assert_target_shuffling_collapses(honest_fit_predict, features, misaligned)


def test_target_shuffling_requires_same_length() -> None:
    features, _ = _panel()
    short = pd.Series(np.zeros(len(features) - 1), index=features.index[:-1])

    def honest_fit_predict(
        training_features: pd.DataFrame, training_target: pd.Series
    ) -> pd.Series:
        return pd.Series(np.zeros(len(training_features)), index=training_features.index)

    with pytest.raises(ValueError, match="same length"):
        assert_target_shuffling_collapses(honest_fit_predict, features, short)
