# Experiment 15: robustness across seeds and population draws

Script: `experiments/15_robustness.py`. Report: `results/15_robustness/report.md`; raw
runs: `results/15_robustness/runs.jsonl`. Neither is versioned. 216 runs, no failures.
57 runs were made with 8 workers before the machine stopped; the other 159 were made
with one worker. A run does not depend on the worker count.

## Question

Earlier experiments mostly used one population draw and 3–5 simulation seeds. Do their
claims survive when the population itself is redrawn? The unit of replication here is
the **population draw** (`population.seed`), and intervals are 95% t-intervals over
draws.

| block | source | draws × seeds | conditions |
|---|---|---|---|
| layers | exp 06 | 5 × 3 | N = 100, 200 |
| asymmetry | exp 12 | 4 × 2 | 5 counterfactuals, plus `misperception_centred` |
| collapse | exp 11 | 2 × 3 | 4 routes, 5 values of q |
| pairing | exp 14 | 4 × 2 (mixed), 2 × 2 (homogeneous) | key cells |

With two draws a t-interval is uninformative (t = 12.7), so those blocks give both draw
means instead.

## Main finding: the draw matters more than the seed

The population draw accounts for most of the run-to-run variance: 0.87–0.99 for the
unreciprocated share, 0.77–0.96 for the +close, +friends and all-ties layers, and
0.53–0.65 for the inner circle.

**Intervals over seeds of a single draw, as in experiments 06 and 12, are therefore too
narrow as statements about the model.** For example, exp 12 gave an unreciprocated share
of 0.244 [0.238, 0.250] at N = 200, where the interval over draws is 0.271 ± 0.023. The
point estimates are compatible, but the exp 12 interval is about four times too narrow.

## 1. Calibrated layering

| N | inner | + close | + friends | all | ratios | μ |
|---|---|---|---|---|---|---|
| 100 | 2.28 ± 0.13 | 6.12 ± 0.52 | 16.4 ± 0.91 | 42.1 ± 0.71 | 2.7 / 2.7 / 2.6 | 0.825 ± 0.028 |
| 200 | 2.33 ± 0.08 | 5.35 ± 0.17 | 15.3 ± 0.39 | 45.8 ± 1.3 | 2.3 / 2.9 / 3.0 | 0.891 ± 0.015 |

- **The calibration survives redrawing.** Ratios stay close to 3, and the inner ratio
  stays the lowest at N = 200, as in exp 06.
- **Independence of N needs a qualification at N = 100.** Between N = 100 and N = 200,
  the inner circle does not change detectably (p = 0.43), but +close falls by 13%
  (p = 0.011), +friends falls by 7% (p = 0.025) and all ties rise by 9% (p = 0.0004).
  These p-values are uncorrected; with a Bonferroni threshold of 0.0125 for the four
  tests, the +friends difference is no longer significant.
- **N = 100 is a finite-size case for butterflies.** They hold 88 ties of 99 possible
  alters at N = 100, against 106 at N = 200. At least part of the rise in all ties
  reflects this saturation.
- This experiment does not include N = 400. The statement "layers change by less than
  3% from N = 200 to N = 400" still rests on one draw (exp 06).

## 2. Asymmetry counterfactuals (N = 100)

| condition | unreciprocated | difference from baseline, paired by draw | p |
|---|---|---|---|
| baseline | 0.257 ± 0.021 | | |
| no_deficit | 0.123 ± 0.018 | −0.133 ± 0.030 | 0.0008 |
| same_decay | 0.163 ± 0.026 | −0.093 ± 0.006 | 2e-05 |
| same_allocation | 0.203 ± 0.028 | −0.053 ± 0.004 | 4e-05 |
| average_only | 0.064 ± 0.018 | −0.192 ± 0.025 | 0.0001 |
| misperception (biased) | 0.227 ± 0.020 | −0.029 ± 0.015 | 0.008 |
| misperception_centred | 0.273 ± 0.025 | +0.017 ± 0.007 | 0.005 |

- **The ordering of exp 12 holds across draws:** the expectation gap, then the decay
  gap, then the allocation gap, and a floor from individual noise. The paired differences
  are much tighter than the absolute intervals, because draws move all conditions
  together.
- **The two mechanisms still target different pairs.** Without the expectation gap,
  butterfly → transactional falls from 0.67 to 0.07 and loyal_few → transactional from
  0.44 to 0.01. Without the decay gap, butterfly → avoidant falls from 0.51 to 0.06.
- **The misperception confound is resolved.** The fall in exp 12 came from the bias:
  π = 0 with σ_p = 0.5 gives a mean perception of 1.13. With π = −σ_p²/2 the mean
  perception stays at the baseline level, and the same noise *raises* the share slightly
  (+0.017 ± 0.007). Perception noise at this level is a minor source of unreciprocated
  ties, well below the three structural gaps.
- These comparisons are at N = 100, where butterflies are close to saturation (§1). At
  N = 200 the baseline share is 0.271 ± 0.023, compatible with N = 100.

## 3. Maintenance collapse (2 draws)

- **Collapse:** q explains 0.982–0.984 of the variance of log(layer) on the B, δ and
  mixed routes pooled over both draws, and at least 0.983 within each draw. With the η
  route the figures for the three inner layers stay at 0.975–0.979, and all ties drop to
  0.862, as in exp 11.
- **Exchangeability is approximate, and the gaps are systematic.** R² hides them. The
  table gives log(layer under δ / layer under B) for draw 0 and draw 1:

  | q | inner | + close | + friends | all |
  |---|---|---|---|---|
  | 0.50 | +0.27, +0.28 | +0.33, +0.27 | +0.24, +0.23 | −0.15, −0.14 |
  | 0.71 | +0.14, +0.15 | +0.14, +0.10 | +0.08, +0.08 | −0.06, −0.07 |
  | 1.41 | −0.01, −0.04 | −0.08, −0.06 | −0.08, −0.06 | +0.02, +0.03 |
  | 2.00 | −0.02, −0.03 | −0.16, −0.16 | −0.13, −0.14 | +0.03, +0.05 |

  The gaps reach about 30% at q = 0.5, and both draws give the same sign in every cell.
  For scale, the inner circle changes about tenfold over the range of q. The paper should
  therefore say that B and δ collapse to first order, not that they are exchangeable.
- **Proposition 2 passes a stronger test.** All 24 sign comparisons of the η route
  (inner circle, all ties and high-mode share, against B and against δ, at the four values
  of q ≠ 1) hold in each draw separately.

## 4. Pairing

- **Calibrated budgets:** exclusive pairs stay rare in the mixed population, at most
  0.048 ± 0.029 (transactional). This slightly loosens the "at most 4%" of exp 14.
- **Budget × 0.3:** loyal_few 0.727 ± 0.029, confirming exp 14 (0.74). Avoidant agents
  reach 0.479 ± 0.079, transactional 0.274 ± 0.048 and butterflies 0.218 ± 0.083.
- **Homogeneous cells (2 draws)** agree between draws: 0.009 at B × 1 and β = 3, 0.46 at
  B × 0.3 and β = 3, and at B × 0.15, 0 / 0.65 / 0.78 for β = 0.5 / 1.5 / 3.

## Limits

- Only two draws for the collapse and the homogeneous pairing cells: their agreement is
  informative, but it does not estimate the spread over draws.
- The asymmetry conditions have 4 draws and the baseline 5; paired differences use the
  four shared draws.
- Not covered: exp 07 (stochastic switching), exp 10 (Morris, single seed) and N = 400.
