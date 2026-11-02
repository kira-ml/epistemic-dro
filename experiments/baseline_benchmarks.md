# Baseline Benchmarks

**Status:** B0 completed 2026-11-02 — null linear signal; other baselines pending.
**Rule:** this file records the mandatory simple baselines before any complex model is adopted. It is not a results table.

| ID | Baseline | Definition | Status | Metrics |
|---|---|---|---|---|
| **B0** | Ridge return forecast | Standardized features → Ridge(alpha=1.0) → cross-sectional rank; same universe, splits, constraints, and costs | **Completed 2026-11-02** | OOS R² −0.0186; mean IC 0.0128 (t 0.56) |
| **B1** | 1/N | Equal weight across eligible ETFs | **Pending** | — |
| **B2** | Mean-variance | Sample mean/covariance, long-only, 5% cap | **Pending** | — |
| **B3** | CVaR-only | Minimize CVaR, no DRO | **Pending** | — |
| **B4** | HRP | Hierarchical risk parity on the same covariance | **Pending** | — |
| **B5** | DRO-point | Box DRO with point-estimate mean and zero uncertainty | **Pending** | — |
| **M1** | DRO-uncertainty | Box DRO with ML mean and ensemble/conformal uncertainty | **Pending** | — |
| **M2** | DRO-ellipsoid | Ellipsoidal DRO with the same uncertainty | **Pending** | — |

## B0 Ridge result (2010-01 .. 2024-12)

| Metric | Value |
|---|---|
| Folds | 14 |
| OOS rows / months / tickers | 11,328 / 158 / 72 |
| Pooled OOS \(R^2\) | **−0.0186** |
| Mean monthly rank IC | **0.0128** |
| IC std / t-stat | 0.2850 / **0.563** |
| Annualized ICIR | 0.155 |
| Shuffled-target mean IC | **−0.0040** (t = −0.480) |

**Interpretation:** the linear forecast is statistically indistinguishable from zero. The shuffled-target run also collapses to zero, so the null is not an obvious leak. The ML layer cannot be assumed to add value. Do not claim alpha, and do not add features or capacity to force a signal.

**Adoption rule (G-R6):** M1/M2 must beat B0 with a Diebold-Mariano test at \(p < 0.01\) on purged OOS data, or the simpler model is reported. No exceptions.

**Metric basket (G-R10):** net Sharpe, max drawdown, CVaR95, turnover, cost drag. No single-metric adoption.
