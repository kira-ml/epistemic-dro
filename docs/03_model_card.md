# Model Card — Epistemic-Aware DRO

**Status:** Frozen template — pre-fit; no fitted model yet<br>
**Version:** 0.1<br>
**Owner:** Ken Ira Talingting<br>
**Last updated:** 2026-11-02

---

## 1. Model details

| Field | Value |
|---|---|
| Model name | Epistemic-aware DRO mean-CVaR portfolio |
| Model type | Cross-sectional ML return model + convex robust optimizer |
| Version | 0.1 (pre-fit) |
| License | MIT (see `LICENSE`) |
| Contact | Ken Ira Talingting |

---

## 2. Intended use

- Research on robust portfolio construction.
- Comparing uncertainty-aware DRO with point-estimate DRO and standard baselines.
- Educational demonstration of leakage-tested walk-forward evaluation.

## 3. Out-of-scope use

- Live trading or capital allocation.
- Individual investment advice.
- Any use with real money without independent validation, execution modelling, and risk review.
- Claims of alpha or market-beating performance.

---

## 4. Data

| Field | Value |
|---|---|
| Source | Public ETF total-return data + FRED `TB3MS` + Fama-French factors (DEC-20261102-001) |
| Coverage | 2005–2024 (planned; ETF inception limits the early cross-section) |
| Frequency | Monthly |
| Universe | 50–100 liquid US-listed ETFs (planned) |
| PIT | Required for prices, returns, and eligibility; ETF metadata is not PIT unless a history exists |
| Claim scope | Methods study; no stock-selection validity, no survivorship-free claim |
| Sensitive data | No personal data; provider terms apply |

---

## 5. Features

Planned, ETF-appropriate: momentum (1, 3, 6, 12 months), realised volatility (3 and 12 months), 12-month drawdown, dollar-volume liquidity, 36-month market beta, and factor exposures (market, size, value, momentum). Expense ratio and distribution yield are used only if a historical series exists; otherwise they are excluded or disclosed as current-snapshot fields.

Feature provenance and leakage audit: `docs/01_data_card.md`.

---

## 6. Targets

Next-month cross-sectional excess-return rank (or winsorized return). The target is not used in feature construction.

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
- The ETF universe is narrower and less dispersed than a stock universe; power is limited.
- Public ETF data may omit closed funds, so the result is not survivorship-free. Do not claim otherwise.
- Expense ratio and distribution yield may be current snapshots rather than point-in-time values.

---

## 11. Ethical and legal considerations

- No personal data.
- Provider data may not be redistributed; check the terms before publishing figures.
- No investment advice.
- Code is MIT-licensed; the license does not grant rights to third-party data.
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
