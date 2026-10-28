# Epistemic-Aware DRO for Mean-CVaR Portfolios

**Research prototype · November 2026 · status: G0/G1 setup**

> Does epistemic uncertainty from an ML return model improve the tail-risk/return trade-off of a distributionally robust mean-CVaR portfolio, net of costs, out-of-sample?

This repository is a research apparatus, not a live strategy. It is designed to answer the question above honestly, including the possibility that the answer is **no**.

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
| Universe | 150–200 liquid US stocks, monthly, point-in-time; fallback: 100 liquid ETFs |
| Period | 2005–2024; out-of-sample 2010–2024 |
| Features | 15–20 lagged cross-sectional signals: momentum, value, quality, low-vol, size, liquidity |
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
- Redistributing licensed vendor data.
- Beating the market. The project tests a risk-management mechanism.

---

## Data status

> **BLOCKED — decision due 2026-10-31.**

A credible stock-level version needs:

- historical universe membership (not today's S&P 500),
- delisting returns,
- point-in-time fundamentals,
- adjusted prices,
- a risk-free series.

Options are compared in [`docs/01_data_card.md`](docs/01_data_card.md). If only free data are available, the project pivots to an ETF/factor universe and is labelled a methods study.

No vendor data are included in this repository. `scripts/run_smoke.py` uses synthetic data only.

---

## Repository layout

```
epistemic-dro/
├── AGENTS.md                 # project-specific operating manual (filled §0)
├── README.md
├── pyproject.toml
├── requirements.txt
├── configs/
│   └── base.yaml             # provisional configuration; freeze before confirmatory runs
├── data/
│   ├── README.md             # data access, schema, licensing
│   ├── raw/                  # gitignored vendor data
│   └── processed/            # gitignored derived panels
├── docs/
│   ├── 00_project_charter.md
│   ├── 01_data_card.md
│   ├── 02_experiment_card.md
│   ├── 03_model_card.md
│   ├── 04_decision_log.md
│   ├── 05_risk_register.md
│   └── 06_literature.md
├── notebooks/                # exploration only
├── results/                  # gitignored outputs
├── scripts/
│   ├── run_smoke.py          # synthetic-data smoke test
│   └── check_data.py         # data-readiness checker
├── src/epistemic_dro/
│   ├── config.py
│   ├── data.py
│   ├── metrics.py
│   ├── optimization.py
│   ├── leakage.py
│   └── ...
└── tests/
```

---

## Quick start

```bash
cd D:\quant-finance-ml\epistemic-dro
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev,ml]"
pytest -q
python scripts/run_smoke.py
```

The smoke test uses **synthetic data**. It proves the optimizer and metrics run; it says nothing about real performance.

---

## Evaluation protocol (summary)

1. **Walk-forward only.** No random train/test splits. Purge and embargo around the test window.
2. **Point-in-time features.** Fundamentals use filing dates, not fiscal-period ends. Prices and universe membership are as-of the decision date.
3. **Net of costs.** 10 bps one-way baseline; sensitivity at 5, 20, and 50 bps.
4. **Primary metric.** Net Sharpe. Max drawdown and CVaR95 are guardrails.
5. **Uncertainty.** Bootstrap intervals; deflated Sharpe ratio to account for multiple trials.
6. **Ablation.** Show which component — uncertainty, DRO, CVaR — drives the result.
7. **No test-set reuse.** The final holdout is touched once; any reuse is disclosed.

The frozen details belong in [`docs/02_experiment_card.md`](docs/02_experiment_card.md), not in this README.

---

## Deliverables

- Reproducible Python package and tests.
- Walk-forward results table and figures.
- `docs/03_model_card.md` and `docs/01_data_card.md`.
- Decision memo with limitations and a clear answer to H1–H3.
- No claim of live readiness.

---

## Limitations

- CVaR is scenario-dependent; historical scenarios may understate tail risk.
- DRO protects against a chosen ambiguity set, not against model misspecification outside it.
- A 4-week backtest cannot validate deployment.
- Multiple testing can produce apparent improvements; the deflated Sharpe ratio and a frozen protocol are mitigations, not guarantees.
- If data are not survivorship-bias-free, the stock-level results are not credible.

---

## License and data

Code license: **TBD** (MIT suggested). Vendor data are **not** distributed. See [`data/README.md`](data/README.md).

---

## Contact

Ken Ira Talingting · research prototype · 2026
