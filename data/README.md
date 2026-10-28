# Data

**Status: BLOCKED.** The data source must be selected by **2026-10-31**. No vendor data are included in this repository.

## Why this is a gate

A stock-level backtest that uses today's index constituents or a free price API will contain:

- **survivorship bias** — delisted and bankrupt firms disappear;
- **look-ahead bias** — today's universe knows which firms survived;
- **restatement bias** — fundamentals are revised after the fact;
- **timestamp leakage** — a macro or filing value is used before it was public.

Any of these can manufacture a result. This project treats data provenance as a first-class research contribution, not plumbing.

## Options

| Source | Pros | Cons | Verdict |
|---|---|---|---|
| **CRSP + Compustat via WRDS** | Historical constituents, delisting returns, PIT fundamentals, academic standard | Requires university/library access; licensing restricts redistribution | Preferred |
| **Sharadar / Norgate** | Practical, survivorship-bias-aware, easier setup | Paid; verify PIT fundamentals and delisting handling | Acceptable if verified |
| **Free prices + current constituents** | Free and fast | Survivorship and look-ahead bias; not credible for a stock-level flagship | Reject for stock-level claims |
| **ETF / factor data** | Clean, reproducible, free or cheap | Weaker cross-sectional ML story; fewer assets | Fallback / methods study |

If the only available data are free prices and current constituents, the project pivots to an ETF/factor universe and is labelled a methods study. It does not claim stock-selection validity.

## Required files

Place vendor exports under `data/raw/` (gitignored). The loader expects these logical tables; exact filenames can be configured.

### `prices`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Month-end trading date |
| `ticker` | string | Stable security identifier preferred |
| `close` | float | Split-adjusted close |
| `adj_close` | float | Total-return-adjusted close |
| `volume` | float | Shares |
| `dollar_volume` | float | Close × volume |

### `returns`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Month-end |
| `ticker` | string | |
| `ret` | float | Total return, including delisting return where applicable |
| `excess_ret` | float | `ret - rf` |

### `fundamentals`

| Column | Type | Notes |
|---|---|---|
| `ticker` | string | |
| `datadate` | date | Fiscal-period end |
| `rdq` | date | Report date; **use this for PIT availability** |
| `fiscal_period` | string | |
| `book_equity` | float | |
| `earnings` | float | |
| `roe` | float | |
| `gross_profitability` | float | |
| `market_cap` | float | |

### `universe`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Formation date |
| `ticker` | string | |
| `eligible` | bool | Passes liquidity/price/history filters as of `date` |

### `risk_free` and `benchmark`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Month-end |
| `rf` | float | Monthly risk-free return |
| `benchmark_ret` | float | Optional benchmark total return |

## Point-in-time rules

1. A fundamental value is available only on or after its `rdq` (report date), not its `datadate`.
2. A feature at month-end `t` may use data timestamped at or before `t`; it may not use `t+1` prices or returns.
3. Universe eligibility is computed from data available at `t`, not from the full sample.
4. Delisting returns are included in the month of delisting; do not silently drop the row.
5. Corporate actions are handled by the vendor's adjusted prices; document the convention.
6. Restatements: use the vintage available at the time, not the final revised value, if the vendor supports vintages.

## Versioning

Record for every snapshot:

- vendor and dataset name;
- pull date;
- coverage start/end;
- row counts and checksum;
- any filters applied;
- the exact query or export script.

Store the manifest in `data/raw/MANIFEST.json` (gitignored) and copy the human-readable summary into `docs/01_data_card.md`.

## Licensing

- Do not commit raw vendor data.
- Do not commit derived rows that reconstruct a licensed dataset.
- A public repo may include code, synthetic smoke-test data, and aggregate results.
- Check the vendor's terms before publishing any figure that contains raw values.
