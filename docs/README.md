# Documentation Register — Epistemic-Aware DRO

**Last reviewed:** 2026-11-02<br>
**Owner:** Ken Ira Talingting<br>
**Risk class:** Medium (research prototype; no live capital — see `00_project_charter.md` §12 and `05_risk_register.md`)<br>
**Frozen protocol:** `v1.0-etf` (tag `docs-freeze-v1`) + `v1.1-rigor` (tag `docs-freeze-v1.1`)

This is the entry point for the project's documentation. If a document is not listed here, it is not part of the operating record.

| File | Purpose | Gate | Status |
|---|---|---|---|
| `00_project_charter.md` | Decision, scope, success criteria, kill criteria | G0 | **Frozen — G0 passed; G1 pivoted to ETF** |
| `01_data_card.md` | Source, schema, PIT rules, leakage audit | G1 | **Frozen — snapshot built; G1 pass with limitation; G-R4 pending** |
| `02_experiment_card.md` | Pre-registered protocol | G3 | **Frozen — v1.1-rigor (2026-11-02)** |
| `03_model_card.md` | Intended use, limits, monitoring | G4 | **Frozen template — reduced experiment completed** |
| `04_decision_log.md` | Append-only decision + deviation log | all | **Frozen — append-only** |
| `05_risk_register.md` | Pre-mortem, risks, ruin scenarios | G0/G4 | **Frozen** |
| `06_literature.md` | Method references and open questions | — | **Frozen working list** |
| `07_domain_overlay.md` | Finance-specific invariants and enforcement | G0 | **Frozen** |
| `08_monitoring_plan.md` | Research re-run, calibration, cost tracking | G4 | **Frozen** |
| `09_deployment_runbook.md` | N/A per DEC-20261027-005; documents what deployment would require | — | **Frozen (N/A placeholder)** |
| `10_postmortem_template.md` | Incident/postmortem format | post-G5 | **Frozen (template)** |
| `11_lessons_log.md` | Per-project lessons | close | **Frozen — append-only** |
| `12_research_rigor.md` | 12-model binding addendum, gates, protocol amendments | all | **Active — v1.1-rigor** |
| `13_final_report.md` | Final decision memo: H1/H3 fail, H2 pass; limitations; close | close | **Final — negative result** |
| `14_v2_preregistration.md` | v2 conformal-quantile pre-registration; new holdout | v2 | **Frozen — holdout untouched; G-R4v2 failed** |
| `15_v2_report.md` | v2 development result and pre-holdout stop | v2 | **Final — stopped before holdout** |
| `16_v3_preregistration.md` | v3 conditional tail-risk pre-registration | v3 | **Frozen — holdout untouched; G-R4v3 failed** |
| `17_v3_report.md` | v3 development result and pre-holdout stop | v3 | **Final — stopped before holdout** |
| `axiomatic_spec.md` | First-principles spec, data-generating mechanism, Bayes-risk/noise floor | G-R1 | **Active — estimate pending G1** |
| `data_dictionary.md` | Schema, units, lineage, MI/CMI audit | G-R4 | **Active — MI audit pending G1** |
| `pre_mortem.md` | Inversion failure vectors and kill criteria | G-R2 | **Active** |
| `causal_dag.json` | Rung-1 classification; no intervention claim | G-R5 | **Active** |
| `../experiments/README.md` | Ledger schema and baseline law | G-R6/G-R11 | **Active** |
| `../experiments/baseline_benchmarks.md` | B0/B1–B5/M1–M2 baseline record | G-R6 | **Active — B0 null recorded** |
| `../experiments/dro_experiment.md` | Reduced DRO result and H1–H3 verdict | G-R10 | **Active — negative result** |
| `../experiments/ledger.jsonl` | Append-only experiment log | all | **Active — empty** |
| `../scripts/profile_pipeline.py` | Bottleneck profiling | G-R12 | **Active** |
| `../README.md` | Public project overview | — | **Frozen** |
| `../paper/README.md` | Public paper, carousel, card, one-pager | — | **Final — public package** |
| `../data/README.md` | Data access, schema, licensing | G1 | **Frozen — ETF pivot** |
| `../configs/base.yaml` | Runtime configuration (frozen protocol values) | G1/G3 | **Frozen v1.1-rigor** |
| `../LICENSE` | Code license | — | **MIT** |

## Consistency rules (do not break at freeze)

These rules exist because the same fact appears in multiple docs. When a rule is broken, one doc contradicts another and a reader cannot tell which is authoritative.

- **Target wording** identical in `00`, `01`, `02`, `03`: "next-month cross-sectional excess-return rank (or winsorized return)".
- **Prediction / outcome window** identical: month-end decision, one-month outcome.
- **Universe** identical: 50–100 liquid US-listed ETFs with point-in-time eligibility; ETF/factor methods study. Do not reintroduce a stock universe without a new data card and pre-registration.
- **Claim scope** identical: methods study; no stock-selection validity; no survivorship-free claim.
- **Split plan** stated in `02` §5 (canonical): walk-forward, 60-month min train, 12-month validation, 12-month test, 1-month purge, 1-month embargo, final 12-month holdout touched once. `01` carries the PIT rules the split must honor, not the split itself.
- **Primary metric** identical: net Sharpe, monthly, annualized, 10 bps one-way, explicit risk-free series.
- **Guardrails** identical: max drawdown, CVaR95, turnover, max weight 5%, no leverage, no short.
- **Risk class** identical: Medium. (Would be High if deployed — see `05` §3.)
- **Cost model** identical: 10 bps primary; 5/20/50 bps sensitivity.
- **Data status** identical: snapshot built 2026-11-02 (72 ETFs, FRED `TB3MS`); G1 pass with disclosed survivorship limitation; G-R4 MI audit pending.
- **License** identical: MIT in `../LICENSE`, `../pyproject.toml`, `03` §1, and `../README.md`.
- **Rigor gates** identical: `12_research_rigor.md` is binding. B0 Ridge baseline, target-shuffling test, MI audit, conditional robust loss, counter-metric gate, and experiment ledger are mandatory before a confirmatory claim.
- **Final verdict** identical: H1 FAIL, H2 PASS, H3 FAIL; reduced M1 (not LightGBM); no alpha claim; no deployment. See `13_final_report.md`.
- **v2 verdict** identical: G-R4v2 failed (sigma pass rate 0.654 < 0.80); 2025–2026 holdout untouched; v2 stopped. See `15_v2_report.md`.
- **v3 verdict** identical: G-R4v3 failed (sigma pass rate 0.430 < 0.80); 2025–2026 holdout untouched; v3 stopped. See `17_v3_report.md`.
- **Counter-metrics** identical: net Sharpe is never reported alone; max drawdown and CVaR95 travel with it.
- **Year** consistent throughout: 2026.

## How to change a document

Silent edits are the failure mode this register is designed to prevent. The docs were frozen on **2026-11-02**. If you change a frozen doc after that date:

1. Log the change in `04_decision_log.md` under "Deviation log" with the date, the file, the reason, and your approval.
2. Update this register if a status changed.
3. Re-commit with a message that names the doc: `docs(charter): update kill criteria`.

Before the freeze, edits were free — the freeze is what creates the obligation.

## What "frozen" means

Docs are frozen when this register's status column shows "Frozen" for the seven core docs (00–06) and the five new docs (07–11). The tag `docs-freeze-v1` marks that commit. The rigor layer (`12_research_rigor.md` and its companion artifacts) is `v1.1-rigor` and is tagged `docs-freeze-v1.1`.

Frozen does **not** mean the gates passed. G1 is pivoted but not passed (ETF snapshot and leakage audit pending); G3 is frozen-before-confirmatory-run but not run; G4 is N/A by DEC-20261027-005. Frozen docs + open gates is the honest state entering November.

The frozen protocol is `v1.1-rigor` (on top of `v1.0-etf`). Its config hash is recorded in `02_experiment_card.md` §11 and must be re-checked before any confirmatory run. A gate that is not evidenced in `experiments/ledger.jsonl` has not been passed.
