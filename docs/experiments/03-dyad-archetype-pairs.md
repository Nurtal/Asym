# Experiment 03: isolated dyads by archetype pair

Script: `experiments/03_dyad_archetype_pairs.py` (mean-field dyad, horizon 600, no
encounters or shocks). Each ordered pair of archetype centres starts at
x_AB = x_BA = x0, for x0 = 0.1, 0.5 and 0.9. Research question 1: which pairs become
friendships, which stay asymmetric, which break up.

## Results

#### built-in archetypes (γ 0.5, a0 0.5)

| A → B | x0=0.1: x_AB / x_BA (outcome) | x0=0.5: x_AB / x_BA (outcome) | x0=0.9: x_AB / x_BA (outcome) |
|---|---|---|---|
| butterfly → butterfly | 0.96 / 0.96 (friendship) | 0.96 / 0.96 (friendship) | 0.96 / 0.96 (friendship) |
| butterfly → loyal_few | 0.94 / 0.94 (friendship) | 0.94 / 0.94 (friendship) | 0.94 / 0.94 (friendship) |
| butterfly → transactional | 0.95 / 0.67 (friendship) | 0.95 / 0.67 (friendship) | 0.95 / 0.67 (friendship) |
| butterfly → avoidant | 0.95 / 0.82 (friendship) | 0.95 / 0.82 (friendship) | 0.95 / 0.90 (friendship) |
| loyal_few → loyal_few | 0.85 / 0.85 (friendship) | 0.85 / 0.85 (friendship) | 0.92 / 0.92 (friendship) |
| loyal_few → transactional | 0.86 / 0.53 (friendship) | 0.86 / 0.53 (friendship) | 0.92 / 0.57 (friendship) |
| loyal_few → avoidant | 0.86 / 0.76 (friendship) | 0.86 / 0.76 (friendship) | 0.93 / 0.86 (friendship) |
| transactional → transactional | 0.54 / 0.54 (friendship) | 0.54 / 0.54 (friendship) | 0.57 / 0.57 (friendship) |
| transactional → avoidant | 0.56 / 0.77 (friendship) | 0.56 / 0.77 (friendship) | 0.60 / 0.87 (friendship) |
| avoidant → avoidant | 0.78 / 0.78 (friendship) | 0.78 / 0.78 (friendship) | 0.88 / 0.88 (friendship) |

#### calibrated archetypes (experiment 02)

| A → B | x0=0.1: x_AB / x_BA (outcome) | x0=0.5: x_AB / x_BA (outcome) | x0=0.9: x_AB / x_BA (outcome) |
|---|---|---|---|
| butterfly_c → butterfly_c | 0.99 / 0.99 (friendship) | 0.99 / 0.99 (friendship) | 0.99 / 0.99 (friendship) |
| butterfly_c → loyal_few_c | 0.99 / 0.99 (friendship) | 0.99 / 0.99 (friendship) | 0.99 / 0.99 (friendship) |
| butterfly_c → transactional_c | 0.99 / 0.88 (friendship) | 0.99 / 0.88 (friendship) | 0.99 / 0.88 (friendship) |
| butterfly_c → avoidant_c | 0.99 / 0.98 (friendship) | 0.99 / 0.98 (friendship) | 0.99 / 0.98 (friendship) |
| loyal_few_c → loyal_few_c | 0.99 / 0.99 (friendship) | 0.99 / 0.99 (friendship) | 0.99 / 0.99 (friendship) |
| loyal_few_c → transactional_c | 0.99 / 0.82 (friendship) | 0.99 / 0.82 (friendship) | 0.99 / 0.83 (friendship) |
| loyal_few_c → avoidant_c | 0.99 / 0.98 (friendship) | 0.99 / 0.98 (friendship) | 0.99 / 0.98 (friendship) |
| transactional_c → transactional_c | 0.84 / 0.84 (friendship) | 0.84 / 0.84 (friendship) | 0.84 / 0.84 (friendship) |
| transactional_c → avoidant_c | 0.84 / 0.98 (friendship) | 0.84 / 0.98 (friendship) | 0.84 / 0.98 (friendship) |
| avoidant_c → avoidant_c | 0.98 / 0.98 (friendship) | 0.98 / 0.98 (friendship) | 0.98 / 0.98 (friendship) |

## Reading

- **An isolated dyad always ends in friendship.** With nobody else to spend the
  budget on, each agent sends every invitation to the one partner, and acceptance
  is high enough to sustain the tie. Breakup and asymmetric outcomes need
  competition for the budget, which an isolated dyad does not have. The dyad
  analysis therefore answers RQ1 only for "relationships in a vacuum". In the
  population runs (experiments 01 and 02), most ties stay acquaintances.
- **Asymmetry persists even without competition, and it comes from reciprocity
  expectations.** The transactional agent (ρ* = 1.1, κ = 1) is always the less close
  side: 0.53–0.67 against 0.86–0.95 for its partner with the built-in archetypes.
  A balanced exchange gives q ≈ 1 < ρ*, so the transactional agent feels a constant
  deficit that erodes its closeness, while its partner, with ρ* = 0.8, sees no
  deficit. The same mutual exchange is valued differently at the two ends.
- **The circles make the steady state depend on the start.** With the built-in
  archetypes, loyal_few and avoidant pairs settle at 0.85 and 0.78 from x0 ≤ 0.5,
  but at 0.92 and 0.88 from x0 = 0.9. Starting in the inner circle gives the slower
  inner-circle decay. The hysteresis band then keeps the tie there, even though it
  would not have climbed in from below: for loyal_few, promotion needs
  x ≥ 0.8 + w/2 = 0.875, while demotion only happens below 0.725. The dyad thus has two
  stable states that exist only because of the discrete circles, not because of the
  continuous flow.
- With the calibrated archetypes, decay is slower and budgets larger, so every
  dyad saturates near x ≈ 1. Only the transactional side stays clearly below
  (0.82–0.88).

## Open question

A meaningful RQ1 phase diagram needs the dyad embedded in a population: a
background load and competing ties for each agent. Without it, the reduced dyad
cannot produce breakups. Ways to provide it:

- a small mean-field system, the focal dyad plus a few background partners per agent
- an external-load term in the dyad reduction

Either is a modelling decision still to make.

**Resolved:** the embedded-dyad option was chosen (focal dyad plus a clique of
background partners per agent, in the mean-field). See
`docs/experiments/04-embedded-dyad-pairs.md`.
