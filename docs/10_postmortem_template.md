# Postmortem Template — Epistemic-Aware DRO

**Use when:** a material failure occurs — a leakage that reached a reported result, a data-quality incident that invalidated a run, a solver failure that silently replaced weights, or a claim that was retracted. For a research project, "material" includes a result that must be withdrawn.

**Do not use** for a clean negative result. A negative result is a finding, not an incident.

---

## Incident

**ID:** `PM-YYYYMMDD-NNN`
**Date / duration:**
**Detected by:**
**Severity:** informational | material | invalidating

## Timeline

| Time | Event |
|---|---|
| T0 | |
| T1 | |
| ... | |

## Impact

- **What was reported or acted on?**
- **What was wrong?**
- **Who saw it?** (in a research project: which documents cite it)

## Root cause

- **Direct cause:**
- **Contributing factors:**
- **Why the existing checks missed it:** (leakage test? calibration check? review?)

## What worked

## What failed

## Corrective actions

| Action | Owner | Due | Verification |
|---|---|---|---|
| | | | |

## Documentation and test changes

- [ ] New regression test added (path)
- [ ] `01_data_card.md` or `02_experiment_card.md` updated
- [ ] `04_decision_log.md` deviation entry added
- [ ] `05_risk_register.md` new risk added
- [ ] `08_monitoring_plan.md` new signal added
- [ ] `11_lessons_log.md` row added
- [ ] Any reported number corrected in `README.md`, `03_model_card.md`, or results tables

## Lessons

One or two sentences. Link to the lessons log entry.
