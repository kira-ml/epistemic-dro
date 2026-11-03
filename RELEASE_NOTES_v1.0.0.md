# v1.0.0 — Epistemic-Aware DRO

**Release date:** 2026-11-03
**Status:** Research prototype; negative results; no live deployment.

## What this release contains

- A 6-page working paper: `paper/mini_paper.pdf`
- A 7-slide LinkedIn carousel: `paper/linkedin_carousel.pdf`
- A 4:5 visual card: `paper/linkedin_card.png`
- A one-page leave-behind: `paper/one_pager.pdf`
- Aggregate published results: `paper/published-results/`
- The full code, frozen protocols, gates, and experiment ledger.

## Results

| Attempt | Object of uncertainty | Outcome |
|---|---|---|
| **v1** | Epistemic uncertainty (Ridge mean + bootstrap sigma) | **H1/H3 fail, H2 pass.** 0.4% relative MDD improvement; CVaR CI includes zero; Sharpe non-inferior. |
| **v2** | Conformalized LightGBM return quantiles | **Stopped before holdout.** Coverage 89.9% / 85.9%; information gate 65.4% < 80%. |
| **v3** | Conditional tail-risk forecast | **Stopped before holdout.** Calibration 4.29% vs 4.30%, decile spread 3.76 pp; gate 43.0% < 80%; underperformed trailing volatility. |

**The 2025–2026 holdout was never touched.** No holdout result exists.

## Verification

```bash
python scripts/verify_results.py
```

The verifier checks the published verdicts, gates, assets, and the headline numbers in the paper source. CI runs it on every push.

## Reproduction

```bash
python -m pip install -e ".[dev,ml,paper]"
python scripts/build_paper.py
pytest -q
ruff check .
```

Raw vendor data is **not** included. `paper/published-results/` contains aggregate metrics only.

## Licence and data

Code: MIT. The paper text and figures are research artefacts; decide a separate paper licence before redistribution. Yahoo Finance data is not redistributed. No investment advice. No alpha claim.
