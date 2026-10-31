# Experiment 02: calibrated layering and its dependence on population size

Definition: `experiments/02_calibrated_layering_scaling.yaml`
(results in `results/calibrated_layering_scaling/`, not versioned). Run on commit
6f9b8d7; 5 seeds per condition; empty start; horizon 600, burn-in 300.

## Calibration

The default archetypes give far too few close ties (experiment 01). A random search
rescaled every archetype's centre with common factors, run at N = 100, one seed,
horizon 200. The score combined two terms:

- the squared log-distance of the three layer ratios from 3
- a weaker pull of the inner circle towards 4

The search covered:

- the budget factor
- the decay-ladder factor and the ladder's steepness
- the concentration factor β
- η and γ

The retained point is:

| Parameter | Change |
|---|---|
| budget B | ×2.5 (butterfly 20, loyal_few 10, transactional and avoidant 12.5) |
| decay ladder | ×0.3 and flattened: `δ_c = δ_1 · (δ_c/δ_1)^0.75` |
| concentration β | ×1.2 |
| η | 0.09 |
| γ | 0.85 |

Observations from the search:

- **Ratios near 3 need slow, flat decay together with a moderate budget.**
- A steep ladder (inner decay much slower than outer) puts everybody in the inner
  circle, with ratios around 1.3.
- A large η does the same.
- A small budget with fast decay gives tiny inner layers.
- The ratio between close friends and friends stays the hardest to raise, at
  about 2.3. It is set by the gap between the 0.55 and 0.3 thresholds.

A check with 2 seeds at horizon 600 showed the layer sizes are stationary after
about t = 300, which fixes the burn-in.

These calibrated archetypes are an experiment-level preset. The built-in defaults
are unchanged, so the tests and earlier experiments keep their meaning.

## Results (time-averaged after burn-in; mean [95% CI] over 5 seeds)

Cumulative layer sizes per agent:

| N | inner | + close | + friends | all ties | ratios |
|---|---|---|---|---|---|
| 100 | 2.11 [2.03, 2.18] | 6.62 [6.49, 6.74] | 15.3 [15.1, 15.5] | 49.6 [49.2, 50.0] | 3.1 / 2.3 / 3.3 |
| 200 | 2.16 [2.11, 2.21] | 5.27 [5.16, 5.38] | 13.7 [13.5, 13.9] | 62.1 [61.8, 62.5] | 2.4 / 2.6 / 4.6 |
| 400 | 2.18 [2.14, 2.21] | 4.76 [4.70, 4.83] | 12.2 [12.1, 12.2] | 70.8 [70.6, 71.0] | 2.2 / 2.6 / 5.8 |

Per archetype (means over seeds):

| N | archetype | inner | + close | + friends | all |
|---|---|---|---|---|---|
| 100 | butterfly | 2.8 | 14.1 | 38.4 | 91 |
| 100 | loyal_few | 3.5 | 4.4 | 5.5 | 39 |
| 100 | transactional | 0.9 | 3.0 | 6.2 | 28 |
| 100 | avoidant | 1.3 | 5.0 | 11.0 | 40 |
| 400 | butterfly | 2.1 | 6.8 | 28.0 | 156 |
| 400 | loyal_few | 4.2 | 5.1 | 6.1 | 48 |
| 400 | transactional | 1.2 | 2.6 | 5.4 | 31 |
| 400 | avoidant | 1.3 | 4.5 | 9.1 | 49 |

## Reading

- **The inner circle is limited by the budget.** Its size does not change with N:
  2.11, 2.16 and 2.18. An agent can only sustain so many ties that need frequent
  interaction, however many people it could meet.
- **The outermost layer is limited by exposure.** It grows with N, but sub-linearly
  (50 → 62 → 71 for a fourfold increase in N). Agents meet more people, and they
  forget acquaintances they do not maintain.
- **The middle layers shrink as N grows.** Close friends fall from 4.5 to 2.6 and
  friends from 8.6 to 7.4 (non-cumulative counts). The extra acquaintances divert
  part of the budget, through exploration and the weights proportional to x^β,
  away from the ties that would otherwise climb. **The near-Dunbar ratios (≈3) are
  therefore not scale-free in this model.** They hold at N ≈ 100, and the outer
  ratio grows with N (3.3 → 5.8). Dunbar's layers are claimed to hold in large
  societies, so a mechanism that caps the acquaintance layer (higher x_min, or
  encounter rates that do not grow with N) would be needed. This is an open
  modelling question.
- **The archetypes leave recognisable signatures:**
  - **loyal_few** has the largest inner circle (3.5–4.2) and almost nothing between
    the inner circle and acquaintances: a few deep ties, as intended.
  - **butterfly** has a broad middle (28–38 friends or closer) and the largest
    acquaintance layer (up to 156 at N = 400).
  - **transactional** has the smallest inner circle (about 1), consistent with the
    persistent self-felt deficit seen in experiment 03.
  - **avoidant** sits in between, with a wider friends layer than transactional.
