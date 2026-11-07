# Data

**Status: PIVOTED (2026-11-02) — ETF/factor methods study; G1 in progress.** No raw data snapshots are included in this repository. See `docs/01_data_card.md` and `docs/04_decision_log.md` DEC-20261102-001.

## Why this is a gate

A stock-level backtest that uses today's index constituents or a free price API will contain:

- **survivorship bias** — delisted and bankrupt firms disappear;
- **look-ahead bias** — today's universe knows which firms survived;
- **restatement bias** — fundamentals are revised after the fact;
- **timestamp leakage** — a macro or filing value is used before it was public.

No point-in-time stock source was secured by the 2026-10-31 deadline. Rather than manufacture a stock-level result, v1 pivots to ETFs and states the residual limitation: public ETF data may omit closed funds, so the result is a methods study and is **not** survivorship-free.

## Options

| Source | Pros | Cons | Verdict |
|---|---|---|---|
| **CRSP + Compustat via WRDS** | Historical constituents, delisting returns, PIT fundamentals, academic standard | Requires university/library access; licensing restricts redistribution | Not secured for v1; future stock experiment |
| **Sharadar / Norgate** | Practical, survivorship-bias-aware, easier setup | Paid; verify PIT fundamentals and delisting handling | Not selected for v1 |
| **Public ETF total-return data (Yahoo/Stooq)** | Free, reproducible, adjusted prices | Closed-fund coverage incomplete; provider terms apply | **Selected for v1 — methods study** |
| **Fama-French factors** | Free, standard, supports exposures and diagnostics | Factor portfolios are not ETFs | **Supporting data** |
| **Free stock prices + current constituents** | Free and fast | Survivorship and look-ahead bias; not credible | Reject |

## Required files

Place the ETF snapshot under `data/raw/` (gitignored). The loader expects these logical tables; exact filenames can be configured.

### `prices`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Month-end trading date |
| `ticker` | string | ETF ticker; stable identifier preferred |
| `close` | float | Split-adjusted close |
| `adj_close` | float | Total-return-adjusted close |
| `volume` | float | Shares |
| `dollar_volume` | float | Close × volume |

### `returns`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Month-end |
| `ticker` | string | |
| `ret` | float | Total return implied by `adj_close` |
| `excess_ret` | float | `ret - rf` |

### `etf_metadata`

| Column | Type | Notes |
|---|---|---|
| `ticker` | string | |
| `name` | string | |
| `category` | string | Broad category / strategy label |
| `inception_date` | date | **Use for PIT eligibility** |
| `expense_ratio` | float | Current snapshot unless a history exists |
| `distribution_yield` | float | Current snapshot unless a history exists |
| `underlying_index` | string | Optional |

### `universe`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Formation date |
| `ticker` | string | |
| `eligible` | bool | Listed on/before `date`, passes history/price/liquidity filters |

### `factors`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Month-end |
| `mkt_rf` | float | Market excess return |
| `smb` | float | Size factor |
| `hml` | float | Value factor |
| `mom` | float | Momentum factor |
| `rf` | float | Risk-free return |

### `risk_free` and `benchmark`

| Column | Type | Notes |
|---|---|---|
| `date` | date | Month-end |
| `rf` | float | Monthly risk-free return (from FRED `TB3MS`) |
| `benchmark_ret` | float | `SPY` total return (diagnostic) |

## Point-in-time rules

1. A feature at month-end `t` may use data timestamped at or before `t`; it may not use `t+1` prices or returns.
2. An ETF is eligible only on or after its `inception_date`; no backfill before listing.
3. Universe eligibility is computed from data available at `t`, not from the full sample or today's ETF list.
4. A closed ETF remains in the universe until its closure date; the closure month uses the final total return. If the provider omits a closed fund entirely, record that as a survivorship limitation.
5. Distribution-adjusted prices are required; document the provider's adjustment convention.
6. Expense ratio and distribution yield are current snapshots unless a historical series exists. Do not present them as point-in-time values.
7. The risk-free series is converted from the annualized `TB3MS` rate to a monthly return; document the conversion.
8. Factor data are pinned by pull date because the series can be revised.

## Versioning

Record for every snapshot:

- provider and dataset name;
- pull date;
- coverage start/end;
- row counts and checksum;
- any filters applied;
- the exact query or export script.

Store the manifest in `data/raw/MANIFEST.json` (gitignored) and copy the human-readable summary into `docs/01_data_card.md`.

## Licensing

- Do not commit raw snapshots.
- Do not commit derived rows that reconstruct a restricted dataset.
- A public repo may include code, synthetic smoke-test data, and aggregate or derived results that do not reconstruct raw vendor data.
- Check the provider's terms before publishing any figure that contains raw values.
- The repository's MIT license covers the code only; it does not grant rights to third-party data.
