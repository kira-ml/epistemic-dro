# Published aggregate results

These files are the aggregate and derived research outputs behind `paper/mini_paper.pdf` and the LinkedIn assets. They contain **no raw vendor prices** and **no holdout result**.

They are committed so a fresh clone can rebuild the paper without rerunning the models:

```bash
python scripts/build_paper.py
```

| File | Contents |
|---|---|
| `ridge_b0_summary.json` | Ridge B0 walk-forward forecast metrics |
| `ridge_b0_summary_shuffled.json` | Target-shuffling falsification run |
| `diagnostics.json` | Target distribution, factor variance share, Hill tail index |
| `information_audit.json` / `.csv` | v1 feature MI audit |
| `dro_experiment_summary.json` | v1 reduced DRO metrics |
| `dro_experiment_analysis.json` | v1 paired bootstrap and H1–H3 verdicts |
| `dro_experiment_returns.csv` | v1 monthly net returns by strategy |
| `v2_summary_dev.json` | v2 development metrics |
| `v2_uncertainty_audit.json` | v2 pre-holdout gate |
| `v2_uncertainty_dev.parquet` | v2 per-asset sigma and interval width |
| `v3_summary_dev.json` | v3 development metrics |
| `v3_sigma_audit.json` | v3 pre-holdout gate |
| `v3_sigma_dev.parquet` | v3 per-asset sigma and realized absolute return |
| `gate_power_summary.csv` | Synthetic gate size/power grid |
| `gate_power_study.json` | Gate power study design and summary |
| `gate_reevaluation.json` | Actual development signals under a pooled MI test |
| `block_gate_study.json` | Block-aware null: 3/21 signals survive; v2/v3 sigma do not |
| `effect_size_audit.json` | Rank IC and block bootstrap for survivors, sigma, and trailing vol |
| `final_report.json` | Cost sensitivity, stress windows, deflated Sharpe |

**No v2/v3 holdout result exists.** The 2025–2026 holdout was never run.

**Licensing:** aggregate and derived research outputs only. Raw vendor data is not redistributed; see the root README and `data/README.md`.
