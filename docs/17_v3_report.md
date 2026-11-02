# v3 Report — Conditional Tail-Risk Forecast

**Status:** **STOPPED before holdout** — G-R4v3 information gate failed
**Date:** 2026-11-02
**Protocol:** `v3.0-tail` (frozen; `docs/16_v3_preregistration.md`)
**Holdout:** 2025-01 .. 2026-08 — **untouched**
**Decision record:** `DEC-20261102-012`

---

## 1. What was tested

v3 is **not** an epistemic-uncertainty test. It asks whether a conditional forecast of next-month absolute excess return (a realized-volatility proxy) is a better DRO `sigma` than trailing 36-month realized volatility.

- 19 features (same as v2).
- LightGBM `regression_l1` on \(|r^{\text{ex}}_{t+1}|\), 3 seeds.
- 60-month train, 12-month validation, 1-month purge.
- Validation scale calibration \(s = \text{mean}(|r|_{\text{val}}) / \text{mean}(\hat{\sigma}_{\text{val}})\), clipped [0.5, 2.0].
- Strategies: M1_v3 (conditional sigma), B5_uncond_sigma (trailing 36m vol), B3_CVaR, B1.
- Mean forecast: Ridge B0 for every strategy, to isolate sigma.

Development: 2010-01..2024-11 (179 months). Holdout untouched.

---

## 2. Development result (not confirmatory)

| Strategy | Net Sharpe | Max drawdown | CVaR95 | Ann. turnover | Mean sigma |
|---|---:|---:|---:|---:|---:|
| M1_v3 | 0.783 | −25.87% | −8.44% | 3.16 | 4.31% |
| B5_uncond_sigma | 0.840 | −24.76% | −8.18% | 1.26 | 5.66% |
| B3_CVaR | 0.808 | −24.68% | −8.40% | 1.66 | 1e-6 |
| B1_equal_weight | 0.673 | −26.61% | −9.76% | 0.11 | 1e-6 |

The conditional tail forecast **underperforms** trailing volatility on Sharpe, MDD, CVaR, and turnover.

---

## 3. Pre-holdout gate

**G-R4v3:** date-blocked MI between predicted sigma and future realized absolute return, 30 permutations, BH-FDR q < 0.05, 80% pass rule.

| Metric | Value |
|---|---:|
| Dates | 179 |
| Mean MI | 0.121 |
| Null 95th percentile | 0.088 |
| Median q-value | 0.065 |
| **Pass rate** | **0.430** |
| Survives | **No** |

Calibration diagnostics are good:

| Metric | Value |
|---|---:|
| Mean sigma | 4.29% |
| Mean realized absolute return | 4.30% |
| Correlation | 0.284 |
| Top-decile realized abs | 6.52% |
| Bottom-decile realized abs | 2.75% |
| Decile spread | 3.76 pp |

**Interpretation:** the forecast has cross-sectional tail information (a large decile spread) and is well calibrated, but the per-date MI is not stable enough to pass the frozen 80% rule. The gate is strict by design; it prevents a model with only episodic information from being promoted to a holdout claim.

**The 2025-2026 holdout was not touched.**

---

## 4. Why this is a successful kill

- Calibration is not the same as stable conditional information; v3 demonstrates the distinction.
- The conditional forecast does not beat trailing volatility on development, so even without the gate it would not be a promising candidate.
- The holdout is preserved for a genuinely different model, not for a gate relaxation.
- No post-hoc tuning, no holdout consumption.

---

## 5. What would be needed for v4

A new pre-registration, not a relaxation of G-R4v3:

1. A model with a **stable** conditional tail signal (not just good average calibration).
2. A pre-holdout gate that is justified before seeing results.
3. A non-degenerate comparator and an untouched holdout.
4. A clear statement that the object is tail-risk forecasting, not epistemic uncertainty.

At this point, the higher-value action is to **stop experiments and package the three negative results** rather than search for a fourth model on the same data.

---

## 6. Artifacts

- `docs/16_v3_preregistration.md`
- `configs/v3.yaml`
- `scripts/run_v3_experiment.py`
- `scripts/run_v3_sigma_audit.py`
- `results/tables/v3_summary_dev.json`
- `results/tables/v3_returns_dev.csv`
- `results/tables/v3_sigma_dev.parquet`
- `results/tables/v3_sigma_audit.json`
- `experiments/ledger.jsonl`

**No holdout result exists. No deployment. No alpha claim.**
