# Experiment 14: the pairing race in the full population

Script: `experiments/14_pairing_population.py`. Report:
`results/14_pairing_population.md`; raw results: `results/14_pairing_population.json`.
Neither is versioned.

## Question

In experiment 07, stochastic cliques of concentrated agents (β ≥ 1) broke into
exclusive pairs. The scaling theory (`docs/theory/maintenance-scaling.md` §3) gives
a criterion: equal sharing at closeness x is unstable iff β_eff (1 − x) > 1. It
predicted 39 of 40 mean-field cliques. Does this carry over to the full ABM
population, with encounters, forgetting, many partners and noise? It predicts:

1. **A gap.** No maintained tie can rest below x_c = 1 − 1/β_eff, so the closeness
   distribution should be empty there.
2. **Pairing.** Agents should concentrate on few partners when the budget is short.

## Setup

- **Homogeneous population**: N = 100 calibrated transactional agents with κ = 0 (no
  deficit erosion), encounters on, tie-only exploration (ε = 0.05).
- **Grid**: β ∈ {0.5, 1, 1.5, 2, 3} × B ∈ {12.5 (calibrated), 3.75, 1.88, 1.0}, 2 seeds.
- **Run**: random start, horizon 600, burn-in 300, a sample every 25.
- **Calibrated mixed population**: the base of experiment 10, at B × 1 and B × 0.3,
  analysed by profile.
- **Metrics per agent**, averaged over snapshots. "Friends" are ties with
  x ≥ θ_friend = 0.31; "strong" ties have x ≥ 0.6.
  - number of friends;
  - number of strong ties;
  - effective number of friends, (Σx)²/Σx²;
  - top share: the best friend's share of the summed closeness;
  - mutual best friends: my best friend's best friend is me;
  - **exclusive pair**: a mutual best friend who is also my only strong tie.

## Results

### 1. The gap: confirmed, and x_c is a lower bound on it

Closeness distribution at the calibrated budget (B = 12.5): share of ties per bin,
pooled over snapshots.

| β | x_c = 1 − 1/((1−ε)β) | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | antimode |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | — | 0.182 | 0.183 | 0.148 | 0.062 | 0.024 | 0.004 | 0.000 | 0.000 | none |
| 1 | — (0.95 < 1) | 0.080 | 0.076 | 0.094 | 0.087 | 0.125 | 0.106 | 0.021 | 0.001 | 0.29 |
| 1.5 | 0.30 | 0.030 | 0.019 | 0.018 | 0.018 | 0.047 | 0.098 | 0.217 | 0.048 | 0.51 |
| 2 | 0.47 | 0.015 | 0.005 | 0.004 | 0.003 | 0.006 | 0.017 | 0.167 | 0.191 | 0.59 |
| 3 | 0.65 | 0.008 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.009 | 0.233 | 0.69 |

- **β < 1 gives graded ties; β > 1 gives a bimodal closeness with an empty band.**
- The band widens and the high mode moves up as β grows, as predicted.
- **Bimodality starts already at β = 1**, where the allocation term alone
  ((1 − ε)β = 0.95) predicts stability. The bound leaves out two feedbacks that
  push β_eff above 1:
  - acceptance rises with x;
  - circle-dependent decay: inner ties decay more slowly.
- **The antimode always lies above x_c** (0.51, 0.59, 0.69 against 0.30, 0.47,
  0.65), for the same reason.
- Read as a necessary condition ("no maintained tie below x_c"), the criterion holds
  in every condition. As an estimate of the gap's position, it is a lower bound.

### 2. Pairing: a regime of scarcity × concentration, not of concentration alone

| B | β | friends | strong | effective friends | exclusive pairs |
|---|---|---|---|---|---|
| 12.5 | 0.5 | 25.6 | 1.8 | 24.7 | 0.12 |
| 12.5 | 1.5 | 13.1 | 11.6 | 12.8 | 0.00 |
| 12.5 | 3 | 4.4 | 4.4 | 4.4 | 0.01 |
| 3.75 | 0.5 | 1.6 | 0.0 | 1.6 | 0.00 |
| 3.75 | 1.5 | 3.3 | 2.5 | 3.2 | 0.07 |
| 3.75 | 3 | 1.6 | 1.5 | 1.6 | 0.45 |
| 1.88 | 0.5 | 0.1 | 0.0 | 0.1 | 0.00 |
| 1.88 | 1.5 | 1.2 | 0.7 | 1.2 | 0.63 |
| 1.88 | 3 | 1.1 | 1.0 | 1.1 | 0.79 |
| 1.0 | any | ≤ 0.4 | ≤ 0.1 | ≤ 0.4 | ≤ 0.28 |

(Full table in the report, including β = 1 and 2.)

- **At the calibrated budget, the breakdown of equal sharing does not produce
  pairs.**
  - Raising β from 0.5 to 3 cuts the effective number of friends from 25 to 4.4.
    These remaining ties are all strong: concentration trades many medium ties for
    a few strong ones.
  - But exclusive pairs stay at 0–1%. What breaks is equal sharing, not
    friendship among several partners.
- **The number of strong ties kept is set by the budget.**
  - Above x_c, ties sit on the stable high branch. An agent keeps as many of them as
    its budget can hold there: about 4–12 at B = 12.5, 1.5–2.5 at B = 3.75, and about
    1 at B = 1.88.
  - **Exclusive pairs appear when the budget holds about one strong tie**: 45% at
    B = 3.75 and β = 3, and 63–79% at B = 1.88 and β ≥ 1.5.
  - This is what happened in the cliques of experiment 07, which ran on the
    uncalibrated, smaller budgets.
- **Under scarcity, concentration rescues friendship.**
  - At B = 1.88 and β = 0.5, agents spread their budget so thin that almost
    nobody has a friend (0.1 per agent).
  - At β ≥ 1.5, the same budget gives about one friend each, usually a mutual and
    exclusive pair.
  - At B = 1, friendship collapses at every β.
  - This is the population-level face of Tamarit's inverse regime: scarce
    resources per alter favour few, intense ties.
- **The x_ref-based prediction of pairing is not usable as such.** x_ref is the
  closeness of maintained ties at β = 0.5. At low budgets, that run has almost no
  maintained ties (0.0–1.6 per agent), so x_ref is ill-defined. The criterion
  predicts where equal sharing breaks, but not how many ties survive. That number
  comes from the budget.

### 3. The calibrated mixed population

| B × | profile | friends | strong | effective friends | exclusive pairs |
|---|---|---|---|---|---|
| 1 | butterfly | 38.1 | 11.9 | 35.2 | 0.00 |
| 1 | loyal_few | 6.5 | 5.3 | 6.2 | 0.00 |
| 1 | transactional | 6.1 | 2.7 | 5.7 | 0.04 |
| 1 | avoidant | 10.6 | 4.5 | 9.8 | 0.00 |
| 0.3 | butterfly | 5.7 | 1.1 | 5.3 | 0.15 |
| 0.3 | loyal_few | 1.1 | 1.1 | 1.1 | **0.74** |
| 0.3 | transactional | 0.8 | 0.2 | 0.8 | 0.24 |
| 0.3 | avoidant | 2.0 | 0.8 | 1.9 | **0.54** |

- **At calibrated budgets there is no pairing race**: at most 4% exclusive pairs.
- loyal_few agents (β = 3) do concentrate, on about 6 friends, nearly all strong.
- With budgets cut to 30%, three quarters of loyal_few agents end up in an exclusive
  pair, and half of the avoidant agents do. Butterflies (β = 0.6) mostly do not.
- The profile ordering follows β_eff, plus faster decay for the avoidant agents.

## Reading

- **The criterion carries over as a gap condition.** Concentrated agents have a
  bimodal closeness distribution with an empty band. x_c bounds the band from below,
  and β_eff > 1 already at β = 1 once acceptance and circle feedbacks count.
- **"Pairing race" is a misnomer outside scarcity.** Two separate effects are
  involved:
  - concentration (β_eff > 1) breaks equal sharing into a few strong ties and many
    dropped ones;
  - the budget then fixes how many strong ties remain.

  Exclusive pairs need both: high β and a budget that sustains about one strong
  tie.
- **Correction of experiment 07, finding 5.** The fragmentation of the cliques into
  pairs is real, but it belongs to the small-budget regime of the uncalibrated
  archetypes. At calibrated budgets, it does not occur in the population.
- **For the paper (§6.4):** report the gap condition, and report pairing as a
  scarcity regime that concentration enables. That connects it to the inverse
  regime (§5.4) rather than presenting it as a generic dyadic mechanism.

## Caveats

- 2 seeds, one population draw per condition, N = 100.
- Homogeneous transactional agents with κ = 0. The deficit term would add the
  asymmetry mechanisms of experiment 12.
- "Strong" (x ≥ 0.6) and the friend threshold are fixed cut-offs. Mutual-best-friend
  rates are high whenever agents have only one friend, so the exclusive-pair rate
  is the informative measure.
- The antimode is computed on a smoothed histogram pooled over snapshots and ties.
  Its position is approximate (±0.03).
