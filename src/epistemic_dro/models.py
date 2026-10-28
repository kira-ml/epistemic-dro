"""Return models.

The v1 model is LightGBM with multiple seeds. The interface is fixed now so the
uncertainty and optimizer layers can be developed independently.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = ["ModelPrediction", "predict_ensemble"]


@dataclass(frozen=True)
class ModelPrediction:
    """Point predictions and epistemic uncertainty."""

    mean: pd.Series
    sigma: pd.Series
    n_models: int


def predict_ensemble(
    predictions: np.ndarray,
    index: pd.Index,
    floor: float = 1e-6,
) -> ModelPrediction:
    """Aggregate an ensemble of predictions.

    Args:
        predictions: Array of shape ``(n_models, n_assets)``.
        index: Asset labels, length ``n_assets``.
        floor: Minimum uncertainty to avoid a degenerate ambiguity set.

    Returns:
        Mean and cross-model standard deviation.
    """
    array = np.asarray(predictions, dtype=float)
    if array.ndim != 2:
        raise ValueError("predictions must have shape (n_models, n_assets)")
    if array.shape[1] != len(index):
        raise ValueError("prediction columns must match index length")
    if array.shape[0] < 2:
        raise ValueError("need at least two models for ensemble uncertainty")

    mean = array.mean(axis=0)
    sigma = array.std(axis=0, ddof=1)
    sigma = np.maximum(sigma, floor)

    return ModelPrediction(
        mean=pd.Series(mean, index=index, dtype=float),
        sigma=pd.Series(sigma, index=index, dtype=float),
        n_models=array.shape[0],
    )
