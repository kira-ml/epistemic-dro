"""Verify the published aggregate results, verdicts, gates, assets, and paper source.

Run from the repository root:

    python scripts/verify_results.py

The script is deliberately independent of the local ``results/tables/`` run.
It reads the committed aggregate files in ``paper/published-results/``.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "paper" / "published-results"
PAPER = ROOT / "paper"
TOL = 1e-9


def _load(name: str) -> dict:
    return json.loads((PUBLISHED / name).read_text(encoding="utf-8"))


def _close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(float(a) - float(b)) <= tol


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append((name, bool(condition), detail))

    analysis = _load("dro_experiment_analysis.json")
    verdict = analysis["verdict"]
    check("v1 H1 FAIL", verdict["H1_tail_improvement"]["verdict"] == "FAIL")
    check("v1 H2 PASS", verdict["H2_sharpe_non_inferiority"]["verdict"] == "PASS")
    check("v1 H3 FAIL", verdict["H3_uncertainty_ablation"]["verdict"] == "FAIL")

    summary = _load("dro_experiment_summary.json")
    for strategy in ("M1_reduced", "B5_DRO_point", "B1_equal_weight"):
        for metric in ("net_sharpe", "max_drawdown", "cvar95"):
            check(
                f"v1 {strategy} {metric} matches analysis",
                _close(summary[strategy][metric], analysis["point_estimates"][strategy][metric]),
                f"{summary[strategy][metric]} vs {analysis['point_estimates'][strategy][metric]}",
            )

    v2_gate = _load("v2_uncertainty_audit.json")
    check("v2 holdout not allowed", v2_gate["holdout_allowed"] is False)
    check(
        "v2 gate below 80%",
        all(item["pass_rate"] < 0.80 for item in v2_gate["features"]),
        str([item["pass_rate"] for item in v2_gate["features"]]),
    )

    v3_gate = _load("v3_sigma_audit.json")
    check("v3 holdout not allowed", v3_gate["holdout_allowed"] is False)
    check(
        "v3 gate below 80%",
        v3_gate["sigma"]["pass_rate"] < 0.80,
        str(v3_gate["sigma"]["pass_rate"]),
    )

    final = _load("final_report.json")
    check("final H1 FAIL", final["verdict"]["H1"] == "FAIL")
    check("final H2 PASS", final["verdict"]["H2"] == "PASS")
    check("final H3 FAIL", final["verdict"]["H3"] == "FAIL")

    with (PUBLISHED / "gate_power_summary.csv").open(encoding="utf-8") as handle:
        gate_rows = list(csv.DictReader(handle))
    gate_row = next(
        (
            row
            for row in gate_rows
            if row["n_assets"] == "72"
            and row["n_dates"] == "179"
            and row["signal"] == "linear"
            and row["beta"] == "0.5"
        ),
        None,
    )
    check("gate power row exists", gate_row is not None)
    if gate_row is not None:
        check("80% MI gate zero power at 20% R2", float(gate_row["mi_power"]) == 0.0)
        check("pooled gate full power at 20% R2", float(gate_row["pooled_power"]) == 1.0)

    gate_reeval = _load("gate_reevaluation.json")
    v1_passes = sum(1 for row in gate_reeval["v1_features"] if row["passes"])
    check("pooled v1 features pass", v1_passes >= 15, str(v1_passes))
    check("v2 pooled sigma passes", gate_reeval["v2_sigma"]["passes"] is True)
    check("v3 pooled sigma passes", gate_reeval["v3_sigma"]["passes"] is True)

    for pattern in ("*holdout*", "*v2_holdout*", "*v3_holdout*"):
        for directory in (ROOT / "results" / "tables", PUBLISHED):
            matches = list(directory.glob(pattern)) if directory.exists() else []
            check(f"no holdout result {directory.name}/{pattern}", not matches, str(matches))

    for asset in ("mini_paper.pdf", "linkedin_carousel.pdf", "one_pager.pdf", "linkedin_card.png"):
        path = PAPER / asset
        check(f"asset exists: {asset}", path.exists() and path.stat().st_size > 50_000, str(path))

    numbers = (PAPER / "generated" / "numbers.typ").read_text(encoding="utf-8")

    def _match(pattern: str) -> list[float]:
        match = re.search(pattern, numbers)
        if not match:
            raise ValueError(f"pattern not found: {pattern}")
        return [float(value) for value in match.groups()]

    v1_values = _match(
        r"m1: \(sharpe: ([-\d.]+), mdd: ([-\d.]+), cvar: ([-\d.]+), turnover: ([-\d.]+)\)"
    )
    v1_keys = ("net_sharpe", "max_drawdown", "cvar95", "annualized_turnover")
    for value, key in zip(v1_values, v1_keys, strict=True):
        check(f"paper v1 {key} matches summary", _close(value, summary["M1_reduced"][key]))

    v2_values = _match(r"v2 = \(m1_sharpe: ([-\d.]+), m1_mdd: ([-\d.]+), m1_cvar: ([-\d.]+)")
    v2_summary = _load("v2_summary_dev.json")
    for value, key in zip(v2_values, ("net_sharpe", "max_drawdown", "cvar95"), strict=True):
        check(f"paper v2 {key} matches summary", _close(value, v2_summary["M1_v2"][key]))

    v3_values = _match(r"v3 = \(m1_sharpe: ([-\d.]+), m1_mdd: ([-\d.]+), m1_cvar: ([-\d.]+)")
    v3_summary = _load("v3_summary_dev.json")
    for value, key in zip(v3_values, ("net_sharpe", "max_drawdown", "cvar95"), strict=True):
        check(f"paper v3 {key} matches summary", _close(value, v3_summary["M1_v3"][key]))

    gate_values = _match(r"v2_gate = \(pass: ([-\d.]+)")
    check(
        "paper v2 gate matches audit",
        _close(gate_values[0], v2_gate["features"][0]["pass_rate"]),
    )
    gate_values = _match(r"v3_gate = \(pass: ([-\d.]+)")
    check(
        "paper v3 gate matches audit",
        _close(gate_values[0], v3_gate["sigma"]["pass_rate"]),
    )

    failures = [item for item in checks if not item[1]]
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        print(f"{status:4s}  {name}" + (f"  [{detail}]" if detail and not ok else ""))
    print(f"\n{len(checks) - len(failures)}/{len(checks)} checks passed")
    if failures:
        print("VERIFICATION FAILED")
        return 1
    print("VERIFICATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
