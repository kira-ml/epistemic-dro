# One-page summary — Epistemic-Aware DRO

**Question:** Does an epistemic-uncertainty layer improve the tail-risk / return trade-off of a distributionally robust mean-CVaR portfolio, net of costs, out-of-sample?

**Answer:** No — not detectably, under three pre-registered protocols.

| Attempt | Object of uncertainty | Outcome |
|---|---|---|
| **v1** | Epistemic uncertainty (Ridge mean + bootstrap sigma) | **H1/H3 fail, H2 pass.** 0.4% relative MDD improvement; CVaR CI includes zero; Sharpe non-inferior. |
| **v2** | Conformalized LightGBM return quantiles | **Stopped before holdout.** Coverage 89.9% / 85.9%, but information gate 65.4% < 80%. |
| **v3** | Conditional tail-risk forecast (absolute return) | **Stopped before holdout.** Calibration 4.29% vs 4.30%, decile spread 3.76 pp, but gate 43.0% < 80%; underperformed trailing volatility. |

**What was tested**

- 72 liquid US ETFs, point-in-time, 2010–2024 development.
- 19 lagged features; monthly walk-forward; 60-month train, 12-month validation, 1-month purge.
- Long-only, sum=1, 5% cap, 10 bps one-way costs; net Sharpe primary; MDD and CVaR95 guardrails.
- Mandatory Ridge B0; date-blocked information audit; target-shuffling test; counter-metric gate.

**Key finding**

Calibration is not information. A model can be well calibrated, show a clean decile spread, and still fail a stability gate. The binding constraint is the weak conditional mean and the instability of the uncertainty signal — not the optimizer.

**What would change the answer**

A new pre-registration with a feature set that survives an information audit, an uncertainty model with a stable pre-holdout signal, a non-degenerate comparator, and an untouched holdout. Not a feature search on the same data.

**Artifacts**

- Paper: `paper/mini_paper.pdf`
- Code: `github.com/kira-ml/epistemic-dro`
- Frozen protocols, gates, and experiment ledger in the repository.

**Disclosure**

Not investment advice. No alpha claim. No live deployment. The ETF universe is current-listed, so results are not survivorship-free. v1 is a reduced M1 (Ridge + bootstrap sigma), not the original LightGBM ensemble. v2/v3 never reached the holdout.
