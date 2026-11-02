# Data Card — Epistemic-Aware DRO

**Status:** PIVOTED — ETF/factor methods study (DEC-20261102-001); G1 in progress<br>
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
| Start date | At least 2005-01; 2010-01 minimum for OOS | Pending snapshot |
| End date | 2024-12 or later | Pending snapshot |
| Frequency | Monthly | Pending snapshot |
| Universe | 50–100 liquid US-listed ETFs, PIT eligibility | Pending snapshot |
| Returns | Total return, adjusted for distributions | Pending snapshot |
| Prices | Split- and distribution-adjusted | Pending snapshot |
| ETF metadata | Expense ratio, distribution yield, category, inception date | Pending snapshot; historical availability limited |
| Factors | Fama-French 3-factor + momentum, monthly | Pending snapshot |
| Risk-free | FRED `TB3MS`, converted to a monthly return | Pending snapshot |
| Benchmark | `SPY` total return (diagnostic) | Pending snapshot |
| Corporate actions | Vendor-adjusted; convention documented | Pending snapshot |
| Identifier | Ticker plus ISIN/CUSIP where available | Pending snapshot |

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
| Target leakage | Check that no feature is derived from the label or future returns | Pending dataset audit; code guard exists |
| Temporal leakage | Assert `feature_date <= decision_date` for every row | Pending dataset audit; `tests/test_leakage.py` passes |
| Group leakage | No entity in both train and test (walk-forward time split; duplicate check) | Pending dataset audit |
| Preprocessing leakage | Fit imputation/scaling/winsorization inside training only | Pending implementation |
| Universe leakage | PIT eligibility, no backfill before inception | Pending dataset audit |
| Closure leakage | Closed ETFs remain until closure; omission disclosed | Pending dataset audit |
| Metadata leakage | Expense ratio / yield not treated as PIT without history | Pending dataset audit |
| Benchmark contamination | No test-period data in model selection | Pending implementation |
| Duplicate leakage | Deduplicate by security/date before splitting | Pending dataset audit |

The code-level guard lives in `src/epistemic_dro/leakage.py`; tests live in `tests/test_leakage.py`.

---

## 7. Quality checks

- Row counts by month and ticker.
- Missingness by field and by subgroup.
- Duplicate `(date, ticker)` rows.
- Extreme returns and their provenance.
- Price jumps around splits/distributions.
- Universe count over time; months below 50 eligible ETFs.
- ETF metadata coverage and whether it is historical or current.
- Label distribution over time.
- ETF closures by month.
- Risk-free series completeness.
- Factor series completeness and revision date.
- Train/serving schema consistency.

---

## 8. Versioning and licensing

Record:

- provider and dataset;
- pull date;
- coverage start/end;
- row counts;
- SHA-256 manifest;
- filters applied;
- query/export script.

Do **not** commit raw data snapshots. Do **not** publish derived rows that reconstruct a restricted dataset. Public artefacts should be code, synthetic smoke-test data, and aggregate results. Check the provider's terms before publishing any figure containing raw values.

---

## 9. Open questions

1. Which public provider gives the most complete adjusted ETF history for 2005–2024?
2. How many ETFs have sufficient history in 2005–2010, and does the in-sample start need to move later?
3. Are closed ETFs represented at all? If not, how is the survivorship limitation disclosed in every results table?
4. Is historical expense-ratio or distribution-yield data available, or is only a current snapshot possible?
5. Is the FRED risk-free series complete for every month, and how is the annualized-to-monthly conversion documented?
6. What redistribution terms apply to the chosen provider's adjusted prices?

---

## 10. Sign-off

| Gate | Criterion | Status |
|---|---|---|
| G1 | Source selected; snapshot manifest; schema validated; leakage audit clean; splits match deployment | **Not passed** — source selected (ETF pivot); snapshot and audit pending |
| Reviewer | Ken Ira Talingting | Pending |

The docs freeze does **not** pass G1. The protocol is frozen before the data audit; the data gate remains open and is tracked in `08_monitoring_plan.md`.
