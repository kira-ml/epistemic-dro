from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from epistemic_dro.models import predict_ensemble


def test_predict_ensemble_mean_and_sigma() -> None:
    predictions = np.array(
        [
            [0.01, 0.02],
            [0.03, 0.04],
            [0.05, 0.06],
        ]
    )
    result = predict_ensemble(predictions, pd.Index(["A", "B"]))
    assert result.mean["A"] == pytest.approx(0.03)
    assert result.sigma["A"] == pytest.approx(np.std([0.01, 0.03, 0.05], ddof=1))
    assert result.n_models == 3


def test_predict_ensemble_rejects_single_model() -> None:
    with pytest.raises(ValueError, match="at least two"):
        predict_ensemble(np.array([[0.01, 0.02]]), pd.Index(["A", "B"]))


def test_predict_ensemble_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="columns"):
        predict_ensemble(np.zeros((3, 2)), pd.Index(["A", "B", "C"]))
