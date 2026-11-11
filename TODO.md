# TODO — Epistemic-Aware DRO

**Last updated:** 2026-11-11
**Current state:** v1 closed (H1/H3 fail, H2 non-inferiority pass); v2 and v3 stopped before holdout; the gate/effect-size study is complete and is a **post-hoc methods audit**; **no v4 on this data**; 2025–2026 holdout **untouched**.
**Release state:** `v1.0.0` tag → `7511597` (paper 7 pages, 2026-11-04); **`v1.0.1` published 2026-11-11 with 7 assets** (corrected 8-page paper, carousel, card, one-pager, summary, LICENSE, CITATION; tag → `7550f5b`; CI green); verifier 63/63; claim-precision and metadata passes complete.  
**Repo note:** the 2026-11-04 docs/asset pass is committed and pushed to `main`; the release remains anchored to tag `v1.0.0`.
**Session close (2026-11-04):** GitHub release is live and verified; claim-precision pass is committed; **LinkedIn launch is paused by owner before upload**. No LinkedIn post was made; verified on the activity/Documents tabs (last document is `V2.1 — The Baseline Audit`, fraud detection). Resume only when the owner chooses.
**2026-11-08:** master TODO, portfolio page, project briefs, and external-review outreach kit prepared outside the repo. External review and launch remain paused; no research change.
**2026-11-11:** `v1.0.1` published: corrected the H1 relative-MDD interval sign, disclosed the 13-vs-19 feature distinction and the 158-vs-179 evaluation paths, and added numbered references/table formatting. Results unchanged (0.4% point estimate, H1 FAIL; holdout untouched). All 23 unique references were validated against Crossref, NeurIPS, OpenLibrary, and Semantic Scholar; two full published titles were restored. Tag `v1.0.1` → `7550f5b`; 7 assets; asset digest matches the committed paper; CI green. Release: https://github.com/kira-ml/epistemic-dro/releases/tag/v1.0.1
**Rule:** the remaining work is **release, verification, and distribution** — not another model search on the same data.

---

## Ground rules (do not break)

- [ ] **Do not run the 2025–2026 holdout retrospectively.** It is preserved for a genuinely new dataset/model.
- [ ] **Do not start a v4 on the same data.** The effect-size audit closed the question: survivors' IC intervals include zero; trailing volatility dominates the conditional sigma.
- [ ] **Do not claim alpha, market-beating performance, investability, causal effects, or live readiness.**
- [ ] **Keep the v1 label accurate:** “reduced M1” = Ridge mean + bootstrap sigma, not the original LightGBM ensemble.
- [ ] **Keep the v2/v3 label accurate:** “stopped before holdout.” No holdout result exists.
- [ ] **Keep the gate labels accurate:** 80% gate too strict; iid pooled gate too permissive; block-aware + effect size is the defensible design.
- [ ] **No raw vendor data in the repo.** Aggregate and derived research outputs only; no raw vendor prices.

---

## P0 — Release and publication (remaining)

### 1. Completed release layer

- [x] `paper/published-results/` with aggregate-only tables.
- [x] `scripts/verify_results.py` — 63/63 checks.
- [x] `.github/workflows/ci.yml` — tests, lint, verifier, paper build.
- [x] `paper/mini_paper.pdf`, `paper/linkedin_carousel.pdf`, `paper/linkedin_card.png`, `paper/one_pager.pdf`.
- [x] `v1.0.0` tag, `RELEASE_NOTES_v1.0.0.md`.
- [x] Gate power study + block-aware null + effect-size audit in the paper and carousel.

### 2. Create the GitHub release — **manual web UI**

- [x] Open GitHub → Releases → **Draft a new release**.
- [x] Choose tag `v1.0.0`.
- [x] Title: `v1.0.0 — Epistemic-Aware DRO`.
- [x] Body: paste `RELEASE_NOTES_v1.0.0.md`.
- [x] Attach:
  - `paper/mini_paper.pdf`
  - `paper/linkedin_carousel.pdf`
  - `paper/linkedin_card.png`
  - `paper/one_pager.pdf`
  - `paper/one_page_summary.md`
  - `paper/LICENSE`
  - `CITATION.cff`
- [x] Verify the release page loads and every asset downloads.
- [x] Verify `https://github.com/kira-ml/epistemic-dro/releases/tag/v1.0.0` resolves.
- [x] Do **not** attach raw data.
- [x] CI check on `7511597` is green; all 7 assets return HTTP 200.
- [x] CI actions pinned to commit SHAs and permissions limited to `contents: read` (2026-11-07).

**Release:** https://github.com/kira-ml/epistemic-dro/releases/tag/v1.0.0

**Definition of done:** a public release exists with the paper and visual assets.

### 3. Publish the LinkedIn package — **PAUSED by owner (2026-11-04)**

- [ ] Upload `paper/linkedin_carousel.pdf` as a native document post.
- [ ] Use **Version 0 — flagship** from `paper/linkedin_post.md`.
- [ ] Put the release link in the first comment and in the featured section.
- [ ] Post the 4:5 `paper/linkedin_card.png` 3–7 days later if the carousel performs.
- [ ] Keep `paper/one_pager.pdf` for email/events, not the primary post.

**Status:** no LinkedIn post was made. The web composer has a **Share a document** modal; the remaining step is the native file picker → `paper/linkedin_carousel.pdf`. The card is a fallback, not the primary post. Resume only on owner request.

**Definition of done:** carousel published; release linked; card scheduled.

---

## P0.5 — LinkedIn launch gate (model-driven, started 2026-11-04)

**Positioning:** research-engineering credential, not an alpha product. The post should make a skeptical reader conclude: *this person can build a process that kills weak ideas before they consume a holdout.*

**Go/no-go:** do not publish until (1) the `v1.0.0` release resolves, (2) one external quant/ML reader has attacked the claims, and (3) the claim-precision pass below is complete.

**Strategic bet:** convex — low-cost public artifact, capped reputational downside, open-ended research-credential upside. The claims must stay smaller than the evidence.

### Launch gate — 12 models applied

- **01 First principles:** narrow methods study; 72 current-listed ETFs; low SNR. Do not imply market-wide generality.
- **02 Inversion:** pre-mortem the launch: broken release link, "three failures" reading, overclaimed H2, mobile unreadability, missing survivorship/working-paper labels.
- **03 Bayesian:** low prior on "another trading project"; shrink claims; label the working paper; one completed result + two pre-holdout stops.
- **04 Shannon:** one idea per slide; cut redundant metrics; mobile legibility.
- **05 Causal hierarchy:** observational/predictive only; use "did not separate," never "improves."
- **06 Parsimony:** keep the 7-slide, three-attempt story; no v4; no new model search.
- **07 Fat tails / non-ergodicity:** research prototype, no live deployment; preserve the holdout; keep CVaR/MDD framing.
- **08 Payoff asymmetry:** publish after inversion fixes; capped downside, open-ended credential upside.
- **09 Feedback loops:** target quant/ML peers; monitor qualified comments; prepare a response memo for objections.
- **10 Goodhart:** success = saves, qualified comments, paper downloads, inbound conversations; not likes/impressions.
- **11 Exploration/exploitation:** 75% flagship paper/carousel; 25% card/essay/video; stop unpromising formats.
- **12 Theory of constraints:** the bottleneck is release proof + external falsifier + claim precision, not content.

### Must-fix claims before publishing

- [x] "Three negative results" → "one completed negative result; two pre-holdout stops."
- [x] "H2 pass" → "H2 non-inferiority guardrail pass."
- [x] "Each stopped by a gate" → v1 closed after the reduced test; v2/v3 stopped before the holdout.
- [x] B5/B3 zero-sigma collapse disclosed; DRO-vs-no-DRO comparison marked uninformative.
- [x] Gate study labeled post-hoc methods audit; stops defensible ex post, not ex ante.
- [x] Slide 1/card/caption: working paper; current-listed ETF universe; not survivorship-free.
- [x] Added `scripts/reproduce_all.py` as a one-command result-level reproduction gate.
- [x] Release link live; CI green; assets attached.
- [ ] Mobile accessibility pass: body text at least 16pt at 540pt; one idea per slide. Audit recorded in [`notes/mobile_accessibility_audit_2026-11-07.md`](notes/mobile_accessibility_audit_2026-11-07.md): current body is 13–14pt, so the v1.0.0 carousel fails the criterion; rebuild only with the launch decision.
- [ ] One external reader; record strongest objection and factual fixes.

**Claim-precision pass completed 2026-11-04:** paper, carousel, card, one-page summary, README, release notes, and post drafts corrected; assets rebuilt; 7-page paper, 7-slide carousel, verifier 63/63 (expanded from 54 checks on 2026-11-07). **Release v1.0.0 published and verified:** 7 assets, all HTTP 200, CI success. Remaining gates: mobile readability and one external reader.

**Metadata and verifier pass completed 2026-11-07:** `pyproject.toml` and `__init__.py` aligned to `1.0.0`; `CITATION.cff` release date aligned to `2026-11-04`; "aggregate metrics only" corrected to "aggregate and derived research outputs; no raw vendor prices" in the paper README, release notes, and published-results README; verifier expanded from 54 to 63 checks (v2 coverage, v2/v3 survival flags, v3 calibration, and paper cross-checks); 26 mutation tests added so every checked claim must fail when changed; 81 tests pass; `ruff` clean; verifier 63/63.

### Launch sequence

1. **Day 0:** create/verify the release; one external reader; fix factual errors only.
2. **Day 1:** carousel + Version 0 caption; release link in the first comment.
3. **Day 3–7:** card + Version B only if the carousel produces saves/qualified comments.
4. **Week 2:** essay only if the pull is real; keep the 75/25 split.
5. Record objections and fixes in `docs/11_lessons_log.md` or a short response memo.

**Definition of done:** a truthful, link-complete carousel published to the target audience, with one external objection recorded and no overclaim left unfixed.

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

- [x] Document the v2 snapshot (`data/raw_v2/`) in `docs/01_data_card.md` or a short addendum: 72 ETFs, 2000-01..2026-09, FRED `TB3MS`, 21,224 price rows.
- [x] Add a one-paragraph "how to read the three attempts + gate study" to `paper/README.md` or `docs/13_final_report.md`.
- [x] Verify all links in `README.md`, `paper/README.md`, and `docs/README.md`.
- [x] Confirm `paper/README.md` accurately describes the 7-page paper and 7-slide carousel.
- [x] Decide the **paper/figures license**: MIT covers code; the paper text/figures may need a separate license (e.g., CC BY 4.0) or an explicit "all rights reserved" note.
- [x] Add `CITATION.cff` with author, title, year, repo URL, and paper title.
- [x] Add a short "Data and licensing" note to the paper/repo: Yahoo terms, no raw redistribution, aggregate results only.

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

- [x] v1 closed: H1/H3 fail, H2 non-inferiority pass; reduced M1 results and bootstrap intervals.
- [x] v2 pre-registered, developed, stopped before holdout (gate 0.654).
- [x] v3 pre-registered, developed, stopped before holdout (gate 0.430).
- [x] 2025–2026 holdout preserved.
- [x] Mini paper, carousel, card, one-pager, post drafts, and one-page summary built.
- [x] Gate power study: 80% gate zero power at 20% R².
- [x] Block-aware null: iid 20/21 vs block 3/21; v2/v3 sigma do not survive.
- [x] Effect-size audit: survivors' IC CIs include zero; trailing vol dominates sigma; **no v4**.
- [x] 81 tests pass; `ruff` clean; verifier 63/63; CI green (2026-11-07 metadata/verifier pass).

---

## Session status — closed 2026-11-04

**Closed for the day. No action required.**

- GitHub release `v1.0.0` is live and verified: 7 assets, CI green.
- Claim-precision pass is committed and pushed to `main`.
- **No LinkedIn post was made.** Verified on the activity/Documents tabs; the last document is `V2.1 — The Baseline Audit` (fraud detection).
- LinkedIn launch, mobile pass, and external reader are **paused by owner**. Resume only on request.
- **Do not start a v4 on this data. Do not touch the 2025–2026 holdout.**
