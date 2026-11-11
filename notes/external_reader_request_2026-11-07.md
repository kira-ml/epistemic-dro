# Independent reader request

**Date:** 2026-11-07
**Goal:** one adversarial quant/ML reader for the v1.0.1 package, before 2026-11-30. The ask is for the strongest objection, not an endorsement. A factual error or an overread claim is the useful outcome.

**State.** `v1.0.1` is released (2026-11-11); `v1.0.0` remains the original release. The corrected paper is 8 pages, its uploaded PDF matches the committed source, and all 22 unique references were validated against primary metadata. The 2025-2026 holdout is untouched; v2 and v3 stopped before it. No raw vendor data is redistributed. The verifier has 63 checks; 81 tests pass and `ruff` is clean.

## The message

Send as-is, personalise the first line.

> Hi [name] — I built a pre-registered test of whether ML epistemic uncertainty improves the tail-risk/return trade-off of a distributionally robust mean-CVaR portfolio. It produced a mixed negative result: H1 and H3 failed, H2 passed only as a non-inferiority test, and I stopped two follow-up versions before the holdout. I am looking for one adversarial reader, not an endorsement. The paper, code, and aggregate results are public; no raw vendor data is redistributed. Would you read the paper and tell me the strongest objection — the one that would change a claim? I will record it and fix factual errors only; I will not run a new experiment in response.
> <link to the repository, the paper, and `docs/18_gate_power_study.md`>

## What they can run without vendor data

```bash
git clone https://github.com/kira-ml/epistemic-dro.git && cd epistemic-dro
python -m pip install -e ".[dev,ml,paper]"
python -m pytest -q                 # 81 tests
python -m ruff check .
python scripts/verify_results.py    # 63/63 checks
python scripts/reproduce_all.py     # tests + lint + verifier + paper rebuild
```

`reproduce_all.py` rebuilds the paper from the committed aggregate tables. It does **not** rebuild the vendor snapshot; raw data is external and is not redistributed.

## The adversarial questions

Ask the reader to pick the one that matters most, not to answer all six.

1. **Is H2 overread?** The pass is non-inferiority against the best baseline, not superiority. Is the margin pre-registered and defensible, and does the paper keep the distinction visible?
2. **Does the v2/v3 stop follow from instability, or only from an underpowered gate?** The 80% date-level gate had zero power at a 20% R² signal. The block-aware null and effect-size audit are the response. Check whether they actually separate "no signal" from "no detectable signal."
3. **Is the block-aware null defensible?** It preserves 6/12/24-month blocks and passes 3/21 signals against 20/21 under the iid pooled test. Are the block length and test statistic appropriate for monthly, overlapping targets?
4. **Does the effect-size audit close v4 on this data?** The surviving v1 features have 90% block-bootstrap IC intervals that include zero, and trailing 36-month volatility has a higher mean IC than either v2 or v3 sigma. Is that comparison computed on the same sample and target?
5. **Is the holdout genuinely untouched?** No v2/v3 holdout result exists; the verifier checks that no holdout-named file appears in `results/tables/` or `paper/published-results/`. Try to falsify that.
6. **Is there leakage?** Check the feature/target timing, the 60-month train / 12-month validation / 12-month test split, the purge/embargo, and the per-date information tests.

## What to send back

- Operating system, Python version, and whether the install was clean.
- Which checks they ran: tests, verifier, paper review, or a specific claim review.
- The strongest objection, with the claim and the evidence.
- Any factual error, leakage, or overclaim.
- Whether the objection changes a claim, a limitation, or only the presentation.

## Log

| Date | Person | Scope | Objection / result | Action |
|---|---|---|---|---|
| | | | | |
| | | | | |

## Rules

- Ask for an objection, not a quote or an endorsement.
- Do not send raw vendor data or a snapshot archive.
- Do not run the 2025-2026 holdout in response to a review.
- Fix factual errors and claim wording only; no new experiment, no v4.
- Record the first substantive objection in `docs/11_lessons_log.md` or a short response memo.
- One reader, then stop; ask a second only if the first is inconclusive.
