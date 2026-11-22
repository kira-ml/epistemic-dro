#set document(title: "Epistemic DRO — LinkedIn card (Computer Modern)")

#let paper = rgb("#f7f5f0")
#let ink = rgb("#1a1a1a")
#let muted = rgb("#6b6b6b")
#let navy = rgb("#14213d")
#let blue = rgb("#1f5c99")
#let oxblood = rgb("#9c3527")
#let gold = rgb("#b07a1e")
#let white = rgb("#ffffff")
#let rule = rgb("#dddddd")

#set page(
  width: 160mm,
  height: 200mm,
  margin: 10mm,
  fill: paper,
)

#set text(font: "New Computer Modern", size: 9pt, fill: ink, lang: "en")
#set par(justify: false, leading: 0.55em, spacing: 0.6em)

#let kicker(body) = text(size: 7pt, tracking: 0.12em, fill: muted)[#body]

#let project-box(title, verdict, detail, color) = block(
  width: 100%,
  fill: white,
  stroke: 0.5pt + rule,
  inset: (x: 7pt, y: 6pt),
  radius: 3pt,
)[
  #text(size: 11pt, weight: "bold", fill: ink)[#title]
  #v(0.15em)
  #text(size: 8.8pt, weight: "bold", fill: color)[#verdict]
  #v(0.1em)
  #text(size: 8.4pt, fill: muted)[#detail]
]

#v(2mm)

#kicker[EPISTEMIC-AWARE DRO · 72 US ETFs · 2010–2024 · WORKING PAPER]

#v(5mm)
#text(size: 25pt, weight: "bold", fill: ink)[Three pre-registered attempts.]
#v(0.1em)
#text(size: 25pt, weight: "bold", fill: blue)[The holdout is still untouched.]

#v(2mm)
#text(size: 11.5pt, fill: muted)[What I learned trying to make uncertainty pay.]

#v(5mm)
#project-box(
  "v1  Epistemic uncertainty",
  "H1 / H3 fail  ·  H2 non-inferiority pass",
  [Ridge mean + bootstrap σ #linebreak() no stable mean or uncertainty signal],
  oxblood,
)

#v(2mm)
#project-box(
  "v2  Conformal quantiles",
  "Stopped before holdout",
  [coverage 0.899 / 0.859 #linebreak() information gate 65.4% < 80%],
  gold,
)

#v(2mm)
#project-box(
  "v3  Conditional tail risk",
  "Stopped before holdout",
  [calibration 4.29% vs 4.30% #linebreak() information gate 43.0% < 80%],
  gold,
)

#v(4mm)
#block(
  width: 100%,
  fill: blue,
  inset: (x: 8pt, y: 7pt),
  radius: 3pt,
)[
  #text(size: 12.5pt, weight: "bold", fill: white)[Calibration ≠ information. Gates > narratives.]
  #v(0.25em)
  #text(size: 8.6pt, fill: rgb("#dce8f3"))[
    One completed result. Two pre-holdout stops. Zero holdout touches. #linebreak()
    The apparatus is the result.
  ]
]

#v(4mm)
#place(bottom + left)[
  #grid(
    columns: (1fr, auto),
    [
      #text(size: 7.4pt, fill: muted)[Paper + code: github.com/kira-ml/epistemic-dro]
    ],
    [
      #text(size: 7.4pt, fill: muted)[Paper CC BY 4.0]
    ],
  )
  #v(0.6mm)
  #text(size: 6.8pt, fill: rgb("#8a8a8a"))[
    Not investment advice. No alpha claim. No live deployment. Current-listed; not survivorship-free.
  ]
]
