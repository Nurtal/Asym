# Experiment 10: Morris sensitivity screening

Script: `experiments/10_morris.py`; module: `asym/sensitivity.py`. Results are in
`results/morris/` (`morris.npz`, `indices.json`, `report.md` with every index), not
versioned.

## Setup

- **Base:** the calibrated model of experiment 06, at N = 100.
- **Shortened transient:** each run starts from a random acquaintance network
  (density 0.2, x ~ U(0.05, 0.3)). Horizon 600, burn-in 300, samples every 25.
- **18 factors:**
  - archetype parameters, as multipliers on every archetype centre:
    - ×0.5–2, log-scale: budget B, decay ladder δ, concentration β, encounter
      rate ν, exploration ε, deficit sensitivity κ, patience τ, hysteresis w,
      memory rate λ;
    - linear: reciprocity expectation ρ* ×0.85–1.15 and loyalty ℓ ×0.5–1.25;
  - global parameters:
    - η 0.045–0.18 and γ 0.425–1.7, log-scale;
    - a0 −0.5–1.5 and a 2–6;
    - x_min 0.01–0.04 and x0 0.05–0.2, log-scale;
    - inner threshold θ4 0.76–0.88.
- **Design:** Morris with 4 levels and r = 10 trajectories, i.e. 190 ABM runs,
  one simulation seed each. Mean run time 104 s on 8 workers.
- **11 outputs:**
  - time-averaged cumulative layers (inner, + close, + friends, all);
  - the three layer ratios;
  - the layer exponent μ;
  - mean |x_ij − x_ji| over mutual dyads;
  - the share of one-sided dyads;
  - the "high-mode share", i.e. the fraction of ties with x ≥ 0.75.

Ranges over the design (min / median / max):

| output | min / median / max |
|---|---|
| inner | 0 / 0.96 / 19 |
| + close | 0.1 / 4.8 / 42 |
| + friends | 0.8 / 11 / 65 |
| all | 3.6 / 30 / 87 |
| μ | −0.22 / 0.77 / 2.83 |
| abs asymmetry | 0.026 / 0.099 / 0.21 |
| one-sided | 0.03 / 0.18 / 0.38 |
| high-mode share | 0.002 / 0.11 / 0.53 |

The outputs vary widely. The factor ranges cover the normal and the inverse
regime, μ < 0 in some runs.

## Results: relative importance

The table gives the share of μ* (mean absolute elementary effect) of each factor,
per output; each column sums to 1, and shares ≥ 0.10 are in bold.

**Ratio 1 (+close / inner) is left out.** It is undefined in 9 runs (no inner
circle) and explodes, up to 1.6·10³, when the inner circle is nearly empty. Its
indices are dominated by these outliers (γ, θ4, ε). The exponent μ is the robust
summary of the layer profile.

| factor | inner | +close | +friends | all | ratio 2 | ratio 3 | mu | abs asymmetry | one-sided | high-mode share |
|---|---|---|---|---|---|---|---|---|---|---|
| budget B | **0.26** | **0.30** | **0.24** | **0.16** | 0.06 | **0.15** | **0.13** | **0.12** | **0.16** | **0.20** |
| gain η | **0.18** | **0.24** | **0.20** | 0.05 | **0.15** | **0.16** | **0.14** | **0.19** | 0.07 | **0.20** |
| decay δ | **0.16** | **0.17** | **0.16** | **0.20** | 0.07 | 0.04 | 0.07 | 0.09 | 0.06 | 0.09 |
| concentration β | 0.08 | 0.06 | **0.11** | **0.10** | **0.20** | **0.19** | 0.09 | **0.10** | 0.06 | 0.09 |
| encounter rate ν | 0.05 | 0.02 | 0.05 | **0.14** | **0.10** | 0.08 | 0.07 | 0.08 | 0.09 | **0.11** |
| reciprocity expectation ρ* | 0.02 | 0.03 | 0.04 | 0.05 | 0.03 | 0.02 | 0.05 | **0.10** | **0.17** | 0.01 |
| acceptance intercept a0 | 0.02 | 0.04 | 0.05 | 0.06 | 0.09 | 0.04 | 0.03 | 0.03 | 0.06 | 0.03 |
| issuing rate γ | 0.01 | 0.06 | 0.05 | 0.02 | 0.06 | 0.03 | 0.05 | 0.05 | 0.04 | 0.04 |
| forgetting x_min | 0.00 | 0.01 | 0.01 | 0.07 | 0.02 | 0.09 | 0.05 | 0.07 | 0.05 | 0.05 |
| exploration ε | 0.02 | 0.02 | 0.03 | 0.05 | 0.05 | 0.05 | 0.02 | 0.03 | 0.03 | 0.05 |
| inner threshold θ4 | **0.10** | 0.01 | 0.00 | 0.00 | 0.01 | 0.01 | **0.11** | 0.02 | 0.02 | 0.03 |
| first closeness x0 | 0.01 | 0.02 | 0.03 | 0.05 | 0.04 | 0.04 | 0.03 | 0.02 | 0.02 | 0.04 |
| patience τ | 0.01 | 0.01 | 0.02 | 0.02 | 0.03 | 0.02 | 0.05 | 0.02 | 0.02 | 0.01 |
| acceptance weight a | 0.01 | 0.02 | 0.01 | 0.01 | 0.03 | 0.04 | 0.03 | 0.02 | 0.02 | 0.01 |
| deficit sensitivity κ | 0.01 | 0.01 | 0.01 | 0.02 | 0.02 | 0.01 | 0.01 | 0.02 | 0.09 | 0.00 |
| hysteresis w | 0.05 | 0.00 | 0.00 | 0.00 | 0.02 | 0.01 | 0.03 | 0.01 | 0.01 | 0.01 |
| memory rate λ | 0.00 | 0.01 | 0.00 | 0.01 | 0.02 | 0.03 | 0.02 | 0.01 | 0.02 | 0.01 |
| loyalty ℓ | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.02 | 0.01 | 0.01 |

The top factors have σ/μ* ≈ 0.7–1.2 on the layer sizes, i.e. strongly non-linear
or interacting effects (full values in `results/morris/report.md`).

## Reading

- **Layer sizes are governed by three factors that form a maintenance balance:
  budget B, gain η and decay δ.** B and η increase every layer, and δ decreases
  every layer. Together they account for 55–70% of μ* on the four layer sizes. Their
  effects are strongly non-linear (σ ≈ μ*), as expected if they act through a
  combination such as η·B/δ: the interaction-driven gain against the decay. This
  suggests a reduced control parameter to test with Sobol indices or analytically.
- **The outer layer is exposure-bound, and the inner layer is not.** The encounter
  rate ν matters for the total number of ties (share 0.14) but hardly for the inner
  circle (0.05). The inner circle instead depends on its own threshold θ4 (0.10)
  and is the only output where the hysteresis width w matters (0.05). This is the
  same split as claim C2 (budget-bound inner circle, exposure-bound outer layer),
  now obtained from a global analysis.
- **The shape of the hierarchy is set by concentration β, not by the budget.** β is
  the top factor for the outer ratios, ratio 2 and ratio 3 (0.20 and 0.19), whereas
  B mainly scales every layer up together (0.06 and 0.15). Concentrating the
  allocation steepens the hierarchy. That separates the *size* of the personal
  network (B, η, δ) from its *shape* (β).
- **One-sided ties are driven by the reciprocity expectation.** ρ* is the top
  factor for the share of one-sided dyads (0.17), with κ adding 0.09, although both
  are negligible for the layer sizes. Higher expectations give more unreciprocated
  ties. **This is global support for the mechanism of claim C6.** A larger budget
  reduces one-sided ties (μ < 0).
- **The bimodal high mode grows with gain and budget, and shrinks with exposure.**
  The share of ties at x ≥ 0.75 depends on η and B (0.20 each, positive) and on ν
  (0.11, negative): more encounters dilute the budget across more weak ties.
- **Several factors are negligible over these ranges:** loyalty ℓ, memory rate λ,
  patience τ, acceptance weight a and first closeness x0 (each ≤ 0.05 everywhere).
  So are κ and ρ*, except for asymmetry. These can be fixed at their calibrated
  values in further analyses, which is factor fixing. The negligible effect of
  loyalty and patience means the invitation-lifecycle details matter little for
  the aggregate structure. They may still matter for individual dyads.

## Limitations

- **One seed per point.** Elementary effects include simulation noise. Factors with
  μ* comparable to the seed-to-seed spread, e.g. a0 and ε, cannot be ranked
  reliably. With 3–5 seeds per point the ranking of the small factors would be
  firmer; the top four are well separated.
- **The transient is shortened by a random start and horizon 600,** which is
  stationary for the calibrated point but possibly not at every corner of the design.
- **Morris ranks the factors but does not split the variance.**

## Next step

Run a variance-based Sobol analysis on the influential factors: B, η, δ, β, ν, ρ*,
θ4, and possibly γ. It would give first-order and total-order indices, and would
test whether η·B/δ is the single control parameter of the layer sizes. With 8
factors and a base sample of 64 the cost is 64 × 10 = 640 ABM runs, i.e. about
2.5 hours on 8 workers. A cheaper alternative is to check the η·B/δ collapse
directly on a one-dimensional sweep.
