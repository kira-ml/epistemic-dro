# Data Card — Epistemic-Aware DRO

**Status:** PIVOTED — ETF/factor methods study (DEC-20261102-001); **snapshot built 2026-11-02; G1 audit in progress**<br>
**Owner:** Ken Ira Talingting<br>
**Decision date:** 2026-11-02<br>
**Last updated:** 2026-11-02

> **Scope change.** No point-in-time stock-level source was secured by the
> 2026-10-31 deadline. Charter §9 kill criterion 1 was executed: v1 uses a
> 50–100 ETF universe and is a **methods study**. It makes no stock-selection
> claim and no survivorship-free claim.

---

## 1. Purpose

This card documents the data needed to test whether epistemic uncertainty improves a DRO mean-CVaR portfolio. It is also the G1 gate artefact: modelling does not start until the source, provenance, timing, and leakage risks are resolved.

The v1 pivot keeps the original question — does an uncertainty-aware robust optimizer improve the tail-risk/return trade-off? — while removing the stock-level claim that the available data cannot support.

---

## 2. Source decision

| Candidate | Historical universe | Closure / delisting handling | PIT fundamentals | Cost / access | Verdict |
|---|---|---|---|---|---|
| **CRSP + Compustat (WRDS)** | Yes | Yes | Yes | University/library access; redistribution restricted | **Not secured by 2026-10-31** |
| **Sharadar** | Yes, if using the survivorship-bias-free tier | Verify | Verify `datekey` / filing-date semantics | Paid | Not selected |
| **Norgate** | Yes | Yes | Verify fundamentals coverage | Paid | Not selected |
| **Public ETF total-return data (Yahoo/Stooq)** | Listing history assembled from inception/closure dates; incomplete for closed funds | Closures only partly represented | N/A (ETF metadata instead) | Free | **Selected for v1 — methods study** |
| **Fama-French factor data** | Factor portfolios, not individual ETFs | N/A | N/A | Free | **Supporting data** (exposures, benchmark, robustness) |

**Decision (DEC-20261102-001):** use 50–100 liquid US-listed ETFs with public total-return data, FRED for the risk-free series, and Fama-French factors for exposures and diagnostics.

**Why this is honest:** public ETF sources do not guarantee a complete history of closed funds. The v1 result is therefore a **methods study on the ETFs that the source covers**, not a survivorship-free asset-pricing test. The limitation is stated in `03_model_card.md` §10 and `05_risk_register.md` R2.

**If a PIT stock source becomes available later:** it is a new experiment with a new pre-registration. Do not silently swap universes and reuse the frozen protocol.

---

## 3. Required coverage

| Item | Requirement | Status |
|---|---|---|
| Start date | At least 2005-01; 2010-01 minimum for OOS | **Snapshot 2000-01-03 .. 2024-12-31** (warmup from 2000; features from 2003) |
| End date | 2024-12 or later | **2024-12-31** |
| Frequency | Monthly | **252 month-end observations** |
| Universe | 50–100 liquid US-listed ETFs, PIT eligibility | **72 ETFs; 68+ eligible in every 2010+ month** |
| Returns | Total return, adjusted for distributions | **19,640 rows; no missing ret/excess/rf** |
| Prices | Split- and distribution-adjusted | **19,712 rows; adjusted close** |
| ETF metadata | Expense ratio, distribution yield, category, inception date | **Category/inception present; expense ratio/yield null (not PIT)** |
| Factors | Fama-French 3-factor + momentum, monthly | **252 months, complete** |
| Risk-free | FRED `TB3MS`, converted to a monthly return | **FRED `TB3MS`, 252 aligned months** |
| Benchmark | `SPY` total return (diagnostic) | **251 months** |
| Corporate actions | Vendor-adjusted; convention documented | **Yahoo adjusted close; documented** |
| Identifier | Ticker plus ISIN/CUSIP where available | **Ticker; no ISIN/CUSIP in source** |

**Snapshot summary:** 72/72 tickers succeeded; 19,712 price rows; 19,640 returns; 300-month maximum history; breadth min/median/max = 21/72/72 (min 68 in 2010+). Manifest: `data/raw/MANIFEST.json` with SHA-256 per table. Provider: Yahoo Finance chart API (adjusted close), FRED `TB3MS`, Ken French 3-factor + momentum. Pull date: 2026-11-02.

**Minimum breadth:** at least 50 eligible ETFs in every test month. If a month has fewer than 50, the run stops and the limitation is reported rather than backfilled.

---

## 4. Schema (logical)

### Prices

`date, ticker, close, adj_close, volume, dollar_volume`

### Returns

`date, ticker, ret, excess_ret`

`ret` is the total return implied by `adj_close`; `excess_ret = ret - rf`.

### ETF metadata

`ticker, name, category, inception_date, expense_ratio, distribution_yield, underlying_index`

A single current metadata snapshot is acceptable for v1 **only if** the card records that expense ratio and yield are not point-in-time. If the provider supplies a history, use the as-of value.

### Universe

`date, ticker, eligible`

Eligibility is computed from data available at `date`: listed on or before `date`, minimum history, minimum price, minimum dollar volume, and not scheduled for closure before the decision date.

### Factors

`date, mkt_rf, smb, hml, mom, rf`

### Risk-free / benchmark

`date, rf, benchmark_ret`

Exact filenames and provider mappings belong in the loader and `data/raw/MANIFEST.json`, not in this card.

---

## 5. Point-in-time rules

1. **Prices and returns:** a feature at month-end `t` uses only prices and returns timestamped at or before `t`.
2. **Universe eligibility:** computed from data available at `t`; no asset is eligible before its inception date, and no asset is backfilled from a later listing.
3. **Closed ETFs:** an ETF remains in the universe until its closure date; the closure month uses the final total return. If the public source omits a closed fund entirely, that is a documented survivorship limitation, not a silent gap.
4. **Distributions and splits:** use distribution-adjusted prices; document the vendor convention. Do not reconstruct returns from unadjusted closes.
5. **ETF metadata:** expense ratio and distribution yield are treated as current snapshots unless a historical series exists. Do not present them as point-in-time values.
6. **Factor data:** use the published monthly series as of the snapshot date; record the download date because factor data can be revised.
7. **Risk-free:** use the release/vintage available at the decision date; convert the annualized T-bill rate to a monthly return and document the convention.
8. **Timezone:** all timestamps normalized to UTC; month-end defined explicitly.

---

## 6. Leakage audit

| Risk | Test | Status |
|---|---|---|
| Target leakage | Check that no feature is derived from the label or future returns | **PASS** — `build_features` has no target; `build_targets` is separate |
| Temporal leakage | Assert `feature_date <= decision_date` for every row | **PASS** — `tests/test_leakage.py`; features use rolling past windows only |
| Group leakage | No entity in both train and test (walk-forward time split; duplicate check) | **PASS** — time split; duplicate keys = 0 |
| Preprocessing leakage | Fit imputation/scaling/winsorization inside training only | **PASS by construction** — per-date rank; Ridge scaler fits train only |
| Universe leakage | PIT eligibility, no backfill before inception | **PASS** — 0 eligible rows before inception |
| Closure leakage | Closed ETFs remain until closure; omission disclosed | **DISCLOSED, not eliminated** — current-listed universe |
| Metadata leakage | Expense ratio / yield not treated as PIT without history | **PASS** — fields null and excluded by the vintage check |
| Benchmark contamination | No test-period data in model selection | **PENDING** — confirmatory run not started |
| Duplicate leakage | Deduplicate by security/date before splitting | **PASS** — 0 duplicates in prices/returns/universe |

The code-level guard lives in `src/epistemic_dro/leakage.py`; tests live in `tests/test_leakage.py`.

---

## 7. Quality checks

**Completed 2026-11-02:** row counts; missingness; duplicate keys; universe count; metadata vintage; risk-free completeness; factor completeness; target distribution; schema validation. **Pending:** manual provenance review of extreme returns and split/distribution price jumps.

- Row counts by month and ticker: 19,712 prices; 72 tickers.
- Missingness by field and by subgroup: returns/factors/risk-free complete; metadata fields null by design.
- Duplicate `(date, ticker)` rows: 0.
- Extreme returns and their provenance: **pending manual review**.
- Price jumps around splits/distributions: **pending manual review**.
- Universe count over time; months below 50 eligible ETFs: min 21 in the 2000s; 68+ in every 2010+ month.
- ETF metadata coverage and whether it is historical or current: current snapshot, expense/yield null.
- Label distribution over time: mean 0.00644; std 0.06064; skew −0.281; excess kurtosis 3.804.
- ETF closures by month: **N/A / disclosed** — current-listed universe.
- Risk-free series completeness: 252/252 aligned months.
- Factor series completeness and revision date: 252/252; pull date in manifest.
- Train/serving schema consistency: `load_panel` validation passes.

---

## 8. Versioning and licensing

**Snapshot record (2026-11-02):**

- Provider: Yahoo Finance chart API (adjusted close); FRED `TB3MS`; Ken French 3-factor + momentum.
- Pull date: 2026-11-02.
- Coverage: 2000-01-03 .. 2024-12-31 (prices); 252 month-end observations.
- Row counts: prices 19,712; returns 19,640; metadata 72; universe 19,712; factors 252; risk-free 300; benchmark 299.
- SHA-256: recorded per table in `data/raw/MANIFEST.json`.
- Filters: price ≥ $5; average daily dollar volume ≥ $1M; ≥36 months since inception.
- Script: `scripts/build_snapshot.py`; universe: `configs/etf_universe.csv`.
- Universe: 72 current-listed equity ETFs. Closed funds are not represented.

Do **not** commit raw data snapshots. Do **not** publish derived rows that reconstruct a restricted dataset. Public artefacts should be code, synthetic smoke-test data, and aggregate results. Check the provider's terms before publishing any figure containing raw values.

---

## 9. Open questions

1. Which public provider gives the most complete adjusted ETF history for 2005–2024? **Answered for v1:** Yahoo Finance chart API, 72/72 tickers; closed-fund coverage remains incomplete.
2. How many ETFs have sufficient history in 2005–2010, and does the in-sample start need to move later? **Answered:** 39–60 eligible in 2005–2009; 68+ in every 2010+ month. The frozen 60-month train uses the 2000–2004 warmup.
3. Are closed ETFs represented at all? If not, how is the survivorship limitation disclosed in every results table? **Open limitation:** not represented. Every results table must state "current-listed ETF universe; not survivorship-free."
4. Is historical expense-ratio or distribution-yield data available? **Answered for v1:** no; fields are null and excluded from the primary model.
5. Is the FRED risk-free series complete for every month? **Answered:** yes, 252/252 aligned months; FRED `TB3MS` used (no fallback).
6. What redistribution terms apply? **Open:** check Yahoo/French terms before publishing raw values; only aggregate results will be published.

---

## 10. Sign-off

| Gate | Criterion | Status |
|---|---|---|
| G1 | Source selected; snapshot manifest; schema validated; leakage audit clean; splits match deployment | **PASS with disclosed limitation** — snapshot validated; closure survivorship disclosed; G-R4 MI audit complete (null) |
| Reviewer | Ken Ira Talingting | Pending |

The docs freeze does **not** pass G1. The G1 schema/lineage/leakage checks pass for the covered universe; the MI audit (G-R4) found no surviving feature, so LightGBM is not justified and the reduced Ridge-based uncertainty test is the next step. The survivorship limitation is permanent for this snapshot.
