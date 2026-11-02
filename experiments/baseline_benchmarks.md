# Baseline Benchmarks

**Status:** No runs yet — G1 snapshot pending.
**Rule:** this file records the mandatory simple baselines before any complex model is adopted. It is not a results table.

| ID | Baseline | Definition | Status | Metrics |
|---|---|---|---|---|
| **B0** | Ridge return forecast | Standardized features → Ridge(alpha=1.0) → cross-sectional rank; same universe, splits, constraints, and costs | **Pending G1** | — |
| **B1** | 1/N | Equal weight across eligible ETFs | **Pending G1** | — |
| **B2** | Mean-variance | Sample mean/covariance, long-only, 5% cap | **Pending G1** | — |
| **B3** | CVaR-only | Minimize CVaR, no DRO | **Pending G1** | — |
| **B4** | HRP | Hierarchical risk parity on the same covariance | **Pending G1** | — |
| **B5** | DRO-point | Box DRO with point-estimate mean and zero uncertainty | **Pending G1** | — |
| **M1** | DRO-uncertainty | Box DRO with ML mean and ensemble/conformal uncertainty | **Pending G1** | — |
| **M2** | DRO-ellipsoid | Ellipsoidal DRO with the same uncertainty | **Pending G1** | — |

**Adoption rule (G-R6):** M1/M2 must beat B0 with a Diebold-Mariano test at \(p < 0.01\) on purged OOS data, or the simpler model is reported. No exceptions.

**Metric basket (G-R10):** net Sharpe, max drawdown, CVaR95, turnover, cost drag. No single-metric adoption.
