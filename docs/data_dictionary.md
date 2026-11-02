# Project Data Dictionary & Lineage Specification

**Status:** Active — G-R4 artifact (2026-11-02; MI audit pending G1)
**Protocol:** v1.1-rigor / v1.0-etf
**Companion:** `docs/01_data_card.md` (source decision, PIT rules, leakage audit)

This file is the definitive schema, unit, lineage, and information-audit record. It is stricter than `data/README.md`: the README says what files are expected; this dictionary says what each column means and which invariants it must satisfy.

---

## 1. Dataset overview and authoritative source

| Field | Value |
|---|---|
| Dataset name | `epistemic-dro-etf-monthly` |
| Primary source | Public ETF total-return data (provider recorded in `data/raw/MANIFEST.json`) |
| Supporting sources | FRED `TB3MS`; Fama-French 3-factor + momentum |
| Immutable raw path | `data/raw/` (gitignored; never overwrite) |
| Processed path | `data/processed/` (deterministic transforms only) |
| Frequency | Monthly, month-end |
| Unit of analysis | ETF-month |
| Update cadence | One frozen snapshot per experiment; no live feed |
| Data generation mechanism | Secondary-market ETF prices + distributions + factor returns; see `docs/axiomatic_spec.md` §2 |

**Lineage rule:** every processed artefact must be reproducible from `data/raw/` plus a versioned script. No manual edits to processed data.

---

## 2. Target variable specification (Models 1 & 8)

| Field | Value |
|---|---|
| Target name | `forward_excess_return_1m` |
| Formula | \(r^{\text{ex}}_{i,t+1} = r_{i,t+1} - r_{f,t+1}\) |
| Return construction | `adj_close(t+1) / adj_close(t) - 1`, distribution-adjusted |
| Temporal alignment | Features at month-end \(t\); outcome over \((t, t+1]\) |
| Decision use | Cross-sectional rank or winsorized return; the model does not trade the raw level |
| Distribution characteristics | Pareto \(\alpha\), kurtosis, skew, and tail quantiles: **pending G1** |
| Absorbing barrier | ETF closure / total loss; a closed fund must not be silently dropped |
| Theoretical Bayes risk | See `docs/axiomatic_spec.md` §5; **pending G1** |

**Leakage invariant:** no target-derived column may appear in the feature matrix. The target is constructed only after the feature snapshot is frozen.

---

## 3. Feature definitions and information audit (Models 4 & 5)

All features are lagged to month-end \(t\). Returns and prices use only data \(\le t\). The MI columns are intentionally blank until the G1 audit; filling them with invented values would defeat the purpose.

| Feature | Raw / derived | Unit | Frequency | Causal role | MI \(I(X;Y)\) | Conditional MI | Lag / window |
|---|---|---|---|---|---|---|---|
| `mom_1m` | Derived | decimal return | monthly | proxy for short-term reversal/momentum | pending | pending | 1 month |
| `mom_3m` | Derived | decimal return | monthly | momentum proxy | pending | pending | 3 months |
| `mom_6m` | Derived | decimal return | monthly | momentum proxy | pending | pending | 6 months |
| `mom_12m` | Derived | decimal return | monthly | momentum proxy | pending | pending | 12 months |
| `vol_3m` | Derived | decimal volatility | monthly | risk-state proxy | pending | pending | 3 months |
| `vol_12m` | Derived | decimal volatility | monthly | risk-state proxy | pending | pending | 12 months |
| `mdd_12m` | Derived | decimal drawdown | monthly | tail-state proxy | pending | pending | 12 months |
| `dollar_vol_12m` | Derived | USD | monthly | liquidity proxy | pending | pending | 12 months |
| `beta_36m` | Derived | unitless | monthly | factor exposure | pending | pending | 36 months |
| `exp_mkt` | Derived | unitless loading | monthly | factor exposure | pending | pending | 36 months |
| `exp_smb` | Derived | unitless loading | monthly | factor exposure | pending | pending | 36 months |
| `exp_hml` | Derived | unitless loading | monthly | factor exposure | pending | pending | 36 months |
| `exp_mom` | Derived | unitless loading | monthly | factor exposure | pending | pending | 36 months |
| `expense_ratio` | Raw metadata | decimal | current snapshot | selection proxy | pending | pending | as-of only if history exists |
| `distribution_yield` | Raw metadata | decimal | current snapshot | selection proxy | pending | pending | as-of only if history exists |

**MI audit rule (G-R4):** compute \(I(X_i;Y)\) and \(I(X_i;Y \mid X_{\text{selected}})\) on each training window with a permutation null. A feature that fails to beat the 95th percentile of the null in at least 80% of windows is dropped. Record every drop and its reason in this table or in the experiment ledger.

**Metadata caveat:** if historical expense ratio/yield is unavailable, the field is excluded from the primary model or explicitly disclosed as a current-snapshot feature. It must never be described as point-in-time.

---

## 4. Leakage and integrity invariants (Model 2)

1. **Timestamp invariant:** every feature row satisfies `feature_timestamp <= decision_timestamp`.
2. **No-backfill invariant:** an ETF is ineligible before `inception_date`.
3. **Closure invariant:** a closed ETF remains in the panel through its closure month; omission is recorded as a survivorship limitation.
4. **Scaler invariant:** imputation, scaling, winsorization, and MI screening are fit on the training window only.
5. **Target invariant:** the target is never used in feature construction, feature selection, universe formation, or hyperparameter tuning.
6. **Duplicate invariant:** `(date, ticker)` is unique before splitting.
7. **Survivor invariant:** no silent deletion of failed/closed funds; the universe count by month is reported.
8. **Schema invariant:** train and serving columns, dtypes, and units match; a schema mismatch is a fatal error.

---

## 5. Data quality checks (G1)

- [ ] Row counts by month and ticker.
- [ ] Missingness by field and by month.
- [ ] Duplicate `(date, ticker)` count = 0.
- [ ] Extreme return provenance reviewed.
- [ ] Price jumps around splits/distributions reviewed.
- [ ] Universe count by month; months below 50 flagged.
- [ ] ETF closure count by month.
- [ ] Metadata vintage recorded.
- [ ] Risk-free series complete for every month.
- [ ] Factor series complete and pull date recorded.
- [ ] Target distribution: mean, volatility, skew, kurtosis, Pareto \(\alpha\).
- [ ] Train/serving schema comparison.

---

## 6. Versioning

Every snapshot records:

- provider and dataset;
- pull date;
- coverage start/end;
- row counts;
- SHA-256 manifest;
- filters applied;
- query/export script;
- the commit hash that first consumed it.

The manifest lives in `data/raw/MANIFEST.json` (gitignored); the human-readable summary is copied into `docs/01_data_card.md` §3 and §8.

---

## 7. Sign-off

| Gate | Criterion | Status |
|---|---|---|
| G1 schema | Columns, units, and dtypes match this dictionary | **Pending** |
| G1 lineage | Manifest and pull script recorded | **Pending** |
| G1 leakage | Invariants §4 pass on the real snapshot | **Pending** |
| G-R4 information | MI/CMI audit complete | **Pending** |
| Reviewer | Ken Ira Talingting | Pending |
