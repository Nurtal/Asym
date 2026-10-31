# Experiment 05: layering scaling with encounter-only tie formation

Definition: `experiments/05_tie_exploration_scaling.yaml`
(results in `results/tie_exploration_scaling/`, not versioned). Run on commit 63ff15a.

It is the calibrated population of experiment 02 with `variants.exploration: ties`:

- exploration invitations go only to existing ties;
- new ties form only through encounters, at rate ν_i per agent, independent of N;
- empty start, horizon 1500, burn-in 1000, 3 seeds per condition.

## Why

Experiment 02 found that the outer layer grows with N and the middle layers
shrink, so its near-Dunbar ratios held only at N ≈ 100. Counting events showed the
cause:

- **The encounter rate itself does not depend on N:** 0.069 encounters per agent per
  time unit at N = 100, and 0.067 at N = 200.
- **Exploration invitations to random strangers are a second tie-formation
  channel.** Under the baseline, an ε-invitation goes to a uniform agent, who at
  large N is usually a stranger. That channel formed 0.19 new ties per agent per
  time unit at N = 100 and 0.30 at N = 200.

## Results (time-averaged after burn-in; mean [95% CI] over 3 seeds)

| N | inner | + close | + friends | all ties | ratios |
|---|---|---|---|---|---|
| 100 | 2.74 [2.53, 2.96] | 7.64 [7.59, 7.70] | 16.1 [15.7, 16.4] | 41.2 [40.4, 42.0] | 2.8 / 2.1 / 2.6 |
| 200 | 2.87 [2.57, 3.16] | 7.01 [6.72, 7.31] | 15.8 [15.6, 15.9] | 44.7 [44.2, 45.2] | 2.4 / 2.3 / 2.8 |
| 400 | 3.02 [2.92, 3.13] | 6.80 [6.64, 6.95] | 15.4 [15.1, 15.8] | 45.4 [45.3, 45.5] | 2.3 / 2.3 / 2.9 |

For comparison, experiment 02 with the baseline exploration had an outer layer of
49.6 → 62.1 → 70.8 and an outer ratio of 3.3 → 5.8 over the same range of N.

The layers are stationary over the burn-in window: the first and last 100 time
units differ by less than 2%.

Per archetype (means over seeds; inner / + close / + friends / all):

| N | butterfly | loyal_few | transactional | avoidant |
|---|---|---|---|---|
| 100 | 3.5 / 16.2 / 40.0 / 86 | 4.5 / 5.4 / 6.3 / 26 | 1.2 / 3.2 / 6.5 / 23 | 1.7 / 5.7 / 11.5 / 30 |
| 400 | 3.0 / 11.6 / 38.4 / 111 | 5.5 / 6.5 / 7.3 / 22 | 1.6 / 3.3 / 5.8 / 20 | 2.0 / 5.8 / 10.2 / 28 |

## Reading

- **With tie formation through encounters only, the layered structure is close to
  independent of N.**
  - From N = 200 to N = 400, every layer changes by less than 6%. The outer layer
    goes from 44.7 to 45.4, against 62 to 71 under the baseline.
  - The layer ratios settle at about 2.3–2.9 for all N.
  - What limits the acquaintance layer is now the encounter rate times the
    lifetime of an unmaintained tie, and neither depends on N.
- **The remaining change between N = 100 and N = 200 is a small-population effect.**
  Butterflies (ν = 0.15) keep about 86 ties at N = 100, close to the 99 possible
  partners, and run out of strangers to meet. They reach about 111 when the
  population allows it.
- **Small but significant drifts remain in the inner layers.** The inner circle
  grows slightly (2.7 → 3.0) and close friends shrink (7.6 → 6.8). They are much
  weaker than in experiment 02. They may come from triadic closure, which depends on
  the local network rather than on N.
- **The ratios are now around 2.5 rather than Dunbar's 3.** The calibration was
  done under the baseline exploration, and recalibrating under `exploration: ties`
  should bring them closer to 3. Two candidate knobs:
  - the decay ladder;
  - the gap between the friend and close-friend thresholds, which keeps the middle
    ratio near 2.2.
