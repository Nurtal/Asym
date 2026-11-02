# Experiment 18: do the main results survive finer interactions (k = 3)?

Script: `experiments/18_k3_sensitivity.py`. Report: `results/18_k3_sensitivity/report.md`;
raw runs: `results/18_k3_sensitivity/`. Neither is versioned. k = 1 stays the reference
model; this is a sensitivity test.

**Conclusion: most main results hold at k = 3 in the window measured, but this is not yet
a test at stationarity.** The recalibrated k = 3 model is still relaxing at t = 1000–1500,
where its layers match k = 1. Its plateau differs by about 10–13% on the three outer
layers. Exclusive pairing at low budget is the one result that visibly weakens, and the
cause is not identified.

## Question

Experiment 17 found that finer interactions (B × k; η, investment unit and cancellation
drop / k, at the same Q = ηB/δ) reduce the turnover mismatch, but move the layers away from
the calibration. Can k = 3 be recalibrated to the same layers, and do the main results then
hold?

## Protocol

- **Recalibration:** thresholds t1, t2, t3 and a factor `snu` on openness ν. 18 points on
  draw 0, seed 0, with an empty start and the window 1000–1500, as in exp 15. The target is
  k = 1 on the same draw, mean of 3 seeds: 2.11 / 5.51 / 15.27 / 41.69.
- **Controls:** 49 serial runs at seed 0: layers on 3 draws (N = 100, 200), 5 asymmetry
  counterfactuals on 3 draws, collapse and pairing on 2 draws, inverse regime on 3 draws.
- **k = 1 comparison:** the runs of exp 15 with the same draws and seed 0, except the
  inverse regime, which uses the values reported by exp 09 and was not rerun on these
  draws at k = 1.
- **Time mapping:** the measures of exp 17, at k = 1 and k = 3, 2 seeds, window 1000–1500.
- **Start test:** both starts up to t = 3000 at k = 1 and k = 3 (draw 0, seed 0).

### Protocol errors found on the way

- The first calibration (30 points, random start, window 300–700) reached a score of 0.006,
  but gave 47.9 ties instead of 41.0 under the protocol of the controls. A run from a random
  start up to t = 1500 showed a transient. The 9 control runs made with that point were
  discarded (`results/18_k3_sensitivity/protocol_mismatch/`).
- The collapse and pairing blocks of exp 15 measure over 300–600, inside that transient.
  At k = 3 they were measured over 1000–1500 instead.
- The second calibration, at 1000–1500, is still inside the transient. Only the start test
  showed this, after the controls had run. **The controls were not rerun.**

## Recalibration

Chosen point: t1 = 0.315, t2 = 0.58, t3 = 0.822, `snu` = 0.39. Openness therefore falls by
a factor of more than 2.5, which is a large change on its own.

| draw 0 | inner | + close | + friends | all |
|---|---|---|---|---|
| target (k = 1) | 2.11 | 5.51 | 15.27 | 41.69 |
| k = 3, seed 0, window 1000–1500 | 2.25 | 5.63 | 14.83 | 40.97 |
| k = 3 from t = 2500 to 3000, same start | 2.11 | 4.98 | 13.32 | 45.91 |

## Finding: k = 3 relaxes slowly, and the inner circle keeps its start

Layers at seed 0, draw 0, N = 100:

| k | start | 500–1000 | 1000–1500 | 1500–2000 | 2000–2500 | 2500–3000 |
|---|---|---|---|---|---|---|
| 1 | empty | 2.15 / 5.67 / 15.4 / 40.1 | 2.14 / 5.37 / 15.4 / 42.0 | 2.10 / 5.53 / 15.6 / 41.2 | 2.19 / 5.60 / 15.4 / 41.0 | 2.16 / 5.46 / 15.4 / 41.9 |
| 1 | random | 1.96 / 5.69 / 15.7 / 41.2 | 1.97 / 5.56 / 15.4 / 41.7 | 1.92 / 5.59 / 15.8 / 41.6 | 1.92 / 5.46 / 15.6 / 42.1 | 1.93 / 5.52 / 15.8 / 41.9 |
| 3 | empty | 3.02 / 8.11 / 14.4 / 29.5 | 2.28 / 5.89 / 14.7 / 40.4 | 2.13 / 5.06 / 13.8 / 44.9 | 2.11 / 4.97 / 13.5 / 45.3 | 2.11 / 4.98 / 13.3 / 45.9 |
| 3 | random | 1.34 / 7.18 / 16.3 / 38.6 | 1.30 / 5.64 / 14.9 / 45.2 | 1.33 / 5.33 / 14.4 / 46.4 | 1.38 / 5.27 / 14.2 / 46.4 | 1.42 / 5.16 / 14.3 / 46.5 |

- **Relaxation is much slower at k = 3.** k = 1 has settled by 500–1000. k = 3 takes until
  about t = 2000. This run cannot separate the effect of k from that of `snu`: lower
  openness also slows the filling of the network.
- **The match to k = 1 at 1000–1500 is a passing point.** On the plateau, + close is 9%
  lower, + friends 13% lower and all ties 10% higher than at k = 1.
- **The inner circle depends on the start at t = 3000:** 2.11 (empty) against 1.42 (random)
  at k = 3, and a smaller gap at k = 1 (2.16 against 1.93). The random-start inner circle is
  still rising slowly at k = 3, so very slow relaxation and true hysteresis cannot be told
  apart here. The outer layers converge to within about 7%.
- The same inner gap appears in the collapse block, at q = 1: 1.35 and 1.39 at k = 3 from a
  random start. At k = 1, the collapse runs give 1.95 and 2.20.

## Results

These compare k = 3 at 1000–1500 with k = 1, so they describe a state that is close to the
plateau but not on it.

### Layers (3 draws, seed 0)

| N | k | inner | + close | + friends | all | μ | unreciprocated |
|---|---|---|---|---|---|---|---|
| 100 | 1 | 2.28 | 6.14 | 16.39 | 42.14 | 0.826 | 0.254 |
| 100 | 3 | 2.26 | 6.61 | 16.24 | 41.27 | 0.802 | 0.254 |
| 200 | 1 | 2.29 | 5.36 | 15.24 | 45.50 | 0.891 | 0.273 |
| 200 | 3 | 2.32 | 5.98 | 14.45 | 43.18 | 0.839 | 0.294 |

- N = 100: no paired difference is detectable, including on the two draws not used for the
  calibration. With 3 draws, the intervals are wide (+ close +0.47 ± 0.67).
- N = 200: + close +0.62 ± 0.56, + friends −0.79 ± 0.47, all −2.32 ± 1.32, μ −0.052 ± 0.051,
  unreciprocated +0.021 ± 0.015. These are small differences, but the calibration carries
  over less well to N = 200.
- The closeness histogram keeps its shape: a low mode at 0.05–0.15, a shoulder around 0.40
  and a high mode around 0.90.

### Asymmetry counterfactuals (N = 100, 3 draws)

| condition | k = 1 difference | k = 3 difference |
|---|---|---|
| no_deficit | −0.127 ± 0.043 | −0.136 ± 0.061 |
| same_decay | −0.093 ± 0.002 | −0.083 ± 0.027 |
| same_allocation | −0.050 ± 0.016 | −0.067 ± 0.003 |
| average_only | −0.195 ± 0.041 | −0.217 ± 0.044 |
| misperception_centred | +0.020 ± 0.009 | +0.033 ± 0.020 |

**This holds.** The order is the same, and the two mechanisms still target different pairs.
Without the expectation gap, butterfly → transactional falls from 0.63 to 0.06. Without the
decay gap, butterfly → avoidant falls from 0.57 to 0.05. Both falls match k = 1.

### Collapse (2 draws, q = 0.5, 1, 2)

- **This holds.** q explains 0.977–0.990 of the variance of log(layer) on the B and δ routes,
  against 0.971–0.990 at k = 1 on the same cells.
- **Proposition 2 holds:** 24 of 24 signs of the η route, in each draw.
- **The B/δ gaps keep most of their pattern and are smaller on + close and + friends:**
  +0.13 at q = 0.5, against +0.24–0.35 at k = 1. At q = 2 the inner gap is +0.02 and +0.12
  (k = 1: −0.04 and −0.01). This comparison mixes windows and has few runs, so it does not
  show that finer interactions reduce the gaps.

### Pairing (2 draws, share of agents in an exclusive pair)

| budget | profile | k = 1, draws 0, 1 | k = 3, draws 0, 1 |
|---|---|---|---|
| × 1 | transactional | 0.04, 0.06 | 0.02, 0.13 |
| × 1 | avoidant | 0.00, 0.01 | 0.01, 0.01 |
| × 0.3 | loyal_few | 0.73, 0.69 | 0.75, 0.52 |
| × 0.3 | avoidant | 0.54, 0.53 | 0.42, 0.25 |
| × 0.3 | butterfly | 0.16, 0.22 | 0.23, 0.15 |
| × 0.3 | transactional | 0.24, 0.34 | 0.14, 0.04 |

**This partly holds.** Exclusive pairs stay rare at calibrated budgets and appear at low
budget, with loyal_few highest. But avoidant and transactional agents pair less at k = 3 in
both draws. Lower openness, the later window and the slow relaxation are all candidates, and
this experiment does not separate them. The ordering of profiles is not established at
k = 3 with 2 draws and one seed.

### Inverse regime (3 draws)

| N | k = 3, μ per draw | mean | k = 1 (exp 09) |
|---|---|---|---|
| 12 | −0.31, −0.41, −0.51 | −0.41 | −0.34 |
| 24 | −0.18, −0.22, −0.15 | −0.18 | −0.12 |
| 48 | +0.48, +0.40, +0.39 | +0.43 | +0.42 |

**This holds.** The sign change between N = 24 and N = 48 is unchanged, in every draw.

## Time mapping

Both at window 1000–1500, random start, 2 seeds.

| measure | k = 1 | k = 3, recalibrated |
|---|---|---|
| layers | 2.02 / 5.60 / 15.45 / 41.88 | 1.40 / 5.48 / 14.85 / 45.30 |
| mismatch, contact vs close+ turnover | 68× | 7× |
| close+ loss per year at contact mapping | 75% | 13% |
| hours per interaction | 11.3 | 2.1 |
| social h/week | 420 | 77 |
| interactions to friend | 8 | 43 |
| weeks to friend at contact mapping | 8 | 71 |
| loss hazard, close+ / friend+ | 1.13 | 0.72 |
| contact ratio, close+ / friend+ | 2.02 | 1.87 |
| new ties gone within 200 units | 0.81 | 0.83 |

- **The trade-off of exp 17 survives recalibration.** Turnover and hours improve by a large
  factor, and time to friendship worsens by about the same factor. There is still no single
  mapping.
- **The k = 3 row of exp 17 was not distorted much by its early window:** 9×, 17%, 86 h and
  72 weeks there. This was not rechecked at k = 6, whose relaxation should be slower still.
- **The hazard ratio of 0.72 hints at the expected gradient**, with close ties more stable
  than friends, but 2 seeds cannot support a claim, and the ties are still drifting.
- **The contact gradient stays weak:** 1.87 against 4.35 for weekly versus monthly.

## Consequences for the paper

- Keep k = 1 as the reference model. Finer interactions cannot be claimed as a better
  calibration, because there is no stationary recalibrated point yet.
- The results on asymmetry, collapse, Proposition 2 and the inverse regime can be described
  as qualitatively insensitive to k = 3 at the window measured, with this limit stated. They
  should not be described as invariant.
- Report exclusive pairing as more sensitive than the other results.
- State that the inner circle depends on the start, by about 11% at k = 1 (quantified in
  `19-start-dependence.md`) and more at k = 3 (one seed and draw).

## Limits

- Not a stationary test, as described above. A proper one needs a recalibration on the
  plateau, at about 10–13 min per point, and about 8 h of controls at horizon 3000 or more.
  Reaching 41.7 ties there would need a lower `snu`, which may slow relaxation further.
- One seed per run, and 2–3 draws. These comparisons can reveal large changes, but they do
  not establish equivalence. With 3 draws t = 4.3, and with 2 draws no interval is given.
- k = 1 collapse and pairing are measured over 300–600, and k = 3 over 1000–1500.
- The start test has one draw and one seed.
- The calibration was selected on a single noisy run, and several points were equally good.
- `snu` is confounded with k throughout: the k = 3 model differs from k = 1 in both.
- Runs: 3.8 h for the controls and 36 min for the start test, with one process; each k = 3
  run at N = 100 takes about 4.5 min per 1500 units.
