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

## Deviation log

| Date | Experiment | Deviation | Reason | Approved by |
|---|---|---|---|---|
| 2026-11-02 | `EXP-DRO-2026-11-01` | Universe changed from 150–200 US stocks to 50–100 ETFs; stock-selection claim withdrawn; project reclassified as a methods study | G1 deadline missed; no PIT stock access (DEC-20261102-001) | Ken Ira Talingting (owner) |
