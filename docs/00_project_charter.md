# Project Charter — Epistemic-Aware DRO for Mean-CVaR Portfolios

**Project ID:** EPI-DRO-2026-11  
**Owner:** Ken Ira Talingting  
**Date:** 2026-10-27  
**Status:** G0 draft; G1 blocked on data access  
**Risk class:** Medium (research prototype; no live capital)

---

## 1. Decision

**Decision the work informs:** Whether to include an epistemic-uncertainty layer in a distributionally robust mean-CVaR allocation pipeline, rather than using point-estimate DRO or standard mean-variance.

**User / decision-maker:** Quant researcher or portfolio manager evaluating the method for a research prototype.

**Action that changes:** Include or exclude the uncertainty-aware DRO layer in the prototype. No live trading, no capital allocation, no deployment.

**What this is not:** A stock recommendation system, a live strategy, or a claim of alpha.

---

## 2. Problem

A standard pipeline predicts expected returns, plugs the point estimates into an optimizer, and lets the optimizer concentrate in assets whose returns were overestimated. This is **error maximization**: the optimizer treats estimation noise as signal.

The project tests a specific remedy:

1. An ML model predicts cross-sectional returns and reports epistemic uncertainty.
2. A DRO optimizer treats the true mean as lying inside an uncertainty set around the prediction.
3. A CVaR constraint or penalty controls tail risk.
4. Transaction costs and turnover are explicit.
5. A walk-forward, net-of-cost evaluation compares the result with simple baselines.

---

## 3. Units and timing

| Field | Definition |
|---|---|
| Unit of analysis | Stock-month |
| Universe | 150–200 liquid US stocks, monthly, point-in-time; fallback 100 liquid ETFs |
| Decision date | Month-end close |
| Target | Next-month cross-sectional excess-return rank (or winsorized return) |
| Prediction time | Month-end, using only information available then |
| Outcome window | One month ahead |
| Rebalance frequency | Monthly |
| Sample period | 2005–2024 (data permitting) |
| Out-of-sample period | 2010–2024 (data permitting) |

---

## 4. Hypotheses

| ID | Hypothesis | Falsification condition |
|---|---|---|
| **H1** | Uncertainty-aware DRO has lower max drawdown and CVaR95 than point-estimate DRO and mean-variance, net of costs. | The guardrail improvement is within noise or reverses under plausible costs. |
| **H2** | Uncertainty-aware DRO's net Sharpe is not materially worse than the best baseline. | Net Sharpe is worse than the best baseline by more than the pre-registered margin. |
| **H3** | The tail-risk improvement is attributable to the uncertainty layer. | The ablation without uncertainty matches or beats the full method. |

These are **competing hypotheses**, not a single headline claim. A negative result is reportable.

---

## 5. Success criteria

### Primary metric

**Net Sharpe ratio**: monthly portfolio returns after 10 bps one-way transaction costs, annualized, using an explicit risk-free series. The risk-free series is never silently defaulted to zero.

### Secondary / diagnostic metrics

Max drawdown, CVaR95, Sortino, Calmar, annualized turnover, cost drag, uncertainty calibration.

### Guardrails

Max drawdown, CVaR95, turnover, max weight, leverage, short exposure, leakage checks.

### Minimum meaningful effect

**Provisional, to be frozen before the confirmatory run:**

- Net Sharpe not worse than the best baseline by more than **0.20**.
- Max drawdown reduced by at least **20% relative**.
- CVaR95 improved with a bootstrap interval that excludes zero.
- The ablation without the uncertainty layer does not reproduce the improvement.

If these thresholds are not met, the honest conclusion is that the method did not demonstrate value under this protocol.

---

## 6. Constraints

### Hard

- Long-only.
- Sum of weights = 1.
- Max weight 5%.
- Monthly rebalance.
- 10 bps one-way transaction cost baseline; sensitivity at 5, 20, 50 bps.
- No leverage, no shorting.
- Point-in-time data only.
- No random train/test splits.

### Soft

- Interpretability.
- Runtime under 10 minutes per walk-forward run.
- Local reproducibility.
- No external experiment tracker required.

---

## 7. Data

**Status: BLOCKED.** The source must be selected by **2026-10-31**.

Options:

1. **CRSP + Compustat via WRDS** — preferred: historical constituents, delisting returns, PIT fundamentals.
2. **Sharadar / Norgate** — acceptable if PIT fundamentals and delisting handling are verified.
3. **Free data only** — reject for stock-level claims; pivot to ETF/factor universe and label as a methods study.

See [`01_data_card.md`](01_data_card.md).

---

## 8. Scope

### In scope

- Cross-sectional ML return model with uncertainty.
- Box or ellipsoidal DRO.
- Mean-CVaR optimization.
- Transaction costs and turnover.
- Walk-forward evaluation.
- Baselines and ablations.
- Reproducible repository and report.

### Out of scope

- Live trading or execution.
- Intraday data, market-impact curve, or order-book modelling.
- Deep RL.
- Causal claims from observational data.
- Redistribution of licensed data.
- A guarantee of outperformance.

---

## 9. Kill criteria

Stop or pivot if:

1. **Data access is not secured by 2026-10-31.** Pivot to ETF/factor data and narrow the claim.
2. **Leakage cannot be resolved by 2026-11-07.** Stop and fix the data before modelling.
3. **Baselines are not reproducible by 2026-11-07.** No model comparison is meaningful.
4. **The uncertainty layer cannot be calibrated by 2026-11-14.** Simplify to a defensible uncertainty proxy or stop.
5. **Ablation shows no separation by 2026-11-21.** Report the negative result; do not add complexity to force a positive one.
6. **Results disappear at plausible costs.** Report the cost sensitivity; do not hide it.

---

## 10. Timeline

| Dates | Gate | Deliverable |
|---|---|---|
| Oct 27–31 | G0/G1 | Charter, data decision, repo, smoke test |
| Nov 1–7 | G1 | PIT data pipeline, leakage audit, splits, baselines |
| Nov 8–14 | G2 | ML + uncertainty, calibration, first OOS results |
| Nov 15–21 | G3 | DRO + CVaR + costs, ablations |
| Nov 22–28 | G4 | Stress tests, report, model card, repo polish |
| Nov 29–30 | Buffer | Final review |

---

## 11. Deliverables

- Reproducible Python package with tests.
- `README.md` with results and reproduction commands.
- `docs/01_data_card.md`.
- `docs/02_experiment_card.md` (frozen before confirmatory run).
- `docs/03_model_card.md`.
- `docs/04_decision_log.md`.
- Results tables and figures (net of costs).
- A clear answer to H1–H3, including limitations.

---

## 12. Approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Owner | Ken Ira Talingting | Proceed to G1 | 2026-10-27 |
| Reviewer | TBD | TBD | TBD |

**Next gate:** G1 data readiness. The next action is to select the data source and produce a data card with a leakage audit.