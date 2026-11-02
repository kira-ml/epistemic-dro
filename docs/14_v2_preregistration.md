# v2 Pre-Registration — Conformalized Quantile Uncertainty

**Status:** FROZEN — `v2.0-holdout` (2026-11-02)
**Parent:** `v1.1-rigor`; v1 is closed (`docs/13_final_report.md`)
**Decision record:** `DEC-20261102-009` (v2 pre-registration)
**Tag:** `docs-freeze-v2`
**Holdout:** 2025-01 .. 2026-08 — touched **once** after this file is frozen

> v2 is a **new hypothesis**, not a rescue of v1. v1 found no detectable mean signal and no uncertainty-layer separation. v2 asks whether a stronger, distributional uncertainty model can improve tail-risk allocation even when the mean forecast is weak. The 2010–2024 development period is reused and disclosed; only the 2025–2026 holdout is out-of-time.

---

## 1. Hypotheses

| ID | Hypothesis | Falsification |
|---|---|---|
| **H1v2** | Asset-specific uncertainty from conformalized return quantiles reduces max drawdown and CVaR95 versus an **unconditional-volatility** DRO, net of costs, on the holdout. | MDD or CVaR95 is worse, or the paired CVaR difference interval includes zero. |
| **H2v2** | Net Sharpe is not materially worse than the unconditional-volatility DRO. | Net Sharpe is worse by more than 0.20. |
| **H3v2** | The asset-specific uncertainty is the mechanism. | Replacing it with each asset's **trailing 36-month realized volatility** matches or beats M1v2 on the tail metrics. |

**Power caveat (pre-registered):** the holdout is only 20 months. It cannot reliably detect a 20% relative MDD improvement. H1v2 therefore uses **direction + a paired 90% CVaR interval excluding zero**, not the 20% threshold. The 20% number is reported for continuity but is not the sole pass/fail rule on 20 months.

---

## 2. Data and periods

| Item | Value |
|---|---|
| Snapshot | `data/raw_v2/` (72 ETFs, 2000-01 .. 2026-09; FRED `TB3MS`) |
| Development | 2010-01 .. 2024-11 (179 rebalances; reused, disclosed) |
| Holdout | **2025-01 .. 2026-08 (20 rebalances; touched once)** |
| Universe | 72 liquid US-listed equity ETFs, PIT eligibility |
| Features | 19: momentum 1/3/6/12, vol 3/12, downside vol 12, skew 12, worst month 12, vol ratio, volume shock, 36m market correlation, 12m drawdown, dollar volume, 36m beta, 4 factor exposures |
| Costs | 10 bps one-way primary |
| Constraints | Long-only, sum=1, max weight 5%, no leverage/short |

**Survivorship:** current-listed universe; closed funds omitted. No survivorship-free claim.

---

## 3. Model and uncertainty

### 3.1 Quantile model

- LightGBM quantile regression at \(q = 0.05, 0.50, 0.95\).
- 3 seeds per quantile; predictions averaged across seeds.
- 200 trees, learning rate 0.03, 15 leaves, depth 4, min child 50, subsample 0.8, colsample 0.8.
- Target: next-month excess return.
- Training: 60 months; validation: 12 months; 1-month purge.
- No test-period data in fitting, early stopping, or feature selection.

### 3.2 Split-conformal calibration

For each rebalance \(t\):

1. Fit quantile models on the 60-month training window.
2. Predict the 12-month validation window.
3. Compute residual quantiles \(r_q = \text{Quantile}_q(y_{\text{val}} - \hat{y}_{q,\text{val}})\).
4. Calibrate the test prediction: \(\tilde{y}_q = \hat{y}_{q,\text{test}} + r_q\).
5. Enforce \(\tilde{y}_{0.05} \le \tilde{y}_{0.50} \le \tilde{y}_{0.95}\) per asset.
6. Mean forecast \(\mu = \tilde{y}_{0.50}\).
7. Uncertainty \(\sigma = (\tilde{y}_{0.95} - \tilde{y}_{0.05}) / (2 \times 1.6448536)\), floor \(10^{-6}\).

**Coverage diagnostic:** report empirical 90% interval coverage on validation and on the holdout. Target: 0.85–0.95 on validation. The holdout coverage is reported, not tuned.

---

## 4. Strategies

| ID | Mean | Sigma | DRO | CVaR |
|---|---|---|---|---|
| **M1v2** | Conformal q50 | Asset-specific conformal sigma | Yes, `kappa=1.0` | Yes |
| **B5_uncond_sigma** | Conformal q50 | Each asset's trailing 36-month realized volatility (asset-specific, unconditional) | Yes, `kappa=1.0` | Yes |
| **B3_CVaR** | Conformal q50 | Zero | No, `kappa=0` | Yes |
| **B1_equal_weight** | None | None | No | No |

The comparator is **non-degenerate**: B5_uncond_sigma uses an asset-specific, non-zero ambiguity radius, but it is not conditional on the quantile model. This isolates whether the conditional quantile uncertainty adds information beyond trailing volatility. (A constant sigma was rejected before the holdout because a constant penalty is weight-invariant and collapses to B3.)

---

## 5. Gates before the holdout is touched

1. **G-R4v2 — uncertainty information audit (development only):** predicted sigma must have positive date-blocked MI with future absolute excess return or downside, against a permutation null. If it does not, v2 stops before the holdout.
2. **Conformal coverage (development):** validation coverage must be within 0.85–0.95. If not, the calibration is broken and v2 stops.
3. **PIT/leakage:** the v1 leakage tests and the feature-builder PIT tests must pass on the v2 snapshot.
4. **Freeze:** this file, `configs/v2.yaml`, and the v2 feature set are committed and tagged `docs-freeze-v2` before the holdout run.

Only after these gates pass may `scripts/run_v2_experiment.py --period holdout` be run.

---

## 6. Decision rule

- **H1v2 PASS** if M1v2 max drawdown and CVaR95 are both better than B5_uncond_sigma **and** the paired 90% CVaR difference interval excludes zero.
- **H1v2 FAIL** otherwise.
- **H2v2 PASS** if the paired 90% Sharpe difference lower bound is ≥ −0.20.
- **H3v2 PASS** if the M1v2 minus B5_uncond_sigma tail intervals both exclude zero; otherwise FAIL.
- **INCONCLUSIVE** if the intervals are too wide; report the power limitation, do not claim success.

No post-hoc tuning, feature addition, or threshold change after the holdout is touched.

---

## 7. What does not change from v1

- Net Sharpe primary; MDD and CVaR95 guardrails.
- Long-only, sum=1, 5% cap, monthly rebalance.
- 10 bps primary; 5/20/50 bps sensitivity.
- PIT-only features; ETF inception eligibility.
- No live deployment, no investment advice, no alpha claim, no causal claim.
- No survivorship-free claim.

---

## 8. Freeze record

| Item | Value |
|---|---|
| Protocol version | `v2.0-holdout` |
| Frozen by | Ken Ira Talingting (owner) |
| Freeze date | 2026-11-02 |
| Hash of config | `827d8549ed34bf28f8c0d9f3690019ed681eb61fa30f938e553281a66d3a4131` |
| Git commit | Tag `docs-freeze-v2` |
| Holdout start/end | 2025-01-01 / 2026-08-31 |
| Holdout status | **Untouched at freeze** |

**The holdout is touched once.** Any change after this record requires a new pre-registration, not a deviation.

---

## 9. Post-freeze outcome (2026-11-02)

**G-R4v2 FAILED.** The development-only uncertainty audit found a sigma pass rate of **0.654** (threshold 0.80; 179 dates, 30 permutations, BH-FDR). Conformal coverage was 0.899 on validation and 0.859 on development test, so the model is calibrated but the uncertainty is not a stable conditional tail signal.

**The 2025-2026 holdout was not touched.** Per this pre-registration, v2 stops before the holdout. See `docs/15_v2_report.md` and `DEC-20261102-010`. No post-hoc relaxation was applied.
