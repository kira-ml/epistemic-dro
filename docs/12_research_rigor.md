# Research Rigor Addendum — 12 Mental Models (v1.1)

**Status:** Active — binding addendum (2026-11-02)
**Parent protocol:** `docs/02_experiment_card.md` v1.0-etf (frozen 2026-11-02)
**Authority:** the local `ML_AGENT_SCIENTIFIC_PROTOCOL.md` and the 12 Foundational Mental Models
**Scope:** adds gates and artifacts. It does **not** change the primary metric, walk-forward split, portfolio constraints, cost model, universe, or claim scope.

> **Why this exists.** The v1.0 docs already had purge/embargo splits, PIT rules, net-of-cost evaluation, and a Sharpe/tail-risk pairing. They did not yet have an axiomatic specification, a mandatory regularized baseline, a mutual-information audit, a target-shuffling test, a counter-metric gate, or an experiment ledger. This addendum closes those gaps before the first model run.

---

## 1. Model-to-project map

| # | Mental model | What it means **in this project** | Artifact / gate | Status |
|---|---|---|---|---|
| **1** | First principles | Write the economic and statistical data-generating mechanism for monthly ETF excess returns; state the noise floor and the maximum credible \(R^2\) before model code. | `docs/axiomatic_spec.md`; G-R1 | **Complete 2026-11-02** — Ridge B0 OOS \(R^2\) = −0.0186; linear signal null |
| **2** | Inversion & falsification | Try to break the pipeline: target-shuffling, temporal monotonicity, purge/embargo, universe audit, solver-failure audit. | `docs/pre_mortem.md`; `tests/test_falsification.py`; G-R2 | **B0 shuffled-target passed**; full ML pipeline pending |
| **3** | Bayesian updating | Shrink noisy cross-sectional signals; report uncertainty intervals, not just point estimates; treat a high Sharpe as a low-prior event. | Ridge baseline; bootstrap intervals; deflated Sharpe; G-R3 | **B0 baseline logged**; interval reporting pending |
| **4** | Shannon information | Measure mutual information and conditional mutual information of candidate features against a permutation null; drop features that add nothing. | `docs/data_dictionary.md`; MI audit; G-R4 | **Pending** — data ready |
| **5** | Causal hierarchy | This is Rung 1 (observational forecasting). No live intervention, no causal claim, no `do()` interpretation. | `docs/causal_dag.json`; G-R5 | **Complete** |
| **6** | Parsimony / SRM | A regularized Ridge return forecast is the mandatory baseline. LightGBM must beat it on purged OOS data with a Diebold-Mariano test at \(p < 0.01\). | `src/epistemic_dro/baselines.py`; `experiments/baseline_benchmarks.md`; G-R6 | **B0 established (null)**; DM implementation pending |
| **7** | Fat tails / non-ergodicity | Estimate the Pareto tail index; if \(\alpha < 4\), use a robust LightGBM objective (Huber/quantile) rather than MSE. Keep CVaR and drawdown as first-class risks. | Tail diagnostic; conditional loss; G-R7 | **Complete 2026-11-02** — \(\alpha\) = 3.08; `huber` selected |
| **8** | Payoff asymmetry | The optimizer already penalizes CVaR and drawdown; never evaluate on MSE alone. The report must state the asymmetric loss/tail objective. | `docs/02` §6.3; model card §8; G-R8 | **Already present — documented** |
| **9** | Feedback / reflexivity | No live deployment, so performative feedback is out of scope. The linear 10 bps cost model is a limitation, not a market-impact model. | `docs/09`; `docs/03` §10; G-R9 | **Already present — documented** |
| **10** | Goodhart / counter-metrics | Net Sharpe is never evaluated alone. Every result table carries max drawdown, CVaR95, turnover, and cost drag; a gate rejects a "good" Sharpe with a tail breach. | `src/epistemic_dro/evaluation.py`; G-R10 | **Code added**; not yet exercised on a portfolio result |
| **11** | Exploration vs exploitation | Hyperparameter search uses Bayesian optimization over the frozen bounds, not an unguided grid. Every trial is logged. 75% of effort refines baselines; 25% explores. | `experiments/ledger.jsonl`; G-R11 | **Ledger started**; Bayesian search pending |
| **12** | Theory of constraints | Profile the end-to-end pipeline before optimizing any component. The likely bottleneck is data/feature construction, not the solver. | `scripts/profile_pipeline.py`; G-R12 | **Script added**; real-pipeline profile pending |

---

## 2. Binding gates

A gate is **blocking**. A run may be exploratory without passing it, but it may not be cited as confirmatory.

| Gate | Requirement | Evidence | Blocks |
|---|---|---|---|
| **G-R1 Axiomatic** | Data-generating mechanism, units, timing, constraints, and a Bayes-risk/noise-floor estimate are written and dated. | `docs/axiomatic_spec.md` §2–§5 | Any model code |
| **G-R2 Falsification** | Target-shuffling collapses to chance; temporal monotonicity holds; purge/embargo verified; universe/closure audit complete. | `tests/test_falsification.py`; `tests/test_leakage.py`; `docs/pre_mortem.md` | Any reported result |
| **G-R3 Shrinkage** | Ridge baseline is logged; all headline metrics carry bootstrap intervals; deflated Sharpe is reported. | `experiments/baseline_benchmarks.md`; result tables | Any model claim |
| **G-R4 Information** | MI/CMI audit with a permutation null is complete; dropped features and reasons are recorded. | `docs/data_dictionary.md` §3 | LightGBM fit |
| **G-R5 Causal** | Rung-1 classification is recorded; no interventional or causal language is used. | `docs/causal_dag.json` | Any report |
| **G-R6 Parsimony** | LightGBM beats Ridge with Diebold-Mariano \(p < 0.01\) on purged OOS data, or the simpler model is reported. | Baseline table; DM test | Adopting LightGBM |
| **G-R7 Fat tails** | Pareto \(\alpha\) is estimated; loss choice follows the \(\alpha < 4\) rule; tail diagnostics are reported. | Data dictionary; model card | Any model fit |
| **G-R8 Asymmetry** | Objective includes a tail penalty; no MSE-only evaluation. | Config; `docs/02` §6.3 | Any optimizer run |
| **G-R9 Reflexivity** | No deployment claim; linear-cost limitation stated. | `docs/09`; model card §10 | Any external claim |
| **G-R10 Counter-metric** | Gate passes on Sharpe, max drawdown, and CVaR95 simultaneously. | `evaluation.evaluate_counter_metric_gate` | Any "success" claim |
| **G-R11 Search** | Bayesian optimization, frozen bounds, every trial in the ledger. | `experiments/ledger.jsonl` | Hyperparameter tuning |
| **G-R12 Bottleneck** | Profile before optimizing any component. | `scripts/profile_pipeline.py` output | Performance work |

---

## 3. Protocol amendments (pre-confirmatory)

These are additions to v1.0-etf, logged in `docs/04_decision_log.md` as `DEC-20261102-004`.

1. **B0 Ridge baseline.** A regularized Ridge return forecast is added to the baseline set. It uses the same universe, dates, features, splits, and constraints. M1/M2 must beat it on purged OOS data or the simpler forecast is reported.
2. **Conditional robust loss.** Estimate the Pareto tail index of monthly ETF returns. If \(\alpha < 4\), use LightGBM `huber` (or quantile); otherwise the pre-registered regression objective is allowed.
3. **MI screening.** Compute mutual information and conditional mutual information on each training window, with a permutation null. A feature that fails to beat the null in at least 80% of windows is dropped and logged. This is a screening rule, not a license to fish.
4. **Bayesian optimization.** Tune only within the frozen candidate bounds. Use Optuna/BoTorch-style Bayesian optimization; log every trial. Unguided grid search is prohibited.
5. **Counter-metric gate.** A result is not "successful" unless Sharpe, max drawdown, and CVaR95 pass their pre-registered bounds simultaneously.
6. **Experiment ledger.** Every run — including failed and exploratory runs — appends one JSONL record to `experiments/ledger.jsonl`.
7. **Profiling.** Profile the pipeline before changing model architecture or solver settings.

**No change to:** net Sharpe as primary, 90% bootstrap decision interval, walk-forward split, 5% cap, long-only, 10 bps primary cost, ETF universe, or the negative-result policy.

---

## 4. What "flagship" means here

A flagship project is not a project with a high Sharpe. It is a project where:

- every claim has an artifact behind it;
- every artifact has a test or a gate;
- every failed attempt is logged;
- a negative result is publishable without apology;
- a reader can reproduce the result and the reasoning.

The 12 models are not decoration. They are the operating system for those five properties.

---

## 5. Adoption and versioning

- This addendum is `v1.1-rigor`.
- It is listed in `docs/README.md` and is part of the operating record.
- The original freeze tag `docs-freeze-v1` remains the v1.0-etf record.
- After review, the combined set is tagged `docs-freeze-v1.1`.

**A post-freeze change to any gate in this file requires a dated deviation entry in `docs/04_decision_log.md`.**
