"""Falsification harness (G-R2: Inversion / target shuffling).

A model that can predict randomly shuffled targets has a leak: the features,
preprocessing, or index alignment contains information about the label. The test
is deliberately adversarial. It must be wired to the real model before the first
confirmatory run; until then, the unit tests verify that the harness itself
catches a leaky model and passes an honest one.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

__all__ = ["assert_target_shuffling_collapses", "pearson_score"]


def pearson_score(actual: pd.Series, predicted: pd.Series) -> float:
    """Pearson correlation with a safe zero when either series is constant."""
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)
    if actual_values.size != predicted_values.size:
        raise ValueError("actual and predicted must have the same length")
    if not np.isfinite(actual_values).all() or not np.isfinite(predicted_values).all():
        raise ValueError("actual and predicted must be finite")
    if actual_values.std() == 0.0 or predicted_values.std() == 0.0:
        return 0.0
    return float(np.corrcoef(actual_values, predicted_values)[0, 1])


def assert_target_shuffling_collapses(
    fit_predict: Callable[[pd.DataFrame, pd.Series], pd.Series],
    features: pd.DataFrame,
    target: pd.Series,
    *,
    metric: Callable[[pd.Series, pd.Series], float] = pearson_score,
    max_random_score: float = 0.10,
    seed: int = 0,
) -> float:
    """Train on shuffled labels and assert performance collapses to chance.

    Args:
        fit_predict: Callable that fits on ``(features, target)`` and returns
            predictions aligned to ``target.index``.
        features: Feature frame.
        target: True target series aligned to ``features.index``.
        metric: Similarity metric. The default is Pearson correlation; the
            absolute value is compared to the threshold.
        max_random_score: Maximum absolute score allowed on shuffled labels.
        seed: Deterministic permutation seed.

    Returns:
        The absolute shuffled-target score, for logging.

    Raises:
        AssertionError: If the shuffled-target score exceeds the threshold.
    """
    if not isinstance(features, pd.DataFrame):
        raise TypeError("features must be a pandas DataFrame")
    if not isinstance(target, pd.Series):
        raise TypeError("target must be a pandas Series")
    if len(features) != len(target):
        raise ValueError("features and target must have the same length")

    aligned = target.reindex(features.index)
    if aligned.isna().any():
        raise ValueError("target does not cover every feature row")

    rng = np.random.default_rng(seed)
    shuffled = pd.Series(
        rng.permutation(aligned.to_numpy(dtype=float)),
        index=aligned.index,
        dtype=float,
    )
    predictions = fit_predict(features, shuffled)
    if not isinstance(predictions, pd.Series):
        predictions = pd.Series(predictions, index=aligned.index, dtype=float)
    predictions = predictions.reindex(aligned.index)
    if predictions.isna().any():
        raise ValueError("predictions do not cover every target row")

    score = abs(float(metric(shuffled, predictions)))
    if score > max_random_score:
        raise AssertionError(
            "target-shuffling leakage detected: "
            f"absolute score {score:.4f} exceeds {max_random_score:.4f}. "
            "Inspect feature timestamps, preprocessing fit windows, and index alignment."
        )
    return score
