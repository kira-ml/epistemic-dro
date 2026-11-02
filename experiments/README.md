# Experiments — Ledger and Baseline Benchmarks

**Protocol:** v1.1-rigor
**Rule:** every run — including failed and exploratory runs — appends one JSON object per line to `experiments/ledger.jsonl`. No run may be cited without a ledger entry.

## Files

| File | Purpose |
|---|---|
| `ledger.jsonl` | Machine-readable experiment log. Empty until the first run. |
| `baseline_benchmarks.md` | Human-readable record of the mandatory baselines, starting with Ridge B0. |

## Ledger schema

One JSON object per line:

```json
{
  "experiment_id": "EXP_001_RIDGE_BASELINE",
  "timestamp": "2026-11-07T12:00:00Z",
  "commit_hash": "abc1234",
  "hypothesis": "A regularized Ridge forecast provides a non-trivial baseline for next-month ETF excess returns",
  "model_family": "Ridge",
  "parameters": {"alpha": 1.0},
  "features_count": 15,
  "universe": "us_liquid_etf",
  "split": "walk_forward_60_12_12_purge1_embargo1",
  "metrics": {
    "net_sharpe": null,
    "max_drawdown": null,
    "cvar_95": null,
    "turnover": null,
    "cost_drag": null
  },
  "counter_metrics_passed": false,
  "shuffled_leakage_passed": false,
  "vs_baseline_dm_p_value": null,
  "decision": "PENDING",
  "notes": "No metrics until the G1 snapshot exists."
}
```

## Rules

1. **No fabricated metrics.** A row with no run has `null` metrics and `decision: PENDING`.
2. **No silent trials.** Hyperparameter search, ablations, and failed runs are logged.
3. **No post-hoc editing.** Append a correction row if a value is wrong; do not rewrite history.
4. **Commit hash required.** The code that produced the run must be identifiable.
5. **Shuffled-target result required** before `counter_metrics_passed` or `decision` can be true.
6. **Ledger is append-only.** `experiments/ledger.jsonl` is part of the operating record.

## Baseline law (G-R6)

No LightGBM run may be adopted before:

1. Ridge B0 is logged on identical splits.
2. The candidate beats Ridge with a Diebold-Mariano test at \(p < 0.01\).
3. The comparison is on purged out-of-sample data.

If the candidate does not beat the baseline, the simpler model is reported. That is a valid outcome, not a failure.
