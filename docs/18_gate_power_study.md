# Gate Power Study

**Status:** Development methods study (2026-11-03)
**Scope:** Does the 80% date-level information gate have enough power at 50–150 assets?
**Holdout:** 2025–2026 untouched.

---

## 1. Why this study exists

v2 and v3 were stopped by a pre-holdout gate that required a signal to beat a date-blocked permutation null in at least **80% of dates**. That rule controlled false positives, but its **power** was never tested.

If the gate has low power, a real but modest signal would be stopped. The v2/v3 stops would then be evidence of **instability**, not evidence of **no signal**. That distinction matters for the project's conclusion and for any future pre-registration.

---

## 2. Design

Synthetic monthly panels:

- assets: 50, 72, 150;
- dates: 179;
- signal: linear \(y = \beta x + \epsilon\), or quadratic \(y = \beta(x^2 - 1) + \epsilon\);
- \(\beta \in \{0, 0.2, 0.5\}\);
- noise: standard normal;
- 2 seeds per cell;
- 30 permutations per date;
- BH-FDR q < 0.05;
- gate: pass rate ≥ 0.80.

Effect sizes: \(\beta=0.2\) is \(R^2 \approx 3.8\%\); \(\beta=0.5\) is \(R^2 \approx 20\%\).

Three gates:

1. **80% date-level MI gate** — the original rule.
2. **Pooled MI gate** — within-date-centered pooled MI with a date-blocked permutation null, one p-value.
3. **Decile-spread gate** — top-minus-bottom decile mean, per date, 80% pass rule.

---

## 3. Results at 72 assets, 179 dates, linear signal

| \(\beta\) | \(R^2\) | MI pass rate | **80% MI gate power** | **Pooled gate power** | Decile pass rate | Decile gate power |
|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 0% | 3.4% | 0% | 0% | 2.5% | 0% |
| 0.2 | 3.8% | 6.4% | **0%** | **100%** | 16.8% | 0% |
| 0.5 | 20% | 39.7% | **0%** | **100%** | 73.7% | 0% |

The 80% gate never passes, even at a 20% \(R^2\) signal. The pooled gate detects the same signal in every seed. The decile gate is more powerful than the MI gate but still fails at 72 assets.

### Breadth effect at \(\beta=0.5\)

| Assets | MI pass rate | 80% MI gate | Pooled gate | Decile gate |
|---:|---:|---:|---:|---:|
| 50 | 33.8% | 0% | 100% | 0% |
| 72 | 39.7% | 0% | 100% | 0% |
| 150 | 64.8% | 0% | 100% | 100% |

More breadth raises the per-date pass rate, but the 80% gate still fails at 150 assets.

### Non-linear signal

At 72 assets and \(\beta=0.5\), the quadratic signal has a 45.8% MI pass rate and **0%** gate power; the pooled gate detects it in 100% of seeds. The decile gate is weak for the quadratic signal (8.1% pass rate).

### Null behaviour

At \(\beta=0\), the MI gate has 0% false positives; the pooled gate also has 0% false positives in the tested seeds. The 80% rule is conservative, not broken. The problem is power, not size.

---

## 4. Actual development signals under a pooled test

The pooled gate was applied to the real development data, without the holdout:

| Signal | Pooled MI | p-value | Passes q<0.05? |
|---|---:|---:|---|
| v1 features (18 of 19) | 0.012–0.120 | 0.032 (minimum) | **Yes** |
| v2 conformal sigma | 0.070 | 0.032 | **Yes** |
| v3 conditional sigma | 0.054 | 0.032 | **Yes** |

The v1 feature that does not pass is `volume_shock_1m` (p = 0.161). The other 18 pass at BH q = 0.034.

**Caveats:**

- With 30 permutations, p = 0.032 is the **minimum possible p-value**. The test cannot distinguish “weak” from “strong” dependence at that resolution.
- The pooled test is not a stability test. It can detect weak average dependence that is not stable date by date.
- The v1 features are correlated with each other; 18 “passes” are not 18 independent signals.
- The pooled test was not part of the original pre-registration. It does **not** retroactively promote v2/v3 to the holdout.

### 4.2 Block-aware null

The iid pooled test is anti-conservative when the panel is autocorrelated. We repeated the test with a **block-permutation null** that preserves contiguous 6-, 12-, and 24-month blocks of the target. This keeps time-series structure but breaks the cross-date alignment with the feature.

| Signal set | iid pooled passes | Block-aware passes |
|---|---:|---:|
| 19 v1 features + v2/v3 sigma | **20 / 21** | **3 / 21** |

The three survivors are `mom_6m`, `vol_12m`, and `downside_vol_12m`. The v2 sigma fails every block length (max p = 0.119); the v3 sigma fails every block length (max p = 0.396).

This is the key correction: the iid pooled test was too permissive. Most of the apparent pooled passes were time-series artifacts, not cross-sectional information. The v2/v3 stops remain defensible.

The right gate is therefore neither the 80% date-level rule (too strict) nor the iid pooled test (too permissive). It is a **block-aware pooled gate with a minimum effect size**, plus a stability criterion whose power is declared.

---

## 5. Interpretation

1. **The 80% gate is a stability filter, not a signal-existence test.** It asks “is this detectable in almost every date?” not “is there an average signal?”
2. **The gate has near-zero power for realistic effect sizes.** At 72 assets, a 20% \(R^2\) signal passes only 39.7% of dates; the gate requires 80%.
3. **The v2/v3 stops are evidence of instability, not proof of no signal.** The actual development signals pass an iid pooled test, but a block-aware null cuts 20/21 passes to 3/21; v2/v3 sigma do not survive. The iid pooled test is too permissive, not enough to justify the holdout.
4. **The original protocol conflated two questions.** A better v4 protocol should pre-register two gates:
   - an **average-information gate** with a minimum effect size and a block-aware null;
   - a **stability gate** with a power justification.
5. **Neither gate is right alone.** The 80% rule is too strict; the iid pooled test is too permissive. The block-aware pooled gate is the defensible middle.
6. **Do not run the holdout retrospectively.** The gate change is a new pre-registration, not a reason to consume the preserved sample.

---

## 6. Limitations

- Synthetic panels are iid across dates; real features and returns have autocorrelation. The iid pooled gate is anti-conservative on the actual data; the block-aware null corrects it but uses only three block lengths.
- Only 2 seeds per cell; this is a power illustration, not a precise power curve.
- The minimum p-value with 30 permutations is 0.032; stronger permutation resolution is needed for effect-size ranking. The block study uses 100 permutations.
- Statistical dependence is not economic significance. A block-aware MI pass does not imply a tradable signal.
- The study does not test the v2/v3 holdout.

---

## 7. Next steps

1. ~~Add autocorrelated and block-bootstrap nulls to the pooled gate.~~ **Done:** block lengths 6/12/24; only 3/21 signals survive; v2/v3 sigma do not.
2. Add a **minimum effect size** to the gate, not just a p-value.
3. Add a common-factor/autocorrelated **size simulation** to validate the block-aware null itself.
4. Pre-register a two-part gate for any v4:
   - average information with a minimum effect size and a block-aware null;
   - stability with a power-justified threshold.
5. Keep the 2025–2026 holdout untouched until the new gate passes.

**This is a methods result, not a licence to promote v1/v2/v3.**
