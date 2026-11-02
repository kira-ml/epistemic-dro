from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from epistemic_dro.data import load_panel


def _write_snapshot(root: Path) -> None:
    dates = pd.to_datetime(["2020-01-31", "2020-02-29", "2020-03-31"])
    tickers = ["AAA", "BBB"]
    prices = pd.DataFrame(
        [
            {"date": date, "ticker": ticker, "close": 10.0 + i, "adj_close": 10.0 + i,
             "volume": 1000.0, "dollar_volume": 10000.0}
            for date in dates
            for i, ticker in enumerate(tickers)
        ]
    )
    returns = pd.DataFrame(
        [
            {"date": dates[1], "ticker": ticker, "ret": 0.01, "excess_ret": 0.009, "rf": 0.001}
            for ticker in tickers
        ]
    )
    metadata = pd.DataFrame(
        [
            {"ticker": "AAA", "name": "A", "inception_date": pd.Timestamp("2019-01-01"),
             "category": "Broad", "role": "broad", "expense_ratio": None,
             "distribution_yield": None, "metadata_vintage": "current_snapshot_unavailable"},
            {"ticker": "BBB", "name": "B", "inception_date": pd.Timestamp("2019-01-01"),
             "category": "Broad", "role": "broad", "expense_ratio": None,
             "distribution_yield": None, "metadata_vintage": "current_snapshot_unavailable"},
        ]
    )
    universe = pd.DataFrame(
        [{"date": date, "ticker": ticker, "eligible": True} for date in dates for ticker in tickers]
    )
    factors = pd.DataFrame(
        [
            {"date": date, "mkt_rf": 0.01, "smb": 0.0, "hml": 0.0, "mom": 0.0, "rf": 0.001}
            for date in dates
        ]
    )
    risk_free = pd.DataFrame([{"date": date, "rf": 0.001} for date in dates])
    benchmark = pd.DataFrame([{"date": date, "benchmark_ret": 0.01} for date in dates])

    for name, frame in {
        "prices": prices,
        "returns": returns,
        "etf_metadata": metadata,
        "universe": universe,
        "factors": factors,
        "risk_free": risk_free,
        "benchmark": benchmark,
    }.items():
        frame.to_parquet(root / f"{name}.parquet", index=False)


def test_load_panel_accepts_a_valid_snapshot(tmp_path: Path) -> None:
    _write_snapshot(tmp_path)
    panel = load_panel(tmp_path)
    assert len(panel.prices) == 6
    assert panel.metadata["ticker"].nunique() == 2
    assert panel.universe["eligible"].all()


def test_load_panel_rejects_duplicate_keys(tmp_path: Path) -> None:
    _write_snapshot(tmp_path)
    prices = pd.read_parquet(tmp_path / "prices.parquet")
    prices = pd.concat([prices, prices.iloc[[0]]], ignore_index=True)
    prices.to_parquet(tmp_path / "prices.parquet", index=False)
    with pytest.raises(ValueError, match="duplicate"):
        load_panel(tmp_path)


def test_load_panel_rejects_missing_table(tmp_path: Path) -> None:
    _write_snapshot(tmp_path)
    (tmp_path / "factors.parquet").unlink()
    with pytest.raises(FileNotFoundError, match="factors"):
        load_panel(tmp_path)


def test_load_panel_rejects_non_finite_returns(tmp_path: Path) -> None:
    _write_snapshot(tmp_path)
    returns = pd.read_parquet(tmp_path / "returns.parquet")
    returns.loc[0, "ret"] = np.nan
    returns.to_parquet(tmp_path / "returns.parquet", index=False)
    with pytest.raises(ValueError, match="non-finite"):
        load_panel(tmp_path)
