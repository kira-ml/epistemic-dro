"""Mutation tests for ``scripts/verify_results.py``.

The verifier is the evidence that the published aggregates still say what the
paper says. A check that cannot fail is not evidence, so each test below copies
the committed aggregates, changes exactly one claim, and requires the verifier to
return non-zero. The unmutated copy must pass: without that test a broken fixture
would make every mutation look effective.
"""

from __future__ import annotations

import json
import shutil
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_results as vr  # noqa: E402

PUBLISHED = ROOT / "paper" / "published-results"


@pytest.fixture()
def published_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A writable copy of the published aggregates, with the verifier pointed at it."""
    copy = tmp_path / "published-results"
    shutil.copytree(PUBLISHED, copy)
    monkeypatch.setattr(vr, "PUBLISHED", copy)
    return copy


def _edit_json(path: Path, edit: Callable[[dict[str, Any]], None]) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    edit(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _set(data: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def _run() -> int:
    return vr.main()


def test_the_unmutated_copy_passes(published_copy: Path) -> None:
    """Guard against a fixture that fails for an unrelated reason."""
    assert _run() == 0


# --------------------------------------------------------------------------- #
# Verdicts: H1/H2/H3 in both the analysis and the final report
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "path,replacement",
    [
        (("verdict", "H1_tail_improvement", "verdict"), "PASS"),
        (("verdict", "H2_sharpe_non_inferiority", "verdict"), "FAIL"),
        (("verdict", "H3_uncertainty_ablation", "verdict"), "PASS"),
    ],
)
def test_a_changed_v1_verdict_fails(
    published_copy: Path, path: tuple[str, ...], replacement: str
) -> None:
    _edit_json(
        published_copy / "dro_experiment_analysis.json",
        lambda data: _set(data, path, replacement),
    )
    assert _run() == 1


@pytest.mark.parametrize("hypothesis", ["H1", "H2", "H3"])
def test_a_changed_final_verdict_fails(
    published_copy: Path, hypothesis: str
) -> None:
    original = "PASS" if hypothesis == "H2" else "FAIL"
    replacement = "FAIL" if original == "PASS" else "PASS"
    _edit_json(
        published_copy / "final_report.json",
        lambda data: _set(data, ("verdict", hypothesis), replacement),
    )
    assert _run() == 1


# --------------------------------------------------------------------------- #
# The pre-holdout gates, including the coverage claim
# --------------------------------------------------------------------------- #

def test_v2_holdout_allowed_fails(published_copy: Path) -> None:
    _edit_json(
        published_copy / "v2_uncertainty_audit.json",
        lambda data: _set(data, ("holdout_allowed",), True),
    )
    assert _run() == 1


def test_a_v2_gate_above_the_bar_fails(published_copy: Path) -> None:
    def edit(data: dict[str, Any]) -> None:
        data["features"][0]["pass_rate"] = 0.80

    _edit_json(published_copy / "v2_uncertainty_audit.json", edit)
    assert _run() == 1


def test_a_v2_feature_marked_surviving_fails(published_copy: Path) -> None:
    def edit(data: dict[str, Any]) -> None:
        data["features"][1]["survives"] = True

    _edit_json(published_copy / "v2_uncertainty_audit.json", edit)
    assert _run() == 1


@pytest.mark.parametrize("key", ["mean_validation_coverage", "mean_test_coverage"])
def test_changed_v2_coverage_fails(published_copy: Path, key: str) -> None:
    """Coverage is a paper claim, not a number the verifier may ignore."""

    def edit(data: dict[str, Any]) -> None:
        data["coverage"][key] += 0.01

    _edit_json(published_copy / "v2_uncertainty_audit.json", edit)
    assert _run() == 1


def test_v3_holdout_allowed_fails(published_copy: Path) -> None:
    _edit_json(
        published_copy / "v3_sigma_audit.json",
        lambda data: _set(data, ("holdout_allowed",), True),
    )
    assert _run() == 1


def test_a_v3_gate_above_the_bar_fails(published_copy: Path) -> None:
    def edit(data: dict[str, Any]) -> None:
        data["sigma"]["pass_rate"] = 0.80

    _edit_json(published_copy / "v3_sigma_audit.json", edit)
    assert _run() == 1


def test_v3_sigma_marked_surviving_fails(published_copy: Path) -> None:
    _edit_json(
        published_copy / "v3_sigma_audit.json",
        lambda data: _set(data, ("sigma", "survives"), True),
    )
    assert _run() == 1


@pytest.mark.parametrize("key", ["mean_sigma", "decile_spread"])
def test_changed_v3_calibration_fails(published_copy: Path, key: str) -> None:
    def edit(data: dict[str, Any]) -> None:
        data["calibration"][key] += 0.01

    _edit_json(published_copy / "v3_sigma_audit.json", edit)
    assert _run() == 1


# --------------------------------------------------------------------------- #
# The block-aware null
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "key,replacement",
    [("iid_passes", 19), ("block_passes", 4)],
)
def test_a_changed_block_summary_fails(
    published_copy: Path, key: str, replacement: int
) -> None:
    _edit_json(
        published_copy / "block_gate_study.json",
        lambda data: _set(data, ("summary", key), replacement),
    )
    assert _run() == 1


@pytest.mark.parametrize("signal", ["v2:sigma", "v3:sigma"])
def test_a_signal_surviving_the_block_null_fails(
    published_copy: Path, signal: str
) -> None:
    def edit(data: dict[str, Any]) -> None:
        row = next(row for row in data["results"] if row["signal"] == signal)
        row["passes_all_blocks"] = True

    _edit_json(published_copy / "block_gate_study.json", edit)
    assert _run() == 1


# --------------------------------------------------------------------------- #
# Assets and the untouched holdout
# --------------------------------------------------------------------------- #

def test_a_missing_asset_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paper = tmp_path / "paper"
    (paper / "generated").mkdir(parents=True)
    shutil.copy2(
        ROOT / "paper" / "generated" / "numbers.typ",
        paper / "generated" / "numbers.typ",
    )
    monkeypatch.setattr(vr, "PAPER", paper)

    assert _run() == 1


@pytest.mark.parametrize(
    "name", ["holdout_results.csv", "v2_holdout.csv", "v3_holdout.csv"]
)
def test_a_holdout_file_in_the_published_results_fails(
    published_copy: Path, name: str
) -> None:
    (published_copy / name).write_text("not empty", encoding="utf-8")
    assert _run() == 1


def test_a_holdout_file_in_results_tables_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    tables = root / "results" / "tables"
    tables.mkdir(parents=True)
    (tables / "holdout_metrics.csv").write_text("not empty", encoding="utf-8")
    monkeypatch.setattr(vr, "ROOT", root)

    assert _run() == 1
