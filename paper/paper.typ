#import "generated/numbers.typ": *

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
#let ci(low, high, digits) = "[" + fmt(low, digits) + ", " + fmt(high, digits) + "]"

#set document(
  title: "The holdout is still untouched",
  author: "Ken Ira Lacson Talingting",
  keywords: ("pre-registration", "uncertainty", "DRO", "CVaR", "negative result", "ETFs"),
)
#set page(
  paper: "a4",
  margin: (top: 24mm, bottom: 22mm, x: 24mm),
  footer: context [
    #set text(size: 7.5pt, fill: luma(115))
    #grid(
      columns: (1fr, auto),
      [github.com/kira-ml/epistemic-dro],
      align(right)[#counter(page).display("1")],
    )
  ],
)
#set text(font: "Libertinus Serif", size: 10.4pt, lang: "en", hyphenate: true)
#set par(justify: true, leading: 0.68em, spacing: 1.0em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => block(above: 1.5em, below: 0.5em)[
  #set text(size: 13pt, weight: "bold")
  #it
  #v(-0.3em)
  #line(length: 100%, stroke: 0.4pt + luma(170))
]
#show heading.where(level: 2): it => block(above: 1.2em, below: 0.35em)[
  #set text(size: 11pt, weight: "bold")
  #it
]
#set figure(numbering: "1")
#set table(stroke: none, inset: (x: 4pt, y: 3pt))
#show figure.caption: it => block(width: 100%, above: 0.4em)[
  #set text(size: 8.6pt)
  #set par(justify: false, leading: 0.55em)
  #align(left, it)
]

// ---------------------------------------------------------------------------
// Front matter
// ---------------------------------------------------------------------------

#align(center)[
  #text(size: 20pt, weight: "bold")[The holdout is still untouched]
  #v(0.25em)
  #text(size: 11pt)[
    Three pre-registered tests of uncertainty-aware DRO — and two gates that failed in opposite directions
  ]
  #v(0.85em)
  #text(size: 10pt)[Ken Ira Lacson Talingting]
  #v(0.10em)
  #text(size: 8.5pt, fill: luma(100))[Working paper · November 2026]
]

#v(0.8em)

#block(
  width: 100%,
  fill: luma(246),
  stroke: 0.5pt + luma(200),
  inset: 9pt,
)[
  #set text(size: 9pt)
  #set par(leading: 0.62em)
  *Status: negative results, not a strategy.* v1 is closed (H1 and H3 fail, H2 passes). v2 and v3 were
  stopped by frozen pre-holdout information gates. The 2025–2026 holdout was never touched. This is a
  methods study on 72 US-listed ETFs; it makes no alpha, stock-selection, causal, or live-deployment
  claim. Nothing here is investment advice.
]

#v(0.7em)

#block(inset: (left: 6pt, right: 6pt))[
  #set text(size: 9.5pt)
  #set par(leading: 0.64em)
  *Abstract.* Does epistemic uncertainty improve the tail-risk/return trade-off of a distributionally
  robust mean-CVaR portfolio? This paper reports three pre-registered attempts on a point-in-time
  universe of 72 US ETFs. In v1, a Ridge baseline has no detectable out-of-sample linear signal
  (#fmt(b0.r2, 3) pooled $R^2$; mean rank IC #fmt(b0.ic, 3), $t = #fmt(b0.t, 2)$), the original 80% date-level
  mutual-information audit finds no surviving feature (a pooled re-evaluation finds weak average
  dependence but not stability), and a reduced uncertainty-aware DRO does not separate from
  point-estimate DRO: H1 fails, H2 passes, H3 fails. v2 replaces bootstrap sigma with conformalized
  LightGBM return quantiles; calibration is good (validation coverage #pct(v2_gate.coverage_val, 1),
  test #pct(v2_gate.coverage_test, 1)), but the uncertainty signal passes only #pct(v2_gate.pass, 1) of
  date-level information tests against an 80% gate. v3 replaces return quantiles with a conditional
  forecast of next-month absolute return; calibration is excellent (#pct(v3_gate.mean_sigma, 2) vs
  #pct(v3_gate.mean_realized, 2)), but the signal passes only #pct(v3_gate.pass, 1) and underperforms
  trailing volatility on development. A synthetic power study shows the 80% date-level gate has
  **zero power** at a 20% $R^2$ signal, while an iid pooled test detects the same signal. But the iid
  pooled test is too permissive: under a block-aware null it cuts 20/21 apparent passes to 3/21, and
  the v2/v3 sigma do not survive. The v1/v2/v3 stops are evidence of **instability**, not proof that no
  signal exists; and a pooled test is not a substitute for a block-aware gate. The contribution is the
  apparatus: a frozen protocol, a mandatory baseline, an information gate, a non-degenerate comparator,
  a preserved holdout, and a clean negative result — plus evidence that the gate itself needs a power
  analysis.
]

#v(0.5em)

// ---------------------------------------------------------------------------
// 1
// ---------------------------------------------------------------------------

= The question

A standard pipeline predicts expected returns and feeds the point estimates into an optimizer. The
optimizer then concentrates in assets whose returns were overestimated — the error-maximization
problem. A distributionally robust mean-CVaR optimizer can shrink those bets, and an ML model that
reports *where* it is uncertain could, in principle, tell the optimizer which bets to shrink.

That is the hypothesis. It is not the finding.

The project asks a narrow question: does an epistemic-uncertainty layer improve the tail-risk/return
trade-off of a DRO mean-CVaR portfolio, net of costs, out-of-sample, relative to point-estimate DRO and
simple baselines? The answer is reported under a frozen protocol, with a clean negative result treated
as a successful outcome. The project fails only if it is leaky, non-reproducible, or overclaims.

Three attempts were made. Each had a different object of uncertainty. Each was stopped by a gate that
was written before the result was seen. The 2025–2026 holdout remains untouched.

// ---------------------------------------------------------------------------
// 2
// ---------------------------------------------------------------------------

= Apparatus

*Data.* A frozen snapshot of 72 liquid US-listed equity ETFs, 2000-01 to 2026-09, built from Yahoo
adjusted total-return prices, FRED `TB3MS`, and the Ken French three-factor plus momentum series. The
universe is point-in-time: an ETF enters only on or after its provider first-trade date, and eligibility
requires at least 36 months of history, a \$5 price floor, and \$1M average daily dollar volume. Breadth
is 68+ ETFs in every 2010+ month. The snapshot is current-listed, so closed funds are omitted; no
survivorship-free claim is made.

*Features.* Nineteen lagged ETF features: momentum at 1/3/6/12 months, volatility at 3/12 months,
downside volatility, skew, worst month, volatility ratio, volume shock, 36-month market correlation,
12-month drawdown, dollar volume, 36-month beta, and four factor exposures. Every feature at month-end
$t$ uses only data timestamped at or before $t$. The output is cross-sectionally winsorized and
ranked, with complete cases only.

*Protocol.* Monthly walk-forward. A 60-month training window, a 12-month validation window, a one-month
purge, and a 12-month test window. No random splits. Long-only, sum to one, 5% cap, 10 bps one-way
costs as the primary case, with 5/20/50 bps sensitivity. Net Sharpe is the primary metric; max drawdown
and CVaR95 are guardrails. The solver is CLARABEL; a solver failure is fatal, with no equal-weight
fallback.

*Gates.* Five rules did most of the work:

+ a mandatory Ridge B0 baseline before any complex model;
+ a date-blocked mutual-information audit with a permutation null;
+ a target-shuffling falsification test;
+ a counter-metric gate requiring Sharpe, max drawdown, and CVaR95 to pass together; and
+ a pre-holdout information gate for any new uncertainty signal.

The last gate is why the holdout survived.

// ---------------------------------------------------------------------------
// 3
// ---------------------------------------------------------------------------

= v1: epistemic uncertainty

The first attempt used the original design: Ridge B0 mean, a five-model bootstrap uncertainty proxy, and
a box DRO with a CVaR penalty. The original LightGBM ensemble was not fitted because the information
audit failed first.

*The mean forecast is null.* Ridge B0, 14 folds, 11,328 out-of-sample rows, 2010–2024: pooled OOS
$R^2 = #fmt(b0.r2, 3)$, mean monthly rank IC #fmt(b0.ic, 3), $t = #fmt(b0.t, 2)$. A shuffled-target
run gives mean IC #fmt(-0.004, 3), $t = #fmt(-0.48, 2)$: the null is not an obvious leak.

*The features do not survive.* A date-blocked mutual-information audit over 259 cross-sections finds
no feature that beats a permutation null in 80% of dates. The best pass rate is 0.552. LightGBM is not
justified.

*The reduced DRO does not separate.* Table 1 reports the main result. The uncertainty-aware portfolio
has a slightly higher Sharpe and a marginally smaller drawdown than point-estimate DRO, but the paired
bootstrap intervals include zero for the tail differences. The 0.4% relative max-drawdown improvement
is far below the pre-registered 20% threshold.

#figure(
  table(
    columns: (1.4fr, auto, auto, auto, auto),
    align: (left, right, right, right, right),
    inset: 5pt,
    stroke: none,
    [*Strategy*], [*Net Sharpe*], [*Max DD*], [*CVaR95*], [*Turnover*],
    [M1 reduced], [#fmt(v1.m1.sharpe, 3)], [#pct(v1.m1.mdd, 2)], [#pct(v1.m1.cvar, 2)], [#fmt(v1.m1.turnover, 2)],
    [B5 point DRO], [#fmt(v1.b5.sharpe, 3)], [#pct(v1.b5.mdd, 2)], [#pct(v1.b5.cvar, 2)], [#fmt(v1.b5.turnover, 2)],
    [1/N], [#fmt(v1.b1.sharpe, 3)], [#pct(v1.b1.mdd, 2)], [#pct(v1.b1.cvar, 2)], [#fmt(v1.b1.turnover, 2)],
  ),
  caption: [v1 reduced DRO, 2010–2024, 179 months, net of 10 bps. M1 uses a Ridge mean and bootstrap sigma; it is not the original LightGBM ensemble.]
)

#figure(
  image("figures/v1_cumulative.png", width: 100%),
  caption: [Cumulative net excess return for the three headline strategies. This is the metric's input path, not an investable return. The M1 and B5 paths are close; 1/N lags. The point is the absence of separation between M1 and B5, not the level.]
)

*Verdict.* H1 fails: the tail improvement is 0.4% relative (90% CI [#pct(v1_boot.rel_mdd_ci.at(0), 1), #pct(v1_boot.rel_mdd_ci.at(1), 1)]), and the CVaR difference interval includes zero. H2 passes: the Sharpe difference is +0.018, 90% CI #ci(v1_boot.sharpe_ci.at(0), v1_boot.sharpe_ci.at(1), 3), inside the 0.20 margin. H3 fails: the uncertainty ablation is within noise. The one positive secondary result is that the DRO/CVaR optimizer beats 1/N on Sharpe and tail metrics; that is the optimizer, not the uncertainty layer.

// ---------------------------------------------------------------------------
// 4
// ---------------------------------------------------------------------------

= v2: conformalized quantiles

The second attempt changed the object of uncertainty from bootstrap dispersion to a distributional
forecast. LightGBM quantile regression predicts q05/q50/q95 of next-month excess return, three seeds
are averaged, and split-conformal residual quantiles calibrate the interval on a 12-month validation
window. The mean is the calibrated q50; sigma is the interval half-width divided by 1.645. The
comparator is non-degenerate: each asset's trailing 36-month realized volatility. A constant sigma was
rejected before the holdout because a constant penalty is weight-invariant and collapses to CVaR-only.

Calibration worked. Validation coverage was #pct(v2_gate.coverage_val, 1); development test coverage
was #pct(v2_gate.coverage_test, 1). But coverage is not information. The pre-holdout gate asked whether
the conformal sigma beats a date-blocked permutation null in at least 80% of dates. It passed
#pct(v2_gate.pass, 1). The holdout was not touched.

#figure(
  image("figures/gate_pass_rates.png", width: 88%),
  caption: [Pre-holdout information gates. v2 and v3 both fail the frozen 80% rule. The gate is deliberately strict: it prevents a calibrated but unstable signal from consuming the last untouched holdout.]
)

// ---------------------------------------------------------------------------
// 5
// ---------------------------------------------------------------------------

= v3: conditional tail risk

The third attempt changed the object again. Instead of epistemic uncertainty or a return quantile, it
forecast *next-month absolute excess return* with LightGBM L1 regression and used the forecast as DRO
sigma. This is a conditional tail-risk forecast, not epistemic uncertainty.

The development result is negative: M1 Sharpe #fmt(v3.m1_sharpe, 3), max drawdown #pct(v3.m1_mdd, 2),
CVaR95 #pct(v3.m1_cvar, 2), against trailing volatility at #fmt(v3.b5_sharpe, 3), #pct(v3.b5_mdd, 2),
and #pct(v3.b5_cvar, 2). The conditional forecast also trades more. It loses on every headline metric.

The calibration is the interesting part. Mean sigma is #pct(v3_gate.mean_sigma, 2) against mean realized
absolute return #pct(v3_gate.mean_realized, 2); the correlation is #fmt(v3_gate.corr, 2); the top-decile
realized absolute return exceeds the bottom decile by #pct(v3_gate.decile_spread, 2). A model can be
well calibrated and cross-sectionally informative on average and still fail a stability gate. It
passed #pct(v3_gate.pass, 1) of date-level tests. The holdout was not touched.

#figure(
  image("figures/v3_calibration.png", width: 88%),
  caption: [v3 predicted tail-risk deciles against mean realized absolute excess return. The monotone spread is real; the per-date information is not stable enough for the frozen gate.]
)

// ---------------------------------------------------------------------------
// 6
// ---------------------------------------------------------------------------

= Were the gates wrong in both directions?

The v2/v3 stops were driven by a pre-holdout gate that required a signal to beat a date-blocked
permutation null in at least 80% of dates. That rule controls false positives, but its power was never
tested. We simulated panels with a known linear signal $y = beta x + epsilon$, 179 dates, and 50–150
assets; $beta = 0.2$ is $R^2 approx 3.8$ percent, $beta = 0.5$ is $R^2 approx 20$ percent.

#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (right, right, right, right, right, right),
    inset: 5pt,
    stroke: none,
    [*$beta$*], [*$R^2$*], [*MI pass rate*], [*80% MI gate*], [*Pooled gate*], [*Decile gate*],
    [0.0], [0%], [#pct(gate.mi_pass_00_72, 1)], [#pct(gate.mi_power_00_72, 0)], [#pct(gate.pooled_power_00_72, 0)], [#pct(gate.decile_power_00_72, 0)],
    [0.2], [3.8%], [#pct(gate.mi_pass_02_72, 1)], [#pct(gate.mi_power_02_72, 0)], [#pct(gate.pooled_power_02_72, 0)], [0%],
    [0.5], [20%], [#pct(gate.mi_pass_05_72, 1)], [#pct(gate.mi_power_05_72, 0)], [#pct(gate.pooled_power_05_72, 0)], [#pct(gate.decile_power_05_72, 0)],
  ),
  caption: [Gate power at 72 assets and 179 dates, linear signal, 2 seeds. The 80% gate has zero power even at a 20% $R^2$ signal. The pooled gate detects the same signal in every seed. The decile gate is more powerful than the MI gate but still fails at 72 assets.]
)

At 72 assets, a 20% $R^2$ signal passes only #pct(gate.mi_pass_05_72, 1) of dates; the gate requires
80%, so it never passes. At 150 assets the per-date pass rate rises to 64.8%, still below the threshold.
The pooled gate detects the same signal in 100% of seeds at every breadth. The failure is not false
positives — the gate has 0% size under the null — it is **power**.

The actual development signals tell the same story. Under a pooled, date-blocked MI test, #gate.v1_passes
of #gate.v1_total v1 features pass at BH q < 0.05; the v2 sigma passes at $p = #fmt(gate.v2_pooled_p, 3)$
and the v3 sigma at $p = #fmt(gate.v3_pooled_p, 3)$.
But the pooled test is not a stability test. It can detect weak average dependence that is not stable
date by date. It does **not** retroactively promote v1/v2/v3, and the holdout remains untouched.

The iid pooled gate is also too permissive. Under a block-permutation null that preserves 6-, 12-, and
24-month blocks, only #gate.block_passes of #gate.block_total signals survive. The v2 sigma has a maximum
block p-value of #fmt(gate.v2_block_max, 3); the v3 sigma #fmt(gate.v3_block_max, 3). Neither survives.
The apparent pooled passes were largely time-series artifacts.

*The 80% gate is too strict; the iid pooled gate is too permissive.* A block-aware pooled gate with a
minimum effect size is the defensible middle. The v1/v2/v3 stops remain evidence of **instability**, not
proof that no signal exists. A v4 protocol should pre-register that two-part gate: average information
with a minimum effect size and a block-aware null, plus a stability gate with a power justification.

#figure(
  image("figures/gate_power.png", width: 100%),
  caption: [Left: per-date pass rate versus signal strength at 72 assets. Right: gate power at $beta=0.2$ and $beta=0.5$. The 80% MI gate and the decile gate fail; the iid pooled gate succeeds. But the iid pooled gate is too permissive: on the actual data, a block-aware null cuts 20/21 apparent passes to 3/21.]
)

// ---------------------------------------------------------------------------
// 7
// ---------------------------------------------------------------------------

= Synthesis: why the answer is no

Three mechanisms explain the result.

*The mean signal is weak.* Ridge B0 has no detectable linear OOS signal. The original 80% information
audit finds no surviving feature; a pooled re-evaluation finds weak average dependence but not
stability. If the conditional mean is not reliably predictable, the uncertainty layer has little to
shrink. The binding constraint is the feature set, not the optimizer.

*Uncertainty is easy to calibrate and hard to make informative.* v2 and v3 are both calibrated. v3 has a
clear decile spread. Neither passes a stability gate. Average calibration and cross-sectional spread are
necessary but not sufficient; the signal must be stable date by date.

*Comparison design matters.* A constant sigma is a constant penalty in a long-only, sum-to-one box DRO;
it does not change the optimizer. The first v2 comparator collapsed to CVaR-only for exactly this reason.
The replacement — trailing realized volatility — is non-degenerate and is the right kind of benchmark:
asset-specific, but not conditional on the model being tested.

The gates did their job. A project that only reports the final holdout would have consumed the
2025–2026 sample on a signal that failed its own pre-holdout test. Here the holdout is still available
for a genuinely different model.

// ---------------------------------------------------------------------------
// 7
// ---------------------------------------------------------------------------

= What would change the answer

Not a new feature search on the same data. A credible positive result needs a new pre-registration with:

+ a feature set that survives a pre-registered information audit;
+ an uncertainty model with a *stable* pre-holdout signal, not just good average calibration;
+ a non-degenerate comparator;
+ a new or untouched holdout; and
+ a decision rule fixed before the holdout is seen.

The most plausible next object is not epistemic uncertainty about the mean. It is a different target:
tail risk, volatility, or a longer horizon where the signal-to-noise ratio is less brutal. v3 is the
first step in that direction, and it failed for a specific, diagnosable reason.

// ---------------------------------------------------------------------------
// 8
// ---------------------------------------------------------------------------

= Limitations

- The universe is current-listed; closed funds are omitted. The results are not survivorship-free.
- The ETF cross-section is narrower than a stock universe; power is limited.
- v1's reduced M1 uses bootstrap Ridge sigma, not the original LightGBM ensemble.
- v2 and v3 never reached the holdout. Their negative results are development-period results.
- The v2/v3 holdout is only 20 months and cannot reliably detect a 20% relative MDD improvement.
- The conditional tail forecast is aleatoric, not epistemic; it is labelled as such.
- The linear-cost model is not a market-impact model. There is no live deployment.

// ---------------------------------------------------------------------------
// 9
// ---------------------------------------------------------------------------

= Reproducibility

The code, frozen protocols, gates, and aggregate results are in the repository. Raw snapshots are
gitignored. The main commands are:

```bash
python scripts/build_snapshot.py --force
python scripts/check_data.py
python scripts/run_baseline.py
python scripts/run_information_audit.py
python scripts/run_dro_experiment.py
python scripts/analyze_dro_experiment.py
python scripts/run_v2_experiment.py --period dev
python scripts/run_v2_uncertainty_audit.py
python scripts/run_v3_experiment.py --period dev
python scripts/run_v3_sigma_audit.py
python scripts/build_paper.py
pytest -q
ruff check .
```

The v2/v3 holdout commands are deliberately omitted: the frozen gates did not pass, so the holdout
must not be run retrospectively.

// ---------------------------------------------------------------------------
// 10
// ---------------------------------------------------------------------------

= References

#set text(size: 8.8pt)
#set par(justify: false, leading: 0.55em)

Bailey, D. H., & López de Prado, M. (2014). The Deflated Sharpe Ratio. *Journal of Portfolio Management*, 40(5), 94–107.

Ben-Tal, A., & Nemirovski, A. (1998). Robust Convex Optimization. *Mathematics of Operations Research*, 23(4), 769–805.

Bertsimas, D., Brown, D. B., & Caramanis, C. (2011). Theory and Applications of Robust Optimization. *SIAM Review*, 53(3), 464–501.

Delage, E., & Ye, Y. (2010). Distributionally Robust Optimization Under Moment Uncertainty. *Operations Research*, 58(3), 595–612.

Fama, E. F., & French, K. R. (2015). A Five-Factor Asset Pricing Model. *Journal of Financial Economics*, 116(1), 1–22.

Gu, S., Kelly, B., & Xiu, D. (2020). Empirical Asset Pricing via Machine Learning. *Review of Financial Studies*, 33(5), 2223–2273.

Lakshminarayanan, B., Pritzel, A., & Blundell, C. (2017). Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles. *NeurIPS 30*.

López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.

Mohajerin Esfahani, P., & Kuhn, D. (2018). Data-driven Distributionally Robust Optimization Using the Wasserstein Metric. *Mathematical Programming*, 171(1–2), 115–166.

Rockafellar, R. T., & Uryasev, S. (2000). Optimization of Conditional Value-at-Risk. *Journal of Risk*, 2(3), 21–41.

Vovk, V., Gammerman, A., & Shafer, G. (2005). *Algorithmic Learning in a Random World*. Springer.

Angelopoulos, A. N., & Bates, S. (2021). A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification. arXiv:2107.07511.
