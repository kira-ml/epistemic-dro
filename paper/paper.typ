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
      [github.com/kira-ml/epistemic-dro · CC BY 4.0],
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
    Three pre-registered attempts of uncertainty-aware DRO — and two gates that failed in opposite directions
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
  *Status: one completed negative result and two pre-holdout stops, not a strategy.* v1 is closed (H1 and H3 fail, H2 passes its non-inferiority
  guardrail). v2 and v3 were stopped by frozen pre-holdout information gates. The 2025–2026 holdout was
  never touched. This is a methods study on 72 US-listed ETFs; it makes no alpha, stock-selection,
  causal, or live-deployment claim. Nothing here is investment advice.
]

#v(0.7em)

#block(inset: (left: 6pt, right: 6pt))[
  #set text(size: 9.5pt)
  #set par(leading: 0.64em)
  *Abstract.* Does epistemic uncertainty improve the tail-risk/return trade-off of a distributionally
  robust mean-CVaR portfolio? This paper reports three pre-registered attempts on a point-in-time
  universe of 72 US ETFs. In v1, a Ridge baseline has no detectable out-of-sample linear signal
  (#fmt(b0.r2, 3) pooled $R^2$; mean rank IC #fmt(b0.ic, 3), $t = #fmt(b0.t, 2)$), the original 80% date-level
  mutual-information audit finds no surviving feature among the 13 frozen v1 features (a pooled
  re-evaluation finds weak average dependence but not stability), and a reduced uncertainty-aware DRO does not separate from
  point-estimate DRO: H1 fails, H2 passes its non-inferiority guardrail, H3 fails. v2 replaces bootstrap sigma with conformalized
  LightGBM return quantiles; calibration is good (validation coverage #pct(v2_gate.coverage_val, 1),
  test #pct(v2_gate.coverage_test, 1)), but the uncertainty signal passes only #pct(v2_gate.pass, 1) of
  date-level information tests against an 80% gate. v3 replaces return quantiles with a conditional
  forecast of next-month absolute return; calibration is good on average (#pct(v3_gate.mean_sigma, 2) vs
  #pct(v3_gate.mean_realized, 2)), but the signal passes only #pct(v3_gate.pass, 1) and underperforms
  trailing volatility on development. A synthetic power study shows the 80% date-level gate has
  **zero power** at a 20% $R^2$ signal, while an iid pooled test detects the same signal. But the iid
  pooled test is too permissive: under a block-aware null it cuts 20/21 apparent passes to 3/21, and
  the v2/v3 sigma do not survive. An effect-size audit finds the three block-aware survivors have rank
  IC intervals that include zero; trailing volatility dominates the conditional sigma. No v4 is justified
  on this data. The v1 closure and v2/v3 stops are evidence of **instability**, not proof that no signal exists; and a
  pooled test is not a substitute for a block-aware gate. The contribution is the apparatus: a frozen
  protocol, a mandatory baseline, an information gate, a non-degenerate comparator, a preserved holdout,
  and a clean negative result — plus evidence that the gate itself needs a power and effect-size analysis.
]

#v(0.5em)

// ---------------------------------------------------------------------------
// 1
// ---------------------------------------------------------------------------

= The question

A standard pipeline predicts expected returns [10] and feeds the point estimates into an optimizer.
The optimizer then concentrates in assets whose returns were overestimated — the error-maximization
problem [1]. A distributionally robust mean-CVaR optimizer [3–6] can shrink those bets, and an ML
model that reports *where* it is uncertain could, in principle, tell the optimizer which bets to
shrink. The 1/N portfolio is the mandatory simple comparator [2], and CVaR is the tail-risk
functional [7].

That is the hypothesis. It is not the finding.

The project asks a narrow question: does an epistemic-uncertainty layer improve the tail-risk/return
trade-off of a DRO mean-CVaR portfolio, net of costs, out-of-sample, relative to point-estimate DRO and
simple baselines? The answer is reported under a frozen protocol, with a clean negative result treated
as a successful outcome. The project fails only if it is leaky, non-reproducible, or overclaims.

Three attempts were made. Each had a different object of uncertainty. v1 was closed after its reduced
test; v2 and v3 were stopped by gates written before their results were seen. The 2025–2026 holdout
remains untouched.

// ---------------------------------------------------------------------------
// 2
// ---------------------------------------------------------------------------

= Apparatus

*Data.* A frozen snapshot of 72 liquid US-listed equity ETFs, 2000-01 to 2026-09, built from Yahoo
adjusted total-return prices, FRED `TB3MS`, and the Ken French three-factor plus momentum series
[8, 9]. The
universe is point-in-time: an ETF enters only on or after its provider first-trade date, and eligibility
requires at least 36 months of history, a \$5 price floor, and \$1M average daily dollar volume. Breadth
is 68+ ETFs in every 2010+ month. The snapshot is current-listed, so closed funds are omitted; no
survivorship-free claim is made.

*Features.* Thirteen lagged ETF features in the frozen v1 set: momentum at 1/3/6/12 months,
volatility at 3/12 months, 12-month max drawdown, 12-month dollar volume, 36-month beta, and four
factor exposures. The current code also builds six derived features (downside volatility, skew,
worst month, volatility ratio, volume shock, and 36-month market correlation), but these were added
after the v1 audit and are not part of the v1 result. Every feature at month-end $t$ uses only data
timestamped at or before $t$. The output is cross-sectionally winsorized and ranked, with complete
cases only.

*Protocol.* Monthly walk-forward. A 60-month training window, a 12-month validation window, a one-month
purge, and a 12-month test window [16]. No random splits. Long-only, sum to one, 5% cap, 10 bps one-way
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

*The mean forecast is null.* Ridge B0 [11], 14 folds, 11,328 out-of-sample rows over #b0.months
months with predictions, 2010–2024: pooled OOS $R^2 = #fmt(b0.r2, 3)$, mean monthly rank IC
#fmt(b0.ic, 3), $t = #fmt(b0.t, 2)$. A shuffled-target run gives mean IC #fmt(-0.004, 3),
$t = #fmt(-0.48, 2)$: the null is not an obvious leak.

*The features do not survive.* A date-blocked mutual-information audit over 259 cross-sections of the
13 frozen v1 features finds no feature that beats a permutation null in 80% of dates. The best pass
rate is 0.552 (vol_12m). LightGBM [12] is not justified.

*The reduced DRO does not separate.* Table 1 reports the main result. The reduced M1 re-fits the same
Ridge specification monthly on a rolling 60-month window, so its DRO backtest spans 179 months; the
14-fold B0 diagnostic above has 158 months with predictions. The two paths share the universe,
features and model class, but they are not the same test windows. The uncertainty-aware portfolio has
a slightly higher Sharpe and a marginally smaller drawdown than point-estimate DRO, but the paired
bootstrap intervals include zero for the tail differences. The
#pct(v1_boot.rel_mdd_point, 1) relative max-drawdown improvement is far below the pre-registered 20%
threshold.

#figure(
  table(
    columns: (1.4fr, auto, auto, auto, auto),
    align: (left, right, right, right, right),
    inset: 5pt,
    stroke: none,
    table.hline(stroke: 0.8pt),
    table.header([*Strategy*], [*Net Sharpe*], [*Max DD*], [*CVaR95*], [*Turnover*]),
    table.hline(stroke: 0.4pt),
    [M1 reduced], [#fmt(v1.m1.sharpe, 3)], [#pct(v1.m1.mdd, 2)], [#pct(v1.m1.cvar, 2)], [#fmt(v1.m1.turnover, 2)],
    [B5 point DRO], [#fmt(v1.b5.sharpe, 3)], [#pct(v1.b5.mdd, 2)], [#pct(v1.b5.cvar, 2)], [#fmt(v1.b5.turnover, 2)],
    [1/N], [#fmt(v1.b1.sharpe, 3)], [#pct(v1.b1.mdd, 2)], [#pct(v1.b1.cvar, 2)], [#fmt(v1.b1.turnover, 2)],
    table.hline(stroke: 0.8pt),
  ),
  caption: [v1 reduced DRO, 2010–2024, 179 monthly rebalances from a monthly rolling refit, net of 10 bps. M1 uses a Ridge mean and bootstrap sigma; it is not the original LightGBM ensemble. The 14-fold B0 diagnostic in the text is a separate evaluation path with 158 months with predictions. B5 uses zero sigma; with zero sigma B5 and B3 (CVaR-only) are mathematically identical, so the DRO-vs-no-DRO leg is uninformative. The relevant comparison is M1 versus B5.]
)

B5 is a zero-sigma comparator; with zero sigma it is identical to B3 (CVaR-only), so the DRO-vs-no-DRO leg of H3 is uninformative. The test that matters is M1 versus B5.

#figure(
  image("figures/v1_cumulative.png", width: 100%),
  caption: [Cumulative net excess return for the three headline strategies. This is the metric's input path, not an investable return. The M1 and B5 paths are close; 1/N lags. The point is the absence of separation between M1 and B5, not the level.]
)

*Verdict.* H1 fails: the tail improvement is #pct(v1_boot.rel_mdd_point, 1) relative (90% CI [#pct(v1_boot.rel_mdd_ci.at(0), 1), #pct(v1_boot.rel_mdd_ci.at(1), 1)]), and the CVaR difference interval includes zero. H2 passes its non-inferiority guardrail: the Sharpe difference is +0.018, 90% CI #ci(v1_boot.sharpe_ci.at(0), v1_boot.sharpe_ci.at(1), 3), inside the 0.20 margin. That is not evidence of improvement; it is evidence that the strategy was not materially worse. H3 fails: the uncertainty ablation is within noise. The one positive secondary result is that the DRO/CVaR optimizer beats 1/N on Sharpe and tail metrics; that is the optimizer, not the uncertainty layer.

Strategy-level deflated Sharpe probabilities [15] are reported in `docs/13_final_report.md`; they test each strategy against zero after four trials, **not** M1 against B5. The incremental test is the paired bootstrap, and it fails.

// ---------------------------------------------------------------------------
// 4
// ---------------------------------------------------------------------------

= v2: conformalized quantiles

The second attempt changed the object of uncertainty from bootstrap dispersion to a distributional
forecast. LightGBM [12] quantile regression predicts q05/q50/q95 of next-month excess return, three
seeds are averaged, and split-conformal residual quantiles [13, 14] calibrate the interval on a
12-month validation window. The mean is the calibrated q50; sigma is the interval half-width divided by 1.645. The
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
forecast *next-month absolute excess return* with LightGBM [12] L1 regression and used the forecast as
DRO sigma. This is a conditional tail-risk forecast, not epistemic uncertainty.

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

This is a **post-hoc methods audit**, not part of the original pre-registration. It explains the stops ex post; it does not retroactively promote v2/v3.

#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (right, right, right, right, right, right),
    inset: 5pt,
    stroke: none,
    table.hline(stroke: 0.8pt),
    table.header([*$beta$*], [*$R^2$*], [*MI pass rate*], [*80% MI power*], [*Pooled power*], [*Decile power*]),
    table.hline(stroke: 0.4pt),
    [0.0], [0%], [#pct(gate.mi_pass_00_72, 1)], [#pct(gate.mi_power_00_72, 0)], [#pct(gate.pooled_power_00_72, 0)], [#pct(gate.decile_power_00_72, 0)],
    [0.2], [3.8%], [#pct(gate.mi_pass_02_72, 1)], [#pct(gate.mi_power_02_72, 0)], [#pct(gate.pooled_power_02_72, 0)], [#pct(gate.decile_power_02_72, 0)],
    [0.5], [20%], [#pct(gate.mi_pass_05_72, 1)], [#pct(gate.mi_power_05_72, 0)], [#pct(gate.pooled_power_05_72, 0)], [#pct(gate.decile_power_05_72, 0)],
    table.hline(stroke: 0.8pt),
  ),
  caption: [Gate power at 72 assets and 179 dates, linear signal, 2 seeds. The MI pass rate is the per-date pass rate; the other gate columns are power across the two seeds. The 80% gate has zero power even at a 20% $R^2$ signal. The pooled gate detects that signal in every seed. The decile gate's per-date pass rate is #pct(gate.decile_pass_05_72, 1) at $beta = 0.5$, but its seed-level power is still zero at 72 assets.]
)

At 72 assets, a 20% $R^2$ signal passes only #pct(gate.mi_pass_05_72, 1) of dates; the gate requires
80%, so it never passes. At 150 assets the per-date pass rate rises to 64.8%, still below the threshold.
The pooled gate detects that signal in 100% of seeds at every breadth. The failure is not false
positives — the gate has 0% size under the null — it is **power**. The simulation is deliberately
simple: linear signal, iid errors, two seeds. It establishes the direction of the power problem, not a
universal calibration; a common-factor/autocorrelated size simulation is future work.

The actual development signals tell the same story. Under a pooled, date-blocked MI test, #gate.v1_passes
of the #gate.v1_total features in the current build pass at BH q < 0.05; the v2 sigma passes at
$p = #fmt(gate.v2_pooled_p, 3)$ and the v3 sigma at $p = #fmt(gate.v3_pooled_p, 3)$. The frozen v1 audit
covered 13 features; the pooled re-evaluation includes the six derived features added later.
But the pooled test is not a stability test. It can detect weak average dependence that is not stable
date by date. It does **not** retroactively promote v1/v2/v3, and the holdout remains untouched.

The iid pooled gate is also too permissive. Under a block-permutation null that preserves 6-, 12-, and
24-month blocks, only #gate.block_passes of #gate.block_total signals survive. The v2 sigma has a maximum
block p-value of #fmt(gate.v2_block_max, 3); the v3 sigma #fmt(gate.v3_block_max, 3). Neither survives.
The apparent pooled passes were largely time-series artifacts.

Effect size closes the question. The three block-aware survivors have rank ICs whose 90% block-bootstrap
intervals [17] include zero. The v2 and v3 sigma have strong ICs against future absolute return, but trailing
36-month volatility is stronger still. The conditional uncertainty is redundant with the simple
benchmark.

#figure(
  table(
    columns: (1.2fr, auto, auto),
    align: (left, right, right),
    inset: 5pt,
    stroke: none,
    [*Signal*], [*Mean rank IC*], [*90% block CI*],
    [mom_6m], [#fmt(effect.mom_ic, 3)], [#ci(effect.mom_ci.at(0), effect.mom_ci.at(1), 3)],
    [vol_12m], [#fmt(effect.vol_ic, 3)], [#ci(effect.vol_ci.at(0), effect.vol_ci.at(1), 3)],
    [downside_vol_12m], [#fmt(effect.down_ic, 3)], [#ci(effect.down_ci.at(0), effect.down_ci.at(1), 3)],
    [v2 sigma], [#fmt(effect.v2_ic, 3)], [#ci(effect.v2_ci.at(0), effect.v2_ci.at(1), 3)],
    [v3 sigma], [#fmt(effect.v3_ic, 3)], [#ci(effect.v3_ci.at(0), effect.v3_ci.at(1), 3)],
    [trailing 36m vol], [#fmt(effect.trail_ic, 3)], [#ci(effect.trail_ci.at(0), effect.trail_ci.at(1), 3)],
  ),
  caption: [Development rank IC with 90% block-bootstrap intervals. The three block-aware survivors have intervals that include zero. The conditional sigma is dominated by trailing volatility. No v4 is justified on this data.]
)

*The 80% gate is too strict; the iid pooled gate is too permissive; the survivors have no economic
effect size.* A block-aware pooled gate with a minimum effect size is the defensible middle, and the
effect-size audit says the same thing as the portfolio result: no v4 on this data. The v1 closure and v2/v3 stops
remain evidence of instability, not proof that no signal exists, and the holdout stays untouched.

#figure(
  image("figures/gate_power.png", width: 100%),
  caption: [Left: per-date pass rate versus signal strength at 72 assets. Right: gate power at $beta=0.2$ and $beta=0.5$. The 80% MI gate and the decile gate fail; the iid pooled gate succeeds. But the iid pooled gate is too permissive: on the actual data, a block-aware null cuts 20/21 apparent passes to 3/21.]
)

// ---------------------------------------------------------------------------
// 7
// ---------------------------------------------------------------------------

= Synthesis: why the answer is no on this data

Three mechanisms explain the result.

*The mean signal is weak.* Ridge B0 has no detectable linear OOS signal. The original 80% information
audit finds no surviving feature; a pooled re-evaluation finds weak average dependence but not
stability. If the conditional mean is not reliably predictable, the uncertainty layer has little to
shrink. The binding constraint is the information in the feature set, not the optimizer.

*Uncertainty is easy to calibrate and hard to make informative.* v2 and v3 are both calibrated. v3 has a
clear decile spread. Neither passes a stability gate. Average calibration and cross-sectional spread are
necessary but not sufficient; the signal must be stable date by date.

*Comparison design matters.* A constant sigma is a constant penalty in a long-only, sum-to-one box DRO;
it does not change the optimizer. The first v2 comparator collapsed to CVaR-only for exactly this reason.
The replacement — trailing realized volatility — is non-degenerate and is the right kind of benchmark:
asset-specific, but not conditional on the model being tested.

The gates did their job ex post: they preserved the holdout, and the later block-aware/effect-size
audit supports the stops. The original 80% gate was still underpowered; the stop decision was
defensible, not infallible. A project that only reports the final holdout would have consumed the
2025–2026 sample on a signal that failed its own pre-holdout test. Here the holdout is still available
for a genuinely different model.

// ---------------------------------------------------------------------------
// 8
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
// 9
// ---------------------------------------------------------------------------

= Limitations

- The universe is current-listed; closed funds are omitted. The results are not survivorship-free.
- The ETF cross-section is narrower than a stock universe; power is limited.
- v1's reduced M1 uses bootstrap Ridge sigma, not the original LightGBM ensemble.
- B5 uses zero sigma and is identical to B3 (CVaR-only); the DRO-vs-no-DRO comparison is uninformative.
- The gate power study is a post-hoc, linear/iid, two-seed simulation; it motivates, but does not validate, a block-aware gate.
- Deflated Sharpe is strategy-level; it does not test M1 against B5.
- v2 and v3 never reached the holdout. Their negative results are development-period results.
- The v2/v3 holdout is only 20 months and cannot reliably detect a 20% relative MDD improvement.
- The conditional tail forecast is aleatoric, not epistemic; it is labelled as such.
- The linear-cost model is not a market-impact model. There is no live deployment.

// ---------------------------------------------------------------------------
// 10
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
// 11
// ---------------------------------------------------------------------------

= References

#set text(size: 8.6pt)
#set par(justify: false, leading: 0.50em, hanging-indent: 1.4em)
#set enum(numbering: n => "[" + str(n) + "]")

+ Michaud, R. O. (1989). The Markowitz optimization enigma: is "optimized" optimal?
  *Financial Analysts Journal*, 45(1), 31–42.

+ DeMiguel, V., Garlappi, L., & Uppal, R. (2009). Optimal versus naive diversification:
  how inefficient is the 1/N portfolio strategy? *Review of Financial Studies*, 22(5),
  1915–1953.

+ Ben-Tal, A., & Nemirovski, A. (1998). Robust convex optimization. *Mathematics of
  Operations Research*, 23(4), 769–805.

+ Bertsimas, D., Brown, D. B., & Caramanis, C. (2011). Theory and applications of robust
  optimization. *SIAM Review*, 53(3), 464–501.

+ Delage, E., & Ye, Y. (2010). Distributionally robust optimization under moment
  uncertainty. *Operations Research*, 58(3), 595–612.

+ Mohajerin Esfahani, P., & Kuhn, D. (2018). Data-driven distributionally robust
  optimization using the Wasserstein metric. *Mathematical Programming*, 171(1–2),
  115–166.

+ Rockafellar, R. T., & Uryasev, S. (2000). Optimization of conditional value-at-risk.
  *Journal of Risk*, 2(3), 21–41.

+ Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and
  bonds. *Journal of Financial Economics*, 33(1), 3–56.

+ Carhart, M. M. (1997). On persistence in mutual fund performance. *Journal of Finance*,
  52(1), 57–82.

+ Gu, S., Kelly, B., & Xiu, D. (2020). Empirical asset pricing via machine learning.
  *Review of Financial Studies*, 33(5), 2223–2273.

+ Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: biased estimation for
  nonorthogonal problems. *Technometrics*, 12(1), 55–67.

+ Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017).
  LightGBM: a highly efficient gradient boosting decision tree. *NeurIPS 30*.

+ Vovk, V., Gammerman, A., & Shafer, G. (2005). *Algorithmic Learning in a Random World*.
  Springer.

+ Angelopoulos, A. N., & Bates, S. (2021). A gentle introduction to conformal prediction
  and distribution-free uncertainty quantification. arXiv:2107.07511.

+ Bailey, D. H., & López de Prado, M. (2014). The deflated Sharpe ratio: correcting for
  selection bias, backtest overfitting, and non-normality. *Journal of Portfolio
  Management*, 40(5), 94–107.

+ López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.

+ Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap. *Journal of the
  American Statistical Association*, 89(428), 1303–1313.
