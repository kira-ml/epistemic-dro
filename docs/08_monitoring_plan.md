# Monitoring Plan (Research) — Epistemic-Aware DRO

**Status:** Frozen v1.0-etf
**Last updated:** 2026-11-02
**Scope:** Research prototype / ETF methods study. No live deployment (see `04_decision_log.md` DEC-20261027-005). This plan covers re-run, calibration, and deviation tracking, not production monitoring.

## 1. What is monitored, and why

Because there is no live traffic, "drift" means **data drift between re-runs** and **calibration drift of the uncertainty layer**, not model drift in production.

| Signal | Cadence | Trigger for action | Where recorded |
|---|---|---|---|
| **Data snapshot / manifest** | Weekly during November | Manifest missing; provider history revised; coverage shrinks | `01_data_card.md` §3, §8; `04_decision_log.md` |
| **Universe breadth** | Each walk-forward run | Fewer than 50 eligible ETFs in a test month | `02_experiment_card.md` §5; `05_risk_register.md` R16 |
| **Leakage test status** | Every code change to `src/epistemic_dro/leakage.py` or the loader | Any failing test | `tests/test_leakage.py`; `01_data_card.md` §6 |
| **Baseline reproducibility** | Each walk-forward run | Baseline metrics differ from prior run beyond seed noise | `04_decision_log.md`; frozen card |
| **Solver failure rate** | Each rebalance | > 5% failures | `02_experiment_card.md` §9 stopping rule |
| **Uncertainty calibration** | Each model refit | Empirical coverage deviates from nominal by > 5 pts | `03_model_card.md` §7 |
| **Cost sensitivity** | Each result set | Net Sharpe sign flips between 10 and 20 bps | `02_experiment_card.md` §10 |
| **Multiple-testing count** | Continuously | More than the pre-registered number of trials | `02_experiment_card.md` §8; `04_decision_log.md` deviation log |
| **Claim-evidence match** | Before any report | Claim exceeds the pre-registered evidence | `03_model_card.md` §13; final-review discipline in the local operating manual |

## 2. Cadence during November

| Week | Monitoring action | Owner |
|---|---|---|
| 2026-11-02 | Execute ETF pivot, record MIT license, freeze docs v1.0. | Owner |
| Nov 3-7 | ETF snapshot + manifest; schema validation; leakage audit; baseline reproducibility. | Owner |
| Nov 8-14 | Uncertainty calibration report (reliability / coverage); eligible-ETF breadth per month. | Owner |
| Nov 15-21 | Ablation separation vs. noise; multiple-testing count. | Owner |
| Nov 22-28 | Cost sensitivity; subperiod stability; claim review. | Owner |
| Nov 29-30 | Freeze decision: report as-is, extend, or kill. | Owner |

## 3. What is not monitored (and why)

- **Live prediction drift** — no live predictions exist.
- **Business metric** — no users, no revenue, no capital.
- **Latency / throughput in production** — batch research only; runtime is a soft constraint (< 10 min per walk-forward, `00_project_charter.md` §6).
- **Fairness** — no personal data, no people affected.

## 4. Escalation

Because the owner is also the sole reviewer, escalation means **logging a deviation in `04_decision_log.md` before proceeding**, not paging anyone. Any deviation that changes a pre-registered metric, split, or cost must be logged and dated before the next confirmatory run.

## 5. Relationship to `05_risk_register.md`

The risk register lists the risks; this file lists the signals that would tell you a risk is materializing. They should stay aligned. When a new risk is added to `05`, add a signal here.
