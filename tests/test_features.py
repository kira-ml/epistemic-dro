from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from epistemic_dro.features import FeatureSpec, build_features, build_targets


def _fixture(
    n_months: int = 60,
    n_tickers: int = 3,
    seed: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2015-01-31", periods=n_months, freq="ME")
    tickers = [f"T{i}" for i in range(n_tickers)]
    monthly_returns = rng.normal(0.005, 0.04, size=(n_months, n_tickers))
    adj = pd.DataFrame(
        100.0 * np.cumprod(1.0 + monthly_returns, axis=0),
        index=dates,
        columns=tickers,
    )

    prices = pd.concat(
        [
            pd.DataFrame(
                {
                    "date": dates,
                    "ticker": ticker,
                    "close": adj[ticker].to_numpy(),
                    "adj_close": adj[ticker].to_numpy(),
                    "volume": 1_000_000.0,
                    "dollar_volume": 100_000_000.0,
                }
            )
            for ticker in tickers
        ],
        ignore_index=True,
    )

    factors = pd.DataFrame(
        {
            "date": dates,
            "mkt_rf": rng.normal(0.005, 0.03, size=n_months),
            "smb": rng.normal(0.0, 0.02, size=n_months),
            "hml": rng.normal(0.0, 0.02, size=n_months),
            "mom": rng.normal(0.0, 0.02, size=n_months),
            "rf": 0.001,
        }
    )

    universe = pd.DataFrame(
        [
            {"date": date, "ticker": ticker, "eligible": True}
            for date in dates
            for ticker in tickers
        ]
    )

    metadata = pd.DataFrame(
        [
            {
                "ticker": ticker,
                "name": ticker,
                "inception_date": dates[0],
                "category": "Test",
                "role": "test",
                "expense_ratio": 0.1,
                "distribution_yield": 0.02,
                "metadata_vintage": "current_snapshot_unavailable",
            }
            for ticker in tickers
        ]
    )

    returns = prices.sort_values(["ticker", "date"]).copy()
    returns["ret"] = returns.groupby("ticker")["adj_close"].pct_change()
    returns = returns.dropna(subset=["ret"])
    returns["rf"] = 0.001
    returns["excess_ret"] = returns["ret"] - returns["rf"]
    returns = returns[["date", "ticker", "ret", "excess_ret", "rf"]]

    return prices, metadata, universe, factors, returns


def test_build_features_returns_complete_ranked_panel() -> None:
    prices, metadata, universe, factors, _ = _fixture()
    features = build_features(prices, metadata, universe, factors, FeatureSpec())

    assert features.index.names == ["date", "ticker"]
    assert not features.empty
    assert features.isna().sum().sum() == 0
    assert "forward_excess_return_1m" not in features.columns
    assert "expense_ratio" not in features.columns
    assert features.min().min() >= -0.5
    assert features.max().max() <= 0.5


def test_build_features_uses_only_past_prices() -> None:
    prices, metadata, universe, factors, _ = _fixture()
    spec = FeatureSpec()
    first = build_features(prices, metadata, universe, factors, spec)

    mutated = prices.copy()
    last_date = mutated["date"].max()
    mutated.loc[mutated["date"] == last_date, "adj_close"] *= 2.0
    second = build_features(mutated, metadata, universe, factors, spec)

    earlier_date = sorted(first.index.get_level_values("date").unique())[-2]
    pd.testing.assert_frame_equal(
        first.loc[earlier_date],
        second.loc[earlier_date],
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )


def test_build_features_respects_universe_filter() -> None:
    prices, metadata, universe, factors, _ = _fixture()
    date = sorted(universe["date"].unique())[-1]
    ticker = "T0"
    universe.loc[(universe["date"] == date) & (universe["ticker"] == ticker), "eligible"] = False

    features = build_features(prices, metadata, universe, factors, FeatureSpec())
    assert (date, ticker) not in features.index
    assert (date, "T1") in features.index


def test_build_features_raw_momentum_matches_price_change() -> None:
    prices, metadata, universe, factors, _ = _fixture()
    spec = FeatureSpec(cross_sectional_rank=False, winsorize=0.0)
    features = build_features(prices, metadata, universe, factors, spec)

    ticker = "T0"
    ticker_prices = prices[prices["ticker"] == ticker].sort_values("date").reset_index(drop=True)
    position = 40
    date = ticker_prices.loc[position, "date"]
    expected = (
        ticker_prices.loc[position, "adj_close"]
        / ticker_prices.loc[position - 1, "adj_close"]
        - 1.0
    )
    assert features.loc[(date, ticker), "mom_1m"] == pytest.approx(expected)


def test_build_targets_aligns_next_month_excess_return() -> None:
    _, _, _, _, returns = _fixture()
    targets = build_targets(returns)
    ticker = "T0"
    dates = sorted(returns.loc[returns["ticker"] == ticker, "date"].unique())
    date = dates[10]
    next_date = dates[11]
    expected = returns.loc[
        (returns["ticker"] == ticker) & (returns["date"] == next_date), "excess_ret"
    ].iloc[0]
    assert targets.loc[(date, ticker), "forward_excess_return_1m"] == pytest.approx(expected)
    assert targets.isna().sum().sum() == 0


def test_build_features_rejects_missing_factor_columns() -> None:
    prices, metadata, universe, factors, _ = _fixture()
    with pytest.raises(ValueError, match="missing columns"):
        build_features(
            prices,
            metadata,
            universe,
            factors.drop(columns=["mom"]),
            FeatureSpec(),
        )
