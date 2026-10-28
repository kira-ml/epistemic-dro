# Domain Overlay — Finance

**Status:** Active
**Last updated:** 2026-10-28

`AGENTS.md` §9.5 requires a finance overlay for any finance project. This file is that overlay. It lists the finance-specific invariants that must hold, and points to where each is enforced. If a doc contradicts this file, this file wins.

## 1. Non-negotiable invariants

| Invariant | Enforcement | Source |
|---|---|---|
| **Point-in-time availability** — a feature at month-end `t` uses only data timestamped ≤ `t` | `src/epistemic_dro/leakage.py::assert_no_lookahead`; `tests/test_leakage.py`; `01_data_card.md` §5 | §3.1, §5.3 |
| **Fundamentals use `rdq` (report date), not `datadate`** | `01_data_card.md` §5.1; loader contract; `data/README.md` "Point-in-time rules" | §3.1 |
| **Historical universe, not current constituents** | `01_data_card.md` §2, §5.3; `data/README.md` "Options" | §3.1, §3.11 |
| **Delisting returns included in the delisting month** | `01_data_card.md` §5.4; `data/README.md` "Required files" | §3.1 |
| **No random train/test split** | `02_experiment_card.md` §5; `src/epistemic_dro/backtest.py`; `tests/test_backtest.py` | §3.6, §5.4 |
| **Transaction costs explicit** — 10 bps primary; 5/20/50 bps sensitivity | `02_experiment_card.md` §2, §10; `configs/base.yaml` `cost_bps` | §3.4, §3.6 |
| **Explicit risk-free series** — never silently default to zero | `00_project_charter.md` §5; `01_data_card.md` §3 | §3.2, §3.7 |
| **Tail risk reported** — CVaR95 and max drawdown as guardrails, not afterthoughts | `02_experiment_card.md` §3; `03_model_card.md` §9 | §3.12 |
| **Regime sensitivity** — subperiod analysis (2008, 2020, 2022) required | `02_experiment_card.md` §8 | §3.6, §3.8 |
| **No look-ahead via costs** — costs use the previous period's weights, not the current | `optimization.py` contract; `02_experiment_card.md` §6.3 | §3.1 |
| **Licensed data not redistributed** | `.gitignore`; `data/README.md` "Licensing"; `01_data_card.md` §8 | §1.3.3, §5.6 |
| **No investment advice / no live-deployment claim** | `03_model_card.md` §3, §11; `04_decision_log.md` DEC-005 | §1.3.7, §9.1 |

## 2. Regulatory and licensing

- **Data licensing.** Vendor data (CRSP, Compustat, Sharadar, Norgate) may not be redistributed. `data/raw/` and `data/processed/` are gitignored; see `data/README.md` "Licensing".
- **Publication.** Any figure or table published from this repo must be either aggregate metrics or derived from data the author is licensed to publish. Check the vendor's terms before publishing any figure containing raw values.
- **Advice.** This is a research prototype. It is not investment advice, a solicitation, or a recommendation. See `03_model_card.md` §3.

## 3. Finance-specific failure modes beyond generic ML

| Failure | Detection | Mitigation |
|---|---|---|
| Survivorship bias | Universe count only rises; no delistings | PIT membership; delisting returns |
| Look-ahead via fundamentals | Features predict "too well"; `rdq` missing | Use `rdq`; audit |
| Look-ahead via universe | Current constituents used | As-of eligibility join |
| Look-ahead via costs | Costs computed from current weights | Costs use prior-period weights |
| Restatement bias | Final-revised fundamentals used | Use vintage at decision time if available; document limitation |
| Regime shift | Results only hold in one subperiod | Subperiod analysis; no stability claim |
| Short sample overfit | Many trials, best-of-N | Deflated Sharpe; pre-registered metric; report all trials |
| Cost underestimate | High turnover; result dies at 20 bps | 5/10/20/50 bps sensitivity |
| CVaR scenario insufficiency | < 1/(1-α) scenarios; unstable tails | Use enough history; stress windows |
| Solver instability | Silent fallback to equal weights | `SolverFailure` raised; no fallback (`optimization.py`) |
| Alpha claim inflation | "beats market," "institutional-grade" | `03_model_card.md` §3; claim calibration |

## 4. What this project does not claim

- No live-trading or execution validity.
- No alpha, no market-beating claim.
- No causal claim from observational data.
- No claim of deployment readiness. G4 review is explicitly out of scope for November (see `04_decision_log.md` DEC-005).

## 5. Relationship to `AGENTS.md`

`AGENTS.md` §9.5 calls for this file. It is a local, uncommitted operating manual; this overlay is the committed finance-specific rule set. Where they conflict on finance matters, this file wins for the project; `AGENTS.md` remains the broader protocol.
