"""One-command result-level reproduction for the public package.

This does not rebuild the vendor data snapshot (raw data is not redistributed).
It runs the test suite, lint, the published-results verifier, and the paper build
from the committed aggregate tables.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("pytest", [sys.executable, "-m", "pytest", "-q"]),
    ("ruff", [sys.executable, "-m", "ruff", "check", "."]),
    ("verify_results", [sys.executable, "scripts/verify_results.py"]),
    ("build_paper", [sys.executable, "scripts/build_paper.py"]),
]


def main() -> int:
    for name, command in STEPS:
        print(f"\n==> {name}: {' '.join(command)}", flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
    print("\nResult-level reproduction passed.")
    print("Raw vendor snapshots are external and are not rebuilt by this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
