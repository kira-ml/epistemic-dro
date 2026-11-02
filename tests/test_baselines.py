from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from epistemic_dro.baselines import fit_ridge_baseline
from epistemic_dro.falsification import pearson_score


def _linear_panel(n: int = 120, seed: int = 7) -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    noise = rng.normal(scale=0.1, size=n)
    features = pd.DataFrame({"x1": x1, "x2": x2})
    target = pd.Series(2.0 * x1 - 0.5 * x2 + noise)
    return features, target


def test_ridge_baseline_recovers_linear_signal() -> None:
    features, target = _linear_panel()
    baseline = fit_ridge_baseline(features.iloc[:90], target.iloc[:90], alpha=1.0)
    predictions = baseline.predict(features.iloc[90:])
    assert pearson_score(target.iloc[90:], predictions) > 0.8


def test_ridge_baseline_uses_fit_time_feature_order() -> None:
    features, target = _linear_panel()
    baseline = fit_ridge_baseline(features, target, alpha=1.0)
    reordered = features.loc[:, ["x2", "x1"]]
    assert np.allclose(baseline.predict(reordered), baseline.predict(features))


def test_ridge_baseline_rejects_misaligned_target() -> None:
    features, target = _linear_panel()
    extra = pd.concat([target, pd.Series([1.0], index=[999])])
    with pytest.raises(ValueError, match="outside"):
        fit_ridge_baseline(features, extra)


def test_ridge_baseline_rejects_non_finite_features() -> None:
    features, target = _linear_panel()
    features.loc[0, "x1"] = np.inf
    with pytest.raises(ValueError, match="non-finite"):
        fit_ridge_baseline(features, target)


def test_ridge_baseline_rejects_non_positive_alpha() -> None:
    features, target = _linear_panel()
    with pytest.raises(ValueError, match="alpha"):
        fit_ridge_baseline(features, target, alpha=0.0)
