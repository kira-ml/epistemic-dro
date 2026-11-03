# TODO — Epistemic-Aware DRO

**Last updated:** 2026-11-03
**Current state:** v1 closed (H1/H3 fail, H2 pass); v2 and v3 stopped before holdout; 2025–2026 holdout **untouched**; paper, carousel, card, and one-pager built.
**Rule:** the remaining work is **release, verification, and distribution** — not another model search on the same data.
**Progress 2026-11-03:** P0.1–P0.3 complete; `v1.0.0` tagged; CI run #4 green; first-post strategy memo and flagship caption added; gate power study complete (80% gate zero power at 20% R²; pooled test detects it); paper and carousel updated to 7 pages/slides; GitHub release still needs the web UI; LinkedIn publication pending.

---

## Ground rules (do not break)

- [ ] **Do not run the v2/v3 2025–2026 holdout retrospectively.** It is preserved for a genuinely new pre-registration.
- [ ] **Do not start a v4 on the same data/features** unless there is a new data source, a new uncertainty target, a stable pre-holdout signal, and an untouched holdout.
- [ ] **Do not claim alpha, market-beating performance, investability, causal effects, or live readiness.** The project is a methods study with negative results.
- [ ] **Keep the v1 label accurate:** “reduced M1” = Ridge mean + bootstrap sigma, not the original LightGBM ensemble.
- [ ] **Keep the v2/v3 label accurate:** “stopped before holdout.” No holdout result exists.
- [ ] **No raw vendor data in the repo.** Aggregate metrics only.

---

## P0 — Release and verification (Nov 3–7)

### 1. Publish aggregate result tables

- [x] Create `paper/published-results/` with aggregate-only files:
  - `ridge_b0_summary.json`
  - `ridge_b0_summary_shuffled.json`
  - `diagnostics.json`
  - `information_audit.json`
  - `dro_experiment_summary.json`
  - `dro_experiment_analysis.json`
  - `dro_experiment_returns.csv` (needed for the cumulative figure)
  - `v2_summary_dev.json`
  - `v2_uncertainty_audit.json`
  - `v3_summary_dev.json`
  - `v3_sigma_audit.json`
  - `v3_sigma_dev.parquet` (needed for the calibration figure)
  - `final_report.json`
- [x] Add `paper/published-results/README.md` stating: aggregate metrics only; no raw prices; no holdout result.
- [x] Change `scripts/build_paper.py` to read `paper/published-results/` first, with `results/tables/` as a local fallback.
- [x] Rebuild and verify `paper/mini_paper.pdf`, `paper/linkedin_carousel.pdf`, `paper/one_pager.pdf`, `paper/linkedin_card.png` from the published tables.
- [x] Commit the published tables and regenerated assets.

**Definition of done:** a fresh clone can run `python scripts/build_paper.py` and rebuild the paper without rerunning the models.

### 2. Add a verifier

- [x] Create `scripts/verify_results.py` that checks:
  - v1 verdicts: H1 FAIL, H2 PASS, H3 FAIL;
  - v2 gate < 0.80 and `holdout_allowed == false`;
  - v3 gate < 0.80 and `holdout_allowed == false`;
  - no v2/v3 holdout result files exist;
  - `paper/mini_paper.pdf`, `linkedin_carousel.pdf`, `one_pager.pdf`, and `linkedin_card.png` exist;
  - the paper’s headline numbers match the published JSONs.
- [x] Make it exit non-zero on any mismatch.
- [x] Add it to `paper/README.md` and the root README.

**Definition of done:** `python scripts/verify_results.py` prints PASS and fails if a verdict or gate is tampered with.

### 3. Add CI

- [x] Create `.github/workflows/ci.yml`:
  - Ubuntu, Python 3.10;
  - `pip install -e ".[dev,paper]"`;
  - `pytest -q`;
  - `ruff check .`;
  - `python scripts/verify_results.py`;
  - `python scripts/build_paper.py`;
  - assert `paper/mini_paper.pdf` exists.
- [x] Add `typst` to a `paper` optional dependency or document it in `paper/README.md`.
- [x] Confirm the workflow is green on GitHub — run #4: https://github.com/kira-ml/epistemic-dro/actions/runs/41578819540.

**Definition of done:** every push runs tests, lint, verifier, and paper build.

### 4. Create `v1.0.0`

- [x] Tag `v1.0.0` (separate from the docs freeze tags).
- [ ] Create a GitHub release with:
  - `paper/mini_paper.pdf`
  - `paper/linkedin_carousel.pdf`
  - `paper/linkedin_card.png`
  - `paper/one_pager.pdf`
  - `paper/one_page_summary.md`
  - Use `RELEASE_NOTES_v1.0.0.md`; `gh` is not installed, so use the web UI: Releases → Draft a new release → choose tag `v1.0.0`.
- [x] Write release notes: three pre-registered attempts, one closed negative, two pre-holdout stops, holdout untouched.
- [x] Do **not** attach raw data.

**Definition of done:** a public release exists with the paper and visual assets.

### 5. Publish the LinkedIn package

- [ ] Upload `paper/linkedin_carousel.pdf` as a native document post.
- [ ] Use **Version A** from `paper/linkedin_post.md`.
- [ ] Put the paper link in the first comment and in the featured section.
- [ ] Post the 4:5 `paper/linkedin_card.png` 3–7 days later if the carousel performs.
- [ ] Keep `paper/one_pager.pdf` for email/events, not the primary post.

**Definition of done:** carousel published; paper linked; card scheduled.

### 6. Gate power study — completed 2026-11-03

- [x] Simulate known linear/quadratic signals at 50/72/150 assets.
- [x] Measure size and power of the 80% date-level MI gate.
- [x] Compare a pooled MI gate and a decile-spread gate.
- [x] Re-evaluate actual v1/v2/v3 development signals under the pooled test.
- [x] Add `docs/18_gate_power_study.md`, a paper section, and a carousel slide.
- [ ] Add autocorrelated/block-bootstrap nulls to the pooled gate.
- [ ] Decide the v4 two-part gate only after the block-aware null is tested.

**Key result:** at 72 assets and 179 dates, the 80% gate has **zero power at a 20% R² signal**; the pooled gate detects the same signal in 100% of seeds. The v1/v2/v3 stops are evidence of **instability**, not proof of no signal. The holdout remains untouched.

---

## P1 — Distribution and feedback (Nov 8–14)

- [ ] Send the paper to **3–5 quant/ML peers** and ask: “What is the strongest objection?”
- [ ] Record objections and fixes in `docs/11_lessons_log.md` or a short response memo.
- [ ] Write a **1,200-word essay** for a blog/Medium/LinkedIn article: “Three pre-registered attempts, zero holdout touches.”
- [ ] Add the paper to the GitHub featured section and pin the repo.
- [ ] Add repo topics: `quant-finance`, `machine-learning`, `distributionally-robust-optimization`, `cvar`, `epistemic-uncertainty`, `negative-results`, `pre-registration`.
- [ ] Add a short repo description that leads with the negative result, not “AI trading.”

**Definition of done:** paper shared with external readers; one long-form essay published or drafted.

---

## P2 — Documentation polish (Nov 8–14)

- [ ] Document the v2 snapshot (`data/raw_v2/`) in `docs/01_data_card.md` or a short addendum: 72 ETFs, 2000-01..2026-09, FRED `TB3MS`, 21,224 price rows.
- [ ] Add a one-paragraph “how to read the three attempts” to `docs/13_final_report.md` or `paper/README.md`.
- [ ] Verify all links in `README.md`, `paper/README.md`, and `docs/README.md`.
- [ ] Confirm `paper/README.md` no longer claims published tables are committed before they are.
- [ ] Decide the **paper/figures license**: MIT covers code; the paper text/figures may need a separate license (e.g., CC BY 4.0) or an explicit “all rights reserved” note.
- [ ] Add `CITATION.cff` with author, title, year, repo URL, and paper title.
- [ ] Add a short “Data and licensing” note to the paper/repo: Yahoo terms, no raw redistribution, aggregate results only.

**Definition of done:** a reader can tell what is licensed, what data is included, and how to cite the paper.

---

## P3 — Optional / later (Nov 15–30)

- [ ] Decide whether to submit the mini paper to a blog, SSRN, or a workshop. Do not call it a peer-reviewed publication.
- [ ] Add a **60–90 second video script** for the carousel: hook, three attempts, one lesson.
- [ ] Create an audience-specific cut:
  - quant research/hiring: gates, comparator design, holdout discipline;
  - ML/DS: calibration ≠ information, pre-registration, information audits.
- [ ] Add a Zenodo DOI for the `v1.0.0` release (optional, if you want a citable artifact).
- [ ] Add a `CHANGELOG.md` if the repo will continue.
- [ ] If a genuinely new dataset/uncertainty model appears, write a **v4 pre-registration** — not a v3 rerun.

---

## Already done (for context)

- [x] v1 closed: H1/H3 fail, H2 pass; reduced M1 results and bootstrap intervals.
- [x] v2 pre-registered, developed, stopped before holdout (gate 0.654).
- [x] v3 pre-registered, developed, stopped before holdout (gate 0.430).
- [x] 2025–2026 holdout preserved.
- [x] Mini paper, carousel, card, one-pager, post drafts, and one-page summary built.
- [x] 55 tests pass; `ruff` clean.
- [x] Tags: `docs-freeze-v1`, `docs-freeze-v1.1`, `docs-freeze-v2`, `docs-freeze-v3`.

---

## Suggested order for the first day back

1. `paper/published-results/` + `build_paper.py` fallback.
2. `scripts/verify_results.py`.
3. `.github/workflows/ci.yml`.
4. `v1.0.0` release.
5. Publish the carousel.

**Do not start a v4 until the release and verifier are done.**
