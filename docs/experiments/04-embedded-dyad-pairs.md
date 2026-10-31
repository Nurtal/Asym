# Experiment 04: embedded dyads by archetype pair

Script: `experiments/04_embedded_dyad_pairs.py`. Module: `asym.meanfield.embedded`.

Each focal agent sits in a clique of M background partners of its own archetype,
with background ties starting at x = 0.5. The focal tie A↔B bridges the two cliques
and starts at x0 = 0.1, 0.5 or 0.9. The runs use the built-in archetypes, γ = 0.5,
a0 = 0.5 and horizon 600, all in the mean-field.

Outcome codes:

- **F**: friendship, both ties ≥ 0.3
- **A**: asymmetric, one tie ≥ 0.3
- **Q**: acquaintance
- **B**: breakup, both ties < x_min

Each cell gives the outcome, then x_AB / x_BA.

## Results

#### M = 2 background partners

| A → B | x0=0.1 | x0=0.5 | x0=0.9 |
|---|---|---|---|
| butterfly → butterfly | F 0.55 / 0.55 | F 0.70 / 0.70 | F 0.83 / 0.83 |
| butterfly → loyal_few | Q 0.30 / 0.30 | F 0.79 / 0.79 | F 0.89 / 0.89 |
| butterfly → transactional | A 0.53 / 0.22 | F 0.70 / 0.30 | F 0.83 / 0.32 |
| butterfly → avoidant | A 0.48 / 0.23 | F 0.71 / 0.43 | F 0.86 / 0.60 |
| loyal_few → loyal_few | B 0.02 / 0.02 | F 0.85 / 0.85 | F 0.92 / 0.92 |
| loyal_few → transactional | B 0.02 / 0.01 | F 0.85 / 0.51 | F 0.92 / 0.51 |
| loyal_few → avoidant | B 0.02 / 0.01 | F 0.81 / 0.56 | F 0.90 / 0.82 |
| transactional → transactional | Q 0.02 / 0.02 | F 0.49 / 0.49 | F 0.49 / 0.49 |
| transactional → avoidant | Q 0.04 / 0.06 | F 0.30 / 0.47 | F 0.42 / 0.67 |
| avoidant → avoidant | Q 0.09 / 0.09 | F 0.33 / 0.33 | F 0.56 / 0.56 |

#### M = 4 background partners

| A → B | x0=0.1 | x0=0.5 | x0=0.9 |
|---|---|---|---|
| butterfly → butterfly | Q 0.27 / 0.27 | F 0.44 / 0.44 | F 0.60 / 0.60 |
| butterfly → loyal_few | Q 0.13 / 0.13 | F 0.78 / 0.78 | F 0.88 / 0.88 |
| butterfly → transactional | Q 0.27 / 0.12 | A 0.45 / 0.16 | A 0.82 / 0.29 |
| butterfly → avoidant | Q 0.26 / 0.16 | F 0.50 / 0.33 | F 0.83 / 0.55 |
| loyal_few → loyal_few | B 0.01 / 0.01 | B 0.01 / 0.01 | F 0.92 / 0.92 |
| loyal_few → transactional | B 0.01 / 0.00 | F 0.84 / 0.50 | F 0.91 / 0.51 |
| loyal_few → avoidant | B 0.01 / 0.01 | B 0.01 / 0.01 | F 0.91 / 0.73 |
| transactional → transactional | Q 0.05 / 0.05 | F 0.47 / 0.47 | F 0.47 / 0.47 |
| transactional → avoidant | Q 0.03 / 0.04 | Q 0.03 / 0.04 | F 0.49 / 0.72 |
| avoidant → avoidant | Q 0.02 / 0.02 | Q 0.02 / 0.02 | F 0.72 / 0.72 |

#### M = 8 background partners

| A → B | x0=0.1 | x0=0.5 | x0=0.9 |
|---|---|---|---|
| butterfly → butterfly | Q 0.15 / 0.15 | Q 0.29 / 0.29 | Q 0.29 / 0.29 |
| butterfly → loyal_few | Q 0.09 / 0.09 | F 0.80 / 0.80 | F 0.89 / 0.89 |
| butterfly → transactional | Q 0.27 / 0.11 | A 0.48 / 0.18 | A 0.65 / 0.22 |
| butterfly → avoidant | Q 0.22 / 0.13 | A 0.37 / 0.16 | F 0.79 / 0.36 |
| loyal_few → loyal_few | B 0.00 / 0.00 | B 0.00 / 0.00 | F 0.92 / 0.92 |
| loyal_few → transactional | B 0.00 / 0.00 | F 0.85 / 0.52 | F 0.92 / 0.52 |
| loyal_few → avoidant | B 0.01 / 0.00 | F 0.83 / 0.72 | F 0.91 / 0.72 |
| transactional → transactional | B 0.00 / 0.00 | Q 0.06 / 0.06 | F 0.31 / 0.31 |
| transactional → avoidant | B 0.00 / 0.00 | Q 0.21 / 0.27 | F 0.40 / 0.53 |
| avoidant → avoidant | Q 0.10 / 0.10 | Q 0.10 / 0.10 | F 0.68 / 0.68 |

## Reading

- **Competition produces all four outcomes.** The isolated dyad of experiment 03
  only ever produced friendships. With background partners competing for the
  budget, focal ties also become asymmetric, stay acquaintances or break up.
- **The outcome depends on the starting closeness for most pairs.** Typically a
  tie starting at x0 = 0.1 stays an acquaintance or breaks up, while the same
  pair starting at 0.9 stays friends. The x^β allocation rule is self-reinforcing:
  a close tie gets invited more, so it stays close. Which state the tie reaches
  depends on where it starts. **Both states are stable under the same
  parameters.**
- **β sets the character of the dyad:**
  - **loyal_few (β = 2.5) is all-or-nothing.** Its ties either break up (x ≈ 0.01)
    or settle near 0.9, with nothing in between. This is the clearest case of two
    stable states.
  - **butterfly (β = 0.5) is graded.** Its closeness changes smoothly with x0 and
    with M. It never breaks up; it slides from friendship to acquaintance as the
    neighbourhood grows.
- **The transactional agent is always the less close side.** Against a butterfly
  it ends at 0.16–0.32 while the butterfly stays at 0.45–0.83, which makes the dyad
  asymmetric for M ≥ 4. This is the asymmetry of experiment 03, now strong enough
  to cross the friendship threshold.
- **Larger neighbourhoods shrink the range of starts that lead to friendship.**
  avoidant–avoidant is a friendship from x0 ≥ 0.5 at M = 2, but only from 0.9 at
  M ≥ 4. transactional–transactional starting at x0 = 0.5 is a friendship at
  M ≤ 4 but an acquaintance at M = 8.
- **The effect of M is not always monotone.** loyal_few → avoidant from x0 = 0.5
  breaks up at M = 4 but is a friendship at M = 8. The background partners also
  split their budgets across a larger clique, so the background ties weaken too,
  and the focal tie's relative weight can improve. The neighbourhood's internal
  structure, not just its size, shapes the outcome.

Caveats:

- These are mean-field (expected-rate) results. In the ABM, noise can switch a
  tie between the two stable states.
- The clique topology is a modelling choice. Neighbourhoods drawn from the
  experiment 02 population would be a more faithful environment.
