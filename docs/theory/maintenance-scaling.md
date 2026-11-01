# Why layer sizes collapse on B/δ, and why η deviates

This note derives the collapse measured in experiment 11 from the mean-field
equations (`docs/model-spec.md` §9, solver `asym/meanfield/solver.py`). It then
checks each step numerically with `experiments/13_scaling_theory.py`; the raw
outputs are in `results/13_scaling_theory/` (not versioned).

Experiment 11 found three things:

- B and δ are exchangeable for every layer (R² ≥ 0.985);
- η acts like B/δ on the middle layers;
- η is stronger on the inner circle and weaker on the acquaintance layer.

The derivation explains all three:

1. **Mean values** (§1). In the mean-field, the steady state depends on B, η and δ
   only through Q = ηB/δ, apart from two named corrections.
2. **Fluctuations** (§2). At a given mean closeness, the variance of a tie depends
   on η but not on B or δ. η is therefore the only one of the three that also sets
   the noise.
3. **Stability** (§3). The same calculation gives the condition under which equal
   sharing between ties is unstable. That condition is the pairing race.

## 1. Mean values: a scaling law of the mean-field

### 1.1 Budget enters only as a scale

All budget-related processes act per slot:

- invitations are issued at rate γ·F, with F = B − U;
- the pending masses P and W follow the issuing rate linearly;
- acceptance depends on the load U/B, not on U;
- interaction occupancy and the r and o memories are linear in the interaction
  rate A.

Multiply every agent's budget by s. Then U, F, P, W, A, r and o, all multiplied
by s, solve the scaled system exactly. The only exception is the reciprocity
ratio q = (r + o0)/(o + o0), which is invariant only when o0 ≪ r, o. Every
budget-driven rate can therefore be written as

    A_ij = B · â_ij(x, q, U/B),

where â does not depend on B.

### 1.2 The closeness equation

With D the reciprocity deficit, the closeness of tie i→j in circle c obeys

    dx/dt = η B â (1 − x) − δ_c x − κ (1 − ℓ x) D x.

Divide by δ_c. Of all the other equations (pending masses, memories, occupancy),
none contains η or δ. The stationary condition of the whole system is therefore

    Q_c · â · (1 − x) = x · [1 + K_c (1 − ℓ x) D],
    Q_c = η B / δ_c,    K_c = κ / δ_c.

**Proposition 1.** The mean-field stationary states depend on (B, η, δ) only
through Q_c = ηB/δ_c, the deficit erosion per decay time K_c = κ/δ_c, and the
regulariser o0/B. This holds for a given basin of attraction; scaling the whole δ
ladder keeps the ratios δ_c/δ_c′.

**The three routes of experiment 11 differ only by these corrections:**

| route | Q | K = κ/δ | o0/B |
|---|---|---|---|
| η × q | × q | same | same |
| B × q | × q | same | / q |
| δ × 1/q | × q | × q | same |

The η route is the pure-Q route. The δ route also strengthens deficit erosion
relative to decay. The B route also weakens the prior in q.

The basin caveat matters. The δ route slows the dynamics of x but not those of
the memories, so a system with several attractors can reach a different one from
the same start.

### 1.3 Check

Setup:

- a clique of 8 calibrated agents (2 of each profile), with every directed tie
  started at x ~ U(0.2, 0.8), r = o = 1, and fixed topology;
- the mean-field is integrated to t = 4000 under each route at q = 2;
- the final closeness of the 56 ties is compared with the η route.

| κ | o0 | mean x (q = 1) | mean x (q = 2, η route) | B vs η: mean / max abs. diff. | δ vs η: mean / max abs. diff. |
|---|---|---|---|---|---|
| on | 0.5 | 0.707 | 0.843 | 4.9e-4 / 0.011 | 0.038 / 0.19 |
| on | 0.005 | 0.707 | 0.841 | 6.9e-6 / 1.7e-4 | 0.038 / 0.19 |
| off | 0.5 | 0.878 | 0.953 | 5.6e-7 / 1.4e-6 | 3.3e-15 / 6.1e-15 |
| off | 0.005 | 0.878 | 0.953 | 6.3e-9 / 1.6e-8 | 3.3e-15 / 6.1e-15 |

As predicted:

- **Without deficit erosion (κ = 0), the δ and η routes are identical to machine
  precision.**
- The B route converges to the η route as o0/B → 0. The prior in q matters only
  through the deficit term and the weight g(q), so its effect is small.
- With κ on, the δ route differs by up to 0.19 on single ties. These are the
  transactional ties, the only profile with κ > 0, whose erosion per decay time
  doubles.

### 1.4 What this explains in experiment 11

**The K correction explains every B-versus-δ gap on the inner layers, with the
right sign.**

- At q = 0.5, the δ route doubles δ, so K is halved: less erosion, larger layers.
  Inner circle 0.91 against 0.69 by the B route; +close 2.53 against 1.81;
  +friends 7.71 against 6.0.
- At q = 2, K is doubled: more erosion, smaller layers. Inner circle 6.01 against
  6.15; +close 16.2 against 18.9; +friends 27 against 31.
- The mixed route (B × √q, δ × 1/√q) moves K by √q and lies between the two in
  every one of these cells.

**But the mean-field alone predicts the η route to be the *reference*, not the
odd one out.** In experiment 11 the η route deviates most. The mean values cannot
explain that; the fluctuations do.

## 2. Fluctuations: η sets the noise

### 2.1 One tie as shot noise

Treat one maintained tie as follows:

- it receives interactions at rate Λ(x), with Λ ∝ B;
- each interaction is a jump J = η(1 − x);
- between interactions it decays at rate δ, with κ = 0.

Let β_eff be the elasticity of Λ in x near the fixed point (§3 gives its value).
Write the drift as f(x) = ηΛ(x)(1 − x) − δx. At the fixed point x*,
ηΛ = δx*/(1 − x*), so the relaxation rate is

    k = −f′(x*) = δ · [1 − β_eff (1 − x*)] / (1 − x*).

The linear-noise approximation gives the stationary variance σ² = Λ J² / (2k).
Substituting:

    σ² = (η / 2) · x* (1 − x*)² / [1 − β_eff (1 − x*)].

**Proposition 2.** At a given mean closeness x*, the variance of a tie depends on
η and β_eff only, not on B or δ. B and δ set the mean (through Q) and the time
scale (the correlation time 1/k ∝ 1/δ), but not the noise. Raising η at fixed Q
multiplies the variance by the same factor.

For a single tie the statement is even exact, not just linear. The δ route is the
B route seen in slow motion: rescaling time by q maps one onto the other.

### 2.2 Check: one tie, exact simulation

Each route doubles Q from a base whose fixed point is x* = 0.5 or 0.8:

- B route: rate × 2;
- η route: η × 2;
- δ route: δ / 2.

The interaction rate is c·x^β. The tie is simulated exactly by thinning, over a
time of 10⁶ (2·10⁶ for the δ route), sampled once per unit time.

| β | route | mean-field x* | simulated mean | simulated var | LNA var | sim / LNA |
|---|---|---|---|---|---|---|
| 0 | B | 0.667 | 0.667 | 3.40e-3 | 3.33e-3 | 1.02 |
| 0 | η | 0.667 | 0.666 | 7.02e-3 | 6.67e-3 | 1.05 |
| 0 | δ | 0.667 | 0.667 | 3.40e-3 | 3.33e-3 | 1.02 |
| 0 | B | 0.889 | 0.889 | 5.12e-4 | 4.94e-4 | 1.04 |
| 0 | η | 0.889 | 0.889 | 1.07e-3 | 9.88e-4 | 1.08 |
| 0 | δ | 0.889 | 0.889 | 5.12e-4 | 4.94e-4 | 1.04 |
| 0.5 | B | 0.894 | 0.894 | 4.96e-4 | 4.75e-4 | 1.04 |
| 0.5 | η | 0.894 | 0.894 | 1.05e-3 | 9.50e-4 | 1.11 |
| 0.5 | δ | 0.894 | 0.894 | 4.96e-4 | 4.75e-4 | 1.04 |
| 1.5 | B | 0.906 | 0.905 | 4.48e-4 | 4.19e-4 | 1.07 |
| 1.5 | η | 0.906 | 0.904 | 9.79e-4 | 8.38e-4 | 1.17 |
| 1.5 | δ | 0.906 | 0.905 | 4.48e-4 | 4.19e-4 | 1.07 |

- All three routes give the same mean.
- The B and δ routes give the same variance; with the same seed, it is
  bit-identical, because they are time rescalings of each other.
- The η route doubles the variance (ratio 2.06–2.18).
- The LNA formula is accurate to 2–17%. The error grows with η and β, as expected
  from a first-order expansion in the jump size.

### 2.3 Check: inside the full ABM

Setup:

- the calibrated model of experiment 10 (N = 100, random start);
- 2 seeds per route;
- t from 300 to 1100, sampled every 5;
- per-tie temporal variance, for ties alive over the whole window, normalised by
  x(1 − x)².

Median of the normalised variance, by bin of the tie's mean x:

| mean x | q = 1 | B × 2 | η × 2 | δ / 2 | η / B |
|---|---|---|---|---|---|
| 0.20–0.35 | 0.117 | 0.128 | 0.171 | 0.108 | 1.33 |
| 0.35–0.50 | 0.140 | 0.166 | 0.255 | 0.141 | 1.54 |
| 0.50–0.65 | 0.219 | 0.170 | 0.289 | 0.155 | 1.70 |
| 0.65–0.80 | 0.144 | 0.157 | 0.343 | 0.141 | 2.19 |
| 0.80–0.95 | 0.077 | 0.090 | 0.200 | 0.079 | 2.24 |

(Bins hold 88–1775 ties; the η route has only 3 ties below 0.2, so that bin is
omitted.)

- **B and δ give the same noise at the same mean**, within 10%. The δ route is
  slightly lower, as expected: its correlation time is twice as long, and a finite
  window underestimates the variance more.
- **Doubling η doubles the noise of strong ties** (ratio 2.2). The ratio is lower
  for weak ties (1.3–1.7). Only ties that survive the whole window are kept, and
  surviving cuts off the lower tail, more so when the noise is larger.
- The absolute level is 2–4 times the bare η/2 = 0.045. The LNA fixes the scaling
  with η, not the level. Inside the ABM, β_eff > 0 amplifies the noise, and so do
  sources the single-tie model lacks: acceptance draws, partners' free slots and
  δ jumps at circle changes.

### 2.4 What this explains in experiment 11

At the same Q, the η route gives every tie the same mean but a wider distribution.
Two layers are tails of that distribution:

- **The inner circle is the upper tail.** Most ties' means lie below θ₄ = 0.82, so
  widening the distribution puts more of them above it.
- **The acquaintance layer is cut by the lower tail.** A weak tie whose
  fluctuation touches x_min is forgotten for good.

Prediction: a larger η gives more inner ties and fewer ties in total, and a smaller
η the reverse. The η route against the B route, at the four values of q ≠ 1, gives
12 sign comparisons, **and all agree with experiment 11**:

| q | inner: η vs B | all ties: η vs B | high-mode share: η vs B |
|---|---|---|---|
| 0.5 | 0.64 < 0.69 ✓ | 35.2 > 27.1 ✓ | 0.029 < 0.036 ✓ |
| 0.71 | 1.06 < 1.08 ✓ | 37.5 > 33.2 ✓ | 0.043 < 0.049 ✓ |
| 1.41 | 3.99 > 3.34 ✓ | 41.9 < 44.9 ✓ | 0.139 > 0.115 ✓ |
| 2 | 8.15 > 6.15 ✓ | 44.0 < 50.0 ✓ | 0.255 > 0.186 ✓ |

The 12 corresponding comparisons of the η route against the δ route also all agree.

**Quantitative check of the upper tail, in the ABM runs of §2.3.** The quantity
compared is the number of ties per agent with x ≥ θ₄ at a snapshot (a proxy for
inner-circle membership, without hysteresis):

| | ties ≥ θ₄ per agent |
|---|---|
| q = 1 | 1.97 |
| B × 2 | 5.57 |
| δ / 2 | 5.37 |
| η × 2, observed | 7.35 |
| η × 2, predicted from the B route by widening each tie's fluctuations by √2 around its own mean | 6.86 |

**Widening the noise alone accounts for about 70% of the η excess** (from 5.57 to
6.86, against 7.35 observed). The rest is the lower bound of a crude prediction:

- the widened trajectories keep the B route's time correlations;
- only the ties alive throughout are widened;
- the deficit term is ignored.

## 3. Stability: the condition for the pairing race

The relaxation rate of §2.1 also gives the stability of a maintained tie:

    k > 0   ⟺   β_eff (1 − x) < 1.

A tie whose closeness falls below 1 − 1/β_eff cannot be held. It either climbs or
decays, so intermediate closeness is unstable. The noise amplification
1/[1 − β_eff(1 − x)] diverges at the same boundary: ties near it flicker before
they switch, an early-warning signal.

The same eigenvalue governs competition between ties. Take two ties at a common x
with shares a₁ + a₂ = 1, and perturb them in opposite directions (u = x₁ − x₂).
The total S stays constant to first order, and

    du/dt = δ [β_eff − 1/(1 − x)] u,

so **equal sharing between ties at closeness x is unstable iff
β_eff(x)(1 − x) > 1**.

The effective concentration combines several feedbacks:

    β_eff ≈ (1 − ε) β + a x (1 − P_acc) [+ circle-ladder feedback, since δ drops inward].

- The first term is allocation ∝ x^β, diluted by the exploration share ε.
- The second term is acceptance, which rises with x. With a = 4 it is not small,
  so even β = 1 can be unstable.
- The δ ladder also feeds back: stronger ties decay more slowly. In the smooth
  limit this adds −d ln δ/d ln x.

Consequences:

- **loyal_few** (β = 3) cannot hold any tie below x ≈ 2/3. That is the
  all-or-nothing behaviour found in experiment 04, and the gap between the two
  modes of the bimodal closeness distribution.
- **butterfly** (β = 0.6, ε = 0.15) has β_eff(1 − x) < 1 over most of [0, 1], so
  its ties are graded.

### 3.1 Check: cliques of identical agents

Setup:

- mean-field cliques of M identical agents, with κ = 0 and a flat δ ladder, so that
  only the allocation and acceptance feedbacks remain;
- integrated to t = 3000 from the symmetric state x = 0.5, and from that state with
  a ±0.02 symmetric perturbation;
- predicted from the symmetric run, using β_eff = (1 − ε)β + a·x(1 − P_acc);
- the observed outcome is the spread of x after the perturbation.

Each cell shows β_eff(1 − x_sym), then the observed outcome: **=** means equal sharing persisted (spread < 0.001); **split** means it broke apart (spread 0.18–0.34, ties spread between about 0 and 0.5–0.8).

| profile | B | x_sym | β = 0.5 | β = 1.0 | β = 1.5 | β = 2.0 | β = 3.0 |
|---|---|---|---|---|---|---|---|
| transactional | 12 | 0.88 | 0.07 = | 0.13 = | 0.19 = | 0.25 = | 0.37 = |
| transactional | 3.8 | 0.67 | 0.20 = | 0.36 = | 0.51 = | 0.67 = | 0.98 **split** ✗ |
| transactional | 1.9 | 0.50 | 0.34 = | 0.58 = | 0.81 = | 1.05 **split** | 1.53 **split** |
| transactional | 1 | 0.33 | 0.47 = | 0.79 = | 1.10 **split** | 1.42 **split** | 2.05 **split** |
| loyal_few | 10 | 0.86 | 0.08 = | 0.15 = | 0.22 = | 0.29 = | 0.42 = |
| loyal_few | 3 | 0.63 | 0.23 = | 0.40 = | 0.57 = | 0.75 = | 1.09 **split** |
| loyal_few | 1.5 | 0.46 | 0.37 = | 0.62 = | 0.88 = | 1.14 **split** | 1.66 **split** |
| loyal_few | 0.8 | 0.30 | 0.49 = | 0.82 = | 1.16 **split** | 1.49 **split** | 2.16 **split** |

Here M = 8 and B is reduced to lower x_sym. **The criterion predicts the outcome in 39 of 40 cases.** The one miss is a marginal case, criterion 0.98, which splits; the first-order β_eff leaves out the g(q) and patience feedbacks.

Reading:

- **The pairing race is a regime, not a generic outcome.** It needs both
  concentration (β_eff > 1) and scarce budget per partner (x_sym < 1 − 1/β_eff).
- At the calibrated budgets, a clique of 8 shares equally even at β = 3. Reducing
  the budget per partner, through smaller B or larger M, makes it split into a few
  strong ties and many dropped ones.
- The control parameter is again the budget per alter. This connects the pairing
  race to Tamarit's inverse regime (experiments 08 and 09): with abundant resources
  per alter, equal sharing is stable.
- In the stochastic clique runs of experiment 07, the β ≥ 1 cliques that
  fragmented ran on the uncalibrated archetypes, with smaller budgets. The
  criterion says that the same cliques would not fragment at calibrated budgets.
  This is a prediction for the population-level check.

## 4. What the derivation does not give

- **Layer counts in closed form.** These need the distribution of â over an agent's
  ties, which is set self-consistently by allocation, acceptance and the partners'
  choices. The derivation explains *which* parameter combinations the counts depend
  on, and in which direction η departs from them, not the counts themselves.
- **The outer layer.** Ties form at the encounter rate ν, which the mean-field
  leaves out. ν does not scale with B, so B/δ cannot be the whole story for the
  acquaintance layer. Experiment 11 nonetheless found B and δ exchangeable there
  too (R² = 0.985). The likely reason is that weak ties are kept alive by
  exploration contacts, at rate ∝ εB, so the relevant ratio is again εB/δ.
- **Time scales.** Proposition 1 is about steady states. The δ route slows every
  relaxation by q, and the B route does not. At fixed burn-in, transients can
  therefore differ.

## 5. Consequences for the paper

- §5.2 can state an analytical result:
  - B and δ enter the stationary mean-field only as Q = ηB/δ, with two named,
    measurable corrections, K = κ/δ and o0/B;
  - at a fixed mean, the noise of a tie depends on η alone;
  - therefore B/δ sets the size of the network, and η additionally sets how
    granular each relationship is: how many interactions it takes to cross a
    threshold, and hence the tails.
- §6.4 (pairing race) gets a criterion, β_eff(1 − x) > 1. The same quantity predicts
  the all-or-nothing behaviour of loyal_few and the gap in the bimodal closeness.
- The "early warning" amplification near the boundary is a testable side
  prediction for the stochastic switching of experiment 07.
