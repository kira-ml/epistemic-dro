# First-post strategy — flagship signals

**Goal:** the first public post should make a skeptical reader conclude: *this person can build a research process that separates signal from noise, and can be trusted with a hard problem.*

It should **not** read as “I tried three strategies and none worked.” It should read as “I built a pipeline that killed three weak ideas before they consumed the holdout.”

---

## 1. Positioning

| Dimension | Choice |
|---|---|
| Primary audience | Quant research, ML research, research engineering hiring managers and peers |
| Secondary audience | General ML/data-science practitioners interested in uncertainty and evaluation |
| Not the audience | Retail trading, “best stock picks,” growth-hacking LinkedIn |
| Identity signal | Research engineer who pre-registers, falsifies, and ships reproducible artifacts |
| Proof | 5-page paper, 6-slide carousel, public repo, CI, verifier, preserved holdout |
| CTA | “If you work on uncertainty, DRO, or conformal prediction, I’d like to compare notes.” Optional: open to research roles. |

The project is a **research-engineering portfolio piece**, not an alpha claim. The post should make that explicit in the first three lines.

---

## 2. The 12-model lens on the post

| Model | Application to the first post | Decision |
|---|---|---|
| **1. First principles** | What is the post’s job? To signal research judgment and shipping ability, not to maximize likes. | Lead with the process, not the P&L. |
| **2. Inversion** | How could this post hurt credibility? Overclaiming, jargon without translation, “three failures” framing, no proof link, wrong audience. | Add plain-English labels, a release link, and a capability line. |
| **3. Bayesian** | The audience’s prior on “another trading project” is low. Evidence must be concrete and checkable. | Show the paper, CI, verifier, and holdout discipline. |
| **4. Shannon information** | Every slide must add new information. | One idea per slide; cut redundant metrics. |
| **5. Causal hierarchy** | The post cannot claim it will cause job offers. It is a signal, not an intervention. | Say what the work demonstrates, not what it will produce. |
| **6. Parsimony** | One hook, three attempts, one lesson. | Keep the carousel at 6 slides; do not add a fourth model. |
| **7. Fat tails / career risk** | The downside is being read as “no result.” | Frame the negative result as a deliberate, costly-to-fake capability signal. |
| **8. Convexity** | The post should have capped downside and open-ended upside. | Low-cost artifact; no exaggerated claims; link to verifiable work. |
| **9. Reflexivity** | The post sets expectations for future work. | Do not claim more than the repo can defend; keep the holdout untouched. |
| **10. Goodhart** | Do not optimize for likes or impressions. | Optimize for saves, profile visits, paper downloads, and qualified comments. |
| **11. Exploration vs exploitation** | 75% exploit the flagship paper; 25% explore a second format. | Post the carousel first; only later test the card or a video. |
| **12. Bottleneck** | The bottleneck is proof and release, not more content. | Finish the `v1.0.0` release, citation, and license before posting. |

---

## 3. What is already strong

- The hook: **“Three pre-registered attempts. The holdout is still untouched.”**
- The negative-result discipline: three attempts, zero holdout touches.
- The apparatus: frozen protocol, mandatory baseline, information gate, counter-metric gate, CI, verifier.
- The visual narrative: six slides, one idea each.
- The paper: short, honest, with limitations and reproduction commands.

## 4. What is missing before the first post

1. **A public release link.** The post should link to `v1.0.0`, not a raw repository. Create the GitHub release and attach the paper, carousel, card, and one-pager.
2. **A capability line in the caption.** Say what you build, not just what failed.
3. **A plain-English translation of H1/H2/H3.** “Tail-risk hypothesis failed; non-inferiority passed” before the labels.
4. **A stack line.** Purged walk-forward, Ridge baseline, LightGBM quantiles, split conformal, cvxpy/CLARABEL, CI + verifier.
5. **A citation and paper license.** Add `CITATION.cff` and decide the paper/figures license before inviting readers.
6. **One external reader.** Ask one quant/ML peer to read the paper for the strongest objection. Fix only factual errors, not the result.
7. **A soft CTA.** “If you work on uncertainty, DRO, or conformal prediction, I’d like to compare notes.” Add “open to research roles” only if that is true and you want it.

---

## 5. Posting sequence

### Day 0 — release

- Create the `v1.0.0` GitHub release with the paper and visual assets.
- Confirm CI is green.
- Add the release link to the repo description and featured section.

### Day 1 — carousel

- Upload `paper/linkedin_carousel.pdf` as a native document post.
- Use **Version 0 — flagship** from `paper/linkedin_post.md`.
- Put the release link in the first comment.
- Do not add a link in the post body if reach matters.

### Day 3–7 — card

- Post `paper/linkedin_card.png` as a standalone image with a shorter caption.
- Use a different hook: “Calibration is not information.”
- Link the same paper.

### Week 2 — essay

- Publish a 1,200-word essay: “Three pre-registered attempts, zero holdout touches.”
- Use the paper as the technical anchor; the essay is the narrative.

---

## 6. Metrics that matter

| Metric | Why |
|---|---|
| Saves | The strongest signal that someone wants to revisit the work. |
| Profile visits | Intent to learn more about you. |
| Paper downloads / release views | Actual engagement with the artifact. |
| Qualified comments | People who work on uncertainty, DRO, conformal, or evaluation. |
| Inbound conversations | The real career outcome. |

Do not optimize for likes, impressions, or “great post” comments.

---

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Read as “three failures” | Lead with the capability signal: “a process that killed three weak ideas before the holdout.” |
| Jargon excludes general audience | Add plain-English labels before H1/H2/H3 and DRO/CVaR. |
| Post looks like a strategy pitch | State “not investment advice; no alpha claim” in the caption and visual. |
| No proof link | Release first; link the paper and repo. |
| Overclaiming | Use “associated with,” “did not separate,” “stopped before holdout.” |
| Inconsistent future posts | Keep the same labels and holdout discipline in every follow-up. |

---

## 8. The one-line thesis

> **I build pre-registered research pipelines that can tell the difference between a signal and noise — and I’m willing to publish the no.**
