# Risk Register and Pre-Mortem — Epistemic-Aware DRO

**Date:** 2026-10-27  
**Status:** Draft  
**Owner:** Ken Ira Talingting

---

## 1. Pre-mortem

It is 2026-11-30. The project failed. Why?

1. The data source arrived late or was not survivorship-bias-free, so the stock-level results were not credible.
2. The ML model leaked future information through fundamentals or universe construction.
3. The DRO formulation was wrong, and the “robust” portfolio was just a constrained mean-variance portfolio.
4. CVaR was estimated from too few scenarios, so the tail constraint was noise.
5. Hyperparameters were tuned on the test period, producing a result that did not replicate.
6. Transaction costs were underestimated, and the strategy traded too much.
7. The solver failed silently and equal weights were substituted.
8. The uncertainty layer was uncalibrated, so the ambiguity set was arbitrary.
9. The result was within noise, but the report claimed success.
10. Scope creep added deep ensembles, RL, or market-impact modelling and none of the core pieces was finished.

---

## 2. Risk register

| ID | Risk | Likelihood | Impact | Early warning | Mitigation | Kill / stop |
|---|---|---|---|---|---|---|
| R1 | No PIT data access | High | Critical | No vendor decision by Oct 31 | WRDS/Sharadar/Norgate; ETF fallback | Pivot by Oct 31 |
| R2 | Survivorship bias | High | Critical | Universe count only rises; no delistings | Historical membership; delisting returns | Stop stock-level claims |
| R3 | Look-ahead in fundamentals | High | Critical | Features predict too well; `rdq` missing | Use report dates; lag features; audit | Stop and fix |
| R4 | Universe leakage | Medium | High | Current constituents used | PIT eligibility; as-of joins | Stop and fix |
| R5 | DRO formulation error | Medium | High | “Robust” weights identical to MVO | Unit tests; compare box/ellipsoid; inspect KKT | Fix or drop claim |
| R6 | CVaR scenario insufficiency | Medium | High | Fewer than 1/(1−α) scenarios; unstable tails | Use enough history; stress windows | Widen scenarios or stop |
| R7 | Hyperparameter overfitting | High | High | Many trials; test-set tuning | Validation-only tuning; frozen protocol; DSR | Report as exploratory |
| R8 | Multiple testing | High | High | Best of many runs | Pre-register; report all trials; deflated Sharpe | Do not claim significance |
| R9 | Cost underestimate | Medium | High | High turnover; result dies at 20 bps | 5/10/20/50 bps sensitivity | Report cost sensitivity |
| R10 | Solver failure / fallback | Medium | High | Equal weights after failure | Raise on failure; log status | Stop and fix |
| R11 | Uncalibrated uncertainty | High | Medium | Coverage far from nominal | Reliability plot; conformal calibration | Simplify uncertainty |
| R12 | Reproducibility failure | Medium | High | Results differ across runs | Seeds, lockfile, config hash, manifest | Fix before reporting |
| R13 | Scope creep | High | Medium | Deep ensembles/RL added before baseline | Gate discipline; v1 scope | Defer to v2 |
| R14 | Claim inflation | Medium | High | “Alpha,” “institutional-grade,” “beats market” | Claim calibration table; model card | Rewrite claims |
| R15 | Negative result hidden | Medium | High | Only favorable runs reported | Decision log; all trials logged | Publish honestly |

---

## 3. Ruin scenarios

For a research project, “ruin” means the result is unusable or the claim is false.

| Scenario | Absorbing loss | Prevention |
|---|---|---|
| Data is not PIT | Entire empirical claim collapses | Gate G1; vendor verification |
| Test set reused | No unbiased estimate remains | Frozen holdout; log every evaluation |
| Solver silently fails | Weights are not the optimizer’s output | Fatal errors; no fallback |
| Results are noise | Resume claim is misleading | CIs; DSR; pre-registration |
| Vendor data redistributed | License breach | Gitignore; no raw data in repo |

---

## 4. Monitoring

Weekly during November:

- Data decision status.
- Leakage test status.
- Baseline reproducibility.
- Solver failure rate.
- Number of trials / multiple-testing count.
- Cost sensitivity.
- Whether the claim still matches the evidence.

---

## 5. Review

| Date | Reviewer | Changes |
|---|---|---|
| 2026-10-31 | Owner | Data decision |
| 2026-11-07 | Owner | Leakage/baseline review |
| 2026-11-21 | Owner | Ablation review |
| 2026-11-30 | Owner | Final claim review |
