# Experiment 12: population-level asymmetry and its mechanisms

Definition: `experiments/12_asymmetry_mechanisms.yaml`. Analysis: `asymmetry`
(`asym/experiments.py`), built on `metrics.friendship_reciprocity`. Results are in
`results/asymmetry_mechanisms/`, not versioned. Run on commit 1730dcd.

## Question

Research question 3 asks where persistent asymmetry comes from. The paper outline
flagged claim C6 ("asymmetry arises from heterogeneous reciprocity expectations") as
close to true by construction unless it is shown at population level, against the
alternatives.

## Measures

Every measure is time-averaged over the samples after burn-in.

- **Unreciprocated share:** a *friendship nomination* is a tie i→j at circle ≥
  friend. It is unreciprocated when j→i is absent or below friend. This is the
  closest analogue of the survey measure of Almaatouq et al. (2016), who report that
  about half of friendship nominations are not reciprocated.
- **Correlation:** the correlation of x_ij and x_ji over mutual dyads.
- **One-sided:** the share of dyads with a single direction.
- **|Δx|:** the mean |x_ij − x_ji| over mutual dyads.
- **Per ordered archetype pair A→B:** the unreciprocated share of A's nominations of
  B, and the mean x_AB − x_BA. A negative value means A is the less close side.

## 1. Description: calibrated population (experiment 06 runs, N = 200, 3 seeds)

| measure | value [95% CI] |
|---|---|
| unreciprocated friendship nominations | 0.244 [0.238, 0.250] |
| correlation x_ij, x_ji | 0.79 |
| one-sided dyads | 0.17 |
| mean \|Δx\| | 0.087 |

Unreciprocated nominations are concentrated on a few ordered pairs (mean
x_AB − x_BA in brackets):

| A → B | unreciprocated | x_AB − x_BA |
|---|---|---|
| butterfly → transactional | 0.63 | +0.13 |
| butterfly → avoidant | 0.53 | +0.12 |
| loyal_few → transactional | 0.48 | +0.27 |
| avoidant → transactional | 0.32 | +0.05 |
| transactional → transactional | 0.22 | 0 |
| every other pair | ≤ 0.11 | |

The transactional side is the less close one against every other profile, and
avoidant agents are the less close side against butterflies and loyal_few.

## 2. Counterfactuals (N = 100, empty start, horizon 1500, burn-in 1000, 5 seeds)

Each condition removes one source of heterogeneity from the calibrated population:

| condition | change |
|---|---|
| baseline | calibrated population of experiment 06 |
| no_deficit | transactional ρ* = 0.8, κ = 0: no expectation above balanced exchange |
| same_allocation | every archetype B = 12.5, β = 1.2 |
| same_decay | avoidant agents get the common decay ladder |
| average_only | one average archetype; only the individual sampling noise is left |
| misperception | baseline plus perception noise σ_p = 0.5 |

| condition | unreciprocated [95% CI] | correlation | one-sided | \|Δx\| | layers |
|---|---|---|---|---|---|
| baseline | **0.276** [0.274, 0.278] | 0.74 | 0.170 | 0.108 | 2.1 / 5.5 / 15.3 / 41.6 |
| no_deficit | **0.122** [0.116, 0.128] | 0.91 | 0.068 | 0.062 | 2.4 / 6.9 / 19.4 / 48.6 |
| same_decay | **0.182** [0.180, 0.185] | 0.80 | 0.148 | 0.078 | 2.3 / 7.0 / 18.8 / 45.2 |
| same_allocation | **0.222** [0.217, 0.226] | 0.72 | 0.182 | 0.119 | 1.3 / 7.1 / 14.3 / 35.2 |
| misperception | **0.235** [0.233, 0.238] | 0.79 | 0.179 | 0.100 | 2.5 / 5.9 / 15.0 / 40.1 |
| average_only | **0.067** [0.064, 0.071] | 0.91 | 0.095 | 0.074 | 4.0 / 11.0 / 15.3 / 34.7 |

Pairs with transactional or avoidant targets (unreciprocated share, then
x_AB − x_BA):

| A → B | baseline | no_deficit | same_decay | same_allocation |
|---|---|---|---|---|
| butterfly → transactional | 0.71, +0.19 | **0.06, +0.01** | 0.72, +0.18 | 0.73, +0.21 |
| loyal_few → transactional | 0.39, +0.23 | **0.00, 0.00** | 0.38, +0.23 | 0.69, +0.28 |
| transactional → transactional | 0.42 | **0.02** | 0.44 | 0.36 |
| butterfly → avoidant | 0.53, +0.15 | 0.53, +0.15 | **0.07, +0.01** | 0.40, +0.14 |
| loyal_few → avoidant | 0.03, +0.08 | 0.04, +0.08 | **0.01, 0.00** | 0.21, +0.17 |

## Reading

- **Heterogeneous reciprocity expectations are the main source of unreciprocated
  ties.**
  - Removing the transactional profile's expectation above balanced exchange
    (no_deficit) cuts the unreciprocated share by more than half, from 0.276 to
    0.122.
  - Asymmetry towards transactional agents almost vanishes: butterfly →
    transactional goes from 0.71 to 0.06.
  - The correlation between the two sides rises from 0.74 to 0.91.
  - Transactional agents stop being the less close side.

  **This is the population-level evidence for claim C6.** A partner with higher
  expectations feels a chronic deficit in an exchange that the other side
  experiences as balanced. Its closeness erodes, its side drops out of the
  friendship circles, and the other side's nomination is left unreciprocated.
- **Differential decay is a second, independent mechanism.** Giving avoidant agents
  the common decay (same_decay) lowers the share to 0.182 and removes the asymmetry
  towards avoidant agents (butterfly → avoidant: 0.53 → 0.07). It leaves the
  transactional pattern untouched. **The two mechanisms target different pairs**:
  - an expectation gap creates asymmetry towards demanding partners;
  - a decay gap creates asymmetry towards partners whose ties erode fast.
- **Mismatched budgets and concentration play a minor and mixed role.**
  same_allocation lowers the share only slightly, to 0.222. It even increases some
  asymmetries: loyal_few → transactional rises from 0.39 to 0.69 once loyal_few
  agents are less concentrated.
- **The individual-noise floor is low.** With a single average archetype, the share
  is 0.067. About three quarters of the baseline asymmetry is therefore due to
  profile heterogeneity.
- **The effects are not additive.** The three removals together account for
  15.4 + 9.4 + 5.4 = 30 points, against 21 points above the noise floor. The
  mechanisms overlap on some pairs; transactional → avoidant, for instance, involves
  both.
- **The misperception condition is confounded and should not be read as a noise
  effect.** Perception noise lowered the share (0.235), but the perception factor as
  implemented has mean e^{π + σ²/2} = 1.13 at σ_p = 0.5. It therefore also *raises*
  the average perceived reciprocity, which eases the transactional deficit.
  Separating noise from bias needs a mean-preserving variant (π = −σ²/2), which is
  a follow-up.
- **Comparison with data.** The model gives 0.24–0.28 unreciprocated nominations,
  against about 0.5 in Almaatouq et al. (2016). The direction and the order of
  magnitude agree, and the gap is plausible for three reasons:
  - survey nominations are noisier than the model's noiseless circles;
  - Almaatouq et al. attribute part of the gap to poor perception, which the model
    does not represent (agents do not observe the other side);
  - the threshold of the friend circle (0.31) sets the model's definition of
    "friend".

  The model predicts *which* nominations go unreciprocated: those directed at
  partners with high reciprocity expectations or fast-eroding ties. That is a
  testable, pair-level prediction.

## Caveats

- N = 100 for the counterfactuals and one population draw per condition; the
  descriptive part uses N = 200 and 3 seeds.
- Friendship level is the model's circle ≥ friend for both sides, which is not
  identical to a survey nomination.
- same_allocation also changes the layer sizes (inner 2.1 → 1.3), so part of its
  effect is indirect.
