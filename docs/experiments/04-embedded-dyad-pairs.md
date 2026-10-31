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
| butterfly → butterfly | F 0.77 / 0.77 | F 0.77 / 0.77 | F 0.87 / 0.87 |
| butterfly → loyal_few | F 0.82 / 0.82 | F 0.82 / 0.82 | F 0.90 / 0.90 |
| butterfly → transactional | F 0.80 / 0.43 | F 0.80 / 0.43 | F 0.89 / 0.44 |
| butterfly → avoidant | F 0.57 / 0.31 | F 0.73 / 0.45 | F 0.86 / 0.60 |
| loyal_few → loyal_few | Q 0.03 / 0.03 | F 0.85 / 0.85 | F 0.92 / 0.92 |
| loyal_few → transactional | B 0.00 / 0.00 | F 0.84 / 0.51 | F 0.92 / 0.51 |
| loyal_few → avoidant | Q 0.06 / 0.03 | F 0.81 / 0.56 | F 0.90 / 0.82 |
| transactional → transactional | Q 0.03 / 0.03 | Q 0.03 / 0.03 | F 0.47 / 0.47 |
| transactional → avoidant | Q 0.06 / 0.09 | A 0.27 / 0.43 | F 0.40 / 0.65 |
| avoidant → avoidant | Q 0.11 / 0.11 | F 0.33 / 0.33 | F 0.55 / 0.55 |

#### M = 4 background partners

| A → B | x0=0.1 | x0=0.5 | x0=0.9 |
|---|---|---|---|
| butterfly → butterfly | F 0.52 / 0.52 | F 0.52 / 0.52 | F 0.82 / 0.82 |
| butterfly → loyal_few | Q 0.21 / 0.21 | F 0.81 / 0.81 | F 0.90 / 0.90 |
| butterfly → transactional | A 0.73 / 0.29 | A 0.73 / 0.29 | F 0.87 / 0.38 |
| butterfly → avoidant | Q 0.28 / 0.17 | F 0.49 / 0.32 | F 0.87 / 0.62 |
| loyal_few → loyal_few | B 0.00 / 0.00 | B 0.00 / 0.00 | F 0.92 / 0.92 |
| loyal_few → transactional | B 0.00 / 0.00 | F 0.84 / 0.51 | F 0.92 / 0.51 |
| loyal_few → avoidant | B 0.00 / 0.00 | B 0.00 / 0.00 | F 0.91 / 0.73 |
| transactional → transactional | Q 0.08 / 0.08 | F 0.44 / 0.44 | F 0.45 / 0.45 |
| transactional → avoidant | Q 0.04 / 0.07 | Q 0.04 / 0.07 | F 0.47 / 0.70 |
| avoidant → avoidant | Q 0.04 / 0.04 | Q 0.04 / 0.04 | F 0.70 / 0.70 |

#### M = 8 background partners

| A → B | x0=0.1 | x0=0.5 | x0=0.9 |
|---|---|---|---|
| butterfly → butterfly | Q 0.24 / 0.24 | F 0.40 / 0.40 | F 0.57 / 0.57 |
| butterfly → loyal_few | Q 0.11 / 0.11 | F 0.81 / 0.81 | F 0.89 / 0.89 |
| butterfly → transactional | Q 0.28 / 0.12 | A 0.47 / 0.18 | A 0.80 / 0.24 |
| butterfly → avoidant | Q 0.23 / 0.14 | A 0.38 / 0.17 | F 0.79 / 0.36 |
| loyal_few → loyal_few | B 0.00 / 0.00 | B 0.00 / 0.00 | F 0.92 / 0.92 |
| loyal_few → transactional | B 0.00 / 0.00 | F 0.86 / 0.53 | F 0.92 / 0.54 |
| loyal_few → avoidant | B 0.00 / 0.00 | F 0.84 / 0.72 | F 0.91 / 0.72 |
| transactional → transactional | Q 0.06 / 0.06 | Q 0.06 / 0.06 | Q 0.07 / 0.07 |
| transactional → avoidant | Q 0.16 / 0.21 | Q 0.16 / 0.22 | F 0.31 / 0.47 |
| avoidant → avoidant | Q 0.10 / 0.10 | Q 0.10 / 0.10 | F 0.66 / 0.66 |


## Correction (rerun)

The first version of this experiment let exploration invitations reach agents
outside the two cliques (`variants.exploration` was left at its baseline,
"population"). The mean-field therefore formed cross-clique ties, which changed the
topology. `embedded_dyad_config` now defaults to `exploration: ties`, and the tables
above come from the rerun. The qualitative reading below holds. Butterfly pairs end
higher than in the first run, and transactional–transactional starting at x0 = 0.5
became an acquaintance at M = 2.

## Reading

- **Competition produces all four outcomes.** Breakup, acquaintance, asymmetric
  and friendship all appear, whereas the isolated dyad of experiment 03 only ever
  produced friendships.
- **The outcome often depends on the start.**
  - loyal_few–loyal_few and loyal_few–avoidant break up from x0 ≤ 0.5 (M = 4) and
    stay friends near 0.9 from x0 = 0.9.
  - avoidant–avoidant and transactional–avoidant are acquaintances from low starts
    and friends from x0 = 0.9.
- **β sets the character of the dyad:**
  - **loyal_few (β = 2.5) is all-or-nothing.** Its ties end near 0 or near 0.9,
    never in between.
  - **butterfly (β = 0.5) is graded.** Its closeness falls smoothly with M
    (0.77 → 0.52 → 0.40 from x0 = 0.5) and never breaks up.
- **The transactional agent is always the less close side.** Against a butterfly
  the closeness is 0.73 vs 0.29 (M = 4) and 0.47 vs 0.18 (M = 8), an asymmetric
  outcome.
- **Larger neighbourhoods shrink the range of starts that lead to friendship.**
  transactional–transactional is a friendship from x0 ≥ 0.5 at M = 4 but never at
  M = 8.
- **The effect of M is not always monotone.** loyal_few → avoidant from x0 = 0.5
  breaks up at M = 4 but is a friendship at M = 8. Background partners split their
  budget over a larger clique, so the background ties weaken too.

## Caveat: the symmetric clique is unstable

The mean-field neighbourhood starts perfectly symmetric (every background tie at
x_bg), and symmetry is preserved by the equations. For concentrated archetypes this
symmetric state is **unstable**:

- a ±0.03 random perturbation of the background ties makes the loyal_few cliques
  fragment, from 40 live ties to 16;
- in the stochastic ABM (experiment 07) the cliques of loyal_few and transactional
  agents always fragment into exclusive pairs (42 ties → 12, i.e. 6 dyads);
- butterfly cliques (β = 0.5) survive.

The tables above are therefore the outcome *conditional on an intact
neighbourhood*. Experiment 07 gives the noisy picture.
