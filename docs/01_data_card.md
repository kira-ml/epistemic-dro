# Data Card — Epistemic-Aware DRO

**Status:** BLOCKED — source not selected  
**Owner:** Ken Ira Talingting  
**Decision deadline:** 2026-10-31  
**Last updated:** 2026-10-27

---

## 1. Purpose

This card documents the data needed to test whether epistemic uncertainty improves a DRO mean-CVaR portfolio. It is also the G1 gate artefact: modelling does not start until the source, provenance, timing, and leakage risks are resolved.

---

## 2. Source decision

| Candidate | Historical universe | Delisting returns | PIT fundamentals | Cost / access | Verdict |
|---|---|---|---|---|---|
| **CRSP + Compustat (WRDS)** | Yes | Yes | Yes | University/library access; redistribution restricted | **Preferred** |
| **Sharadar** | Yes, if using the survivorship-bias-free tier | Verify | Verify `datekey` / filing-date semantics | Paid | Acceptable after verification |
| **Norgate** | Yes | Yes | Verify fundamentals coverage | Paid | Acceptable after verification |
| **Yahoo / Stooq + current constituents** | No | No | No | Free | Reject for stock-level claims |
| **ETF / factor data** | Fund universe is limited | Less severe | N/A | Free/low cost | Fallback / methods study |

**Decision:** `UNKNOWN` until 2026-10-31.

**If no PIT stock data:** pivot to a 50–100 ETF universe, keep the DRO/CVaR method, and state that the project is a methods study. Do not claim stock-selection validity.

---

## 3. Required coverage

| Item | Requirement | Status |
|---|---|---|
| Start date | At least 2005-01; 2010-01 minimum for OOS | TBD |
| End date | 2024-12 or later | TBD |
| Frequency | Monthly | TBD |
| Universe | 150–200 liquid US stocks, PIT | TBD |
| Returns | Total return, including delisting | TBD |
| Prices | Split- and dividend-adjusted | TBD |
| Fundamentals | PIT, with report date | TBD |
| Risk-free | Monthly T-bill or equivalent | TBD |
| Benchmark | Optional, for diagnostics | TBD |
| Corporate actions | Vendor-adjusted; convention documented | TBD |
| Identifier | Stable ticker/permno/CUSIP mapping | TBD |

---

## 4. Schema (logical)

### Prices

`date, ticker, close, adj_close, volume, dollar_volume`

### Returns

`date, ticker, ret, excess_ret`

### Fundamentals

`ticker, datadate, rdq, fiscal_period, book_equity, earnings, roe, gross_profitability, market_cap`

### Universe

`date, ticker, eligible`

### Risk-free / benchmark

`date, rf, benchmark_ret`

Exact filenames and vendor mappings belong in `configs/base.yaml` and the loader, not in this card.

---

## 5. Point-in-time rules

1. **Fundamentals:** available on or after `rdq` (report date), not `datadate`.
2. **Prices:** a feature at month-end `t` uses data timestamped at or before `t`.
3. **Universe:** eligibility is computed from data available at `t`, not from the full sample.
4. **Delisting:** include the delisting return in the delisting month; do not drop the row.
5. **Restatements:** use the vintage available at the time if the vendor provides it; otherwise document the limitation.
6. **Timezone:** all timestamps normalized to UTC; month-end defined explicitly.
7. **Macro releases:** use the release date, not the reference period.

---

## 6. Leakage audit

| Risk | Test | Status |
|---|---|---|
| Target leakage | Check that no feature is derived from the label or future returns | TBD |
| Temporal leakage | Assert `feature_date <= decision_date` for every row | TBD |
| Group leakage | No entity in both train and test | TBD |
| Preprocessing leakage | Fit imputation/scaling/winsorization inside training only | TBD |
| Universe leakage | Historical eligibility, not current constituents | TBD |
| Delisting leakage | Delisted firms remain until their delisting date | TBD |
| Benchmark contamination | No test-period data in model selection | TBD |
| Duplicate leakage | Deduplicate by security/date before splitting | TBD |

The code-level guard lives in `src/epistemic_dro/leakage.py`; tests live in `tests/test_leakage.py`.

---

## 7. Quality checks

- Row counts by month and ticker.
- Missingness by field and by subgroup.
- Duplicate `(date, ticker)` rows.
- Extreme returns and their provenance.
- Price jumps around splits/dividends.
- Universe count over time.
- Fundamentals coverage by month.
- Label distribution over time.
- Delisting counts by month.
- Risk-free series completeness.
- Train/serving schema consistency.

---

## 8. Versioning and licensing

Record:

- vendor and dataset;
- pull date;
- coverage start/end;
- row counts;
- SHA-256 manifest;
- filters applied;
- query/export script.

Do **not** commit raw vendor data. Do **not** publish derived rows that reconstruct a licensed dataset. Public artefacts should be code, synthetic smoke-test data, and aggregate results.

---

## 9. Open questions

1. Which source can actually be accessed by 2026-10-31?
2. Does the source provide historical index membership or a survivorship-bias-free universe?
3. Are delisting returns included?
4. Are fundamentals point-in-time, with report dates?
5. Is the risk-free series monthly and complete?
6. What redistribution restrictions apply to figures and tables?

---

## 10. Sign-off

| Gate | Criterion | Status |
|---|---|---|
| G1 | Source selected; schema validated; leakage audit clean; splits match deployment | **Not passed** |
| Reviewer | Ken Ira Talingting | Pending |
