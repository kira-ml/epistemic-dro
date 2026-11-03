# LinkedIn post drafts

## Version 0 — flagship (use this first)

I build pre-registered research pipelines for ML-driven portfolio construction.

This one ended with three negative results — and I’m publishing it because the process is the point.

**v1 — epistemic uncertainty (reduced M1).** Ridge mean + bootstrap sigma. A Ridge baseline had no detectable out-of-sample linear signal (−0.019 pooled R²; mean rank IC 0.013, t = 0.56). The uncertainty-aware DRO did not separate from point-estimate DRO. The tail-risk hypothesis failed; the non-inferiority test passed.

**v2 — conformal quantiles.** Calibration worked: 89.9% validation coverage, 85.9% test coverage. The uncertainty signal still passed only 65.4% of date-level information tests against an 80% gate. Stopped before the holdout.

**v3 — conditional tail risk.** Calibration was excellent: mean sigma 4.29% vs realized 4.30%, with a 3.76 pp top-vs-bottom decile spread. The signal passed only 43.0% of date-level information tests. Stopped before the holdout.

The result is not a Sharpe ratio. It is a pipeline that can tell the difference between a signal and noise — and a 2025–2026 holdout that is still untouched.

Stack: purged walk-forward · Ridge baseline · LightGBM quantile regression · split conformal · cvxpy/CLARABEL · DRO/CVaR · CI + verifier.

Paper + code: https://github.com/kira-ml/epistemic-dro/releases/tag/v1.0.0

If you work on uncertainty quantification, DRO, or conformal prediction, I’d like to compare notes.

Not investment advice. No alpha claim. No live deployment.

#QuantResearch #MachineLearning #PortfolioOptimization #ResearchIntegrity #PreRegistration

> **Do not post until:** the `v1.0.0` GitHub release exists, CI is green, and the release link resolves.

---

## Version A — carousel caption (previous draft)

I tried to make uncertainty pay three times. The holdout is still untouched.

**v1 — epistemic uncertainty.** A Ridge baseline had no detectable out-of-sample linear signal (−0.019 pooled R²; mean rank IC 0.013, t = 0.56). The uncertainty-aware DRO did not separate from point-estimate DRO. H1 and H3 failed; H2 passed.

**v2 — conformal quantiles.** Calibration worked: 89.9% validation coverage, 85.9% test coverage. The uncertainty signal still passed only 65.4% of date-level information tests against an 80% gate. Stopped before the holdout.

**v3 — conditional tail risk.** Calibration was excellent: mean sigma 4.29% vs realized 4.30%, with a 3.76 pp top-vs-bottom decile spread. The signal passed only 43.0% of date-level information tests. Stopped before the holdout.

The lesson: **calibration is not information.** A model can look well calibrated, show a clean decile spread, and still fail a stability gate. The apparatus — frozen protocol, mandatory baseline, information gate, preserved holdout — is the result.

Paper: [link in comments]
Code: github.com/kira-ml/epistemic-dro

Not investment advice. No alpha claim. No live deployment.

#QuantResearch #MachineLearning #PortfolioOptimization #ResearchIntegrity #PreRegistration

---

## Version B — short image-post caption

Three pre-registered attempts. Zero holdout touches.

v1: epistemic uncertainty — H1/H3 failed, H2 passed.
v2: conformal quantiles — calibrated, stopped before holdout (gate 65.4%).
v3: conditional tail risk — calibrated, stopped before holdout (gate 43.0%).

Calibration is not information. Gates > narratives.

Paper + code: github.com/kira-ml/epistemic-dro
Not investment advice.

#QuantResearch #MachineLearning #PortfolioOptimization

---

## Version C — discussion prompt (optional, use sparingly)

The most useful result in my last project was a “no.”

I ran three pre-registered tests of uncertainty-aware DRO on 72 US ETFs. All three failed their pre-holdout information gate. The 2025–2026 holdout was never touched.

The part I keep thinking about: v2 and v3 were both *calibrated*. v3 had a clean 3.76 pp decile spread. That still was not enough to justify spending the holdout.

For people who run research gates: what is the smallest pre-holdout test you trust? Coverage? MI stability? A paired interval? Something else?

Paper + code in the comments. Not investment advice.

---

## Notes

- Put the paper link in the first comment, not the post body, if reach matters.
- Do not say “the model works” or “beats the market.” It does not.
- Do not call v2/v3 “confirmatory.” They never reached the holdout.
- If you post the card alone, use Version B. If you post the carousel, use Version A.
