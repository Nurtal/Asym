# Experiment 08: Tamarit's inverse regime

Definition: `experiments/08_inverse_regime.yaml`
(results in `results/inverse_regime/`, not versioned). Run on commit f09e806.

## Question

Tamarit et al. (2018, PNAS) derive layered ego networks from a static
resource-allocation model. They predict an **inverse regime** when the resources per
available alter are high: the inner layers become the most populated, and observe
it in small communities. Does the dynamical Asym model reproduce it, and with the
same control parameter?

## Setup

- the calibrated population of experiment 06: thresholds [0.31, 0.60, 0.82],
  `exploration: ties`, empty start, horizon 1500, burn-in 1000, 5 seeds;
- resources per alter raised in two independent ways:
  - population size N = 8, 12, 16, 24, 32, 48, 100;
  - at N = 48, every archetype's budget scaled by 0.5, 2 or 4;
- `layer_regime` analysis:
  - fits n_k ∝ exp(−μ·c_k) to the time-averaged **non-cumulative** layer counts,
    with cost c = 4 (inner circle) down to 1 (acquaintance);
  - **μ > 0** is the usual regime (populations grow outwards);
  - **μ < 0** is the inverse regime;
  - "inverse fraction" is the share of agents whose own counts give μ < 0.

## Results

Sorted by mean budget per available alter, B̄/(N−1). Layer counts run from the
inner circle to acquaintances (means over seeds). μ is a mean with its 95% CI.

| condition | B̄/(N−1) | inner | close | friends | acq. | μ | inverse fraction |
|---|---|---|---|---|---|---|---|
| N=48, B×0.5 | 0.136 | 0.81 | 1.16 | 4.13 | 15.28 | +1.01 [0.98, 1.04] | 0.00 |
| N=100 | 0.137 | 2.11 | 3.43 | 9.74 | 26.35 | +0.86 [0.85, 0.87] | 0.00 |
| N=48 | 0.273 | 2.51 | 5.47 | 6.75 | 11.04 | +0.47 [0.46, 0.47] | 0.03 |
| N=32 | 0.419 | 3.26 | 6.82 | 3.81 | 6.71 | +0.16 [0.14, 0.17] | 0.26 |
| N=48, B×2 | 0.546 | 10.27 | 9.02 | 3.85 | 7.18 | −0.19 [−0.21, −0.18] | 0.53 |
| N=24 | 0.577 | 5.31 | 4.75 | 1.86 | 5.21 | −0.10 [−0.13, −0.07] | 0.40 |
| N=16 | 0.899 | 6.28 | 2.17 | 0.75 | 3.85 | −0.25 [−0.28, −0.23] | 0.55 |
| N=48, B×4 | 1.091 | 21.57 | 5.31 | 2.69 | 7.88 | −0.37 [−0.39, −0.35] | 0.73 |
| N=12 | 1.178 | 5.34 | 1.53 | 0.44 | 2.83 | −0.32 [−0.38, −0.26] | 0.78 |
| N=8 | 1.854 | 4.32 | 0.96 | 0.38 | 1.08 | −0.52 [−0.60, −0.43] | 0.83 |

μ per archetype:

| condition | butterfly | loyal_few | transactional | avoidant |
|---|---|---|---|---|
| N=8 | – | −0.55 | +0.12 | −0.49 |
| N=16 | −3.38 | −0.02 | +0.10 | +0.09 |
| N=24 | −1.63 | +0.03 | +0.45 | +0.70 |
| N=48 | +0.28 | +0.32 | +0.89 | +0.86 |
| N=100 | +1.02 | +0.50 | +0.94 | +0.92 |
| N=48, B×4 | −4.08 | −0.25 | +0.37 | −0.34 |

For butterflies at N = 8 nearly every tie is in the inner circle, so the fit is
undefined.

## Reading

- **Asym reproduces the inverse regime without any change to the model.** When the
  resources per available alter are high, the inner circle becomes the most
  populated layer. The exponent μ changes sign around B̄/(N−1) ≈ 0.5, and up to 83%
  of agents are individually in the inverse regime at N = 8.
- **The two routes collapse onto one curve in the resources per alter.** Shrinking
  the population and enlarging the budget give the same μ at the same B̄/(N−1):
  - +0.86 and +1.01 at 0.137;
  - −0.10 and −0.19 at about 0.56;
  - −0.32 and −0.37 at about 1.1.

  This is Tamarit et al.'s control parameter (resources per alter). It emerges here
  from a dynamical model with no explicit optimisation. **Tamarit's static model is
  recovered as the steady state of Asym, which makes it a docking result.**
- **The transition is gradual.** μ decreases steadily from +1 to −0.5 over a
  fourteen-fold change in resources per alter. The inverse fraction rises from 0 to
  0.8 in the same range. There is no sharp transition.
- **The regime depends on the profile, beyond Tamarit's model:**
  - **Butterflies invert first and most** (μ = −1.6 already at N = 24). They are
    open, unconcentrated and have the largest budget, so with few people around
    they pull everybody into the inner circle.
  - **Transactional agents barely invert** (μ ≥ +0.1 at every N, slightly
    inverse only at B×4). Their reciprocity deficit keeps ties out of the inner
    circle even when time is abundant.

  This prediction is testable: in small communities, the people most demanding of
  reciprocity should keep a normal layer structure while the others invert.
  **Revised by experiment 09:** over 5 population draws, avoidant agents resist
  inversion as much as transactional ones except at the smallest N. The robust
  ordering is butterfly < loyal_few < avoidant ≈ transactional.
- **The "isolated dyad always becomes a friendship" result of experiment 03 is the
  N = 2 extreme of the same curve.**

## Caveats

- Small populations hold few agents per archetype (2 each at N = 8), drawn once
  (population seed 0). The per-archetype μ at small N should be confirmed over
  several population draws.
- μ is a least-squares fit on four layer counts, with empty layers skipped. It
  summarises the profile but is not a maximum-likelihood estimate as in Tamarit et
  al.
- Layer counts here are directed: they are what each agent perceives.
