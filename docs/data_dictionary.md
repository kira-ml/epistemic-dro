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
| Distribution characteristics | Mean 0.00644; std 0.06064; skew −0.281; excess kurtosis 3.804; min −0.5526; max 0.6522; Hill loss-tail \(\alpha\) 3.08 (2026-11-02 snapshot) |
| Absorbing barrier | ETF closure / total loss; a closed fund must not be silently dropped |
| Theoretical Bayes risk | See `docs/axiomatic_spec.md` §5: Ridge B0 OOS \(R^2\) = −0.0186; mean IC = 0.0128 (t = 0.56). Linear signal indistinguishable from zero. |

**Leakage invariant:** no target-derived column may appear in the feature matrix. The target is constructed only after the feature snapshot is frozen.

---

## 3. Feature definitions and information audit (Models 4 & 5)

All features are lagged to month-end \(t\). Returns and prices use only data \(\le t\).

**G-R4 audit result (2026-11-02):** date-blocked permutation null (30 permutations, BH-FDR q < 0.05, 248 dates with ≥20 ETFs). No feature passed the 80% date-level survival rule. The table reports mean MI and pass rate. Conditional MI was not evaluated because there were no survivors. This is consistent with the Ridge B0 null and does **not** justify a LightGBM fit.

| Feature | Raw / derived | Unit | Frequency | Causal role | Mean MI \(I(X;Y)\) | Pass rate | Lag / window |
|---|---|---|---|---|---|---|---|
| `mom_1m` | Derived | decimal return | monthly | short-term reversal/momentum proxy | 0.1911 | 0.471 | 1 month |
| `mom_3m` | Derived | decimal return | monthly | momentum proxy | 0.2013 | 0.514 | 3 months |
| `mom_6m` | Derived | decimal return | monthly | momentum proxy | 0.2098 | 0.506 | 6 months |
| `mom_12m` | Derived | decimal return | monthly | momentum proxy | 0.2053 | 0.479 | 12 months |
| `vol_3m` | Derived | decimal volatility | monthly | risk-state proxy | 0.1945 | 0.502 | 3 months |
| `vol_12m` | Derived | decimal volatility | monthly | risk-state proxy | 0.2567 | 0.552 | 12 months |
| `mdd_12m` | Derived | decimal drawdown | monthly | tail-state proxy | 0.2263 | 0.544 | 12 months |
| `dollar_vol_12m` | Derived | USD | monthly | liquidity proxy | 0.0172 | 0.023 | 12 months |
| `beta_36m` | Derived | unitless | monthly | factor exposure | 0.2186 | 0.533 | 36 months |
| `exp_mkt_rf` | Derived | unitless loading | monthly | factor exposure | 0.2057 | 0.498 | 36 months |
| `exp_smb` | Derived | unitless loading | monthly | factor exposure | 0.1820 | 0.413 | 36 months |
| `exp_hml` | Derived | unitless loading | monthly | factor exposure | 0.1907 | 0.448 | 36 months |
| `exp_mom` | Derived | unitless loading | monthly | factor exposure | 0.1790 | 0.463 | 36 months |
| `expense_ratio` | Raw metadata | decimal | current snapshot | selection proxy | N/A | N/A | excluded — not PIT |
| `distribution_yield` | Raw metadata | decimal | current snapshot | selection proxy | N/A | N/A | excluded — not PIT |

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

Snapshot 2026-11-02: 72 ETFs, 19,712 price rows, 19,640 return rows, 252-300 months per fund.

- [x] Row counts by month and ticker (19,712 price rows; 72 tickers).
- [x] Missingness by field and by month (prices, returns, factors, risk-free complete; metadata fields null by design).
- [x] Duplicate `(date, ticker)` count = 0 in prices, returns, and universe.
- [ ] Extreme return provenance reviewed.
- [ ] Price jumps around splits/distributions reviewed.
- [x] Universe count by month; months below 50 flagged (min 21 in the 2000s; 68+ in every 2010+ month).
- [x] ETF closure count by month — **N/A / disclosed**: the snapshot is a current-listed universe; closed funds are not represented.
- [x] Metadata vintage recorded (`current_snapshot_unavailable`; expense ratio/yield null and excluded).
- [x] Risk-free series complete for every month (FRED `TB3MS`, 252/252 aligned months).
- [x] Factor series complete and pull date recorded (Ken French 3-factor + momentum).
- [x] Target distribution: mean 0.00644, std 0.06064, skew −0.281, excess kurtosis 3.804, Hill \(\alpha\) 3.08.
- [x] Train/serving schema comparison via `epistemic_dro.data.load_panel`.

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
| G1 schema | Columns, units, and dtypes match this dictionary | **PASS** — `load_panel` validation |
| G1 lineage | Manifest and pull script recorded | **PASS** — `data/raw/MANIFEST.json` + `scripts/build_snapshot.py` |
| G1 leakage | Invariants §4 pass on the real snapshot | **PASS for keys/PIT/duplication**; closure survivorship is disclosed, not eliminated |
| G-R4 information | MI/CMI audit complete | **PASS (null)** — no feature passed the 80% date-level rule; LightGBM not justified |
| Reviewer | Ken Ira Talingting | Pending |
