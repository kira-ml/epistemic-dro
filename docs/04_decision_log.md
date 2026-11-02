# Decision Log — Epistemic-Aware DRO

Append-only. Each entry records the decision, the alternatives, the rationale, reversibility, and the review date.

---

## DEC-20261027-001 — Project selected

**Decision:** Build an epistemic-aware distributionally robust mean-CVaR portfolio as the November flagship.

**Alternatives considered:** Causal discovery for spurious correlations; regime-conditional HRP; GNN supply-chain contagion; deep RL execution; the DRO mean-CVaR project.

**Rationale:** The DRO project directly demonstrates the error-maximization problem, uses the user's ML background, and maps to the project's reasoning models (see `docs/07_domain_overlay.md` and the local operating manual). It is differentiated from `robustfolio` by the epistemic-uncertainty layer and CVaR objective.

**Reversibility:** High. The repository can be narrowed to a methods study or pivoted to ETFs if data access fails.

**Review:** 2026-11-01.

---

## DEC-20261027-002 — Scope v1

**Decision:** Use monthly US equities, 150–200 names, 2005–2024, walk-forward evaluation, 10 bps one-way costs, and a box DRO with CVaR.

**Alternatives considered:** Intraday data; deep ensembles; Wasserstein DRO; deep RL execution; 500+ names.

**Rationale:** A 4-week build needs a tractable, debuggable core. Deep ensembles and Wasserstein DRO are stretch goals, not baseline requirements. The core claim can be tested with a simpler uncertainty proxy and a convex box ambiguity set.

**Reversibility:** Medium. The universe and optimizer can be extended after the v1 result.

**Review:** 2026-11-07.

---

## DEC-20261027-003 — Data source blocked

**Decision:** Do not start modelling until a survivorship-bias-aware source is selected. Deadline: 2026-10-31.

**Alternatives:** Start with Yahoo/current constituents; use ETFs; use synthetic data.

**Rationale:** A stock-level flagship that uses current constituents or free prices would contain survivorship and look-ahead bias. Synthetic data can test code but cannot support empirical claims. If no PIT stock data are available, pivot to an ETF/factor universe and label the project as a methods study.

**Reversibility:** High (pivot), but the claim changes.

**Review:** 2026-10-31.

---

## DEC-20261027-004 — Primary metric and guardrails

**Decision:** Primary metric: net Sharpe after 10 bps one-way costs. Guardrails: max drawdown, CVaR95, turnover, max weight, leverage, short exposure.

**Alternatives:** Max drawdown as primary; CVaR as primary; a composite score.

**Rationale:** Net Sharpe is a standard, decision-relevant metric and avoids the circularity of evaluating a CVaR-optimized portfolio primarily on CVaR. Tail metrics remain guardrails because the project's thesis is tail-risk control. A composite score would hide trade-offs.

**Reversibility:** Low after the protocol is frozen. Change only with a logged deviation.

**Review:** 2026-11-07.

---

## DEC-20261027-005 — No live deployment

**Decision:** The project is a research prototype. No live capital, no execution, no deployment claims.

**Rationale:** A 4-week backtest cannot establish operational readiness. The project risk class is medium for research; it would be high if deployed (see `docs/05_risk_register.md` §3). Keeping the scope research-only prevents claim inflation.

**Reversibility:** Not applicable within this project.

**Review:** 2026-11-30.

---

## DEC-20261027-006 — Repository setup

**Decision:** Create `D:\quant-finance-ml\epistemic-dro` as a standalone repo with G0/G1 artefacts, a package skeleton, tests, and a synthetic-data smoke test.

**Rationale:** The repository is the apparatus. Starting with the charter, data card, experiment card, and leakage checks prevents the common failure mode of building a model before defining the decision and the data.

**Reversibility:** High.

**Review:** 2026-10-31.

---

## DEC-20261102-001 — ETF/factor pivot (kill criterion 1 executed)

**Decision:** Pivot v1 from 150–200 US stocks to 50–100 liquid US-listed ETFs, supported by Fama-French factors, FRED risk-free data, and public total-return ETF prices. Reclassify the project as a **methods study**.

**Alternatives considered:** Delay the project and wait for WRDS/Sharadar/Norgate access; proceed with free stock prices and current constituents; run a synthetic-only methods paper.

**Rationale:** No point-in-time stock-level source was secured by the 2026-10-31 deadline. Free stock prices with current constituents would manufacture survivorship and look-ahead bias, and synthetic data cannot support an empirical claim. The ETF pivot preserves the core question (does epistemic uncertainty improve a DRO mean-CVaR trade-off?) while narrowing the claim to what the data can support. Public ETF data may omit closed funds, so the project also gives up any survivorship-free claim.

**Reversibility:** Medium. The code path is reusable, but restoring a stock universe requires a new data card and a new pre-registration.

**Review:** 2026-11-07.

---

## DEC-20261102-002 — MIT license

**Decision:** License the code under the MIT License and add a `LICENSE` file; license stays separate from third-party data terms.

**Alternatives considered:** Apache-2.0; keep the license TBD.

**Rationale:** MIT is permissive, short, and standard for research code. Keeping TBD left the repository legally "all rights reserved" and contradicted the public README. MIT does not grant rights to data the project does not own.

**Reversibility:** Medium. A future license change applies prospectively; already-published copies remain under MIT.

**Review:** 2026-11-30.

---

## DEC-20261102-003 — Documentation freeze v1.0

**Decision:** Freeze the documentation set (`docs/00`–`docs/11`, the register, the root README, `data/README.md`, and `configs/base.yaml`) as protocol `v1.0-etf` and tag the commit `docs-freeze-v1`.

**Alternatives considered:** Keep the docs draft until G1 passes; freeze only `02_experiment_card.md`.

**Rationale:** The protocol must be fixed before any confirmatory run, and the ETF pivot changes the universe, features, and data card. Freezing the full set makes later changes auditable through the deviation log. The freeze is explicitly **not** a claim that G1–G4 passed; the data gate is still open.

**Reversibility:** Low for the pre-registered metric, splits, constraints, and cost model. Any change requires a dated deviation entry.

**Review:** 2026-11-30.

---

## DEC-20261102-004 — Adopt the 12-model research rigor layer (v1.1)

**Decision:** Adopt the 12 Foundational Mental Models as a binding research-rigor addendum (`docs/12_research_rigor.md`, `v1.1-rigor`). Add the axiomatic spec, data dictionary, pre-mortem, causal classification, mandatory Ridge B0 baseline, target-shuffling harness, MI screening rule, conditional robust loss, counter-metric gate, experiment ledger, Bayesian-optimization rule, and profiling gate.

**Alternatives considered:** Keep the v1.0 protocol as-is and treat the mental models as advisory; adopt only the leakage and baseline rules; postpone the rigor layer until after the first model run.

**Rationale:** The v1.0 docs already had strong PIT and walk-forward safeguards, but they lacked four things a flagship project needs: (1) an explicit noise-floor argument before model code, (2) a mandatory simple baseline, (3) a target-shuffling falsification test, and (4) a counter-metric gate that prevents a single Sharpe number from being gamed. Adding these before the first data run is cheaper and more credible than retrofitting them after seeing results. The addendum does **not** change the primary metric, split plan, constraints, cost model, universe, or claim scope.

**Reversibility:** Low for the gates. Any weakening requires a dated deviation entry and a new protocol version.

**Review:** 2026-11-07.

---

## DEC-20261102-005 — G1 snapshot, B0 null result, and robust loss

**Decision:** Accept the 2026-11-02 ETF snapshot; establish the mandatory Ridge B0 baseline; set the LightGBM objective to `huber` because the loss-tail Pareto index is below 4.0; continue the project only as a risk-management/uncertainty test, not as an alpha claim.

**Evidence:**
- Snapshot: 72/72 ETFs, 19,712 price rows, 19,640 return rows, 2000-01-03 .. 2024-12-31, 68+ eligible ETFs in every 2010+ month; FRED `TB3MS` used (252/252 months).
- Ridge B0 walk-forward: pooled OOS \(R^2\) = −0.0186; mean rank IC = 0.0128 (t = 0.56); 14 folds; 11,328 OOS rows.
- Shuffled-target Ridge B0: mean rank IC = −0.0040 (t = −0.48). The null is not an obvious leak.
- Target tails: excess kurtosis 3.804; Hill loss-tail \(\alpha\) = 3.08; the G-R7 rule requires a robust objective.
- Cross-sectional target variance: mean 0.001381; median 0.001009.

**Interpretation:** the linear predictive signal is statistically indistinguishable from zero. The ML layer cannot be assumed to add value. The remaining testable claim is whether epistemic uncertainty improves tail risk even with a weak mean forecast. If it does not, that is a clean negative result.

**Alternatives considered:** stop the project now; add features until a signal appears; keep the squared-error objective; claim the ML layer is useful without evidence.

**Rejected:** adding features or capacity to force a signal; keeping MSE when \(\alpha < 4\); claiming alpha from a null linear baseline.

**Reversibility:** Low for the claim. A new feature set requires a new data dictionary, a new G-R1 estimate, and a new pre-registration.

**Review:** 2026-11-07.

---

## DEC-20261102-006 — G-R4 null; reduced uncertainty proxy replaces LightGBM

**Decision:** Record the G-R4 information audit as a null result and do **not** fit LightGBM on the frozen feature set. Run a reduced uncertainty-aware DRO experiment using the Ridge B0 mean plus a 5-model bootstrap ensemble standard deviation as an explicitly labelled epistemic-uncertainty proxy.

**Evidence:** date-blocked MI audit (30 permutations, BH-FDR q < 0.05, 248 dates with ≥20 ETFs). No feature passed the 80% date-level survival rule. Mean MI ranged from 0.179 to 0.257 for the market/factor features and 0.017 for dollar volume; pass rates ranged from 0.023 to 0.552. Conditional MI was not evaluated because there were no marginal survivors. This is consistent with the Ridge B0 null (OOS \(R^2\) = −0.0186; mean IC = 0.0128, t = 0.56).

**Interpretation:** the frozen feature set does not provide a stable, detectable cross-sectional signal. Fitting a high-capacity model would be complexity without evidence. The original M1 (LightGBM ensemble) is not justified.

**Reduced experiment:** use Ridge B0 as the mean forecast and a 5-model bootstrap Ridge ensemble standard deviation as `sigma`. Label it **reduced M1** in every table. Compare reduced M1 vs B5 (DRO-point), B3 (CVaR-only), and B1 (1/N). The uncertainty proxy is epistemic in the weak sense of model-resampling dispersion; it is not a conformal guarantee and not the original LightGBM ensemble.

**Alternatives considered:** fit LightGBM anyway; relax the 80% rule after seeing the result; stop the project; use realized volatility as `sigma`.

**Rejected:** fitting LightGBM without G-R4 evidence; relaxing a pre-registered gate post hoc; presenting realized volatility as epistemic uncertainty.

**Reversibility:** Medium. A new feature set requires a new G-R4 audit and a new pre-registration.

**Review:** 2026-11-07.

---

## DEC-20261102-007 — Reduced DRO result: H1/H3 fail, H2 passes

**Decision:** Record the reduced uncertainty-aware DRO experiment as a **negative result for the epistemic-uncertainty mechanism**. Do not fit LightGBM, add features, or tune the protocol to force H1/H3. Report the DRO/CVaR-vs-1/N result as a secondary finding and close the confirmatory phase honestly.

**Evidence (2010-01 .. 2024-11; 179 months; net 10 bps):**

| Strategy | Net Sharpe | Max drawdown | CVaR95 | Ann. turnover |
|---|---:|---:|---:|---:|
| M1_reduced | 0.816 | −24.18% | −8.31% | 1.90 |
| B5_DRO_point | 0.798 | −24.28% | −8.44% | 1.82 |
| B3_CVaR | 0.798 | −24.28% | −8.44% | 1.82 |
| B1_equal_weight | 0.673 | −26.61% | −9.76% | 0.11 |

- H1: relative MDD improvement 0.4%; 90% CI [−6.2%, +1.1%]; CVaR diff CI [−0.0001, +0.0031] includes zero → **FAIL**.
- H2: M1 − B5 Sharpe +0.018; 90% CI [−0.000, +0.037] → **PASS** (within the 0.20 margin).
- H3: M1 vs B5 MDD CI [−0.0024, +0.0160]; CVaR CI includes zero → **FAIL**.
- Secondary: M1 beats 1/N on Sharpe (+0.143, CI [+0.020, +0.266]), MDD (+0.060, CI [+0.0016, +0.137]), and CVaR (+0.0146, CI [+0.0043, +0.026]). The optimizer structure helps; the uncertainty layer does not separate.

**Interpretation:** the DRO/CVaR machinery is associated with better risk-adjusted performance than naive diversification, but the epistemic-uncertainty layer adds no detectable tail-risk separation in this reduced test. B5 and B3 collapse to the same portfolio because sigma is zero. The mean forecast is weak (B0 OOS \(R^2\) −0.019).

**Alternatives considered:** add features until H1 passes; tune `kappa`/`cvar_penalty` on the test period; swap to a stock universe; claim the 1/N comparison as success for the uncertainty hypothesis; stop without reporting.

**Rejected:** post-hoc tuning; claiming H1/H3; presenting the reduced M1 as the original LightGBM M1; hiding the null.

**Reversibility:** Low for the claim. A new feature set or model requires a new G-R4 audit and a new pre-registration.

**Review:** 2026-11-30.

---

## DEC-20261102-008 — Final report and project close

**Decision:** Accept the final report (`docs/13_final_report.md`), close the confirmatory phase as a clean negative result for H1/H3, and stop modelling. Do not deploy, do not claim alpha, and do not add features or capacity to force a positive result.

**Final evidence:**
- H1 FAIL: 0.4% relative MDD improvement, 90% CI [−6.2%, +1.1%]; CVaR95 difference CI includes zero.
- H2 PASS: +0.018 Sharpe vs B5, 90% CI [−0.000, +0.037], within the 0.20 margin.
- H3 FAIL: uncertainty ablation does not separate from point-DRO.
- Secondary: M1 beats 1/N on Sharpe (+0.143), MDD (+0.060), and CVaR (+0.0146); the optimizer structure helps, not the uncertainty layer.
- Cost sensitivity 5/20/50 bps preserves the ordering; 50 bps M1 0.785, B5 0.771, B1 0.671.
- Stress windows: 2020 M1 0.681 vs B5 0.634; 2022 both negative (−0.508 vs −0.488); differences are small and inconsistent.
- Deflated Sharpe (strategy-level, 4 trials): M1 0.996, B5 0.995, B1 0.986. This does **not** test M1 vs B5; the incremental test fails.

**Alternatives considered:** extend the project with a new feature set; fit LightGBM despite the G-R4 null; tune kappa/CVaR on the test period; present the 1/N comparison as success for the uncertainty hypothesis.

**Rejected:** post-hoc tuning; claiming H1/H3; presenting the reduced M1 as the original LightGBM M1; hiding the null; deploying.

**Reversibility:** Closed for this protocol. A new feature set or uncertainty model requires a new data card, a new G-R4 audit, and a new pre-registration.

**Review:** 2026-11-30.

---

## DEC-20261102-010 — v2 stopped before holdout (G-R4v2 failure)

**Decision:** Stop v2 before touching the 2025-2026 holdout. The conformalized quantile uncertainty failed the pre-registered G-R4v2 information gate: sigma pass rate **0.654** (threshold 0.80, 179 dates, 30 permutations, BH-FDR). Do not relax the gate, do not run the holdout, and do not add features to force a signal.

**Context:** v2 was a new pre-registration (`docs/14_v2_preregistration.md`, `v2.0-holdout`) with a 19-feature set, LightGBM quantile regression (q05/q50/q95, 3 seeds), split-conformal calibration, and a non-degenerate comparator (`B5_uncond_sigma`, trailing 36-month realized volatility). Development only: 2010-01..2024-11.

**Development evidence:**
- M1_v2: Sharpe 0.812, MDD −22.29%, CVaR −8.16%, turnover 3.47, mean sigma 5.27%.
- B5_uncond_sigma: Sharpe 0.813, MDD −22.96%, CVaR −8.19%, turnover 2.57, mean sigma 5.66%.
- B3: Sharpe 0.743, MDD −24.30%, CVaR −8.66%.
- B1: Sharpe 0.673, MDD −26.61%, CVaR −9.76%.
- Conformal coverage: 0.899 validation, 0.859 development test.
- G-R4v2: sigma and interval width both pass rate 0.654; not stable enough.

**Interpretation:** the model is calibrated but its uncertainty is not a stable conditional tail signal. The dev tail improvement over trailing volatility is tiny and comes with worse Sharpe and higher turnover. Touching the holdout would consume it without a credible gate.

**Alternatives considered:** relax the 80% rule to 60%; run the holdout anyway; add features; use a different sigma mapping.

**Rejected:** post-hoc gate relaxation; consuming the holdout on a failed pre-holdout gate; adding capacity.

**Reversibility:** Closed for v2. A v3 requires a new pre-registration, a new uncertainty model, and an untouched holdout.

**Review:** 2026-11-30.

---

## DEC-20261102-011 — v3 pre-registration (conditional tail-risk forecast)

**Decision:** Open v3 as a **separate, narrower hypothesis**: a conditional forecast of next-month absolute excess return (realized-volatility proxy) used as DRO sigma, compared against trailing 36-month realized volatility on the preserved 2025–2026 holdout. This is **not** an epistemic-uncertainty test; label it accordingly.

**Rationale:** v1 and v2 failed because the epistemic uncertainty signal was not stable. Volatility is persistent and forecastable, so it is the most plausible remaining signal. The holdout was untouched by v2 and is reused only after a new pre-holdout gate passes.

**Protocol:** `docs/16_v3_preregistration.md`, `configs/v3.yaml`, tag `docs-freeze-v3`.

**Review:** 2026-11-30.

---

## DEC-20261102-012 — v3 stopped before holdout (G-R4v3 failure)

**Decision:** Stop v3 before touching the 2025–2026 holdout. The conditional tail forecast failed the pre-registered G-R4v3 information gate: sigma pass rate **0.430** (threshold 0.80, 179 dates, 30 permutations, BH-FDR). Do not relax the gate, do not run the holdout, and do not add features.

**Development evidence:**
- M1_v3: Sharpe 0.783, MDD −25.87%, CVaR −8.44%, turnover 3.16.
- B5_uncond_sigma: Sharpe 0.840, MDD −24.76%, CVaR −8.18%, turnover 1.26.
- B3: Sharpe 0.808, MDD −24.68%, CVaR −8.40%.
- B1: Sharpe 0.673, MDD −26.61%, CVaR −9.76%.
- Calibration: mean sigma 4.29% vs realized 4.30%; correlation 0.284; decile spread 3.76 pp.
- G-R4v3: mean MI 0.121 vs null 0.088; pass rate 0.430; fails.

**Interpretation:** calibration and cross-sectional spread are not enough; the per-date conditional information is not stable. The conditional forecast also underperforms trailing volatility on development. The holdout is preserved.

**Alternatives considered:** relax the 80% rule; run the holdout anyway; add features; use a pooled MI gate.

**Rejected:** post-hoc gate relaxation; consuming the last untouched holdout on a failed gate; another feature search.

**Reversibility:** Closed for v3. A v4 requires a new pre-registration, a stable signal, and an untouched holdout.

**Review:** 2026-11-30.

---

## DEC-20261102-013 — Public-facing paper and LinkedIn package

**Decision:** Publish a layered public package: a 6-page working paper (`paper/mini_paper.pdf`), a 6-slide LinkedIn carousel (`paper/linkedin_carousel.pdf`), a 4:5 visual card (`paper/linkedin_card.png`), a one-page leave-behind (`paper/one_pager.pdf`), and a short post draft (`paper/linkedin_post.md`). The paper is the canonical artifact; the carousel is the reach layer.

**Rationale:** a text-only one-pager is a weak acquisition format on LinkedIn. A native document carousel earns dwell time, while the paper carries the technical claim. The hook is the negative result and the preserved holdout, not a performance claim.

**Guardrails:** v1 is described as a reduced M1 (Ridge + bootstrap sigma), not the original LightGBM ensemble; v2/v3 are described as stopped before the holdout; no alpha, investable, causal, or deployment claim; “not investment advice” appears on the visual and in the caption.

**Reversibility:** High. The assets are generated from committed result tables by `scripts/build_paper.py`.

**Review:** 2026-11-30.

---

## Deviation log

| Date | Experiment | Deviation | Reason | Approved by |
|---|---|---|---|---|
| 2026-11-02 | `EXP-DRO-2026-11-01` | Universe changed from 150–200 US stocks to 50–100 ETFs; stock-selection claim withdrawn; project reclassified as a methods study | G1 deadline missed; no PIT stock access (DEC-20261102-001) | Ken Ira Talingting (owner) |
| 2026-11-02 | `EXP-DRO-2026-11-01` | Post-freeze rigor addendum: B0 Ridge baseline, MI screening, conditional robust loss, Bayesian optimization, counter-metric gate, ledger, profiling | Adopt `v1.1-rigor` before the first data run; no change to primary metric, splits, constraints, costs, universe, or claim scope (DEC-20261102-004) | Ken Ira Talingting (owner) |
| 2026-11-02 | `EXP-DRO-2026-11-01` | Snapshot built; B0 null recorded; LightGBM objective changed to `huber`; config hash updated | G1 diagnostics and G-R7 tail rule (DEC-20261102-005); no change to primary metric, splits, constraints, costs, universe, or claim scope | Ken Ira Talingting (owner) |
| 2026-11-02 | `EXP-DRO-2026-11-01` | G-R4 null; LightGBM not fitted; reduced M1 uses Ridge B0 + bootstrap ensemble `sigma` | No feature passed the 80% information rule; complexity is not justified (DEC-20261102-006). Primary metric, splits, constraints, costs, and universe unchanged | Ken Ira Talingting (owner) |
| 2026-11-02 | `EXP-DRO-2026-11-01` | Reduced DRO experiment run; H1/H3 fail, H2 passes; negative result recorded | Pre-registered reduced test completed (DEC-20261102-007). No post-hoc tuning; no capacity added | Ken Ira Talingting (owner) |
| 2026-11-02 | `EXP-DRO-2026-11-01` | Final report added (`docs/13_final_report.md`); cost sensitivity, stress windows, deflated Sharpe recorded; project closed | Complete the reporting obligations without changing the protocol or claim (DEC-20261102-008) | Ken Ira Talingting (owner) |
