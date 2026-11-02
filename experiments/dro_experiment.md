# Reduced DRO / Uncertainty Experiment

**Status:** Completed 2026-11-02 — reduced M1; LightGBM not fitted (G-R4 null)
**Protocol:** `v1.1-rigor`
**Data:** frozen snapshot 2026-11-02 (72 ETFs; 2010-01 .. 2024-11; 179 rebalances)
**Decision record:** `DEC-20261102-006` (G-R4 null), `DEC-20261102-007` (this result)

---

## 1. Question

Does an epistemic-uncertainty layer improve the tail-risk/return trade-off of a DRO mean-CVaR portfolio relative to point-estimate DRO and simple baselines, net of costs?

This is a **reduced** test. The original M1 (LightGBM + 5-seed ensemble) was not fitted because no feature passed the G-R4 information rule. The reduced M1 uses the Ridge B0 mean and a 5-model bootstrap Ridge ensemble standard deviation as an explicitly labelled uncertainty proxy.

---

## 2. Design

| Item | Value |
|---|---|
| Universe | 72 liquid US-listed equity ETFs, PIT eligibility |
| Rebalance | Monthly, 2010-01 .. 2024-11 |
| Training | Rolling 60 months before each rebalance |
| Mean forecast | Ridge(alpha=1.0) on 13 features |
| Uncertainty (M1) | Std. dev. across 5 bootstrap Ridge models; floor 1e-6 |
| Scenarios | Last 60 monthly total returns |
| Optimizer | Box DRO + CVaR, CLARABEL, `kappa=1.0`, `cvar_penalty=1.0` |
| Constraints | Long-only, sum=1, max weight 5% |
| Costs | 10 bps one-way; realized cost subtracted from net return |
| OOS months | 179 |
| Mean eligible ETFs | 70.4 |

### Strategies

| ID | Mean | Uncertainty | DRO | CVaR |
|---|---|---|---|---|
| **M1_reduced** | Ridge bootstrap mean | Bootstrap sigma | Yes, `kappa=1.0` | Yes |
| **B5_DRO_point** | Ridge bootstrap mean | Zero (1e-6 floor) | Yes, `kappa=1.0` | Yes |
| **B3_CVaR** | Ridge bootstrap mean | Zero (1e-6 floor) | No, `kappa=0` | Yes |
| **B1_equal_weight** | None | None | No | No |

**Note:** B5 and B3 are mathematically identical when sigma is zero; this is a design limitation of the frozen baseline set, not a bug.

---

## 3. Results (net of 10 bps)

| Strategy | Net Sharpe | Max drawdown | CVaR95 | Sortino | Calmar | Ann. turnover | Cost drag |
|---|---:|---:|---:|---:|---:|---:|---:|
| **M1_reduced** | **0.816** | **−24.18%** | **−8.31%** | 1.171 | 0.496 | 1.90 | 0.190% |
| **B5_DRO_point** | 0.798 | −24.28% | −8.44% | 1.125 | 0.485 | 1.82 | 0.182% |
| **B3_CVaR** | 0.798 | −24.28% | −8.44% | 1.125 | 0.485 | 1.82 | 0.182% |
| **B1_equal_weight** | 0.673 | −26.61% | −9.76% | 0.939 | 0.420 | 0.11 | 0.011% |

### Paired bootstrap (90% intervals, 2,000 reps)

| Comparison | Metric difference | 90% CI | Reading |
|---|---|---:|---|
| M1 − B5 | Net Sharpe | **[−0.000, +0.037]** | Slight positive point estimate; CI touches zero |
| M1 − B5 | Max drawdown | **[−0.0024, +0.0160]** | No separation |
| M1 − B5 | CVaR95 | **[−0.0001, +0.0031]** | CI includes zero |
| M1 − B5 | Relative MDD improvement | **[−6.2%, +1.1%]** | Far below +20% |
| M1 − B1 | Net Sharpe | **[+0.020, +0.266]** | DRO/CVaR beats 1/N |
| M1 − B1 | Max drawdown | **[+0.0016, +0.137]** | DRO/CVaR beats 1/N |
| M1 − B1 | CVaR95 | **[+0.0043, +0.026]** | DRO/CVaR beats 1/N |

---

## 4. Hypothesis verdict

| Hypothesis | Criterion | Result |
|---|---|---|
| **H1** — uncertainty-aware DRO lowers tail risk vs point DRO | ≥20% relative MDD improvement **and** CVaR95 90% CI excludes zero | **FAIL** — 0.4% MDD improvement; CVaR CI includes zero |
| **H2** — net Sharpe not materially worse | ≥ best baseline − 0.20 | **PASS** — +0.018 vs B5; CI lower bound ≈ 0.000 |
| **H3** — the uncertainty layer is the mechanism | Ablation without uncertainty degrades tail risk | **FAIL** — M1 vs B5 tail differences are within noise |

**Summary:** the DRO/CVaR optimizer itself is associated with better Sharpe and tail metrics than 1/N, but the **epistemic-uncertainty layer does not separate from point-estimate DRO** in this reduced test. The project's primary mechanism claim is not supported.

---

## 5. Interpretation

This is a **clean negative result for H1/H3**, not a failed project:

- The mean forecast is weak (Ridge B0 OOS \(R^2\) = −0.019; IC = 0.013).
- The bootstrap uncertainty proxy is small relative to the mean forecast (mean sigma 0.54% vs mean mu 0.79% monthly) and changes weights only slightly.
- The optimizer's tail improvement comes from the CVaR/DRO structure and diversification, not from the epistemic layer.
- B5/B3 collapse to the same portfolio, so the "DRO vs no DRO" comparison is not informative in this reduced design.

**Do not add features, capacity, or trials to force a positive H1/H3.** The honest report is that the uncertainty layer did not demonstrate value under this protocol.

---

## 6. Limitations

- Reduced M1 is **not** the original LightGBM ensemble; it uses a bootstrap Ridge sigma.
- Bootstrap dispersion is a weak epistemic proxy, not a conformal guarantee.
- Current-listed ETF universe; not survivorship-free.
- B5 and B3 are identical by construction.
- No deflated Sharpe, stress-window table, or cost sensitivity yet.
- 179 OOS months; power is limited.

---

## 7. Artifacts

- `results/tables/dro_experiment_summary.json`
- `results/tables/dro_experiment_returns.csv`
- `results/tables/dro_experiment_weights.parquet`
- `results/tables/dro_experiment_analysis.json`
- `experiments/ledger.jsonl`

**No live deployment and no alpha claim.**
