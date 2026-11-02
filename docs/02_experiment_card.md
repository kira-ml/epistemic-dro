# Experiment Card / Pre-Registration — Epistemic-Aware DRO

**Experiment ID:** `EXP-DRO-2026-11-01`
**Status:** FROZEN — v1.0-etf (2026-11-02)
**Freeze date:** 2026-11-02
**Owner:** Ken Ira Talingting
**Decision record:** `DEC-20261102-001` (ETF pivot), `DEC-20261102-003` (freeze)
**Tag:** `docs-freeze-v1`

> Do not run the confirmatory experiment until this card is frozen and dated. Exploratory runs must be labelled exploratory and may not be cited as confirmation.

---

## 1. Hypotheses

| ID | Hypothesis | Direction | Falsification |
|---|---|---|---|
| **H1** | Uncertainty-aware DRO reduces tail risk versus point-estimate DRO and mean-variance. | Lower max drawdown and CVaR95, net of costs | Improvement within noise or reverses at plausible costs |
| **H2** | Uncertainty-aware DRO is not materially worse on net Sharpe than the best baseline. | Net Sharpe ≥ best baseline − margin | Net Sharpe < best baseline − margin |
| **H3** | The uncertainty layer is the mechanism. | Removing it degrades the tail-risk result | Ablation without uncertainty matches or beats full method |

---

## 2. Primary metric and decision rule

**Primary metric:** Net Sharpe ratio, monthly, annualized, after 10 bps one-way costs, using an explicit risk-free series.

**Decision rule (frozen 2026-11-02):**

- **PASS** if:
  - net Sharpe is within 0.20 of the best baseline, **and**
  - max drawdown improves by at least 20% relative, **and**
  - CVaR95 improves with a 90% bootstrap interval excluding zero, **and**
  - the no-uncertainty ablation does not reproduce the improvement.
- **FAIL** otherwise.
- **INCONCLUSIVE** if the bootstrap interval is too wide to distinguish the effects; report the power limitation rather than declaring success.

The thresholds are frozen and must not be changed after seeing test results; any change requires a deviation entry in `04_decision_log.md`.

**Power note (frozen with the ETF pivot):** the v1 cross-section is 50–100 ETFs, not 150–200 stocks. Lower breadth and lower dispersion reduce the power to detect a tail-risk improvement. Report eligible-asset counts per month and describe the power limitation; do not treat a null result as evidence that the method is useless in a broader universe.

---

## 3. Secondary and guardrail metrics

| Metric | Role | Definition |
|---|---|---|
| Max drawdown | Guardrail | Minimum of cumulative wealth / running peak − 1 |
| CVaR95 | Guardrail | Mean of worst 5% of monthly net returns |
| Sortino | Diagnostic | Mean excess return / downside deviation |
| Calmar | Diagnostic | Annualized return / absolute max drawdown |
| Turnover | Guardrail | Annualized sum of absolute weight changes |
| Cost drag | Diagnostic | Gross Sharpe − net Sharpe |
| Calibration | Diagnostic | Reliability of uncertainty intervals |
| Max weight | Constraint check | Must be ≤ 5% |
| Leverage / short | Constraint check | Must be 0 |

---

## 4. Baselines

All baselines use the same universe, dates, constraints, and cost model.

| ID | Baseline | Definition |
|---|---|---|
| **B1** | 1/N | Equal weight across eligible assets, monthly rebalance |
| **B2** | Mean-variance | Sample mean and sample covariance; long-only; same cap |
| **B3** | CVaR-only | Minimize CVaR; no DRO; same constraints |
| **B4** | HRP | Hierarchical risk parity on the same covariance |
| **B5** | DRO-point | Box DRO with point-estimate mean and zero uncertainty |
| **M1** | DRO-uncertainty | Box DRO with ML mean and ensemble/conformal uncertainty |
| **M2** | DRO-ellipsoid | Ellipsoidal DRO with the same uncertainty |

The primary comparison is **M1 vs B5** (does uncertainty help?) and **M1 vs best baseline** (is the method competitive?).

---

## 5. Data and splits

| Item | Specification |
|---|---|
| Source | Public ETF total-return data + FRED `TB3MS` + Fama-French factors (DEC-20261102-001) |
| Universe | 50–100 liquid US-listed ETFs, PIT eligibility |
| Frequency | Monthly |
| Sample | 2005–2024, data permitting (ETF inception limits the early cross-section) |
| OOS | 2010–2024, data permitting |
| Split | Walk-forward: expanding or rolling training window |
| Train minimum | 60 months |
| Validation | 12 months, used for tuning only |
| Test | 12 months, rolled forward |
| Purge | 1 month between train/validation and test |
| Embargo | 1 month after test before the next training window |
| Final holdout | Last 12 months, touched once |

No random splits. No test-period information in feature construction, universe formation, hyperparameter tuning, or model selection. An ETF enters the panel only at or after its inception date; no backfill is permitted. Months with fewer than 50 eligible ETFs stop the run and are reported as a data limitation (charter §9 kill criterion 7).

---

## 6. Methods

### 6.1 ML return model

- Target: next-month cross-sectional excess-return rank (or winsorized return).
- Features (15–20 lagged signals, ETF-appropriate):
  - momentum: 1, 3, 6, and 12 months;
  - volatility: 3- and 12-month realised volatility;
  - drawdown: 12-month maximum drawdown;
  - liquidity: 12-month average dollar volume;
  - beta: 36-month beta to the market factor;
  - factor exposures: market, size, value, and momentum loadings;
  - metadata: expense ratio and distribution yield, only if a historical series exists. If only a current snapshot exists, either exclude these fields or disclose that they are not point-in-time.
- Model: LightGBM regression or ranking; 5 seeds.
- Tuning: validation window only; no test data.
- Feature preprocessing: fit inside each training window.

### 6.2 Uncertainty

- Ensemble variance across seeds, **or** split-conformal half-width calibrated on the validation window.
- Minimum floor to avoid zero uncertainty.
- Report calibration: empirical coverage of intervals.
- Do not confuse predictive uncertainty with historical volatility.

### 6.3 Optimizer

- Box ambiguity set: \(|\mu_i - \hat{\mu}_i| \le \kappa \hat{\sigma}_i\).
- Worst-case mean for long-only weights: \(\hat{\mu}^\top w - \kappa \sum_i \hat{\sigma}_i w_i\).
- CVaR penalty or constraint using historical scenario returns.
- Transaction cost: \(c \sum_i |w_i - w_{i-1}|\), linearized.
- Constraints: \(w \ge 0\), \(\sum w = 1\), \(w_i \le 0.05\).
- Solver: CLARABEL via `cvxpy`; no silent equal-weight fallback.

### 6.4 Hyperparameters

| Parameter | Candidate values | Selection |
|---|---|---|
| `kappa` | 0.0, 0.5, 1.0, 1.5, 2.0 | Validation only |
| `cvar_penalty` | 0.1, 0.5, 1.0, 2.0 | Validation only |
| `max_weight` | 0.03, 0.05, 0.10 | Fixed at 0.05 for primary |
| `cost_bps` | 5, 10, 20, 50 | 10 primary; others sensitivity |
| `n_estimators` | 100, 300, 600 | Validation only |
| `learning_rate` | 0.01, 0.03, 0.05 | Validation only |

Freeze the selected values before the confirmatory run.

---

## 7. Ablations

| Ablation | Question |
|---|---|
| **A1** DRO vs no DRO | Does robustness help beyond CVaR? |
| **A2** Uncertainty vs point | Does the epistemic layer add value? |
| **A3** CVaR vs variance | Is the tail measure doing the work? |
| **A4** Box vs ellipsoid | Is the ambiguity geometry important? |
| **A5** Costs on/off | Is the result an artifact of ignoring trading? |
| **A6** ML vs simple forecast | Is the ML layer necessary? |

Each ablation uses the same splits and cost model.

---

## 8. Statistical analysis

- Bootstrap the monthly net return series (2,000 reps) for Sharpe, max drawdown, and CVaR95.
- Report 90% intervals.
- Deflated Sharpe ratio to account for the number of trials.
- Paired comparison against the best baseline where possible.
- Subperiod analysis: 2008, 2020, 2022 stress windows.
- Report all trials, including failures, in the decision log.
- Report the number of eligible ETFs per month (effective breadth).
- No claim of significance without a pre-specified comparison.

---

## 9. Stopping rule

Stop the experiment and report if:

- leakage is found and cannot be removed;
- fewer than 50 ETFs are eligible in a test month, or the covered universe is too incomplete to support a methods claim;
- the solver fails on more than 5% of rebalances;
- the baseline cannot be reproduced;
- the uncertainty is uncalibrated after two attempts;
- the ablation shows no separation and the result is within noise.

Do not keep tuning until a positive result appears.

---

## 10. Threats to validity

| Threat | Mitigation |
|---|---|
| ETF closure survivorship | Disclose that public data may omit closed funds; do not claim survivorship-free; prefer a provider with closure history |
| Look-ahead bias | Feature timestamps; listing/inception dates |
| Metadata vintage | Expense ratio / yield are current snapshots unless a history exists; exclude or disclose |
| Universe breadth | Report eligible ETFs per month; state the power limitation; no broad-market claim |
| Data snooping | Frozen protocol; deflated Sharpe |
| Multiple testing | Pre-registered primary metric; report all trials |
| Cost underestimate | 5/10/20/50 bps sensitivity |
| CVaR scenario risk | Report tail scenarios; stress periods |
| DRO misspecification | Box and ellipsoid; sensitivity to `kappa` |
| Small sample | Bootstrap; report power limitations |
| Regime shift | Subperiod analysis; no claim of stability |
| Solver instability | Status checks; no fallback weights |

---

## 11. Freeze record

| Item | Value |
|---|---|
| Protocol version | `v1.0-etf` |
| Frozen by | Ken Ira Talingting (owner) |
| Freeze date | 2026-11-02 |
| Hash of config | `2c380990ae02c76c24044f783a5b9b1fb9e90abba67d228e959ebc7714a5cb83` (SHA-256, `configs/base.yaml`) |
| Git commit | Tag `docs-freeze-v1` (resolve with `git rev-parse docs-freeze-v1`) |
| Deviation log | `docs/04_decision_log.md` |

**No confirmatory run may occur before this record is complete.** The record is complete; the data gate (G1) and the modelling gates (G2–G4) remain open. Frozen protocol ≠ passed gates.
