# Epistemic-Aware DRO for Mean-CVaR Portfolios

[![CI](https://github.com/kira-ml/epistemic-dro/actions/workflows/ci.yml/badge.svg)](https://github.com/kira-ml/epistemic-dro/actions/workflows/ci.yml)

**Research prototype · November 2026 · v1 final (H1/H3 fail) · v2/v3 stopped before holdout****

> Does epistemic uncertainty from an ML return model improve the tail-risk/return trade-off of a distributionally robust mean-CVaR portfolio, net of costs, out-of-sample?

This repository is a research apparatus, not a live strategy. It is designed to answer the question above honestly, including the possibility that the answer is **no**.

**Read the paper:** [`paper/mini_paper.pdf`](paper/mini_paper.pdf) — *The holdout is still untouched: three pre-registered tests of uncertainty-aware DRO*.
**Visual summary:** [`paper/linkedin_carousel.pdf`](paper/linkedin_carousel.pdf) · [`paper/linkedin_card.png`](paper/linkedin_card.png)

---

## Why this project

Most student portfolio projects predict returns and feed point estimates into a Markowitz optimizer. The optimizer then aggressively allocates to assets whose returns were overestimated — the classic **error-maximization** problem.

This project tests a narrower and more defensible claim:

> If the ML model knows *where* it is uncertain, a robust optimizer can use that uncertainty to avoid concentrated bets that look good only in-sample.

The deliverable is not a stock-price forecast. It is a leakage-tested walk-forward apparatus, a convex robust optimizer, and an honest comparison against simple baselines.

### Relationship to `../robustfolio`

`robustfolio` already tests whether robust covariance and turnover-aware portfolio methods beat plain baselines on a small ETF universe under a frozen protocol. This project is deliberately different:

- it uses a cross-sectional ML return model with **epistemic uncertainty**;
- it optimizes **mean-CVaR**, not mean-variance;
- it isolates the uncertainty layer in an **ablation**;
- it targets a broader US equity universe, data permitting.

If the available data force an ETF-only universe, this becomes a methods study rather than a stock-selection study. That limitation will be stated in the report.

> **v1 status (2026-11-02):** this is now the actual scope. No point-in-time stock source was secured, so the project pivoted to 50–100 liquid US ETFs. The result is a methods study and makes no stock-selection claim. See [`docs/04_decision_log.md`](docs/04_decision_log.md) DEC-20261102-001.

---

## Research question

In a walk-forward monthly US equity allocation, does a distributionally robust mean-CVaR optimizer that uses ML epistemic uncertainty produce lower drawdown/CVaR without materially worse net Sharpe, relative to:

1. equal weight (1/N),
2. sample mean-variance,
3. CVaR-only optimization,
4. hierarchical risk parity (HRP),
5. DRO with point estimates?

---

## Hypotheses

| ID | Hypothesis | Primary evidence |
|---|---|---|
| **H1** | Uncertainty-aware DRO has lower max drawdown and CVaR95 than point-estimate DRO and mean-variance, net of costs. | Walk-forward OOS metrics with bootstrap intervals |
| **H2** | Uncertainty-aware DRO's net Sharpe is not materially worse than the best baseline. | Pre-registered non-inferiority margin |
| **H3** | The tail-risk improvement is attributable to the uncertainty layer. | Ablation: uncertainty vs point; DRO vs no DRO; CVaR vs variance |

A clean negative result is acceptable. The project fails only if it is leaky, non-reproducible, or overclaims.

---

## Scope (v1)

| Layer | v1 choice |
|---|---|
| Universe | 50–100 liquid US-listed ETFs, monthly, point-in-time eligibility (ETF/factor methods study) |
| Period | 2005–2024; out-of-sample 2010–2024 |
| Features | 15–20 lagged cross-sectional signals: momentum, volatility, drawdown, liquidity, beta, factor exposures |
| Model | LightGBM + 5-seed ensemble; conformal calibration optional |
| Uncertainty | Ensemble variance or conformal half-width |
| Optimizer | Box (or ellipsoidal) DRO + CVaR + turnover cost |
| Baselines | 1/N, Markowitz, CVaR-only, HRP, DRO-point |
| Evaluation | Walk-forward, net of 10 bps one-way costs, bootstrap CIs, deflated Sharpe |
| Ablations | DRO vs no DRO; uncertainty vs point; CVaR vs variance; box vs ellipsoid; costs on/off |

### Non-goals

- Live trading or execution.
- Intraday alpha, deep RL, or market-impact modelling beyond a linear cost.
- Claiming causality from observational data.
- Stock-selection validity in v1 (the universe is ETFs).
- A survivorship-free ETF claim (public data may omit closed funds).
- Redistributing provider data.
- Beating the market. The project tests a risk-management mechanism.

---

## Data status

> **Snapshot built 2026-11-02 — 72 ETFs, FRED `TB3MS`, 68+ eligible ETFs in every 2010+ month. G1 passes with a disclosed survivorship limitation; G-R4 MI audit is still open.**

No point-in-time stock-level source was secured by the 2026-10-31 deadline, so charter §9 kill criterion 1 was executed. v1 uses:

- 72 liquid US-listed equity ETFs with point-in-time eligibility;
- Yahoo Finance adjusted total-return prices (provider recorded in the snapshot manifest);
- FRED `TB3MS` for the risk-free series;
- Fama-French 3-factor + momentum data for exposures and diagnostics.

Public data may omit closed funds. The project therefore makes **no survivorship-free claim** and **no stock-selection claim**. Details and the leakage audit are in [`docs/01_data_card.md`](docs/01_data_card.md).

No raw data snapshots are included in this repository. `scripts/run_smoke.py` uses synthetic data only.

### Early evidence (baseline + reduced DRO)

The mandatory Ridge B0 walk-forward baseline was run on 2010–2024:

- pooled OOS \(R^2\): **−0.019**
- mean monthly rank IC: **0.013** (t = 0.56)
- shuffled-target mean IC: **−0.004** (t = −0.48)

This is a **null linear signal**. The G-R4 information audit also found no feature passing the 80% date-level rule, so LightGBM was not fitted.

The reduced uncertainty-aware DRO experiment (Ridge B0 mean + 5-model bootstrap sigma) ran on 2010–2024, 179 months, net 10 bps:

| Strategy | Net Sharpe | Max drawdown | CVaR95 |
|---|---:|---:|---:|
| M1_reduced | 0.816 | −24.18% | −8.31% |
| B5_DRO_point | 0.798 | −24.28% | −8.44% |
| B1_equal_weight | 0.673 | −26.61% | −9.76% |

**Verdict: H1 fails, H2 passes, H3 fails.** The DRO/CVaR optimizer beats 1/N, but the epistemic-uncertainty layer does not separate from point-estimate DRO. This is a clean negative result for the uncertainty hypothesis; it is not a claim of alpha. See [`experiments/dro_experiment.md`](experiments/dro_experiment.md) and the final memo [`docs/13_final_report.md`](docs/13_final_report.md).

The shuffled-target run collapses to zero, so the null is not an obvious leak. The ML layer cannot be assumed to add value. See [`experiments/baseline_benchmarks.md`](experiments/baseline_benchmarks.md).

### v2 attempt: stopped before the holdout

A v2 pre-registration tested a stronger model: 19 features, LightGBM quantile regression, split-conformal calibration, and a non-degenerate trailing-volatility comparator. Development coverage was 0.899 (validation) and 0.859 (test), but the uncertainty signal passed only **65.4%** of date-level information tests — below the frozen 80% gate.

**The 2025–2026 holdout was not touched.** v2 stopped before the confirmatory test. See [`docs/15_v2_report.md`](docs/15_v2_report.md). This is the rigor layer working: a calibrated but uninformative uncertainty model was not promoted to a holdout claim.

### v3 attempt: conditional tail risk, also stopped before holdout

v3 tested a different object — a conditional forecast of next-month absolute return, used as DRO sigma. It was well calibrated (mean sigma 4.29% vs realized 4.30%; top-vs-bottom decile spread 3.76 pp), but the **per-date information pass rate was 0.430**, below the frozen 80% gate. It also underperformed trailing volatility on development (Sharpe 0.783 vs 0.840).

**The 2025–2026 holdout remains untouched.** See [`docs/17_v3_report.md`](docs/17_v3_report.md). Three pre-registered attempts, zero promoted to the holdout — the gates worked.

### But the gate itself was underpowered

A synthetic power study tested the 80% date-level information gate. At 72 assets and 179 dates, it had **zero power** even at a 20% \(R^2\) signal; an iid pooled test detected the same signal. But the iid pooled test was too permissive: a **block-aware null** cut 20/21 apparent passes to **3/21**, and the v2/v3 sigma did not survive.

That does **not** promote v1/v2/v3. The 80% gate was too strict; the iid pooled test was too permissive. The defensible gate is a block-aware pooled gate with a minimum effect size. The holdout remains untouched. See [`docs/18_gate_power_study.md`](docs/18_gate_power_study.md).

---

## Repository layout

```
epistemic-dro/
├── README.md
├── LICENSE                   # MIT (code only; data terms separate)
├── .env.example              # FRED_API_KEY template; .env is gitignored
├── pyproject.toml
├── requirements.txt
├── configs/
│   └── base.yaml             # frozen v1.1-rigor configuration (2026-11-02)
├── data/
│   ├── README.md             # data access, schema, licensing
│   ├── raw/                  # gitignored data snapshots
│   └── processed/            # gitignored derived panels
├── docs/
│   ├── README.md             # documentation register
│   ├── 00_project_charter.md
│   ├── 01_data_card.md
│   ├── 02_experiment_card.md
│   ├── 03_model_card.md
│   ├── 04_decision_log.md
│   ├── 05_risk_register.md
│   ├── 06_literature.md
│   ├── 07_domain_overlay.md
│   ├── 08_monitoring_plan.md
│   ├── 09_deployment_runbook.md
│   ├── 10_postmortem_template.md
│   ├── 11_lessons_log.md
│   ├── 12_research_rigor.md  # 12-model binding addendum (v1.1)
│   ├── 13_final_report.md    # final memo: H1/H3 fail, H2 pass
│   ├── 14_v2_preregistration.md # v2 conformal-quantile pre-registration
│   ├── 15_v2_report.md       # v2 stopped before holdout
│   ├── 16_v3_preregistration.md # v3 conditional tail-risk pre-registration
│   ├── 17_v3_report.md       # v3 stopped before holdout
│   ├── axiomatic_spec.md     # first-principles / Bayes-risk gate
│   ├── data_dictionary.md    # schema, lineage, MI audit
│   ├── pre_mortem.md         # falsification and kill criteria
│   └── causal_dag.json       # Rung-1 causal classification
├── experiments/
│   ├── README.md             # ledger schema and baseline law
│   ├── ledger.jsonl          # append-only run log
│   ├── baseline_benchmarks.md
│   └── dro_experiment.md     # reduced DRO result and verdict
├── paper/
│   ├── mini_paper.pdf        # 6-page working paper
│   ├── linkedin_carousel.pdf # 7-slide native document post
│   ├── linkedin_card.png     # 4:5 visual card
│   ├── one_pager.pdf         # one-page leave-behind
│   └── README.md             # publishing strategy and assets
├── notebooks/                # exploration only
├── results/                  # gitignored outputs
├── scripts/
│   ├── build_snapshot.py     # frozen ETF/FRED/FF snapshot builder
│   ├── run_smoke.py          # synthetic-data smoke test
│   ├── check_data.py         # schema/data-readiness checker
│   ├── run_diagnostics.py    # G-R1/G-R7 noise-floor and tail diagnostics
│   ├── run_baseline.py       # Ridge B0 walk-forward baseline
│   ├── run_information_audit.py  # G-R4 MI audit
│   ├── run_dro_experiment.py # reduced M1 vs B5/B3/B1
│   ├── analyze_dro_experiment.py # paired bootstrap verdict
│   ├── report_final.py       # cost sensitivity, stress, deflated Sharpe
│   ├── run_v2_experiment.py  # quantile/conformal v2
│   ├── run_v2_uncertainty_audit.py # G-R4v2 gate
│   ├── run_v3_experiment.py  # conditional tail-risk v3
│   ├── run_v3_sigma_audit.py # G-R4v3 gate
│   └── profile_pipeline.py   # bottleneck profiling (G-R12)
├── src/epistemic_dro/
│   ├── __init__.py
│   ├── backtest.py           # walk-forward splits
│   ├── baselines.py          # mandatory Ridge B0 baseline
│   ├── config.py             # YAML loader
│   ├── data.py               # snapshot loader + synthetic smoke panel
│   ├── evaluation.py         # counter-metric gate
│   ├── falsification.py      # target-shuffling harness
│   ├── features.py           # ETF feature builder + targets
│   ├── leakage.py            # lookahead / group / key guards
│   ├── metrics.py            # Sharpe, CVaR, drawdown, turnover
│   ├── models.py             # ensemble prediction + uncertainty
│   ├── optimization.py       # box DRO + mean-CVaR
│   └── report.py             # table formatting
└── tests/
```

The project's operating manual (`AGENTS.md`) is maintained locally and is **not committed**; committed rules live in [`docs/07_domain_overlay.md`](docs/07_domain_overlay.md). See [`docs/README.md`](docs/README.md) for the documentation register.

---

## Quick start

```bash
cd D:\quant-finance-ml\epistemic-dro
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev,ml,paper]"
pytest -q
ruff check .
python scripts/run_smoke.py
```

**Snapshot rebuild (requires `FRED_API_KEY` in `.env`):**

```bash
python scripts/build_snapshot.py --force
python scripts/check_data.py
python scripts/run_diagnostics.py
python scripts/run_baseline.py
python scripts/run_information_audit.py
python scripts/run_dro_experiment.py
python scripts/analyze_dro_experiment.py
python scripts/report_final.py
python scripts/build_paper.py
python scripts/verify_results.py
```

The smoke test uses **synthetic data**. The snapshot and baseline scripts use the real frozen data and write to `data/raw/` and `results/tables/` (both gitignored). The B0 baseline is a null result; do not cite it as a strategy result.

---

## Evaluation protocol (summary)

1. **Walk-forward only.** No random train/test splits. Purge and embargo around the test window.
2. **Point-in-time features.** An ETF is eligible only at or after its inception date. Prices, returns, and universe eligibility are as-of the decision date. ETF metadata is not treated as point-in-time unless a historical series exists.
3. **Net of costs.** 10 bps one-way baseline; sensitivity at 5, 20, and 50 bps.
4. **Primary metric.** Net Sharpe. Max drawdown and CVaR95 are guardrails.
5. **Uncertainty.** Bootstrap intervals; deflated Sharpe ratio to account for multiple trials.
6. **Ablation.** Show which component — uncertainty, DRO, CVaR — drives the result.
7. **No test-set reuse.** The final holdout is touched once; any reuse is disclosed.

The frozen details belong in [`docs/02_experiment_card.md`](docs/02_experiment_card.md), not in this README.

---

## Research rigor (v1.1)

The project is built against the 12 foundational mental models, not just a backtest checklist. The binding addendum is [`docs/12_research_rigor.md`](docs/12_research_rigor.md). Its main gates:

- **First principles:** an [axiomatic specification](docs/axiomatic_spec.md) with a Bayes-risk/noise-floor estimate before model code.
- **Inversion:** a target-shuffling harness (`src/epistemic_dro/falsification.py`) and a [pre-mortem](docs/pre_mortem.md) with explicit kill criteria.
- **Parsimony:** a mandatory Ridge B0 baseline (`src/epistemic_dro/baselines.py`); LightGBM must beat it with a Diebold-Mariano test at \(p < 0.01\).
- **Information:** a mutual-information audit with a permutation null ([data dictionary](docs/data_dictionary.md)).
- **Goodhart:** a [counter-metric gate](src/epistemic_dro/evaluation.py) that requires net Sharpe, max drawdown, and CVaR95 to pass together.
- **Causality:** a [Rung-1 classification](docs/causal_dag.json); no interventional or causal claim.
- **Fat tails:** a Pareto tail diagnostic; robust loss if \(\alpha < 4\).
- **Search discipline:** Bayesian optimization over frozen bounds, with every trial in [`experiments/ledger.jsonl`](experiments/ledger.jsonl).
- **Bottlenecks:** `scripts/profile_pipeline.py` before optimizing any component.

The gates are blocking for a confirmatory claim. A negative result that passes them is a successful project; a positive-looking result that fails them is not.

---

## Deliverables

- Reproducible Python package and tests.
- Walk-forward results table and figures.
- `docs/03_model_card.md` and `docs/01_data_card.md`.
- Rigor artifacts: axiomatic spec, data dictionary, pre-mortem, causal classification, experiment ledger.
- Decision memo with limitations and a clear answer to H1–H3.
- No claim of live readiness.

---

## Limitations

- CVaR is scenario-dependent; historical scenarios may understate tail risk.
- DRO protects against a chosen ambiguity set, not against model misspecification outside it.
- A 4-week backtest cannot validate deployment.
- Multiple testing can produce apparent improvements; the deflated Sharpe ratio and a frozen protocol are mitigations, not guarantees.
- The ETF universe is narrower and less dispersed than a stock universe; statistical power is limited.
- Public ETF data may omit closed funds, so the results are not survivorship-free.
- ETF metadata (expense ratio, yield) may be a current snapshot rather than a point-in-time series.
- The reduced M1 uses a bootstrap Ridge uncertainty proxy, not the original LightGBM ensemble; H1/H3 are not supported by this test.

---

## License and data

Code license: **MIT** (see [`LICENSE`](LICENSE)). Third-party data are **not** distributed and remain subject to their provider terms. See [`data/README.md`](data/README.md).

---

## Contact

Ken Ira Talingting · research prototype · 2026
