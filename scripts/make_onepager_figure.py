"""Build the two-panel evidence figure for the one-page research summary.

The Epistemic DRO values come from the published aggregate audit tables.
The Robustfolio values come from the sibling Robustfolio repository's
published outcomes table. The chart is intentionally small and readable
at the width used in `paper/one_pager.typ`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
RESULTS = PAPER / "published-results"
OUT = PAPER / "figures" / "onepager_evidence.png"

INK = "#101820"
MUTED = "#5C6B73"
GRID = "#CFC6B8"
PAPER_BG = "#F6F1E7"
NAVY = "#0B1F33"
GOLD = "#A98754"
OXBLOOD = "#6E2B2B"


def load_json(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--robustfolio",
        type=Path,
        default=ROOT.parent / "robustfolio",
        help="Path to the sibling robustfolio repository.",
    )
    args = parser.parse_args()

    v2 = load_json("v2_uncertainty_audit.json")
    v3 = load_json("v3_sigma_audit.json")
    v2_gate = v2["features"][0]["pass_rate"] * 100
    v3_gate = v3["sigma"]["pass_rate"] * 100

    outcomes_path = args.robustfolio / "docs" / "published-run" / "outcomes.csv"
    if not outcomes_path.exists():
        raise SystemExit(f"Robustfolio outcomes not found: {outcomes_path}")
    outcomes = pd.read_csv(outcomes_path).set_index("method")
    b3 = float(outcomes.loc["B3", "net_sharpe"])
    bl_gap = float(outcomes.loc["M2", "net_sharpe"]) - b3
    shrinkage_gap = float(outcomes.loc["M1", "net_sharpe"]) - b3

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": MUTED,
            "ytick.color": INK,
            "axes.edgecolor": GRID,
            "axes.linewidth": 0.8,
            "figure.facecolor": PAPER_BG,
            "axes.facecolor": PAPER_BG,
            "savefig.facecolor": PAPER_BG,
        }
    )

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.2, 2.55),
        gridspec_kw={"width_ratios": [1.0, 1.0]},
    )

    ax = axes[0]
    labels = ["v2 · conformal", "v3 · tail"]
    values = [v2_gate, v3_gate]
    bars = ax.barh(
        labels,
        values,
        color=[NAVY, OXBLOOD],
        height=0.52,
        edgecolor="none",
    )
    ax.axvline(80, color=GOLD, linestyle="--", linewidth=1.2)
    ax.annotate(
        "80% rule",
        xy=(80, 0.5),
        xycoords=("data", "axes fraction"),
        xytext=(4, 0),
        textcoords="offset points",
        color=GOLD,
        fontsize=7.2,
        va="center",
        ha="left",
    )
    for bar, value in zip(bars, values, strict=False):
        ax.text(
            value + 1.8,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}%",
            va="center",
            fontsize=8.2,
            fontweight="bold",
            color=INK,
        )
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("date-level pass rate (%)", fontsize=7.4)
    ax.set_title("Epistemic DRO · information gate", fontsize=9.2, loc="left", pad=7)
    ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", labelsize=7.8, length=0)
    ax.tick_params(axis="x", labelsize=7.0)

    ax = axes[1]
    labels = ["Black–Litterman", "Shrinkage"]
    values = [bl_gap, shrinkage_gap]
    bars = ax.barh(
        labels,
        values,
        color=[GOLD, MUTED],
        height=0.52,
        edgecolor="none",
    )
    ax.axvline(0.20, color=GOLD, linestyle="--", linewidth=1.2)
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.annotate(
        "0.20 bar",
        xy=(0.20, 0.5),
        xycoords=("data", "axes fraction"),
        xytext=(-4, 0),
        textcoords="offset points",
        color=GOLD,
        fontsize=7.2,
        va="center",
        ha="right",
    )
    for bar, value in zip(bars, values, strict=False):
        x = value + 0.006 if value >= 0 else 0.006
        ha = "left"
        ax.text(
            x,
            bar.get_y() + bar.get_height() / 2,
            f"{value:+.3f}",
            va="center",
            ha=ha,
            fontsize=8.2,
            fontweight="bold",
            color=INK,
        )
    ax.set_xlim(-0.02, 0.22)
    ax.set_xticks([0.00, 0.05, 0.10, 0.15, 0.20])
    ax.set_xlabel("net Sharpe gap vs best baseline", fontsize=7.4)
    ax.set_title("Robustfolio · treatment gap", fontsize=9.2, loc="left", pad=7)
    ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", labelsize=7.8, length=0)
    ax.tick_params(axis="x", labelsize=7.0)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
