# Documentation Register — Epistemic-Aware DRO

**Last reviewed:** 2026-10-28
**Owner:** Ken Ira Talingting
**Risk class:** Medium (research prototype; no live capital — see `00_project_charter.md` §12 and `05_risk_register.md`)

This is the entry point for the project's documentation. If a document is not listed here, it is not part of the operating record.

| File | Purpose | Gate | Status |
|---|---|---|---|
| `00_project_charter.md` | Decision, scope, success criteria, kill criteria | G0 | **Draft — G0 passing (reviewer TBD)** |
| `01_data_card.md` | Source, schema, PIT rules, leakage audit | G1 | **BLOCKED — source decision due 2026-10-31** |
| `02_experiment_card.md` | Pre-registered protocol | G3 | **DRAFT — not frozen** |
| `03_model_card.md` | Intended use, limits, monitoring | G4 | **Template — pre-fit** |
| `04_decision_log.md` | Append-only decision + deviation log | all | **Live** |
| `05_risk_register.md` | Pre-mortem, risks, ruin scenarios | G0/G4 | **Draft** |
| `06_literature.md` | Method references and open questions | — | **Working list** |
| `07_domain_overlay.md` | Finance-specific invariants and enforcement | G0 | **Written — see file** |
| `08_monitoring_plan.md` | Research re-run, calibration, cost tracking | G4 | **Written — see file** |
| `09_deployment_runbook.md` | N/A per DEC-20261027-005; documents what deployment would require | — | **Written (N/A placeholder)** |
| `10_postmortem_template.md` | Incident/postmortem format | post-G5 | **Written (template)** |
| `11_lessons_log.md` | Per-project lessons | close | **Written (empty)** |
| `../README.md` | Public project overview | — | **Live** |
| `../data/README.md` | Data access, schema, licensing | G1 | **Live** |
| `../configs/base.yaml` | Runtime configuration (TBDs are G1 blockers) | G1/G3 | **Provisional** |

## Consistency rules (do not break at freeze)

These rules exist because the same fact appears in multiple docs. When a rule is broken, one doc contradicts another and a reader cannot tell which is authoritative.

- **Target wording** identical in `00`, `01`, `02`, `03`: "next-month cross-sectional excess-return rank (or winsorized return)".
- **Prediction / outcome window** identical: month-end decision, one-month outcome.
- **Split plan** stated in `02` §5 (canonical): walk-forward, 60-month min train, 12-month validation, 12-month test, 1-month purge, 1-month embargo, final 12-month holdout touched once. `01` carries the PIT rules the split must honor, not the split itself.
- **Primary metric** identical: net Sharpe, monthly, annualized, 10 bps one-way, explicit risk-free series.
- **Guardrails** identical: max drawdown, CVaR95, turnover, max weight 5%, no leverage, no short.
- **Risk class** identical: Medium. (Would be High if deployed — see `05` §3.)
- **Cost model** identical: 10 bps primary; 5/20/50 bps sensitivity.
- **Data status** identical: BLOCKED, decision due 2026-10-31.
- **Year** consistent throughout: 2026.

## How to change a document

Silent edits are the failure mode this register is designed to prevent. If you change a frozen doc after Oct 31:

1. Log the change in `04_decision_log.md` under "Deviation log" with the date, the file, the reason, and your approval.
2. Update this register if a status changed.
3. Re-commit with a message that names the doc: `docs(charter): update kill criteria`.

Before Oct 31, edits are free — the freeze is what creates the obligation.

## What "frozen" means

Docs are frozen when this register's status column shows "Frozen" for the seven core docs (00–06) and the five new docs (07–11). The tag `docs-freeze-v1` marks that commit.

Frozen does **not** mean the gates passed. G1 is still blocked on the 2026-10-31 data decision; G3 is draft-until-frozen-before-confirmatory-run; G4 is N/A by DEC-20261027-005. Frozen docs + open gates is the honest state entering November.
