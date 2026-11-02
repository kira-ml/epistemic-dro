# v3 Pre-Registration — Conditional Tail-Risk Forecast

**Status:** FROZEN — `v3.0-tail` (2026-11-02)
**Parent:** `v2.0-holdout`; v1/v2 closed
**Decision record:** `DEC-20261102-011`
**Tag:** `docs-freeze-v3`
**Holdout:** 2025-01 .. 2026-08 — **untouched** at freeze

> **This is not an epistemic-uncertainty test.** v1 and v2 tested epistemic uncertainty and failed. v3 tests whether a **conditional tail-risk forecast** (next-month realized volatility) improves DRO tail-risk allocation relative to trailing volatility. It is a different, narrower claim. Do not describe it as epistemic uncertainty.

---

## 1. Hypothesis

| ID | Hypothesis | Falsification |
|---|---|---|
| **H1v3** | A conditional tail-risk forecast used as DRO `sigma` reduces max drawdown and CVaR95 versus trailing 36-month realized volatility, net of costs, on the holdout. | MDD or CVaR95 is worse, or the paired 90% CVaR interval includes zero. |
| **H2v3** | Net Sharpe is not materially worse than the trailing-volatility DRO. | Net Sharpe is worse by more than 0.20. |
| **H3v3** | The conditional forecast is the mechanism. | Trailing volatility matches or beats the conditional forecast on the tail metrics. |

**Power caveat:** the holdout is 20 months. It cannot reliably detect a 20% relative MDD improvement. H1v3 uses **direction + paired 90% CVaR interval excluding zero**, not the 20% threshold. Report the 20% number for continuity only.

---

## 2. Data and periods

| Item | Value |
|---|---|
| Snapshot | `data/raw_v2/` (72 ETFs, 2000-01 .. 2026-09; FRED `TB3MS`) |
| Development | 2010-01 .. 2024-11 (179 rebalances; reused, disclosed) |
| Holdout | **2025-01 .. 2026-08 (20 rebalances; untouched at freeze)** |
| Universe | 72 liquid US-listed equity ETFs, PIT eligibility |
| Features | 19 (same as v2) |
| Costs | 10 bps one-way primary |
| Constraints | Long-only, sum=1, 5% cap, no leverage/short |

---

## 3. Model and uncertainty

### 3.1 Target

For each ETF-month \(t\), the target is the **absolute next-month excess return**:

\[
y_{i,t+1} = \left| r^{\text{ex}}_{i,t+1} \right|
\]

This is a realized-volatility proxy. It is **aleatoric tail risk**, not epistemic uncertainty.

### 3.2 Model

- LightGBM regression with `objective="regression_l1"` (robust absolute loss).
- 3 seeds; predictions averaged.
- 200 trees, learning rate 0.03, 15 leaves, depth 4, min child 50, subsample 0.8, colsample 0.8.
- Training: 60 months; validation: 12 months; 1-month purge.
- No test-period data in fitting or early stopping.

### 3.3 Calibration

- Compute the validation scale \(s = \text{mean}(|r^{\text{ex}}_{\text{val}}|) / \text{mean}(\hat{\sigma}_{\text{val}})\).
- Clip \(s\) to \([0.5, 2.0]\).
- Test sigma: \(\sigma = \max(s \cdot \hat{\sigma}_{\text{test}}, 10^{-6})\).

### 3.4 DRO

- `M1_v3`: mean = Ridge B0 (or conformal q50? **No** — use Ridge B0 for the mean to isolate the sigma change), sigma = conditional tail forecast, `kappa=1.0`.
- `B5_uncond_sigma`: same mean, sigma = trailing 36-month realized volatility (monthly), `kappa=1.0`.
- `B3_CVaR`: same mean, sigma = 0, `kappa=0`.
- `B1_equal_weight`.

**Mean forecast:** Ridge B0 is used for all strategies. This isolates the **sigma** treatment. The v2 quantile mean is not used because the v2 quantile model failed its information gate and its q50 mean is not the object of v3.

---

## 4. Pre-holdout gate

**G-R4v3 — tail-forecast information audit (development only):**

- Date-blocked permutation null, 30 permutations, BH-FDR q < 0.05.
- Test: mutual information between predicted sigma and future absolute excess return.
- Pass rule: **≥80% of dates** must beat the null.
- Secondary calibration: mean predicted sigma vs mean realized absolute return, and the spread between top/bottom sigma deciles.
- If G-R4v3 fails, v3 stops **before** the holdout.
- If it passes, freeze/tag and run the holdout **once**.

---

## 5. Decision rule

- **H1v3 PASS** if M1v3 max drawdown and CVaR95 are both better than B5_uncond_sigma **and** the paired 90% CVaR difference interval excludes zero.
- **H2v3 PASS** if the paired 90% Sharpe difference lower bound is ≥ −0.20.
- **H3v3 PASS** if the M1v3 − B5_uncond_sigma tail intervals both exclude zero.
- **INCONCLUSIVE** if the intervals are too wide; report the power limitation.

No post-hoc tuning, feature addition, threshold change, or holdout reuse.

---

## 6. What does not change

- Net Sharpe primary; MDD and CVaR95 guardrails.
- Long-only, sum=1, 5% cap, monthly rebalance.
- 10 bps primary; 5/20/50 bps sensitivity.
- PIT-only features; ETF inception eligibility.
- No live deployment, no investment advice, no alpha claim, no causal claim.
- No survivorship-free claim.

---

## 7. Freeze record

| Item | Value |
|---|---|
| Protocol version | `v3.0-tail` |
| Frozen by | Ken Ira Talingting (owner) |
| Freeze date | 2026-11-02 |
| Hash of config | `f030e8b6dc446477becce7bbd392520fb6d598f705463ed927df2d986ecc4091` |
| Git commit | Tag `docs-freeze-v3` |
| Holdout start/end | 2025-01-01 / 2026-08-31 |
| Holdout status | **Untouched at freeze** |

**The holdout is touched once, only if G-R4v3 passes.** Any change after this record requires a new pre-registration.

---

## 8. Post-freeze outcome (2026-11-02)

**G-R4v3 FAILED.** The development-only tail-forecast audit found a sigma pass rate of **0.430** (threshold 0.80; 179 dates, 30 permutations, BH-FDR). Calibration was good (mean sigma 4.29% vs realized 4.30%; decile spread 3.76 pp), but the per-date information was not stable.

**The 2025-2026 holdout was not touched.** Per this pre-registration, v3 stops before the holdout. See `docs/17_v3_report.md` and `DEC-20261102-012`. No post-hoc relaxation was applied.
