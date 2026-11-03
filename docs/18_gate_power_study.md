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

---

## 5. Interpretation

1. **The 80% gate is a stability filter, not a signal-existence test.** It asks “is this detectable in almost every date?” not “is there an average signal?”
2. **The gate has near-zero power for realistic effect sizes.** At 72 assets, a 20% \(R^2\) signal passes only 39.7% of dates; the gate requires 80%.
3. **The v2/v3 stops are evidence of instability, not proof of no signal.** The actual development signals pass a pooled test, but the pooled test is not enough to justify the holdout.
4. **The original protocol conflated two questions.** A better v4 protocol should pre-register two gates:
   - an **average-information gate** with a minimum effect size and a block-aware null;
   - a **stability gate** with a power justification.
5. **Do not run the holdout retrospectively.** The gate change is a new pre-registration, not a reason to consume the preserved sample.

---

## 6. Limitations

- Synthetic panels are iid across dates; real features and returns have autocorrelation. The pooled gate may be anti-conservative on real data.
- Only 2 seeds per cell; this is a power illustration, not a precise power curve.
- The minimum p-value with 30 permutations is 0.032; stronger permutation resolution is needed for effect-size ranking.
- Statistical dependence is not economic significance. A pooled MI pass does not imply a tradable signal.
- The study does not test the v2/v3 holdout.

---

## 7. Next steps

1. Add autocorrelated and block-bootstrap nulls to the pooled gate.
2. Add a **minimum effect size** to the gate, not just a p-value.
3. Pre-register a two-part gate for any v4:
   - average information with a minimum effect size;
   - stability with a power-justified threshold.
4. Keep the 2025–2026 holdout untouched until the new gate passes.

**This is a methods result, not a licence to promote v1/v2/v3.**
