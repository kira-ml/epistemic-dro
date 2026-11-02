"""Data-readiness checker.

Run this after building the ETF snapshot in ``data/raw/``. It checks the
logical files, then validates schema, keys, dates, and finite values through
``epistemic_dro.data.load_panel``. It does not validate every PIT edge case;
the full audit lives in ``docs/01_data_card.md`` and ``docs/data_dictionary.md``.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

REQUIRED = [
    "prices.parquet",
    "returns.parquet",
    "etf_metadata.parquet",
    "universe.parquet",
    "factors.parquet",
    "risk_free.parquet",
    "benchmark.parquet",
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

    try:
        from epistemic_dro.data import load_panel
    except ImportError as exc:
        print("\nCould not import epistemic_dro; install with `pip install -e .`.")
        raise SystemExit(1) from exc

    try:
        panel = load_panel(RAW)
    except (FileNotFoundError, ValueError) as exc:
        print(f"\nSchema validation FAILED: {exc}")
        raise SystemExit(1) from exc

    breadth = panel.universe.groupby("date")["eligible"].sum()
    print("\nSchema validation: PASS")
    print(f"  dates: {panel.prices['date'].min().date()} .. {panel.prices['date'].max().date()}")
    print(f"  tickers: {panel.metadata['ticker'].nunique()}")
    print(f"  prices rows: {len(panel.prices)}")
    print(f"  returns rows: {len(panel.returns)}")
    print(f"  eligible ETF-months: {int(panel.universe['eligible'].sum())}")
    print(
        "  breadth min/median/max: "
        f"{int(breadth.min())}/{int(breadth.median())}/{int(breadth.max())}"
    )
    print("\nNext: PIT/leakage audit and the G-R1/G-R4/G-R7 diagnostics.")


if __name__ == "__main__":
    main()
