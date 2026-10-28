# Model Card — Epistemic-Aware DRO

**Status:** Template; no fitted model yet  
**Version:** 0.1  
**Owner:** Ken Ira Talingting  
**Last updated:** 2026-10-27

---

## 1. Model details

| Field | Value |
|---|---|
| Model name | Epistemic-aware DRO mean-CVaR portfolio |
| Model type | Cross-sectional ML return model + convex robust optimizer |
| Version | 0.1 (pre-fit) |
| License | TBD |
| Contact | Ken Ira Talingting |

---

## 2. Intended use

- Research on robust portfolio construction.
- Comparing uncertainty-aware DRO with point-estimate DRO and standard baselines.
- Educational demonstration of leakage-free walk-forward evaluation.

## 3. Out-of-scope use

- Live trading or capital allocation.
- Individual investment advice.
- Any use with real money without independent validation, execution modelling, and risk review.
- Claims of alpha or market-beating performance.

---

## 4. Data

| Field | Value |
|---|---|
| Source | TBD |
| Coverage | 2005–2024 (planned) |
| Frequency | Monthly |
| Universe | 150–200 liquid US stocks (planned) |
| PIT | Required; see data card |
| Sensitive data | No personal data; vendor licensing applies |

---

## 5. Features

Planned: momentum (1, 6, 12 months), volatility, value (book-to-market, earnings yield), quality (ROE, gross profitability), size, liquidity. All lagged and available at the decision date.

Feature provenance and leakage audit: `docs/01_data_card.md`.

---

## 6. Targets

Next-month cross-sectional excess-return rank (or winsorized excess return). The target is not used in feature construction.

---

## 7. Uncertainty

| Method | Description | Calibration |
|---|---|---|
| Ensemble | Variance across 5 seeds | Reliability / coverage |
| Conformal | Split-conformal half-width | Empirical coverage |

The uncertainty estimate feeds the DRO ambiguity set. It is not a guarantee of return bounds.

---

## 8. Optimization

- Box or ellipsoidal ambiguity set around the predicted mean.
- Mean-CVaR objective or CVaR constraint.
- Long-only, sum = 1, max weight 5%.
- Transaction costs and turnover penalty.
- Convex solver; failure is fatal, not replaced by equal weights.

---

## 9. Evaluation

| Metric | Role |
|---|---|
| Net Sharpe | Primary |
| Max drawdown | Guardrail |
| CVaR95 | Guardrail |
| Sortino, Calmar | Diagnostic |
| Turnover, cost drag | Diagnostic |
| Calibration | Diagnostic |

Walk-forward, net of costs, bootstrap intervals, deflated Sharpe. See `docs/02_experiment_card.md`.

---

## 10. Limitations

- No live-trading validation.
- CVaR depends on historical scenarios.
- DRO protects only within the chosen ambiguity set.
- Results may not survive higher transaction costs.
- A short sample cannot establish regime robustness.
- The model is not a causal model.

---

## 11. Ethical and legal considerations

- No personal data.
- Vendor data may not be redistributed.
- No investment advice.
- Results must be presented with limitations and without hype.

---

## 12. Monitoring (research)

- Re-run the frozen protocol after data updates.
- Track calibration, turnover, and cost sensitivity.
- Log deviations in `docs/04_decision_log.md`.
- Do not deploy without a separate G4 review.

---

## 13. Fill-in checklist

- [ ] Data source and vintage recorded.
- [ ] Features and labels documented.
- [ ] Model hyperparameters frozen.
- [ ] Uncertainty calibration reported.
- [ ] Optimizer constraints verified.
- [ ] Walk-forward results and ablation complete.
- [ ] Limitations and failure modes written.
- [ ] No claim beyond the evidence.
