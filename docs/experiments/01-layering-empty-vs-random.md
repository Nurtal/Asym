# Experiment 01: emergent layering, empty vs random initial network

Definition: `experiments/01_layering_empty_vs_random.yaml`
(results in `results/layering_empty_vs_random/`, not versioned; regenerate with
`python -m asym.experiments run experiments/01_layering_empty_vs_random.yaml --workers 6`).

## Setup

- N = 200 agents, 25% of each archetype (butterfly, loyal_few, transactional,
  avoidant), noise 0.15, population seed 0
- γ = 0.5, a0 = 0.5, everything else at the defaults; no imposed circle capacity
- horizon 300, burn-in 150, samples every 10 time units; 10 simulation seeds per
  condition
- conditions: `empty` (nobody knows anybody) and `random` (G(N, 0.05), x ~ U(0.1, 0.5))
- run on commit 8836daa (engine before the ticket-14 optimisations)

## Results (time-averaged after burn-in; mean [95% CI] over seeds)

Cumulative layer sizes per agent, from the inner circle outwards:

| Layer | empty | random | Welch p |
|---|---|---|---|
| inner circle | 0.17 [0.16, 0.18] | 0.14 [0.13, 0.15] | 4e-5 |
| + close friends | 0.62 [0.60, 0.64] | 0.57 [0.56, 0.58] | 1e-4 |
| + friends | 1.32 [1.30, 1.33] | 1.30 [1.28, 1.31] | 0.048 |
| all ties | 11.41 [11.32, 11.51] | 11.51 [11.44, 11.59] | 0.09 |

Mean ratios between consecutive layers: empty 3.7 / 2.1 / 8.7, random 4.2 / 2.3 / 8.9.

## Reading

- **A layered structure emerges without any imposed capacity.** Each agent keeps
  about 11 acquaintance-level ties, but only about 1.3 friends or closer and well
  under one inner-circle tie.
- **The structure is close to independent of the initial condition, but not
  entirely.** The outer layers agree within a few percent. The inner layers are
  5–20% larger when starting from an empty network, and the difference is
  statistically significant. This could mean that 150 time units of burn-in is too
  short for the inner circles, or that there is a genuine weak memory of the start.
  A longer-horizon rerun is the obvious next check.
- **The layer sizes are much smaller than Dunbar's 5/15/50/150**, and the ratios
  (≈4, 2, 9) do not show the constant ≈3 scaling. With the default calibration,
  budgets (B ≈ 4–8 slots) are too small and decay too fast to sustain many close
  ties. Calibration is an open point in the model spec (§12).

## Follow-up: long-horizon rerun (experiment 01b)

Definition: `experiments/01b_layering_long_horizon.yaml`, the same as experiment 01
except horizon 1200, burn-in 800 and samples every 20 time units. Run on commit
6f9b8d7 (after the ticket-14 optimisations), 10 seeds per condition.

| Layer | empty | random | Welch p |
|---|---|---|---|
| inner circle | 0.209 [0.197, 0.220] | 0.197 [0.183, 0.210] | 0.15 |
| + close friends | 0.595 [0.575, 0.614] | 0.560 [0.552, 0.568] | 0.003 |
| + friends | 1.285 [1.275, 1.295] | 1.257 [1.240, 1.274] | 0.007 |
| all ties | 11.41 [11.36, 11.47] | 11.49 [11.43, 11.55] | 0.04 |

Mean ratios between consecutive layers: empty 2.9 / 2.2 / 8.9, random 2.9 / 2.2 / 9.1.

- **The inner-circle gap closes with more burn-in.** It falls from 0.03 to 0.01, and
  the difference is no longer significant. Part of the gap in experiment 01 was
  therefore a transient.
- **Small differences remain in the middle layers:** 6% for close friends and 2% for
  friends, both significant, with no sign of shrinking between burn-in 150 and 800.
  That suggests a weak but lasting memory of the start, possibly through the network
  structure (who knows whom) that the random start seeds. It is too small to change
  the qualitative picture: **the layered structure is, to within a few percent, an
  attractor of the dynamics.**
- The inner circle is a little larger here than in experiment 01 (0.21 versus 0.17).
  The engine's random stream changed between the two runs, but the more likely cause
  is the slow build-up of inner ties: inner-circle decay is slow (δ = 0.015), so it
  takes a long time to reach steady state.
