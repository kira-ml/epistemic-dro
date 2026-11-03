# Final Report — Epistemic-Aware DRO

**Status:** Final — reduced experiment complete; **H1/H3 fail, H2 passes**
**Date:** 2026-11-02
**Protocol:** `v1.1-rigor` (frozen); config hash `ded5c26d3302676ac5f3a403d3d3284cf564cd8a02500454d5263509b08b4e37`
**Decision record:** `DEC-20261102-007` (result), `DEC-20261102-008` (close)
**Scope:** 72 liquid US-listed ETFs, 2010–2024, methods study. Not investment advice. No live deployment.

---

## 1. Executive answer

**Does epistemic uncertainty improve the tail-risk/return trade-off of a DRO mean-CVaR portfolio?**

**No — not detectably, under this protocol.**

- **H1 FAILS:** the uncertainty-aware portfolio's max-drawdown improvement is **0.4% relative** (90% CI [−6.2%, +1.1%]), far below the pre-registered 20% threshold. The CVaR95 difference interval includes zero.
- **H2 PASSES:** net Sharpe is not materially worse than the best baseline (+0.018 vs point-DRO; 90% CI [−0.000, +0.037], within the 0.20 margin).
- **H3 FAILS:** removing the uncertainty layer does not degrade the tail result in a detectable way. The ablation is within noise.

The **DRO/CVaR optimizer** is associated with better risk-adjusted performance than 1/N (Sharpe +0.143, 90% CI [+0.020, +0.266]; max drawdown +0.060, CI [+0.0016, +0.137]; CVaR +0.0146, CI [+0.0043, +0.026]). That is a secondary finding about portfolio construction, **not** evidence for the epistemic-uncertainty mechanism.

---

## 2. What was tested

| Item | Value |
|---|---|
| Universe | 72 liquid US-listed equity ETFs, PIT eligibility |
| Period | 2010-01 .. 2024-11 (179 monthly rebalances) |
| Mean forecast | Ridge B0 on 13 ETF features; OOS \(R^2\) = −0.019; IC = 0.013 (t = 0.56) |
| Uncertainty | 5-model bootstrap Ridge sigma (reduced M1); mean sigma 0.54% vs mean mu 0.79% monthly |
| Information audit | G-R4 null: 0/13 features passed the 80% date-level MI rule |
| Optimizer | Box DRO + CVaR, CLARABEL, long-only, sum=1, 5% cap |
| Costs | 10 bps primary; 5/20/50 bps sensitivity |
| LightGBM | **Not fitted** — G-R4 null |

The reduced M1 is **not** the original LightGBM ensemble. The negative result applies to the frozen feature set and the bootstrap-sigma proxy.

---

## 3. Main result (10 bps)

| Strategy | Net Sharpe | Max drawdown | CVaR95 | Sortino | Calmar | Ann. turnover | Cost drag |
|---|---:|---:|---:|---:|---:|---:|---:|
| **M1_reduced** | **0.816** | **−24.18%** | **−8.31%** | 1.171 | 0.496 | 1.90 | 0.190% |
| B5_DRO_point | 0.798 | −24.28% | −8.44% | 1.125 | 0.485 | 1.82 | 0.182% |
| B3_CVaR | 0.798 | −24.28% | −8.44% | 1.125 | 0.485 | 1.82 | 0.182% |
| B1_equal_weight | 0.673 | −26.61% | −9.76% | 0.939 | 0.420 | 0.11 | 0.011% |

**B5 and B3 are mathematically identical** when sigma is zero; the DRO-vs-no-DRO comparison is uninformative in this reduced design.

### Paired bootstrap (90%, 2,000 reps)

| Comparison | Metric | Difference | 90% CI | Reading |
|---|---|---|---:|---|
| M1 − B5 | Net Sharpe | +0.018 | [−0.000, +0.037] | CI touches zero |
| M1 − B5 | Max drawdown | +0.0010 | [−0.0024, +0.0160] | No separation |
| M1 − B5 | CVaR95 | +0.0013 | [−0.0001, +0.0031] | CI includes zero |
| M1 − B5 | Relative MDD improvement | +0.4% | [−6.2%, +1.1%] | Far below +20% |
| M1 − B1 | Net Sharpe | +0.143 | [+0.020, +0.266] | Optimizer beats 1/N |
| M1 − B1 | Max drawdown | +0.060 | [+0.0016, +0.137] | Optimizer beats 1/N |
| M1 − B1 | CVaR95 | +0.0146 | [+0.0043, +0.026] | Optimizer beats 1/N |

---

## 4. Cost sensitivity

Net Sharpe / max drawdown / CVaR95:

| Cost | M1_reduced | B5_DRO_point | B1_equal_weight |
|---:|---|---|---|
| 5 bps | 0.830 / −24.26% / −8.26% | 0.817 / −24.39% / −8.42% | 0.674 / −26.61% / −9.76% |
| 10 bps | 0.816 / −24.18% / −8.31% | 0.798 / −24.28% / −8.44% | 0.673 / −26.61% / −9.76% |
| 20 bps | 0.803 / −24.33% / −8.38% | 0.789 / −24.36% / −8.45% | 0.673 / −26.61% / −9.76% |
| 50 bps | 0.785 / −24.16% / −8.41% | 0.771 / −24.11% / −8.49% | 0.671 / −26.61% / −9.76% |

The ordering is stable: M1 ≈ B5 > B1. The M1−B5 gap is tiny at every cost level. Costs erode Sharpe but do not flip the conclusion.

---

## 5. Stress windows

Net Sharpe / max drawdown / CVaR95 (10 bps):

| Window | M1_reduced | B5_DRO_point |
|---|---|---|
| 2010–2019 | 1.041 / −14.48% / −6.90% | 1.032 / −14.54% / −6.90% |
| 2020 | 0.681 / −12.33% / −12.33% | 0.634 / −13.24% / −13.24% |
| 2022 | −0.508 / −19.72% / −9.62% | −0.488 / −19.92% / −9.63% |
| 2020–2024 | 0.502 / −24.18% / −10.30% | 0.482 / −24.28% / −10.60% |

2008 is outside the 2010+ OOS window and is not reported as an OOS stress test. The 2020 and 2022 differences are small and inconsistent in sign across metrics.

---

## 6. Deflated Sharpe

Strategy-level tests against zero, 4 pre-registered strategy trials, 179 months:

| Strategy | Annualized Sharpe | Deflated Sharpe probability | Probabilistic Sharpe probability |
|---|---:|---:|---:|
| M1_reduced | 0.816 | 0.996 | 0.998 |
| B5_DRO_point | 0.798 | 0.995 | 0.998 |
| B1_equal_weight | 0.673 | 0.986 | 0.993 |

**Important:** the deflated Sharpe tests whether each strategy's Sharpe is distinguishable from zero after four trials. It does **not** test whether M1 beats B5. That incremental test is the paired bootstrap, and it fails. A high DSR is not evidence for the uncertainty layer.

---

## 7. Interpretation

1. **The mean forecast is weak.** Ridge B0 has no detectable OOS linear signal; the G-R4 MI audit found no surviving feature. This is the binding constraint.
2. **The uncertainty proxy is small.** Bootstrap sigma is 0.54% monthly against a 0.79% mean forecast and changes weights only slightly.
3. **The optimizer structure helps.** DRO/CVaR beats 1/N on Sharpe and tail metrics, but that is not the project's mechanism claim.
4. **The uncertainty layer does not separate.** H1 and H3 fail; the honest conclusion is a negative result for epistemic uncertainty under this protocol.
5. **No alpha claim.** The project is a methods study, not a strategy.

---

## 8. What would change the conclusion

Not post-hoc tuning. A credible positive result would require a **new pre-registration** with:

- a feature set that survives a pre-registered information audit;
- a stronger uncertainty model (LightGBM ensemble or conformal) with calibration evidence;
- a non-degenerate point-DRO comparator (B5 and B3 currently collapse);
- a new data snapshot and a new holdout.

Adding features, capacity, or trials to the current result would violate the protocol and the project's honesty standard.

---

## 9. Limitations

- Reduced M1 uses bootstrap Ridge sigma, not the original LightGBM ensemble.
- Current-listed ETF universe; closed funds omitted; not survivorship-free.
- 179 OOS months; limited power.
- B5/B3 collapse; the DRO-vs-no-DRO comparison is uninformative.
- No transaction-cost market impact beyond linear 10 bps.
- No live deployment, no execution model, no investment advice.
- The 2008 crisis is outside the OOS window.
- The DSR tests strategy-level Sharpe, not the incremental M1−B5 effect.

---

## 10. Reproduction

```bash
python scripts/build_snapshot.py --force
python scripts/check_data.py
python scripts/run_diagnostics.py
python scripts/run_baseline.py
python scripts/run_baseline.py --shuffle-target
python scripts/run_information_audit.py
python scripts/run_dro_experiment.py
python scripts/analyze_dro_experiment.py
python scripts/run_dro_experiment.py --cost-bps 5 --suffix _5bp
python scripts/analyze_dro_experiment.py --suffix _5bp
python scripts/run_dro_experiment.py --cost-bps 20 --suffix _20bp
python scripts/analyze_dro_experiment.py --suffix _20bp
python scripts/run_dro_experiment.py --cost-bps 50 --suffix _50bp
python scripts/analyze_dro_experiment.py --suffix _50bp
python scripts/report_final.py
pytest -q
ruff check .
```

All data snapshots and result tables are gitignored. The code, frozen protocol, ledger, and aggregate report are committed.

---

## 11. Final decision

**Close the confirmatory phase as a clean negative result for H1/H3.** Report H2 as passed. Do not deploy. Do not claim alpha. Do not add features or capacity to force a positive result.

The flagship value is the apparatus: a PIT-tested ETF snapshot, a frozen protocol, a mandatory baseline, an information audit, a target-shuffling falsification test, a counter-metric gate, an experiment ledger, and an honest negative finding.

**No live deployment. No investment advice.**

---

## 12. Postscript — v2/v3 attempts (2026-11-02)

Two separate pre-registrations tested stronger models on a new 2025–2026 snapshot.

- **v2 — conformalized quantile LightGBM:** development coverage 0.899/0.859, but sigma passed only 65.4% of date-level information tests (< 80%). Holdout untouched.
- **v3 — conditional tail-risk forecast:** well calibrated (mean sigma 4.29% vs realized 4.30%; decile spread 3.76 pp) but passed only 43.0% of date-level information tests and underperformed trailing volatility on development (Sharpe 0.783 vs 0.840). Holdout untouched.

See `docs/15_v2_report.md`, `docs/17_v3_report.md`, and `DEC-20261102-010/012`. This does not change the v1 conclusion. It reinforces it: calibration and average spread are not enough; stable conditional information is the binding constraint.

### Gate power postscript

A follow-up simulation tested the **gate**, not the models. At 72 assets and 179 dates, the 80% date-level MI gate had **zero power** even at a 20% \(R^2\) signal; a pooled, date-blocked test detected the same signal in 100% of seeds. The actual v1 features and v2/v3 sigma also pass the pooled test on development data.

That does **not** promote v1/v2/v3: the pooled test is not a stability test, and its p-values sit at the 30-permutation floor. A block-aware null cuts the 20/21 pooled passes to 3/21; the v2/v3 sigma do not survive. The correct reading is that the stops were evidence of **instability**, not proof that no signal exists. The 2025–2026 holdout remains untouched. See `docs/18_gate_power_study.md` and `DEC-20261102-014/015`.
