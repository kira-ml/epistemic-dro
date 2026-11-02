# v2 Report — Conformalized Quantile Uncertainty

**Status:** **STOPPED before holdout** — G-R4v2 information gate failed
**Date:** 2026-11-02
**Protocol:** `v2.0-holdout` (frozen; `docs/14_v2_preregistration.md`)
**Holdout:** 2025-01 .. 2026-08 — **untouched**
**Decision record:** `DEC-20261102-010`

---

## 1. What was attempted

v2 tested a stronger uncertainty model than v1:

- 19 ETF features, including downside volatility, skew, worst month, volume shock, and 36-month market correlation.
- LightGBM quantile regression at q05/q50/q95, 3 seeds.
- Split-conformal calibration on a 12-month validation window.
- Uncertainty: `sigma = (q95 - q05) / (2 * 1.645)`.
- Non-degenerate comparator: `B5_uncond_sigma` uses each asset's trailing 36-month realized volatility (asset-specific, but not conditional on the quantile model).
- New snapshot through 2026-09; holdout 2025-01..2026-08.

Development period: 2010-01..2024-11 (179 months). The holdout was not touched.

---

## 2. Development result (not confirmatory)

| Strategy | Net Sharpe | Max drawdown | CVaR95 | Ann. turnover | Mean sigma |
|---|---:|---:|---:|---:|---:|
| M1_v2 | 0.812 | −22.29% | −8.16% | 3.47 | 5.27% |
| B5_uncond_sigma | 0.813 | −22.96% | −8.19% | 2.57 | 5.66% |
| B3_CVaR | 0.743 | −24.30% | −8.66% | 3.30 | 1e-6 |
| B1_equal_weight | 0.673 | −26.61% | −9.76% | 0.11 | 1e-6 |

Conformal coverage:

- validation: **0.899**
- development test: **0.859**

The conditional uncertainty model produces a small tail improvement over trailing volatility (MDD −22.29% vs −22.96%; CVaR −8.16% vs −8.19%), but **worse** Sharpe (0.812 vs 0.813) and **higher** turnover (3.47 vs 2.57). This is not a strong separation.

---

## 3. Pre-holdout gate failure

The frozen v2 pre-registration required a **G-R4v2** uncertainty-information audit on development data:

- Date-blocked permutation null, 30 permutations, BH-FDR q < 0.05.
- Pass rule: sigma must beat the null in at least **80%** of dates.

Result:

| Signal | Mean MI | Null 95th | Median q | Pass rate | Survives |
|---|---:|---:|---:|---:|---|
| `sigma` | 0.162 | 0.087 | 0.032 | **0.654** | **No** |
| `interval_width` | 0.162 | 0.087 | 0.032 | **0.654** | **No** |

The uncertainty signal is above the null on average but not stable enough across dates. It fails the pre-registered 80% rule. Coverage is acceptable, but coverage alone does not make the uncertainty informative.

**Per the pre-registration, the 2025-2026 holdout was not touched.** v2 stops here.

---

## 4. Interpretation

- The quantile model is **calibrated** (coverage 0.86–0.90) but its sigma is **not a stable conditional tail signal**.
- The dev tail improvement over trailing volatility is tiny and comes with worse Sharpe and higher turnover.
- Touching the holdout would not rescue a signal that failed its pre-holdout information gate; it would just consume the holdout.
- This is a **successful kill**, not a failure of the process. The gate prevented a low-information model from being promoted to a confirmatory test.

---

## 5. What would be needed for a v3

A new pre-registration, not a relaxation of this gate:

1. A new uncertainty model with a stable, pre-holdout information signal (e.g., a different calibration target, a longer horizon, or a different feature set).
2. A holdout that has never been touched.
3. A non-degenerate comparator (v2's `B5_uncond_sigma` is the right shape).
4. Calibration and information gates frozen before the holdout.

Do not run v2 on the 2025-2026 holdout retrospectively.

---

## 6. Artifacts

- `docs/14_v2_preregistration.md` — frozen v2 protocol.
- `configs/v2.yaml` — v2 config (hash `827d8549ed34bf28f8c0d9f3690019ed681eb61fa30f938e553281a66d3a4131`).
- `scripts/run_v2_experiment.py` — quantile/conformal experiment.
- `scripts/run_v2_uncertainty_audit.py` — G-R4v2 audit.
- `results/tables/v2_summary_dev.json`
- `results/tables/v2_returns_dev.csv`
- `results/tables/v2_uncertainty_dev.parquet`
- `results/tables/v2_uncertainty_audit.json`
- `experiments/ledger.jsonl`

**No holdout result exists. No deployment. No alpha claim.**
