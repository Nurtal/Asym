# Experiment 06: Dunbar-calibrated layering with encounter-only tie formation

Definition: `experiments/06_dunbar_calibrated_scaling.yaml`
(results in `results/dunbar_calibrated_scaling/`, not versioned).

It is experiment 05 (calibrated archetypes, `variants.exploration: ties`) with the
circle thresholds recalibrated to **[0.31, 0.60, 0.82]**; the default is
[0.3, 0.55, 0.8]. Empty start, horizon 1500, burn-in 1000, 3 seeds per condition.

## Calibration

Tool: `experiments/calibrate_layering.py`. Each candidate was screened at N = 200
with one seed and horizon 600 (burn-in 300). The run started from a random
acquaintance network (density 0.2, x ~ U(0.05, 0.3)) to shorten the transient; the
early and late halves of the window differed by at most 7%.

1. **A random search over the thresholds and a decay factor (24 points)** found
   that the thresholds dominate. The inner circle is very sensitive to t3: it
   ranged from 0.04 to 6.2 ties across the range searched.
2. **The closeness distribution is bimodal.** Most ties sit below 0.3, and a second
   peak at 0.85–0.95 holds the inner ties. Thresholds read off its quantiles
   (giving ratios of exactly 3 if the dynamics did not respond) were
   [0.307, 0.652, 0.875]. **They failed: the inner circle collapsed to 0.35.**
3. **The thresholds feed back on the dynamics.** A tie demoted out of the inner
   circle gets the faster close-friend decay and slides down. Raising t3 above
   the high peak removes the peak itself instead of relabelling it. The size of the
   inner circle is therefore set by the budget and the decay ladder, and t3 has to
   sit below the peak for the inner circle to exist.
4. **A grid around t3 = 0.8** gave [0.31, 0.60, 0.82] as the most balanced point:
   layers 2.0 / 5.7 / 15.7 / 42.5, ratios 2.9 / 2.8 / 2.7.

## Results (empty start; time-averaged after burn-in; mean [95% CI] over 3 seeds)

Run on commit 99170fe.

| N | inner | + close | + friends | all ties | ratios |
|---|---|---|---|---|---|
| 100 | 2.11 [2.02, 2.20] | 5.51 [5.27, 5.74] | 15.3 [14.9, 15.7] | 41.7 [41.5, 41.9] | 2.6 / 2.8 / 2.7 |
| 200 | 2.35 [2.21, 2.49] | 5.35 [5.28, 5.42] | 14.8 [14.5, 15.1] | 44.4 [43.5, 45.4] | 2.3 / 2.8 / 3.0 |
| 400 | 2.35 [2.24, 2.45] | 5.24 [5.14, 5.33] | 14.6 [14.4, 14.7] | 45.7 [45.3, 46.2] | 2.2 / 2.8 / 3.1 |

Stationarity: the first and last 100 time units of the window differ by less than 3%.

Per archetype at N = 400 (inner / + close / + friends / all):

| archetype | layers |
|---|---|
| butterfly | 2.0 / 7.7 / 35.9 / 112 |
| loyal_few | 4.7 / 5.9 / 6.8 / 22 |
| transactional | 1.4 / 2.7 / 5.6 / 20 |
| avoidant | 1.3 / 4.6 / 9.9 / 28 |

## Reading

- **The calibration holds from an empty start.** The ratios are 2.2–2.8–3.1 at
  N ≥ 200, against 2.3–2.3–2.9 before recalibration (experiment 05). The two outer
  ratios are now close to 3. The inner ratio stays low (about 2.2–2.6), because
  the inner circle is the stiffest layer (see the calibration feedback above).
- **The layers are almost independent of N.** From N = 200 to N = 400 they change
  by less than 3%, with an inner-circle p-value of 1.0. The changes from N = 100
  come mainly from butterflies running out of people to meet.
- **The absolute sizes stay small** (all ties ≈ 45 rather than Dunbar's 150). Only
  the shape of the hierarchy is calibrated. Larger absolute sizes would need larger
  budgets and encounter rates, or a time-unit mapping.
- **The archetype signatures of experiment 02 survive.** loyal_few has the largest
  inner circle (4.7) and almost no middle layers. butterfly has a wide middle (36
  friends or closer) and over 100 acquaintances. transactional has the smallest
  layers.
