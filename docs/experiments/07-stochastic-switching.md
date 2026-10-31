# Experiment 07: noise-induced switching of embedded dyads (stochastic ABM)

Script: `experiments/07_stochastic_switching.py`; switching metric:
`metrics.dyad_switching`.

## Setup

The set-up is that of experiment 04, simulated with the stochastic ABM:

- a focal dyad bridging two cliques of M = 4 background partners of the focal
  agents' archetypes, with background ties at 0.5;
- built-in archetypes, γ = 0.5, a0 = 0.5, `exploration: ties`;
- no encounters, so a forgotten tie stays broken.

Five pairs × nine focal starts x0 ∈ {0.1, …, 0.9} × 40 seeds were run, with horizon
1000.

The dyad closeness (mean of x_AB and x_BA) is read as a two-state signal with
hysteresis bands: **high** once ≥ 0.6, **low** once ≤ 0.15, **broken** when both
ties are gone. "MF closeness" is the mean-field dyad closeness at the horizon from
the same start. A value between the bands, e.g. 0.45, counts as neither state.

Column definitions:

- **P(high) end / P(broken) end**: state at t = 1000.
- **P(stay high … | reached)**: among runs that reached the high state, the fraction
  that stayed high without interruption until t = 250, 500 and 1000.
- **down / up switches**: mean number of high→(low or broken) and (low or mid)→high
  transitions per run.

## Results

#### loyal_few ↔ loyal_few

| x0 | MF closeness | P(high) end | P(broken) end | P(stay high ≥250 / 500 / 1000 \| reached) | mean breakup time | down / up switches per run |
|---|---|---|---|---|---|---|
| 0.1 | 0.00 | 0.00 | 1.00 | – | 24 | 0.00 / 0.00 |
| 0.2 | 0.00 | 0.03 | 0.97 | 1.00 / 1.00 / 1.00 | 36 | 0.00 / 0.03 |
| 0.3 | 0.00 | 0.00 | 1.00 | 0.00 / 0.00 / 0.00 | 54 | 0.03 / 0.03 |
| 0.4 | 0.00 | 0.12 | 0.88 | 1.00 / 1.00 / 1.00 | 67 | 0.00 / 0.12 |
| 0.5 | 0.00 | 0.20 | 0.80 | 0.91 / 0.73 / 0.73 | 98 | 0.07 / 0.28 |
| 0.6 | 0.85 | 0.80 | 0.20 | 0.82 / 0.80 / 0.80 | 150 | 0.20 / 0.00 |
| 0.7 | 0.85 | 0.93 | 0.07 | 0.97 / 0.95 / 0.93 | 346 | 0.07 / 0.00 |
| 0.8 | 0.92 | 0.97 | 0.03 | 0.97 / 0.97 / 0.97 | 179 | 0.03 / 0.00 |
| 0.9 | 0.92 | 1.00 | 0.00 | 1.00 / 1.00 / 1.00 | – | 0.00 / 0.00 |

#### avoidant ↔ avoidant

| x0 | MF closeness | P(high) end | P(broken) end | P(stay high ≥250 / 500 / 1000 \| reached) | mean breakup time | down / up switches per run |
|---|---|---|---|---|---|---|
| 0.1 | 0.04 | 0.00 | 1.00 | 0.00 / 0.00 / 0.00 | 22 | 0.03 / 0.03 |
| 0.2 | 0.04 | 0.07 | 0.93 | 1.00 / 1.00 / 1.00 | 34 | 0.00 / 0.07 |
| 0.3 | 0.04 | 0.20 | 0.80 | 1.00 / 1.00 / 1.00 | 48 | 0.00 / 0.20 |
| 0.4 | 0.04 | 0.23 | 0.78 | 0.91 / 0.82 / 0.82 | 95 | 0.10 / 0.33 |
| 0.5 | 0.04 | 0.35 | 0.65 | 0.81 / 0.81 / 0.81 | 74 | 0.07 / 0.42 |
| 0.6 | 0.04 | 0.40 | 0.60 | 0.33 / 0.33 / 0.33 | 108 | 0.75 / 0.15 |
| 0.7 | 0.04 | 0.25 | 0.75 | 0.30 / 0.25 / 0.25 | 124 | 0.78 / 0.03 |
| 0.8 | 0.53 | 0.47 | 0.53 | 0.40 / 0.40 / 0.40 | 107 | 0.60 / 0.07 |
| 0.9 | 0.70 | 0.68 | 0.28 | 0.70 / 0.65 / 0.62 | 240 | 0.47 / 0.15 |

#### transactional ↔ transactional

| x0 | MF closeness | P(high) end | P(broken) end | P(stay high ≥250 / 500 / 1000 \| reached) | mean breakup time | down / up switches per run |
|---|---|---|---|---|---|---|
| 0.1 | 0.13 | 0.03 | 0.97 | 1.00 / 1.00 / 1.00 | 16 | 0.00 / 0.03 |
| 0.2 | 0.13 | 0.07 | 0.93 | 0.67 / 0.67 / 0.67 | 27 | 0.05 / 0.12 |
| 0.3 | 0.16 | 0.10 | 0.90 | 1.00 / 1.00 / 1.00 | 28 | 0.00 / 0.10 |
| 0.4 | 0.44 | 0.12 | 0.80 | 1.00 / 1.00 / 0.83 | 27 | 0.03 / 0.15 |
| 0.5 | 0.45 | 0.12 | 0.85 | 1.00 / 1.00 / 1.00 | 30 | 0.00 / 0.12 |
| 0.6 | 0.45 | 0.33 | 0.62 | 0.12 / 0.12 / 0.12 | 32 | 0.90 / 0.23 |
| 0.7 | 0.45 | 0.28 | 0.68 | 0.07 / 0.05 / 0.05 | 42 | 0.97 / 0.25 |
| 0.8 | 0.45 | 0.30 | 0.65 | 0.15 / 0.15 / 0.15 | 38 | 0.88 / 0.17 |
| 0.9 | 0.45 | 0.28 | 0.70 | 0.10 / 0.10 / 0.10 | 43 | 0.90 / 0.17 |

#### butterfly ↔ butterfly

| x0 | MF closeness | P(high) end | P(broken) end | P(stay high ≥250 / 500 / 1000 \| reached) | mean breakup time | down / up switches per run |
|---|---|---|---|---|---|---|
| 0.1 | 0.52 | 0.97 | 0.03 | 1.00 / 1.00 / 1.00 | 21 | 0.00 / 0.97 |
| 0.2 | 0.52 | 1.00 | 0.00 | 1.00 / 1.00 / 1.00 | – | 0.00 / 1.00 |
| 0.3 | 0.52 | 0.97 | 0.00 | 0.97 / 0.97 / 0.93 | – | 0.10 / 1.07 |
| 0.4 | 0.52 | 1.00 | 0.00 | 1.00 / 0.97 / 0.95 | – | 0.05 / 1.05 |
| 0.5 | 0.52 | 1.00 | 0.00 | 1.00 / 0.95 / 0.93 | – | 0.07 / 1.07 |
| 0.6 | 0.67 | 0.97 | 0.00 | 1.00 / 1.00 / 0.97 | – | 0.03 / 0.00 |
| 0.7 | 0.67 | 1.00 | 0.00 | 1.00 / 1.00 / 1.00 | – | 0.00 / 0.00 |
| 0.8 | 0.82 | 1.00 | 0.00 | 1.00 / 1.00 / 1.00 | – | 0.00 / 0.00 |
| 0.9 | 0.82 | 1.00 | 0.00 | 1.00 / 0.97 / 0.97 | – | 0.03 / 0.03 |

#### butterfly ↔ transactional

| x0 | MF closeness | P(high) end | P(broken) end | P(stay high ≥250 / 500 / 1000 \| reached) | mean breakup time | down / up switches per run |
|---|---|---|---|---|---|---|
| 0.1 | 0.51 | 0.65 | 0.28 | 0.97 / 0.87 / 0.83 | 270 | 0.20 / 0.85 |
| 0.2 | 0.51 | 0.68 | 0.12 | 0.91 / 0.88 / 0.79 | 152 | 0.25 / 0.93 |
| 0.3 | 0.51 | 0.72 | 0.15 | 0.92 / 0.89 / 0.78 | 362 | 0.28 / 1.00 |
| 0.4 | 0.51 | 0.60 | 0.25 | 0.93 / 0.90 / 0.77 | 343 | 0.23 / 0.82 |
| 0.5 | 0.51 | 0.70 | 0.20 | 0.86 / 0.72 / 0.72 | 592 | 0.45 / 1.15 |
| 0.6 | 0.51 | 0.70 | 0.20 | 0.72 / 0.65 / 0.65 | 579 | 0.55 / 0.25 |
| 0.7 | 0.55 | 0.72 | 0.15 | 0.75 / 0.70 / 0.68 | 629 | 0.47 / 0.20 |
| 0.8 | 0.62 | 0.70 | 0.12 | 0.70 / 0.62 / 0.60 | 396 | 0.57 / 0.28 |
| 0.9 | 0.63 | 0.85 | 0.07 | 0.85 / 0.82 / 0.78 | 372 | 0.28 / 0.12 |

## Reading

**1. Noise turns the mean-field threshold into a probability.** In the mean-field,
the loyal_few pair has a sharp separatrix between x0 = 0.5 (breakup) and x0 = 0.6
(friendship at 0.85). In the ABM the probability of ending as friends rises
smoothly with the start:

| x0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|---|---|---|---|
| P(high at end) | 0.00 | 0.03 | 0.00 | 0.12 | 0.20 | 0.80 | 0.93 | 0.97 | 1.00 |

The probability crosses 1/2 between the same two starts as the mean-field
separatrix. **The deterministic threshold survives as the location of the steepest
rise.** A first meeting below the threshold still becomes a friendship about one
time in ten, and above it ends in a breakup about one time in five.

**2. Friendships that the mean-field calls stable break up under noise.**

- **avoidant–avoidant.** The mean-field predicts a stable friendship from
  x0 ≥ 0.8. In the ABM:
  - 32–60% of runs from those starts end broken;
  - the high state is lost 0.5–0.8 times per run;
  - only 40–62% of the friendships that formed last to t = 1000.
- **transactional–transactional.** The mean-field predicts a stable intermediate
  closeness (0.45) from every start ≥ 0.4. In the ABM, 62–85% of runs end broken,
  most within 30–45 time units. The friendships that do form from x0 ≥ 0.6 almost
  all collapse: only 5–15% stay high, with about 0.9 down-switches per run. **The
  intermediate mean-field state does not survive noise.** For these two profiles,
  "start, then break" is the typical stochastic trajectory.
- **loyal_few.** Friendships are robust once established: 73–100% of those reached
  stay high until the end. The pair is all-or-nothing in time as well as in level.

**3. When a breakup happens depends on the pair:**

| pair | typical breakup time |
|---|---|
| transactional pairs | 16–45, early |
| loyal_few from low starts | 24–98 |
| avoidant pairs | 22–240 |
| butterfly–transactional | 150–630, late |

The butterfly–transactional pair has a "slow-burn" regime:

- the start barely matters: P(high) is 0.60–0.85 from every x0;
- the friendship forms in most runs, but 20–40% of formed friendships are lost
  before t = 1000;
- breakups happen at t ≈ 150–630.

The transactional side's chronic reciprocity deficit eventually wins, after a long
apparent friendship.

**4. Butterflies are more robust than the mean-field predicts.** butterfly pairs
reach and keep the high state from every start: P(high) ≥ 0.97, against a
mean-field closeness of 0.52–0.82. The mean-field is the large-budget limit, and at
these small budgets the discrete interactions and the x^β weighting with β < 1
favour the focal tie.

**5. Neighbourhoods fragment into exclusive pairs, which may be the deeper
mechanism.** For loyal_few and transactional agents, the stochastic clique never
survives. 42 ties fall to 12, i.e. 6 mutual pairs: every agent ends up with exactly
one partner. Noise breaks the symmetric neighbourhood, and the rich-get-richer
allocation (β ≥ 1) concentrates each agent on one tie. The focal outcome is
therefore largely a **pairing race**. Does A pair with B, or with one of its own
background partners? Butterfly cliques (β < 1) survive intact.

## Implications

- **Bistability (claim C5) survives in the stochastic model, but as a probabilistic
  threshold with noise-induced crossings in both directions.** The mean-field gives
  the threshold's location. The ABM is needed for the probabilities and timescales.
  This should be stated against the deterministic picture of experiment 04.
- **The model generates three distinct relationship histories, each tied to a
  profile:**
  - early failure (transactional);
  - all-or-nothing commitment (loyal_few);
  - a long apparent friendship followed by a late breakup (butterfly–transactional).

  These are testable against tie-lifetime data. Hidd et al. 2023, cited in the
  literature review, find that a tie's fate is predictable from its early weeks.
- **The pairing-race mechanism under β ≥ 1 (cliques fragmenting into exclusive
  pairs) is a candidate result in its own right.** It needs a dedicated check:
  fragmentation versus β and versus M, in the full population model rather than
  in cliques.

## Caveats

- 40 seeds per cell, so a single proportion has a 95% margin of about ±0.15.
- Exploration is restricted to ties, and there are no encounters, so a breakup is
  final. With encounters, broken dyads could reform.
- The cliques are an idealised neighbourhood (see experiment 04).
