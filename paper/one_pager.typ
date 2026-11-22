#set document(title: "Epistemic DRO — Institutional Research Note")

#let ivory = rgb("#F6F1E7")
#let paper = rgb("#FBF8F2")
#let ink = rgb("#101820")
#let navy = rgb("#0B1F33")
#let slate = rgb("#5C6B73")
#let gold = rgb("#A98754")
#let oxblood = rgb("#6E2B2B")
#let rule = rgb("#CFC6B8")
#let white = rgb("#FFFFFF")

#let serif = ("New Computer Modern", "Liberation Serif")
#let sans = ("Arial", "DejaVu Sans")

#set page(width: 210mm, height: 297mm, margin: 0pt, fill: ivory)
#set text(font: serif, size: 8.4pt, fill: ink)
#set par(leading: 0.53em, spacing: 0.65em)

#let label(body, color: gold) = text(font: sans, size: 6.6pt, weight: "bold", fill: color, tracking: 0.12em)[#body]

#let section(title, color: navy) = block(
  width: 100%,
  stroke: (top: 0.7pt + ink),
  inset: (top: 4pt),
)[
  #label(title, color: color)
]

#let fact(value, label) = block(
  width: 100%,
  stroke: (left: 0.4pt + rule),
  inset: (x: 7pt, y: 4pt),
)[
  #text(font: serif, size: 17pt, weight: "bold", fill: navy)[#value]
  #v(0.05em)
  #text(font: sans, size: 6.8pt, fill: slate)[#label]
]

// ---------------------------------------------------------------------------
// MASTHEAD
// ---------------------------------------------------------------------------
#block(
  width: 100%,
  fill: navy,
  inset: (x: 14mm, y: 3.5mm),
)[
  #set text(font: sans, size: 6.4pt)
  #grid(
    columns: (1fr, auto),
    [
      #text(weight: "bold", tracking: 0.12em, fill: rgb("#D9C7A6"))[
        INDEPENDENT RESEARCH · QUANTITATIVE METHODS
      ]
    ],
    [
      #text(fill: rgb("#D9C7A6"))[NOVEMBER 2026]
    ],
  )
]

#block(inset: (x: 14mm, y: 7mm))[
  #grid(
    columns: (1fr, auto),
    gutter: 8mm,
    [
      #text(font: sans, size: 6.7pt, weight: "bold", fill: gold, tracking: 0.12em)[
        EPISTEMIC DRO · EVALUATION STUDY
      ]
      #v(0.35em)
      #text(font: serif, size: 26pt, weight: "bold", fill: ink)[
        Calibration is not information.
      ]
      #v(0.25em)
      #line(length: 100%, stroke: 0.8pt + gold)
      #v(0.25em)
      #text(size: 9pt, fill: slate)[
        Three pre-registered attempts to make ML uncertainty pay in a distributionally
        robust mean–CVaR portfolio. The 2025–2026 holdout remains untouched.
      ]
    ],
    [
      #align(right)[
        #text(font: sans, size: 6.4pt, weight: "bold", fill: oxblood)[RESEARCH NOTE]
        #v(0.1em)
        #text(font: sans, size: 6.4pt, fill: slate)[NOV 2026]
      ]
    ],
  )
]

// ---------------------------------------------------------------------------
// KEY FACTS
// ---------------------------------------------------------------------------
#block(
  width: 100%,
  stroke: (top: 0.8pt + ink, bottom: 0.4pt + rule),
)[
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    fact("72", "US ETFs"),
    fact("3", "pre-registered attempts"),
    fact("2", "pre-holdout stops"),
    fact("0", "holdout touches"),
  )
]

// ---------------------------------------------------------------------------
// EXECUTIVE SUMMARY
// ---------------------------------------------------------------------------
#block(inset: (x: 14mm, y: 6mm))[
  #grid(
    columns: (1.55fr, 0.85fr),
    gutter: 9mm,
    [
      #section("EXECUTIVE SUMMARY", color: navy)
      #v(0.3em)
      #text(size: 8.5pt)[
        The project tests whether ML epistemic uncertainty improves the tail-risk /
        return trade-off of a distributionally robust mean–CVaR portfolio, net of
        costs, out of sample. Three pre-registered attempts: one completed negative
        result, two pre-holdout stops, and a preserved 2025–2026 holdout.
      ]
    ],
    [
      #section("KEY TAKEAWAYS", color: oxblood)
      #v(0.25em)
      #text(size: 8.1pt)[
        • Calibration is not information. \
        • The gate was underpowered. \
        • Power the gate before spending the holdout. \
        • No v4; the holdout is untouched.
      ]
    ],
  )
]

// ---------------------------------------------------------------------------
// EXHIBIT 1
// ---------------------------------------------------------------------------
#block(inset: (x: 14mm, y: 3mm))[
  #grid(
    columns: (auto, 1fr),
    gutter: 5mm,
    [
      #text(size: 6.8pt, weight: "bold", fill: gold, tracking: 0.1em)[EXHIBIT 1]
    ],
    [
      #text(size: 7pt, fill: slate)[
        Information gates and treatment gaps · pre-registered bar shown
      ]
    ],
  )
  #v(0.3em)
  #image("figures/onepager_evidence.png", width: 100%)
  #v(0.2em)
  #text(size: 6.9pt, fill: slate)[
    *Different metrics. Same evaluation logic: the pre-registered bar decides.*
    Both Epistemic DRO attempts are well calibrated but fail the information gate;
    Robustfolio’s positive point estimate remains below the materiality bar.
  ]
  #v(0.15em)
  #text(size: 6.5pt, fill: slate)[
    Source: Epistemic DRO published aggregate audits; Robustfolio published outcomes.
  ]
]

// ---------------------------------------------------------------------------
// EVIDENCE TABLE
// ---------------------------------------------------------------------------
#block(inset: (x: 14mm, y: 5mm))[
  #section("EVIDENCE", color: navy)
  #v(0.3em)
  #block[
    #set text(font: sans, size: 7.4pt)
    #table(
      columns: (auto, 0.85fr, auto, 1.45fr),
      inset: (x: 4pt, y: 3.5pt),
      stroke: (top: 0.8pt + ink, bottom: 0.5pt + ink, rest: 0.4pt + rule),
      align: left,
      [*Attempt*], [*Object of uncertainty*], [*Status*], [*Result*],
      [*v1*], [Ridge mean + bootstrap σ], [
        #text(size: 6.5pt, weight: "bold", fill: oxblood)[NEGATIVE]
      ], [
        H1/H3 fail; H2 non-inferiority passes. No stable mean or uncertainty signal.
      ],
      [*v2*], [Conformal LightGBM quantiles], [
        #text(size: 6.5pt, weight: "bold", fill: gold)[STOPPED]
      ], [
        Coverage 89.9% / 85.9%. Gate 65.4% < 80%. Stopped before holdout.
      ],
      [*v3*], [Conditional tail risk], [
        #text(size: 6.5pt, weight: "bold", fill: gold)[STOPPED]
      ], [
        Calibration 4.29% vs 4.30%. Gate 43.0% < 80%. Trailing volatility dominates.
      ],
    )
  ]
]

// ---------------------------------------------------------------------------
// CONTEXT AND DECISION
// ---------------------------------------------------------------------------
#block(inset: (x: 14mm, y: 5mm))[
  #grid(
    columns: (1fr, 1fr),
    gutter: 9mm,
    [
      #section("RELATED WORK · ROBUSTFOLIO", color: gold)
      #v(0.25em)
      #text(size: 7.7pt)[
        Robustfolio applies the same evaluation logic to portfolio construction:
        seven constructions, 168 out-of-sample months, eight pre-registered gates.
        Black–Litterman has the highest point estimate, but its +0.064 gap is below
        the 0.20 materiality bar; both treatments fail. The run is exploratory because
        the blind test was lost. The projects are separate; the shared object is the
        evaluation apparatus.
      ]
      #v(0.2em)
      #text(font: sans, size: 5.9pt, weight: "bold", fill: gold, tracking: 0.08em)[
        COMPARATOR · PRE-REGISTRATION · MULTIPLE TESTING · HOLDOUT
      ]
    ],
    [
      #section("WHAT WOULD CHANGE THE ANSWER", color: oxblood)
      #v(0.25em)
      #text(size: 7.7pt)[
        A new pre-registration with a feature set that survives an information audit,
        a stable pre-holdout signal, a non-degenerate comparator, and an untouched
        holdout. Not another feature search on this data.
      ]
    ],
  )
]

// ---------------------------------------------------------------------------
// CONTRIBUTION + FOOTER
// ---------------------------------------------------------------------------
#block(inset: (x: 14mm, y: 4mm))[
  #set text(font: sans)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(0.35em)
  #text(size: 7.6pt)[
    *Contributions.* Pre-registered protocol · completed negative result ·
    gate-power, block-null, and effect-size audits · open-source code, aggregate
    results, and paper · preserved holdout.
  ]
  #v(0.35em)
  #grid(
    columns: (1fr, auto),
    gutter: 4mm,
    [
      #text(size: 6.6pt, fill: slate)[
        Paper · github.com/kira-ml/epistemic-dro/blob/main/paper/mini_paper.pdf
        \ Code · github.com/kira-ml/epistemic-dro
      ]
    ],
    [
      #align(right)[
        #text(size: 6.6pt, fill: slate)[CC BY 4.0 paper · MIT code]
      ]
    ],
  )
  #v(0.2em)
  #text(size: 6.3pt, fill: slate)[
    Working paper. Not investment advice. No alpha claim. No live deployment.
    Current-listed ETF universe; not survivorship-free.
  ]
]
