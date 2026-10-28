"""Data-readiness checker.

Run this after placing vendor exports in ``data/raw/``. It checks for the
logical files the pipeline needs; it does not validate PIT correctness.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

REQUIRED = [
    "prices.parquet",
    "returns.parquet",
    "fundamentals.parquet",
    "universe.parquet",
    "risk_free.parquet",
]


def main() -> None:
    print(f"Raw data directory: {RAW}")
    if not RAW.exists():
        raise SystemExit("data/raw does not exist")

    missing = [name for name in REQUIRED if not (RAW / name).exists()]
    for name in REQUIRED:
        status = "OK" if (RAW / name).exists() else "MISSING"
        print(f"  {status:8s} {name}")

    if missing:
        print("\nData gate NOT passed. Missing:", ", ".join(missing))
        print("See data/README.md and docs/01_data_card.md.")
        raise SystemExit(1)

    print("\nFiles present. Next: schema validation and leakage audit (G1).")


if __name__ == "__main__":
    main()
