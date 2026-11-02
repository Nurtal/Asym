# Experiment 19: dependence on the initial state at k = 1

Script: `experiments/19_start_dependence.py`. Report:
`results/19_start_dependence/report.md`; raw runs: `results/19_start_dependence/runs.jsonl`.
Neither is versioned. 15 runs, no failures.

**Conclusion: the calibrated model keeps a small memory of its start, in the inner circle
only.** A random start gives an inner circle 11% smaller than an empty start at t = 1000–1500.
The other layers and the unreciprocated share change by less than 2%.

## Question

Experiment 18 found an inner circle of 2.16 from an empty start and 1.93 from a random start
at t = 2500–3000, on one draw and one seed. Is the gap real? It matters because experiments
06, 12 and the layers and asymmetry blocks of 15 start empty, while experiments 10, 11, 14 and
17 start at random.

## Protocol

The layers block of exp 15 (N = 100, 5 draws, 3 seeds, window 1000–1500), rerun from the random
start (density 0.2, closeness 0.05–0.3). Each run is compared with the empty-start run of
exp 15 with the same draw and seed. Intervals are 95% t-intervals over the 5 draws.

## Results

| measure | empty | random | random − empty | relative | p |
|---|---|---|---|---|---|
| inner | 2.283 | 2.035 | −0.248 ± 0.093 | −10.9% | 0.002 |
| + close | 6.120 | 6.016 | −0.104 ± 0.139 | −1.7% | 0.11 |
| + friends | 16.351 | 16.590 | +0.239 ± 0.113 | +1.5% | 0.004 |
| all | 42.090 | 42.449 | +0.359 ± 0.243 | +0.9% | 0.015 |
| μ | 0.825 | 0.861 | +0.035 ± 0.015 | +4.3% | 0.003 |
| unreciprocated | 0.257 | 0.258 | +0.001 ± 0.002 | +0.6% | 0.15 |

The p-values are uncorrected.

- **The inner gap is real.** It has the same sign in all 5 draws (2.11 → 1.97, 2.30 → 2.10,
  2.35 → 2.01, 2.39 → 2.12, 2.26 → 1.98). Its size is about that of the spread between draws.
- **The layer ratio moves.** The ratio of + close to inner goes from 2.68 to 2.96. So the
  closeness of that ratio to 3 depends on the start, and the calibration, made from an empty
  start, is not unique in this respect.
- **The effect is confined to the inner circle.** The outer layers shift by 2% at most, and
  the share of unreciprocated ties does not change detectably.

## Consequences for the paper

- Comparisons of the inner circle across experiments with different starts carry a difference
  of about 0.25 that does not come from the factor being compared. For example, exp 11 and 14
  (random start) against exp 06 (empty start).
- Comparisons within one experiment share a start, so they are not affected by this offset.
- Report the start used with each inner-circle value.

## Limits

- This shows that the gap persists through t = 1500. Only one run (exp 18: one draw, one seed)
  goes to t = 3000, so very slow relaxation and true hysteresis cannot be told apart.
- The mechanism was not tested.
- Only one random start was tried, and N = 100 only. Another density or closeness range could
  change the gap.
- Runs: 34 min with one process.
