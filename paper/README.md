# Public-facing package — Epistemic-Aware DRO

**Recommendation:** do **not** lead with a text-only one-page summary. For LinkedIn, use a **native document carousel** (or the 4:5 card) and keep the paper as the credibility layer. The one-pager is a leave-behind, not the primary format.

## The layered release

| Layer | File | Job | Where it goes |
|---|---|---|---|
| **Mini paper** | [`mini_paper.pdf`](mini_paper.pdf) | Credibility; full method, three results, limitations | Featured link, comments, repo, email |
| **LinkedIn carousel** | [`linkedin_carousel.pdf`](linkedin_carousel.pdf) | Reach and dwell time; 6 native slides | LinkedIn document post |
| **Visual card** | [`linkedin_card.png`](linkedin_card.png) | Single-image hook; 4:5 feed card | LinkedIn image post / carousel cover |
| **One-page summary** | [`one_pager.pdf`](one_pager.pdf) | Leave-behind / print | Email, attachment, event handout |
| **Short post** | [`linkedin_post.md`](linkedin_post.md) | Context and CTA | Post caption |
| **Career strategy** | [`career_post_strategy.md`](career_post_strategy.md) | 12-model lens, positioning, pre-post checklist | Read before posting |
| **Traditional one-pager** | [`one_page_summary.md`](one_page_summary.md) | Plain-text summary if you need one | Doc/PDF export |

## Why this order

- **LinkedIn rewards dwell time.** A 6-page carousel keeps the reader on the post; a single block of text does not.
- **The paper carries the technical claim.** The carousel cannot defend the method; the paper can.
- **The negative result is the hook.** “Three pre-registered attempts. The holdout is still untouched.” is more distinctive than another “I built a strategy” post.
- **The one-pager is still useful**, but as a leave-behind after someone has already clicked. It is not the acquisition layer.

## Posting sequence

1. Upload `linkedin_carousel.pdf` as a **document post**.
2. Use the short caption in [`linkedin_post.md`](linkedin_post.md).
3. Put the paper link in the **first comment** and in your featured section, so the post does not lose reach to an outbound link.
4. Post the 4:5 `linkedin_card.png` as a standalone image 3–7 days later if the carousel performs; use a different hook, same paper.
5. Optional: a 60–90s screen-recorded walkthrough of the gate table. The carousel is the low-effort version; the video is the high-effort one.

## Guardrails

- No alpha claim, no “beat the market,” no investable framing.
- Say **v1 reduced M1** when referring to the v1 uncertainty result; it is not the original LightGBM ensemble.
- Say **v2/v3 stopped before the holdout**; do not imply a holdout result.
- Keep “not investment advice” on the visual and in the caption.
- Do not add a fourth model search to the post. The story is the apparatus and the negative results.

## Rebuild

```bash
python scripts/build_paper.py
python scripts/verify_results.py
```

`verify_results.py` checks the published verdicts, gates, paper assets, and the
headline numbers in `paper/generated/numbers.typ` against the committed aggregate
tables. CI runs it on every push.

This regenerates the numbers, figures, card, carousel, one-pager, and paper from the committed result tables. If a number changes in `paper/published-results/`, the PDF changes with it.
