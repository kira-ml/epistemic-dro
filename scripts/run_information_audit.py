"""G-R4 information audit: marginal MI with a date-blocked permutation null.

For each month, compute mutual information between each feature and the
next-month excess return within the cross-section. Shuffle the target within
the same date to build the null. Apply Benjamini-Hochberg FDR across features
per date. A feature survives only if it passes in at least 80% of dates.

This is deliberately conservative. With 68-72 ETFs, per-date MI is noisy; a
null result is evidence that the feature set is weak, not proof of zero
information. Conditional MI is only evaluated if at least one feature survives
the marginal screen.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import Ridge

from epistemic_dro.data import load_panel
from epistemic_dro.features import FeatureSpec, build_features, build_targets

ROOT = Path(__file__).resolve().parents[1]


def _bh_qvalues(pvalues: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg q-values for one date."""
    order = np.argsort(pvalues)
    ranked = pvalues[order]
    m = len(pvalues)
    qvalues = ranked * m / np.arange(1, m + 1)
    qvalues = np.minimum.accumulate(qvalues[::-1])[::-1]
    output = np.empty_like(qvalues)
    output[order] = np.clip(qvalues, 0.0, 1.0)
    return output


def _conditional_mi_proxy(
    frame: pd.DataFrame,
    features: list[str],
    target: str,
    survivors: list[str],
) -> dict[str, float]:
    """Approximate CMI: MI(candidate; target residual after Ridge on survivors)."""
    if not survivors:
        return {}
    output: dict[str, float] = {}
    for candidate in features:
        if candidate in survivors:
            continue
        mi_values = []
        for _, group in frame.groupby(level="date"):
            x_selected = group[survivors].to_numpy(dtype=float)
            y = group[target].to_numpy(dtype=float)
            x_candidate = group[[candidate]].to_numpy(dtype=float)
            model = Ridge(alpha=1.0).fit(x_selected, y)
            residual = y - model.predict(x_selected)
            mi = mutual_info_regression(
                x_candidate, residual, n_neighbors=5, random_state=0
            )[0]
            mi_values.append(float(mi))
        output[candidate] = float(np.mean(mi_values))
    return output


def main() -> None:
    panel = load_panel(ROOT / "data" / "raw")
    features = build_features(
        panel.prices, panel.metadata, panel.universe, panel.factors, FeatureSpec()
    )
    targets = build_targets(panel.returns)
    frame = features.join(targets, how="inner").sort_index()
    target = targets.columns[0]
    feature_names = list(features.columns)

    rng = np.random.default_rng(42)
    n_permutations = 30
    dates = [
        date
        for date, group in frame.groupby(level="date")
        if len(group) >= 20
    ]
    actual_rows = []
    null_rows = []
    pvalue_rows = []

    for date in dates:
        group = frame.loc[date]
        x = group[feature_names].to_numpy(dtype=float)
        y = group[target].to_numpy(dtype=float)
        actual = mutual_info_regression(x, y, n_neighbors=5, random_state=0)
        null = np.empty((n_permutations, len(feature_names)), dtype=float)
        for permutation in range(n_permutations):
            shuffled = rng.permutation(y)
            null[permutation] = mutual_info_regression(
                x, shuffled, n_neighbors=5, random_state=0
            )
        pvalues = (1.0 + (null >= actual).sum(axis=0)) / (n_permutations + 1.0)
        actual_rows.append(actual)
        null_rows.append(null)
        pvalue_rows.append(_bh_qvalues(pvalues))

    actual_matrix = np.vstack(actual_rows)
    null_matrix = np.vstack(null_rows)
    q_matrix = np.vstack(pvalue_rows)

    summary_rows = []
    for index, feature in enumerate(feature_names):
        pass_rate = float((q_matrix[:, index] < 0.05).mean())
        summary_rows.append(
            {
                "feature": feature,
                "mean_mi": float(actual_matrix[:, index].mean()),
                "mean_null_95": float(np.percentile(null_matrix[:, index], 95)),
                "median_qvalue": float(np.median(q_matrix[:, index])),
                "pass_rate": pass_rate,
                "survives": pass_rate >= 0.80,
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values("mean_mi", ascending=False)
    survivors = summary.loc[summary["survives"], "feature"].tolist()
    cmi = _conditional_mi_proxy(frame, feature_names, target, survivors)

    args = {
        "dates_evaluated": len(dates),
        "permutations": n_permutations,
        "fdr": "Benjamini-Hochberg, q < 0.05",
        "survival_rule": "pass_rate >= 0.80",
        "survivors": survivors,
        "conditional_mi_proxy": cmi,
        "features": summary_rows,
        "note": (
            "Per-date MI is noisy at 68-72 assets. A null result is evidence "
            "that the frozen feature set is weak, not proof of zero information."
        ),
    }

    out_dir = ROOT / "results" / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "information_audit.json").write_text(
        json.dumps(args, indent=2) + "\n", encoding="utf-8"
    )
    summary.to_csv(out_dir / "information_audit.csv", index=False)

    print(summary.to_string(index=False))
    print(f"\nsurvivors ({len(survivors)}): {survivors}")
    if cmi:
        print("conditional MI proxy:", cmi)
    print(f"wrote {out_dir / 'information_audit.json'}")


if __name__ == "__main__":
    main()
