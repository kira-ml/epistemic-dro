# Deployment Runbook — Epistemic-Aware DRO

**Status:** N/A — research prototype, no deployment
**Authority:** `04_decision_log.md` DEC-20261027-005 ("No live deployment")
**Last updated:** 2026-10-28

This project does not deploy a model. There is no live trading, no execution, no capital allocation, and no user-facing decision. This file exists so that the absence is documented rather than forgotten, and so that any future pivot to deployment has a starting checklist.

## 1. If the scope ever changes

The following would be required **before any deployment** (mapped to `AGENTS.md` §8.1 and §9.1). None of these are met today.

- [ ] G4 readiness checklist from `AGENTS.md` §8.1 complete.
- [ ] Risk class re-classified from **Medium** (research) to **High** (live capital) per `AGENTS.md` §9.1; new safeguards required.
- [ ] Independent validation on data the model has never seen.
- [ ] Execution model (slippage, market impact) beyond the linear 10 bps assumption.
- [ ] Model registry and versioned artifact.
- [ ] Shadow mode with logged predictions compared against outcomes.
- [ ] Canary rollout with a hard capital cap.
- [ ] Feature-flag kill switch, tested.
- [ ] Monitoring dashboard live (see `08_monitoring_plan.md`, extended for production).
- [ ] Rollback plan tested end-to-end.
- [ ] Incident owner and escalation path assigned.
- [ ] Legal / compliance review (investment advice, fiduciary, licensing).
- [ ] Human-in-the-loop or abstention design for low-confidence cases.

## 2. Why this file exists

`AGENTS.md` §8.7 expects a deployment runbook. This project has none because it has no deployment. A placeholder that says so is more honest than a runbook for a system that does not exist, and it prevents a future reader from assuming deployment readiness.
