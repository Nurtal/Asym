# Experiment 09: inverse regime across population draws

Definition: `experiments/09_inverse_regime_populations.yaml`; aggregation:
`experiments/09_aggregate.py` (results in `results/inverse_regime_populations/`,
not versioned). Run on commit fe1cb30.

## Question

Experiment 08 used a single population draw. Do its per-archetype exponents hold
across draws? It suggested two things: butterflies invert first, and transactional
agents resist inversion.

## Setup

The setup is that of experiment 08 (calibrated population, empty start, horizon
1500, burn-in 1000):

- N = 12, 16, 24, 48 and 100;
- 5 population draws (`population.seed` 0–4) × 2 simulation seeds each;
- **population draws are the statistical unit**: μ is averaged over the
  simulation seeds of each draw, then summarised across draws (mean, 95%
  t-interval);
- "(k/n <0)" counts the draws with μ < 0;
- the last column is a paired contrast within each draw: transactional μ minus the
  mean μ of loyal_few and avoidant. Butterfly is left out because its μ is extreme
  or undefined at small N.

## Results

| N | all agents μ | inverse fraction | butterfly | loyal_few | transactional | avoidant | transactional − mean(loyal_few, avoidant), paired |
|---|---|---|---|---|---|---|---|
| 12 | -0.34 [-0.43, -0.24] (5/5 <0) | 0.77 | -4.56 [-5.91, -3.20] (4/4 <0) | -0.17 [-0.43, +0.09] (4/5 <0) | +0.20 [-0.07, +0.46] (1/5 <0) | -0.23 [-0.31, -0.16] (5/5 <0) | +0.40 [+0.12, +0.67] (n=5) |
| 16 | -0.26 [-0.27, -0.24] (5/5 <0) | 0.61 | -3.20 [-4.02, -2.38] (5/5 <0) | -0.10 [-0.20, -0.01] (5/5 <0) | +0.20 [+0.00, +0.39] (1/5 <0) | +0.13 [-0.18, +0.44] (2/5 <0) | +0.18 [-0.13, +0.50] (n=5) |
| 24 | -0.12 [-0.17, -0.07] (5/5 <0) | 0.46 | -1.52 [-1.98, -1.06] (5/5 <0) | +0.00 [-0.05, +0.06] (3/5 <0) | +0.45 [+0.31, +0.60] (0/5 <0) | +0.51 [+0.32, +0.71] (0/5 <0) | +0.20 [+0.01, +0.38] (n=5) |
| 48 | +0.42 [+0.37, +0.46] (0/5 <0) | 0.06 | +0.24 [+0.17, +0.32] (0/5 <0) | +0.27 [+0.23, +0.30] (0/5 <0) | +0.63 [+0.44, +0.83] (0/5 <0) | +0.86 [+0.70, +1.02] (0/5 <0) | +0.07 [-0.14, +0.28] (n=5) |
| 100 | +0.83 [+0.80, +0.85] (0/5 <0) | 0.00 | +0.98 [+0.94, +1.02] (0/5 <0) | +0.46 [+0.43, +0.50] (0/5 <0) | +0.89 [+0.73, +1.04] (0/5 <0) | +0.98 [+0.87, +1.09] (0/5 <0) | +0.17 [-0.03, +0.36] (n=5) |

## Reading

- **The regime change is robust.** All 5 draws are in the inverse regime at
  N ≤ 24 and all 5 in the normal regime at N ≥ 48. The population-level μ goes from
  −0.34 to +0.83, with narrow intervals. Experiment 08's main result is confirmed.
- **Butterflies invert first and most (confirmed).** Their μ is −1.5 at N = 24 and
  −4.6 at N = 12, in every draw.
- **"Transactional agents resist inversion" is only partly confirmed:**
  - At the smallest N (12), transactional is the only profile that stays normal on
    average (μ = +0.20, 4 of 5 draws positive). The paired contrast is
    +0.40 [+0.12, +0.67], which excludes 0.
  - At N = 16 and 24, **avoidant agents are just as resistant**. Their μ is +0.13
    and +0.51, against +0.20 and +0.45 for transactional. The contrast is no longer
    clear (+0.18 [−0.13, +0.50] at N = 16).
  - The robust statement is an ordering of the profiles:
    **butterfly < loyal_few < avoidant ≈ transactional**. The profiles whose ties
    erode fastest invert last: transactional through the reciprocity deficit,
    avoidant through faster decay. Transactional is the most resistant only when
    resources per alter are highest.
  - Experiment 08's wording ("transactional agents barely invert", as a profile of
    its own) overstated a single draw.
- **loyal_few sits at the boundary at small N** (μ ≈ −0.1 to 0). It has the
  smallest μ at N = 100 (+0.46), the "few deep ties" signature: a strong inner
  circle and few middle ties.

## Implication for the article

The testable prediction becomes: **in small communities, the people whose
relationships erode fastest keep a normal layer structure while the others invert.**
Those are the people with high reciprocity expectations or fast decay. The
reciprocity-specific version holds only in the most resource-rich settings.
