# Release Notes — v1.1.0

**Date:** 2026-11-22
**Tag:** `v1.1.0`
**Nature:** disclosure and naming release. No result changed; the holdout remains untouched.

## What changed

- **Feature screening (G-R4).** Both readings of the rule are now reported. The implementation
  keeps a feature only if it beats the null in at least 80% of windows — the strict rule. Under
  the looser reading, 12 of 13 features would survive. The paper states this in the v1 section,
  not only in the limitations.
- **v2/v3 naming.** "Pre-registered" is replaced by "pre-specified" wherever the record does not
  support prospective registration. The plans and stop decisions were committed together after
  the development results were computed; that timing is disclosed.
- **Bootstrap.** The paired bootstrap resamples months iid; max drawdown is path-dependent. The
  limitation is stated, and H3 is framed as "not separated by this test" rather than "within
  noise".
- **Reproduction.** v1 is pinned to commit `d5dca68`, when the feature builder produced 13
  features. HEAD builds 19; the six derived features were added after the v1 audit.
- **Power study.** "Zero power" corrected to "0 of 2 seeds" in the abstract, figure caption, and
  claim ledger.
- **Naming.** Plain names replace internal codes in the title, status box, abstract, section
  headings, and notation table.
- **One-pager.** An A4 Typst research summary with a two-panel evidence figure.

## What did not change

- v1 results, v2/v3 gate outcomes, and the untouched 2025–2026 holdout.

## Verify

```bash
pytest -q                      # 81 passed
python scripts/verify_results.py   # 63/63
ruff check .                   # clean
```
