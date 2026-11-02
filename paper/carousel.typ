#import "generated/numbers.typ": *

#let accent = rgb("#1f5c99")
#let red = rgb("#9c3527")
#let amber = rgb("#b07a1e")
#let muted = rgb("#6b6b6b")
#let ink = rgb("#1a1a1a")
#let paper = rgb("#f7f5f0")

#let fmt(x, digits) = {
  let s = str(calc.round(x, digits: digits))
  if s.len() > 0 and s.at(s.len() - 1) == "." { s = s.slice(0, s.len() - 1) }
  let parts = s.split(".")
  let out = if parts.len() == 1 {
    if digits == 0 { s } else { s + "." + "000000".slice(0, digits) }
  } else {
    let have = parts.at(1).len()
    if have < digits { s + "000000".slice(0, digits - have) } else { s }
  }
  out.replace("-", "−")
}
#let pct(x, digits) = fmt(x * 100, digits) + "%"

#set page(width: 540pt, height: 675pt, margin: 38pt, fill: paper)
#set text(font: "New Computer Modern", size: 14pt, fill: ink, lang: "en")
#set par(justify: false, leading: 0.65em, spacing: 0.9em)

#let eyebrow(x) = text(size: 9pt, fill: muted, tracking: 1.2pt)[#x]
#let footer = place(bottom + left, text(size: 8pt, fill: muted)[github.com/kira-ml/epistemic-dro · not investment advice])

// 1 -------------------------------------------------------------------------
#v(70pt)
#eyebrow[EPISTEMIC-AWARE DRO · 72 US ETFs · 2010–2024]
#v(22pt)
#text(size: 31pt, weight: "bold")[Three pre-registered attempts.]
#v(3pt)
#text(size: 31pt, weight: "bold", fill: accent)[The holdout is still untouched.]
#v(22pt)
#text(size: 17pt, fill: muted)[What I learned trying to make uncertainty pay.]
#v(95pt)
#text(size: 11pt, fill: accent, weight: "bold")[Swipe →]
#footer

#pagebreak()

// 2 -------------------------------------------------------------------------
#eyebrow[THE QUESTION]
#v(14pt)
#text(size: 25pt, weight: "bold")[Can uncertainty improve a DRO portfolio?]
#v(16pt)
#text(size: 14pt)[A mean-CVaR optimizer can shrink bets when the forecast is uncertain. The hypothesis: an ML uncertainty layer should improve the tail-risk / return trade-off, net of costs.]
#v(12pt)
#text(size: 14pt)[I tested it three ways. Each was frozen before the holdout. Each was stopped by a gate.]
#v(18pt)
#block(fill: white, stroke: 0.6pt + rgb("#dddddd"), inset: 12pt)[
  #text(size: 12pt)[*v1* epistemic uncertainty → H1/H3 fail, H2 pass]
  #v(4pt)
  #text(size: 12pt)[*v2* conformal quantiles → gate 65.4%]
  #v(4pt)
  #text(size: 12pt)[*v3* conditional tail risk → gate 43.0%]
]
#footer

#pagebreak()

// 3 -------------------------------------------------------------------------
#eyebrow[V1 · EPISTEMIC UNCERTAINTY]
#v(14pt)
#text(size: 24pt, weight: "bold")[The mean signal was not there.]
#v(14pt)
#text(size: 13pt)[Ridge B0, 2010–2024: pooled OOS #fmt(b0.r2, 3) $R^2$; mean rank IC #fmt(b0.ic, 3), $t = #fmt(b0.t, 2)$.]
#v(8pt)
#text(size: 13pt)[A date-blocked information audit found no feature surviving the 80% rule. The reduced DRO did not separate from point-estimate DRO.]
#v(16pt)
#table(
  columns: (1.6fr, auto, auto, auto),
  align: (left, right, right, right),
  inset: 5pt,
  stroke: none,
  [*Strategy*], [*Sharpe*], [*Max DD*], [*CVaR95*],
  [M1 reduced], [#fmt(v1.m1.sharpe, 3)], [#pct(v1.m1.mdd, 1)], [#pct(v1.m1.cvar, 1)],
  [B5 point DRO], [#fmt(v1.b5.sharpe, 3)], [#pct(v1.b5.mdd, 1)], [#pct(v1.b5.cvar, 1)],
  [1/N], [#fmt(v1.b1.sharpe, 3)], [#pct(v1.b1.mdd, 1)], [#pct(v1.b1.cvar, 1)],
)
#v(10pt)
#text(size: 12pt, fill: red, weight: "bold")[H1 / H3 fail · H2 pass]
#text(size: 11pt, fill: muted)[No alpha claim. The DRO/CVaR optimizer beat 1/N; the uncertainty layer did not separate.]
#footer

#pagebreak()

// 4 -------------------------------------------------------------------------
#eyebrow[V2 · CONFORMAL QUANTILES]
#v(14pt)
#text(size: 24pt, weight: "bold")[Calibration worked. Information did not.]
#v(14pt)
#text(size: 13pt)[LightGBM quantile regression at q05/q50/q95, three seeds, split-conformal calibration. Coverage was #pct(v2_gate.coverage_val, 1) on validation and #pct(v2_gate.coverage_test, 1) on development test.]
#v(8pt)
#text(size: 13pt)[The frozen gate asked whether the conformal sigma carries stable date-level information. It passed #pct(v2_gate.pass, 1) against an 80% bar.]
#v(14pt)
#image("figures/gate_pass_rates.png", width: 100%)
#v(8pt)
#text(size: 12pt, fill: amber, weight: "bold")[Stopped before the 2025–2026 holdout.]
#footer

#pagebreak()

// 5 -------------------------------------------------------------------------
#eyebrow[V3 · CONDITIONAL TAIL RISK]
#v(14pt)
#text(size: 24pt, weight: "bold")[A calibrated forecast can still be uninformative.]
#v(14pt)
#text(size: 13pt)[LightGBM L1 forecast of next-month absolute excess return. Mean sigma #pct(v3_gate.mean_sigma, 2) vs realized #pct(v3_gate.mean_realized, 2). Correlation #fmt(v3_gate.corr, 2). Top-minus-bottom decile spread #pct(v3_gate.decile_spread, 2).]
#v(8pt)
#text(size: 13pt)[It passed #pct(v3_gate.pass, 1) of date-level information tests and underperformed trailing volatility on development.]
#v(12pt)
#image("figures/v3_calibration.png", width: 100%)
#v(6pt)
#text(size: 12pt, fill: amber, weight: "bold")[Stopped before the holdout. Still untouched.]
#footer

#pagebreak()

// 6 -------------------------------------------------------------------------
#eyebrow[WHAT I LEARNED]
#v(18pt)
#text(size: 27pt, weight: "bold")[Calibration ≠ information.]
#v(3pt)
#text(size: 27pt, weight: "bold", fill: accent)[Gates > narratives.]
#v(18pt)
#text(size: 13pt)[*The mean signal is the binding constraint.* A better optimizer cannot rescue a weak forecast.]
#v(8pt)
#text(size: 13pt)[*Stability is the hard part.* Average calibration and a decile spread are not enough.]
#v(8pt)
#text(size: 13pt)[*Preserve the holdout.* Three attempts, zero holdout touches. The apparatus is the result.]
#v(14pt)
#block(fill: accent, inset: 12pt)[
  #text(size: 12pt, fill: white, weight: "bold")[Paper + code: github.com/kira-ml/epistemic-dro]
]
#footer
