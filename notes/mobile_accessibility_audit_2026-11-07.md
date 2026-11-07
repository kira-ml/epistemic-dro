# Mobile accessibility audit — carousel

**Date:** 2026-11-07
**Subject:** `paper/linkedin_carousel.pdf` (the v1.0.0 release asset) and `paper/carousel.typ`.
**Criterion (roadmap):** body text at least 16pt at a 540pt page width; one idea per slide.

## Measured layout

| Property | Value |
|---|---|
| Page size | 540 × 675pt |
| Margin | 38pt |
| Content width | 464pt |
| Carousel slides | 7 |
| Heading sizes | 24–31pt |
| Body sizes | **13–14pt** |
| Box / callout text | 12pt |
| Notes and footnotes | 8–11pt |

## Verdict

**The body text does not meet the 16pt criterion.** The headings are large enough, and
the slides are already one-idea-per-slide in structure, but the explanatory body is
13–14pt on slides 2–7 and 12pt inside callout boxes. At a 390pt phone viewport, 13pt
text scales to roughly 9.4pt; even 16pt would scale to about 11.6pt. The current asset
is readable on a desktop PDF viewer but not comfortably readable on a phone.

A second issue is density, not only size. Several slides carry two body paragraphs plus
a table or figure plus a caveat line. Increasing font size without cutting copy will
overflow the 675pt page.

## Required changes before a launch

1. Raise body text to at least **18pt** (16pt is the floor; 18pt leaves margin for a
   phone at 390pt).
2. Cut body copy by roughly 30%: keep one claim and one piece of evidence per slide;
   move method detail to the paper and the speaker notes.
3. Keep headings at 24–27pt and keep the footer/notes at 9pt or above, but do not count
   footnotes as body text.
4. Rebuild `paper/linkedin_carousel.pdf` and `paper/linkedin_card.png` with
   `python scripts/build_paper.py`, then re-run `python scripts/reproduce_all.py`.
5. Re-check the rebuilt PDF at phone width before uploading. Do not edit the v1.0.0
   release assets until the launch decision is made; a changed asset needs a new
   release or an explicit asset replacement.

## What is not changed

No claim, number, or experiment changes. This is a presentation fix only. The
2025-2026 holdout remains untouched, and the v1.0.0 tag remains the research
reference until a launch decision.
