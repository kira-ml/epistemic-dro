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

## Deviation log

| Date | Experiment | Deviation | Reason | Approved by |
|---|---|---|---|---|
| — | — | — | — | — |
