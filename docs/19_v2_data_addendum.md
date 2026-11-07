# v2 Data Snapshot Addendum

**Status:** v2 development-only snapshot; holdout untouched<br>
**Snapshot date:** 2026-11-02<br>
**Addendum date:** 2026-11-03<br>
**Related:** [`01_data_card.md`](01_data_card.md), [`14_v2_preregistration.md`](14_v2_preregistration.md), [`15_v2_report.md`](15_v2_report.md)

This addendum records the v2 snapshot used for the conformal-quantile development run. It does not change the v1 data card, the frozen protocol, or the claim scope.

| Field | v2 snapshot |
|---|---|
| Universe | 72 US-listed ETFs; same frozen universe |
| Requested window | 2000-01-01 .. 2026-10-01 |
| Realised coverage | 2000-01 .. 2026-09 |
| Prices | 21,224 rows |
| Returns | 21,152 rows |
| Risk-free | FRED `TB3MS`, 321 aligned months; no fallback |
| Factors | Ken French 3-factor + momentum, 321 months |
| Benchmark | 320 months |
| Provider | Yahoo Finance chart API (adjusted close); FRED; Ken French Data Library |
| Manifest | `data/raw_v2/MANIFEST.json` with SHA-256 per table |
| Builder | `scripts/build_snapshot.py`; universe `configs/etf_universe.csv` |
| Redistribution | Raw snapshot local-only and gitignored; aggregate and derived research outputs only, no raw vendor prices |
| Holdout | 2025–2026 untouched; no v2 holdout result exists |

The snapshot is a **current-listed** ETF universe; closed funds are not represented, so there is no survivorship-free claim. Expense ratio and distribution yield are unavailable and excluded from the primary model. The 2025–2026 holdout was not read for v2; the development gate stopped the attempt before it.
