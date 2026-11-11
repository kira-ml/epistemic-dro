# v1.0.1 — Epistemic-Aware DRO

**Released:** 2026-11-11  
**Tag:** `v1.0.1`  
**Status:** Correction patch. No result changed.

## Why this release exists

An internal pre-review audit found three presentation issues in the v1.0.0 paper:

1. **The H1 relative max-drawdown interval was sign-flipped.** The point estimate (0.4%) and the verdict (FAIL) were correct; the interval was printed as `[-6.2%, +1.1%]` instead of `[-1.1%, +6.2%]`. The analysis code, the published analysis JSON, the paper, and the companion documents are corrected.
2. **The paper described 19 lagged features, but the frozen v1 audit and Ridge B0 used 13.** The six derived features (downside volatility, skew, worst month, volatility ratio, volume shock, and 36-month market correlation) were added with v2. The paper now distinguishes the 13-feature frozen v1 audit from the 19-feature current build and the pooled re-evaluation.
3. **The paper conflated two evaluation paths.** The 14-fold B0 diagnostic has 158 months with predictions; the monthly-refit DRO backtest spans 179 months. The paper now states that they share the universe, features, and model class but are not the same test windows.

The paper also gains numbered references (17 entries, all cited) and clearer table rules and headers. No return, metric, verdict, method, cost, or solver changed. The 2025–2026 holdout remains untouched.

## What is published

- Corrected paper PDF (8 pages), carousel (7 slides), one-pager, and card.
- Corrected `paper/generated/numbers.typ` and `paper/published-results/dro_experiment_analysis.json`.
- No raw vendor data. No holdout result.

## Relationship to v1.0.0

`v1.0.0` remains the original release. `v1.0.1` is the corrected artifact; use it for citation and external review. The `v1.0.0` tag is not moved.

## Limits

Methods study; no alpha, causal, or live-deployment claim. v2 and v3 were stopped before the holdout. No v4 is justified on this data.
