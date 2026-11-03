# TODO — Epistemic-Aware DRO

**Last updated:** 2026-11-03
**Current state:** v1 closed (H1/H3 fail, H2 pass); v2 and v3 stopped before holdout; the gate/effect-size study is complete; **no v4 on this data**; 2025–2026 holdout **untouched**.
**Release state:** `v1.0.0` tag → `7511597`; paper 7 pages; carousel 7 slides; verifier 54/54; CI green on `7511597`; GitHub release still needs the web UI.
**Rule:** the remaining work is **release, verification, and distribution** — not another model search on the same data.

---

## Ground rules (do not break)

- [ ] **Do not run the 2025–2026 holdout retrospectively.** It is preserved for a genuinely new dataset/model.
- [ ] **Do not start a v4 on the same data.** The effect-size audit closed the question: survivors' IC intervals include zero; trailing volatility dominates the conditional sigma.
- [ ] **Do not claim alpha, market-beating performance, investability, causal effects, or live readiness.**
- [ ] **Keep the v1 label accurate:** “reduced M1” = Ridge mean + bootstrap sigma, not the original LightGBM ensemble.
- [ ] **Keep the v2/v3 label accurate:** “stopped before holdout.” No holdout result exists.
- [ ] **Keep the gate labels accurate:** 80% gate too strict; iid pooled gate too permissive; block-aware + effect size is the defensible design.
- [ ] **No raw vendor data in the repo.** Aggregate metrics only.

---

## P0 — Release and publication (remaining)

### 1. Completed release layer

- [x] `paper/published-results/` with aggregate-only tables.
- [x] `scripts/verify_results.py` — 54/54 checks.
- [x] `.github/workflows/ci.yml` — tests, lint, verifier, paper build.
- [x] `paper/mini_paper.pdf`, `paper/linkedin_carousel.pdf`, `paper/linkedin_card.png`, `paper/one_pager.pdf`.
- [x] `v1.0.0` tag, `RELEASE_NOTES_v1.0.0.md`.
- [x] Gate power study + block-aware null + effect-size audit in the paper and carousel.

### 2. Create the GitHub release — **manual web UI**

- [ ] Open GitHub → Releases → **Draft a new release**.
- [ ] Choose tag `v1.0.0`.
- [ ] Title: `v1.0.0 — Epistemic-Aware DRO`.
- [ ] Body: paste `RELEASE_NOTES_v1.0.0.md`.
- [ ] Attach:
  - `paper/mini_paper.pdf`
  - `paper/linkedin_carousel.pdf`
  - `paper/linkedin_card.png`
  - `paper/one_pager.pdf`
  - `paper/one_page_summary.md`
- [ ] Verify the release page loads and every asset downloads.
- [ ] Verify `https://github.com/kira-ml/epistemic-dro/releases/tag/v1.0.0` resolves.
- [ ] Do **not** attach raw data.

**Definition of done:** a public release exists with the paper and visual assets.

### 3. Publish the LinkedIn package

- [ ] Upload `paper/linkedin_carousel.pdf` as a native document post.
- [ ] Use **Version 0 — flagship** from `paper/linkedin_post.md`.
- [ ] Put the release link in the first comment and in the featured section.
- [ ] Post the 4:5 `paper/linkedin_card.png` 3–7 days later if the carousel performs.
- [ ] Keep `paper/one_pager.pdf` for email/events, not the primary post.

**Definition of done:** carousel published; release linked; card scheduled.

---

## P1 — Distribution and feedback (Nov 8–14)

- [ ] Send the paper to **3–5 quant/ML peers** and ask: “What is the strongest objection?”
- [ ] Record objections and fixes in `docs/11_lessons_log.md` or a short response memo.
- [ ] Write a **1,200-word essay**: *“I tested the gate in both directions — and then I stopped.”*
- [ ] Add the paper to the GitHub featured section and pin the repo.
- [ ] Add repo topics: `quant-finance`, `machine-learning`, `distributionally-robust-optimization`, `cvar`, `epistemic-uncertainty`, `negative-results`, `pre-registration`.
- [ ] Add a short repo description that leads with the gate/negative result, not “AI trading.”

**Definition of done:** paper shared with external readers; one long-form essay published or drafted.

---

## P2 — Documentation polish and licensing (Nov 8–14)

- [ ] Document the v2 snapshot (`data/raw_v2/`) in `docs/01_data_card.md` or a short addendum: 72 ETFs, 2000-01..2026-09, FRED `TB3MS`, 21,224 price rows.
- [ ] Add a one-paragraph “how to read the three attempts + gate study” to `paper/README.md` or `docs/13_final_report.md`.
- [ ] Verify all links in `README.md`, `paper/README.md`, and `docs/README.md`.
- [ ] Confirm `paper/README.md` accurately describes the 7-page paper and 7-slide carousel.
- [ ] Decide the **paper/figures license**: MIT covers code; the paper text/figures may need a separate license (e.g., CC BY 4.0) or an explicit “all rights reserved” note.
- [ ] Add `CITATION.cff` with author, title, year, repo URL, and paper title.
- [ ] Add a short “Data and licensing” note to the paper/repo: Yahoo terms, no raw redistribution, aggregate results only.

**Definition of done:** a reader can tell what is licensed, what data is included, and how to cite the paper.

---

## P3 — Optional / later

- [ ] Add a **common-factor/autocorrelated size simulation** to validate the block-aware null itself. This is a methods appendix, not a reason to touch the holdout.
- [ ] Decide whether to submit the mini paper to a blog, SSRN, or a workshop. Do not call it a peer-reviewed publication.
- [ ] Add a **60–90 second video script** for the carousel: hook, three attempts, gate study, effect-size stop.
- [ ] Create audience-specific cuts:
  - quant research/hiring: gates, block-aware null, effect size, holdout discipline;
  - ML/DS: calibration ≠ information, pre-registration, information audits.
- [ ] Add a Zenodo DOI for the `v1.0.0` release (optional).
- [ ] Add a `CHANGELOG.md` if the repo will continue.
- [ ] Only with a genuinely new dataset/uncertainty model: write a **new pre-registration** with a block-aware pooled gate and a minimum effect size. Do not call it v4-on-the-same-data.

---

## Completed (for context)

- [x] v1 closed: H1/H3 fail, H2 pass; reduced M1 results and bootstrap intervals.
- [x] v2 pre-registered, developed, stopped before holdout (gate 0.654).
- [x] v3 pre-registered, developed, stopped before holdout (gate 0.430).
- [x] 2025–2026 holdout preserved.
- [x] Mini paper, carousel, card, one-pager, post drafts, and one-page summary built.
- [x] Gate power study: 80% gate zero power at 20% R².
- [x] Block-aware null: iid 20/21 vs block 3/21; v2/v3 sigma do not survive.
- [x] Effect-size audit: survivors' IC CIs include zero; trailing vol dominates sigma; **no v4**.
- [x] 55 tests pass; `ruff` clean; verifier 54/54; CI green.

---

## Suggested order for the next session

1. Create the GitHub `v1.0.0` release and verify the link.
2. Publish the carousel with Version 0.
3. Add `CITATION.cff` and the paper/figures license.
4. Send the paper to one external reader.
5. Write the 1,200-word essay.
6. Optional methods appendix: common-factor size simulation.

**Do not start a v4 on this data. Do not touch the holdout.**
