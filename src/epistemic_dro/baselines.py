"""Mandatory regularized baseline (G-R6: Parsimony / SRM).

The baseline is deliberately simple: standardized features and a Ridge
regression, fitted on the training window only. A more complex return model may
be adopted only if it beats this baseline on purged out-of-sample data with a
Diebold-Mariano test at the pre-registered threshold.

The class does not make a forecast for a real asset universe by itself; it is a
contract that the pipeline must use on identical splits and features.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

__all__ = ["RidgeBaseline", "fit_ridge_baseline"]


@dataclass(frozen=True)
class RidgeBaseline:
    """A fitted Ridge baseline plus the feature order used at fit time."""

    model: Pipeline
    feature_names: tuple[str, ...]
    alpha: float

    def predict(self, features: pd.DataFrame) -> pd.Series:
        """Predict on a feature frame with the same columns as fit time."""
        if not isinstance(features, pd.DataFrame):
            raise TypeError("features must be a pandas DataFrame")
        missing = [name for name in self.feature_names if name not in features.columns]
        if missing:
            raise ValueError(f"features missing required columns: {missing}")
        matrix = features.loc[:, list(self.feature_names)].to_numpy(dtype=float)
        if not np.isfinite(matrix).all():
            raise ValueError("features contain non-finite values")
        predictions = np.asarray(self.model.predict(matrix), dtype=float).ravel()
        return pd.Series(predictions, index=features.index, dtype=float)


def fit_ridge_baseline(
    features: pd.DataFrame,
    target: pd.Series,
    *,
    alpha: float = 1.0,
) -> RidgeBaseline:
    """Fit the mandatory Ridge baseline on a training window.

    Args:
        features: Training features, indexed by ``(date, ticker)`` or a flat row
            index. All columns must be numeric and finite.
        target: Training target aligned to ``features.index``. Missing or extra
            labels are an error, not something to impute silently.
        alpha: Ridge regularization strength. The default is the frozen
            baseline value; tuning it is a logged trial, not a silent choice.

    Returns:
        A fitted :class:`RidgeBaseline`.

    Raises:
        TypeError: If the inputs are not pandas objects.
        ValueError: If the target is misaligned, empty, or non-finite.
    """
    if not isinstance(features, pd.DataFrame):
        raise TypeError("features must be a pandas DataFrame")
    if not isinstance(target, pd.Series):
        raise TypeError("target must be a pandas Series")
    if features.empty or target.empty:
        raise ValueError("features and target must be non-empty")
    if features.columns.has_duplicates:
        raise ValueError("features contain duplicate column names")
    if alpha <= 0.0:
        raise ValueError("alpha must be positive")

    aligned = target.reindex(features.index)
    if aligned.isna().any():
        raise ValueError("target does not cover every feature row")
    if len(aligned) != len(target):
        raise ValueError("target contains labels outside the feature index")

    matrix = features.to_numpy(dtype=float)
    labels = aligned.to_numpy(dtype=float)
    if not np.isfinite(matrix).all():
        raise ValueError("features contain non-finite values")
    if not np.isfinite(labels).all():
        raise ValueError("target contains non-finite values")

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("ridge", Ridge(alpha=float(alpha))),
        ]
    )
    model.fit(matrix, labels)

    return RidgeBaseline(
        model=model,
        feature_names=tuple(str(name) for name in features.columns),
        alpha=float(alpha),
    )
