# Experiment 11: a single maintenance parameter for the layer sizes?

Script: `experiments/11_maintenance_collapse.py`. Raw results:
`results/11_maintenance_collapse.json`, not versioned.

## Question

The Morris screening (experiment 10) found that budget B, gain η and decay δ
dominate the layer sizes, with strongly non-linear effects. Do they act only
through the combination **Q = η·B/δ**, i.e. the interaction-driven gain against
the decay?

## Setup

- Base of experiment 10: the calibrated model of experiment 06 at N = 100, random
  start, horizon 600, burn-in 300.
- Q is scaled by q ∈ {0.5, 0.71, 1, 1.41, 2} along four routes:
  - B × q;
  - η × q;
  - δ × 1/q, applied to the whole ladder of every archetype;
  - mixed: B × √q and δ × 1/√q.
- 2 seeds per point.

If the layers depend only on Q, the four routes give the same value at the same q.

## Results

Means over 2 seeds. "spread" is the max/min ratio across routes at a given q.


#### inner

| q | B | eta | delta | mixed | spread (max/min) |
|---|---|---|---|---|---|
| 0.50 | 0.688 | 0.636 | 0.91 | 0.798 | 1.43 |
| 0.71 | 1.08 | 1.06 | 1.27 | 1.23 | 1.20 |
| 1.00 | 2.04 | 2.04 | 2.04 | 2.04 | 1.00 |
| 1.41 | 3.34 | 3.99 | 3.25 | 3.41 | 1.23 |
| 2.00 | 6.15 | 8.15 | 6.01 | 6.11 | 1.36 |

#### +close

| q | B | eta | delta | mixed | spread (max/min) |
|---|---|---|---|---|---|
| 0.50 | 1.81 | 1.67 | 2.53 | 2.26 | 1.51 |
| 0.71 | 3.31 | 3.2 | 3.95 | 3.66 | 1.24 |
| 1.00 | 6.25 | 6.25 | 6.25 | 6.25 | 1.00 |
| 1.41 | 11.3 | 11.8 | 10.2 | 10.8 | 1.15 |
| 2.00 | 18.9 | 19.3 | 16.2 | 17.9 | 1.19 |

#### +friends

| q | B | eta | delta | mixed | spread (max/min) |
|---|---|---|---|---|---|
| 0.50 | 6 | 5.12 | 7.71 | 6.98 | 1.51 |
| 0.71 | 10.3 | 9.91 | 11.1 | 10.6 | 1.12 |
| 1.00 | 15.7 | 15.7 | 15.7 | 15.7 | 1.00 |
| 1.41 | 23.1 | 22.6 | 21.5 | 22.1 | 1.08 |
| 2.00 | 31 | 29.3 | 27 | 29.3 | 1.15 |

#### all

| q | B | eta | delta | mixed | spread (max/min) |
|---|---|---|---|---|---|
| 0.50 | 27.1 | 35.2 | 23.4 | 25.2 | 1.50 |
| 0.71 | 33.2 | 37.5 | 30.9 | 32.1 | 1.21 |
| 1.00 | 39.5 | 39.5 | 39.5 | 39.5 | 1.00 |
| 1.41 | 44.9 | 41.9 | 46.2 | 45.6 | 1.10 |
| 2.00 | 50 | 44 | 51.3 | 50.8 | 1.17 |

#### μ

| q | B | eta | delta | mixed | spread (max/min) |
|---|---|---|---|---|---|
| 0.50 | 1.16 | 1.28 | 0.972 | 1.06 | 1.31 |
| 0.71 | 1.03 | 1.09 | 0.922 | 0.963 | 1.19 |
| 1.00 | 0.818 | 0.818 | 0.818 | 0.818 | 1.00 |
| 1.41 | 0.602 | 0.506 | 0.656 | 0.621 | 1.30 |
| 2.00 | 0.334 | 0.166 | 0.425 | 0.374 | 2.56 |

#### high-mode share

| q | B | eta | delta | mixed | spread (max/min) |
|---|---|---|---|---|---|
| 0.50 | 0.0361 | 0.0291 | 0.0552 | 0.0468 | 1.90 |
| 0.71 | 0.0487 | 0.0433 | 0.0616 | 0.0571 | 1.42 |
| 1.00 | 0.0762 | 0.0762 | 0.0762 | 0.0762 | 1.00 |
| 1.41 | 0.115 | 0.139 | 0.107 | 0.112 | 1.29 |
| 2.00 | 0.186 | 0.255 | 0.172 | 0.181 | 1.48 |

The share of the variance of log(layer size) explained by q alone (between-q
variance over total variance) was computed over all routes, then over the routes
that keep η fixed (B, δ, mixed):

| layer | all four routes | B, δ, mixed |
|---|---|---|
| inner | 0.983 | 0.992 |
| + close | 0.986 | 0.989 |
| + friends | 0.980 | 0.988 |
| all ties | 0.863 | 0.985 |

## Reading

- **Q = η·B/δ is close to a single control parameter for the inner layers.** Over a
  fourfold range of Q, the inner circle grows ninefold (0.7 → 6.2) and the friends
  layer fivefold. Yet 98–99% of the variance of these layers is explained by Q
  alone, whichever parameter is moved. Across routes at the same Q, values differ
  by 8–50%; the largest gaps are at the lowest Q, where layers are small and
  noisy. Within each q, each value is a mean over only 2 seeds.
- **B and δ are exchangeable: the B/δ collapse holds for every layer** (R² ≥ 0.985,
  the outer layer included). Doubling the time available and halving the decay rate
  give the same personal network. Only the ratio of the two rates (interaction
  supply against erosion) matters. This sharpens claims C1/C2. The size of the
  layered network is fixed by a single dimensionless number, and the hierarchy's
  shape by β (experiment 10).
- **η acts like B/δ on the middle layers, but differently at the two ends:**
  - **It is stronger on the inner circle and the high mode.** At q = 2, the inner
    circle reaches 8.2 by the η route against 6.0–6.2 otherwise, and the high-mode
    share 0.26 against 0.17–0.19. η is also the jump size of one interaction, so a
    larger η carries ties over the inner threshold in fewer interactions. That
    effect cannot be traded for budget.
  - **It is weaker on the acquaintance layer.** Raising η by four times changes the
    number of ties only from 35 to 44, against 23 to 51 by the B or δ routes. Weak
    ties are rarely interacted with, so their lifetime depends on decay and on the
    budget available for exploration, not on the gain per interaction. This is
    why the full collapse is weaker for "all ties" (R² = 0.86 with η included).
- **Implication for the model:** B and δ could be merged into a single parameter
  for aggregate-structure questions. η should stay separate. This reduces the
  effective parameter space found by the screening to:
  - **B/δ**, which sets the size;
  - **η**, which sets the jump size and the inner circle;
  - **β**, which sets the shape;
  - **ν**, which sets the exposure;
  - **ρ\***, which sets the asymmetry.

## Caveats

- 2 seeds and one population draw per point. The within-q spread includes
  simulation noise, so the collapse may be tighter than measured.
- The ranges stay within the normal regime (μ > 0 everywhere). The collapse was not
  tested across the inverse regime.
- ~~This is an empirical collapse, not a derivation.~~ **Derived since then** in
  `docs/theory/maintenance-scaling.md` (experiment 13). In the mean-field, B, η and δ
  enter the steady state only through ηB/δ, apart from the corrections κ/δ and
  o0/B. At a fixed mean, the noise of a tie depends on η alone. This explains
  both why B and δ are exchangeable and why η deviates at the tails. The original
  sketch follows. In the steady state of a maintained tie, ηA(1 − x) = δx, with A ∝ B, so
  the closeness of a maintained tie depends on ηB/δ. The circle thresholds then
  turn that into layer counts. The derivation would explain why η deviates through
  the discreteness of jumps.
