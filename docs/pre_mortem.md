# Project Pre-Mortem & Falsification Protocol

**Status:** Active — G-R2 artifact (2026-11-02)
**Protocol:** v1.1-rigor / v1.0-etf
**Owner:** Ken Ira Talingting
**Companion:** `docs/05_risk_register.md` (risk register), `docs/02_experiment_card.md` (frozen protocol)

> **Inversion premise.** It is 2026-11-30. The project failed. The result was leaky, non-reproducible, or overclaimed. Enumerate how that happened and the test that would have caught it today.

---

## 1. Catastrophic failure vectors

### Vector A — Data leakage and look-ahead (Model 2)
- **How it happens:** features use prices after month-end \(t\); ETF eligibility is backfilled before inception; metadata is current but treated as historical; a scaler is fitted on the full sample.
- **Test today:** `tests/test_falsification.py` target-shuffling harness; `tests/test_leakage.py` temporal/group guards; universe audit in `docs/data_dictionary.md` §4.
- **Failure signal:** shuffled-target score above the random baseline; `feature_timestamp > decision_timestamp`; eligible count before inception.

### Vector B — Spurious cross-sectional signal and multiple testing (Models 2 & 3)
- **How it happens:** 15–20 features and many hyperparameter combinations produce an apparent pattern in a short sample.
- **Test today:** mandatory Ridge baseline; deflated Sharpe; pre-registered primary metric; per-trial ledger; MI audit against a permutation null.
- **Failure signal:** LightGBM fails the Diebold-Mariano test against Ridge; the deflated Sharpe is below the threshold; the MI audit drops most features.

### Vector C — Regime shift and tail liquidation (Model 7)
- **How it happens:** the model is fit in a low-volatility period and fails in 2008, 2020, or 2022; CVaR is estimated from too few scenarios; the portfolio draws down beyond the guardrail.
- **Test today:** stress-period subanalysis; CVaR scenario count check; Pareto \(\alpha\) diagnostic; robust loss if \(\alpha < 4\).
- **Failure signal:** max drawdown breach in a stress window; CVaR unstable across scenario windows; \(\alpha < 4\) with MSE still in use.

### Vector D — Execution and cost erosion (Models 9 & 10)
- **How it happens:** turnover is high, the 10 bps assumption is optimistic, and the result disappears at 20–50 bps; the linear cost model ignores market impact.
- **Test today:** 5/10/20/50 bps sensitivity; turnover and cost-drag counter-metrics; no deployment claim.
- **Failure signal:** net Sharpe sign flips at 20 bps; turnover exceeds the pre-registered guardrail.

### Vector E — ETF survivorship and breadth (Models 2 & 7)
- **How it happens:** public data omit closed ETFs; fewer than 50 ETFs are eligible in a test month; the cross-section is too thin to detect the effect.
- **Test today:** eligible-count-by-month report; closure audit; explicit no-survivorship-free claim; stop if breadth < 50.
- **Failure signal:** universe count only rises; closure count is zero in a period with known closures; breadth below 50.

### Vector F — Solver failure and silent fallback (Model 2)
- **How it happens:** CLARABEL returns a non-optimal status and the pipeline substitutes equal weights; the reported weights are not the optimizer's output.
- **Test today:** `SolverFailure` is fatal; no fallback; `tests/test_optimization.py` covers failure paths; solver status logged in `DROSolution`.
- **Failure signal:** any rebalance uses equal weights after a failure; solver failure rate > 5%.

### Vector G — Claim inflation (Model 10)
- **How it happens:** the report says "beats the market", "institutional-grade", or "alpha" from a 4-week ETF methods study.
- **Test today:** model card §3 and §10; claim-evidence table; counter-metric gate; negative-result policy.
- **Failure signal:** any claim not backed by a pre-registered comparison or any causal language.

---

## 2. Mandatory kill criteria

These are consistent with `docs/00_project_charter.md` §9 and `docs/02_experiment_card.md` §9. A **negative result** is not a kill; it is a reportable finding.

| # | Condition | Action |
|---|---|---|
| 1 | No usable ETF snapshot: fewer than 50 eligible ETFs in any test month, or coverage too incomplete to support a methods claim | Stop and report the data limitation; do not backfill |
| 2 | Leakage: target-shuffling fails, temporal invariant fails, or a closed ETF is silently dropped | Stop; fix the data; no result may be reported |
| 3 | Baseline irreproducibility: Ridge B0 or 1/N cannot be reproduced across seeds | Stop; no model comparison is meaningful |
| 4 | Solver failure on more than 5% of rebalances | Stop and fix; no fallback weights |
| 5 | Uncertainty uncalibrated after two documented attempts | Simplify to a defensible proxy or stop |
| 6 | Ablation A2 shows no separation | Report the negative result; do not add complexity to force a positive one |
| 7 | Net Sharpe worse than the best baseline by more than 0.20 **and** no tail-risk improvement | Report as a negative result; do not claim success |
| 8 | Result disappears at 20 bps or 50 bps costs | Report the cost sensitivity; do not hide it |

**Sunk-cost rule:** a failed gate is not a reason to add features, layers, or trials. It is a reason to stop, simplify, or report.

---

## 3. Tests that must exist before the first confirmatory run

| Test | File | Status |
|---|---|---|
| Temporal monotonicity | `tests/test_leakage.py` | **Exists and passes** |
| Group/duplicate leakage | `tests/test_leakage.py` | **Exists and passes** |
| Target-shuffling harness | `tests/test_falsification.py` | **Added** |
| Counter-metric gate | `src/epistemic_dro/evaluation.py` + tests | **Added** |
| Ridge baseline | `src/epistemic_dro/baselines.py` + tests | **Added** |
| Solver failure path | `tests/test_optimization.py` | **Exists and passes** |
| Universe/closure audit | G1 notebook/script | **Pending data** |
| MI/CMI audit | G1 notebook/script | **Pending data** |
| Pareto tail diagnostic | G1 notebook/script | **Pending data** |

---

## 4. Review

| Date | Reviewer | Decision |
|---|---|---|
| 2026-11-02 | Ken Ira Talingting | Adopt pre-mortem; no kill criteria triggered (no data runs yet) |
| 2026-11-07 | Owner | Re-check after leakage/baseline gate |
| 2026-11-21 | Owner | Re-check after ablation |
| 2026-11-30 | Owner | Final claim review |
