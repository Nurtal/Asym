# Asym — Model Specification (v0, draft)

This document fixes the baseline model agreed in the design session. Terminology
follows `CONTEXT.md`. Items marked **[variant]** are not in the baseline but must be
switchable later. Items marked **[open]** are listed in §11.

Time is measured in an **arbitrary unit** (see ADR-0006).

---

## 1. Two levels of description

| Level | Purpose | Formalism |
|---|---|---|
| **ABM** | Simulation of populations, noise-driven threshold crossings | Piecewise-deterministic Markov process (PDMP): discrete stochastic events (invitations, responses, cancellations, encounters, shocks) + deterministic flow between events |
| **Mean-field** | Analysis: fixed points, stability, bifurcations, phase diagrams | Deterministic ODE obtained by replacing event rates with their expectations |

The two levels must agree: ABM ensemble averages converge to the mean-field
trajectories when interaction rates are large (see §10, convergence test).

---

## 2. Agents and parameters

### 2.1 Per-agent parameters θ_i

| Symbol | Name | Role |
|---|---|---|
| `B` | budget | capacity in interaction slots |
| `β` | concentration | exponent on closeness in allocation |
| `ε` | exploration | share of invitations sent to random targets |
| `δ_c` | decay | closeness decay rate in circle c (δ decreases inward) |
| `ρ*` | reciprocity expectation | expected reciprocity ratio |
| `κ` | deficit sensitivity | strength of erosion under reciprocity deficit |
| `λ` | memory rate | decay rate of r and o |
| `w` | hysteresis width | gap between promotion/demotion thresholds |
| `m` | dwell time | minimum time in a circle before any transition |
| `ν` | openness | rate of new encounters |
| `π` | perception bias | log-bias on perceived investment of others |
| `τ` | base patience | scale of waiting time before cancellation |
| `ℓ` | loyalty | protection of close ties against negative signals, in [0, 1] |
| `α` | conflict avoidance | P(silence \| not accepting) |

Agents are sampled from **archetypes with noise**: each archetype is a vector of
centres; agents draw each parameter around the centre (log-normal for positive
parameters, logit-normal for parameters in [0, 1]).

Initial archetypes (centres to be calibrated):

| Archetype | Distinguishing traits |
|---|---|
| butterfly | high B, low β, high ν, high ε |
| loyal-few | moderate B, high β, high ℓ, high τ, wide w |
| transactional | high κ, high ρ*, low ℓ, low τ |
| avoidant | high δ, high α, low ν |

### 2.2 Global parameters

| Symbol | Role |
|---|---|
| `η` | closeness gain per accepted interaction |
| `d` | duration an accepted interaction occupies a slot |
| `c_wait` | slot fraction held by a pending invitation (baseline 0.5) |
| `c_rej` | own-investment cost of a declined invitation |
| `γ` | invitation issuing rate per free slot |
| `ω` | invitee response rate |
| `ζ` | late-acceptance rate for silent invitees |
| `a, b, c` | acceptance coefficients |
| `ψ` | scale of the cancellation drop on r |
| `θ_1 < θ_2 < θ_3 < θ_4` | circle thresholds (acquaintance, friend, close, inner) |
| `x_min` | forgetting threshold |
| `x_0` | closeness at first encounter |
| `σ_p` | perception noise |
| `μ_rand, μ_tri` | random / triadic encounter weights |
| `Λ_s` | shock rate |
| `h_1` | slope of patience in closeness |

---

## 3. State

Per **directed tie** i→j:

- `x_ij ∈ [0,1]`: closeness
- `r_ij ≥ 0`: perceived reciprocity memory
- `o_ij ≥ 0`: own investment memory
- `c_ij ∈ {1,2,3,4}`: circle (1 = acquaintance … 4 = inner circle)
- `s_ij`: time since last circle transition

Per **agent** i:

- `U_i`: committed budget = d-slots of ongoing interactions + `c_wait` × number of pending outgoing invitations
- set of pending outgoing invitations, each with its issue time

Invariant: **U_i ≤ B_i at all times.**

---

## 4. Deterministic flow (between events)

Reciprocity ratio and deficit:

```
q_ij = r_ij / (o_ij + o_0)            (o_0 small regulariser)
D_ij = max(0, ρ*_i − q_ij)
```

Flow:

```
dx_ij/dt = − δ_{i,c_ij} · x_ij
           − κ_i · (1 − ℓ_i · x_ij) · D_ij · x_ij
           [+ μ_s · max(0, q_ij − ρ*_i) · x_ij (1 − x_ij)]     [variant, μ_s ≥ 0 small]

dr_ij/dt = − λ_i · r_ij
do_ij/dt = − λ_i · o_ij
```

The deficit term is asymmetric (negativity bias): a deficit erodes, and a surplus is
neutral in the baseline. Saturation keeps x in [0, 1].

---

## 5. Budget allocation and invitation issuing

Free capacity: `F_i = B_i − U_i`. Agent i issues invitations at total rate `γ · F_i`
(no invitation can be issued if it would violate U_i ≤ B_i).

Target choice:

- with prob. `1 − ε_i`: partner j among existing ties, with weight
  `w_ij = x_ij^{β_i} · g(q_ij)`, where `g(q) = q / (q + ρ*_i)` (saturating, increasing)
- with prob. `ε_i`: a uniformly random agent (stranger or existing tie). This is
  **exploration**.

Issuing an invitation adds `c_wait` to U_i.

---

## 6. Invitation lifecycle (events)

1. **Issue** i→j (rate above). The invitation is *pending*.
2. **Response** by j, at rate `ω`:
   - **accept** with probability
     `P_acc(j,i) = σ(a · x_ji + b · g(q_ji) − c · U_j / B_j)`, provided j has
     ≥ 1 free slot;
   - otherwise **decline** with probability `1 − α_j`, or stay **silent** with
     probability `α_j`.
3. **Late acceptance**: while the invitation is pending after silence, j accepts at
   rate `ζ · P_acc(j,i)` (re-evaluated on the current state).
4. **Cancellation** by i, hazard `1 / T_ij` with `T_ij = τ_i · h(x_ij)`,
   `h(x) = 1 + h_1 · x`. This competes with late acceptance.

Effects:

| Outcome | Budget | Inviter i | Invitee j |
|---|---|---|---|
| accepted | i: −c_wait, +1 slot for d; j: +1 slot for d | `x_ij += η(1−x_ij)`; `o_ij += 1`; `r_ij += e^{π_i+ξ}` | `x_ji += η(1−x_ji)`; `o_ji += 1`; `r_ji += e^{π_j+ξ}` |
| declined | i: −c_wait | `o_ij += c_rej` (unreturned investment) | none |
| cancelled after wait `t_w` | i: −c_wait | `r_ij ← max(0, r_ij − ψ · (1 − ℓ_i x_ij) · t_w)` | none (baseline); **[variant]** guilt effect on x_ji |

`ξ ~ N(0, σ_p²)` is the perception noise. On an accepted invitation the initiator
also perceives j's acceptance as investment.

---

## 7. Circles (discrete transitions)

Global thresholds `θ_1 < θ_2 < θ_3 < θ_4`. Agent i has its own hysteresis width `w_i`
and dwell time `m_i`. Transitions are only allowed when `s_ij ≥ m_i`:

- **promote** c → c+1 when `x_ij ≥ θ_{c+1} + w_i/2`
- **demote** c → c−1 when `x_ij < θ_c − w_i/2`
- **forget** (delete tie) when `x_ij < x_min` (with `x_min < θ_1`)

Circle feedback on the continuous dynamics:

- decay `δ_{i,c}` decreases with c (inner ties are more durable)
- **[open]** an optional allocation priority bonus per circle on `w_ij`

Capacity: **no imposed circle size** in the baseline. Layering must emerge from
budget scarcity + β + hysteresis (ADR-0003). **[variant]** a soft capacity cost on
x growth when circle c exceeds a target `K_c^i`.

**[variant]** a *dormant* state replacing deletion, which an old friend can revive
with a bonus.

---

## 8. Encounters, shocks, initial conditions

**Encounters** (tie formation), at rate `ν_i` per agent:

- random: with weight `μ_rand`, meet a uniform stranger
- triadic closure: with weight `μ_tri`, pick a friend k ∝ x_ik, then k's partner
  j ∝ x_kj (j not already tied to i)

An encounter creates both ties i→j and j→i with `x = x_0`, `r = o = 0`, circle 1.

The encounter rate `ν_i` does not depend on N. In the baseline, though, an accepted
exploration invitation to a stranger also creates a tie. That is a second
tie-formation channel, and its rate grows with N, because a uniform target is more
often a stranger. **[variant]** `exploration: ties` restricts exploration to
existing ties, so that new ties form only through encounters, at a rate independent
of N.

**Shocks**, at global rate `Λ_s` (experimental knob):

- tie shock: `x_ij ← φ · x_ij` for a random tie (φ drawn, e.g. in (0, 1))
- budget shock: `B_i ← φ_B · B_i` for a random duration

**Initial conditions**: a model parameter `init.mode`:

- `empty`: no ties
- `random`: random graph (density, x distribution as parameters)
- `file`: load a specific situation from JSON or CSV, for example
  - `agents.csv`: `id, archetype[, param overrides…]`
  - `ties.csv`: `i, j, x[, r, o, circle]` (directed rows)

---

## 9. Mean-field model

Replace the stochastic events by their expected rates. For a dyad {i, j} with
issuing rates `I_ij` and acceptance probabilities `P_ij`, the accepted interaction
rate is `A_ij = I_ij · P_acc(j,i) + I_ji · P_acc(i,j)` (plus late-acceptance
contributions), and

```
dx_ij/dt = η (1 − x_ij) A_ij − δ_{i,c} x_ij − κ_i (1 − ℓ_i x_ij) D_ij x_ij
dr_ij/dt = (perceived j-investment rate) − λ_i r_ij
do_ij/dt = (own investment rate)        − λ_i o_ij
```

An isolated dyad is 6-dimensional (x, r, o for each direction). For phase-plane
analysis it is reduced by:

- a quasi-steady-state on the memories (r, o) when λ is fast, giving a 2-D system in
  (x_ij, x_ji); or
- the symmetric-agent subspace.

Circles enter as a piecewise-smooth (Filippov / hybrid) system with hysteresis.

Tooling: SymPy (fixed points, Jacobians) + SciPy (integration) + parameter sweeps.
Numerical continuation (PyDSTool / AUTO) only if the sweeps reveal bifurcations
worth following.

---

## 10. Observables, experiments, validation

**Research questions (core):**

1. Dyad phase diagram per archetype pair: basins of stable friendship vs breakup,
   bifurcations.
2. Emergence of Dunbar-like layering, and which parameters set the layer ratios.
3. Origins of asymmetry: preference mismatch vs perception bias.
4. Shock resilience: recovery time and circle-drop probability vs hysteresis width.

**Secondary:** network structure (clustering, communities, inequality of close-tie
degree), and the effect of archetype composition on global stability.

**Metrics:** circle sizes per agent and their ratios; asymmetry |x_ij − x_ji| and
circle mismatch; reciprocity distribution; tie lifetime and churn; fraction of
budget locked in pending invitations (isolation trap); clustering coefficient,
modularity.

**Validation & testing:**

- unit tests on invariants: x ∈ [0,1], U_i ≤ B_i, hysteresis respected, dwell time
  respected, saturation
- **convergence test**: ABM ensemble mean → mean-field ODE as rates scale up
- reproducibility: seeded RNG + versioned YAML configs under `experiments/`
- baseline vs robustness: `init.mode = empty` vs `random` must lead to statistically
  similar steady-state layering
- burn-in period discarded before measuring

---

## 11. Implementation decisions (v0.1)

These were settled while implementing the tickets. Where they differ from the text
above, they take precedence.

- **Budget semantics.** B_i is a *stock* of concurrent slots. An accepted interaction
  occupies 1 slot on both sides for duration d, and a pending invitation occupies
  `c_wait` slots of the inviter. An agent issues invitations at rate γ·(B_i − U_i)
  only while it has at least one full free slot. An invitee can accept only if it
  has a free slot and the inviter can still turn its `c_wait` into a full slot.
- **Own-investment memory o_ij** makes the reciprocity ratio well-defined. The ratio
  uses a neutral prior: `q = (r + o0)/(o + o0)`, so a fresh tie starts at q = 1 (no
  deficit as long as ρ* < 1). `o0 > 0` is required.
- **Circle thresholds.** `globals.thresholds` holds 3 values, the lower bounds of
  friend, close friend and inner circle. Acquaintance is the floor of every existing
  tie. Below `x_min` the tie is forgotten.
- **Targets.** With probability ε an invitation goes to a uniformly random other
  agent (exploration). Otherwise its target is drawn among existing ties ∝ x^β·g(q).
  An agent without any weighted tie issues nothing on that branch.
- **Accepting a stranger** (exploration) creates both ties at x0, then applies the
  interaction jump.
- **Perception.** Each accepted interaction adds `inv_unit · e^{π+ξ}` to r and
  `inv_unit` to o on both sides. A decline adds `c_rej · inv_unit` to the inviter's o.
- **Population sampling** uses `population.seed`, independently of the simulation
  seed, so an ensemble of seeds shares one population.
- **Exactness.** Event rates are drawn by thinning against constant bounds, so the
  PDMP is simulated exactly. Circle transitions and forgetting are checked after
  events on the ties concerned and every `simulation.check_interval`.
- **Mean-field.** The waiting-age masses Wu, Ws carry the expected cancellation drop.
  Interaction occupancy is a delay of length d (or exponential, used for the dyad
  reduction). Encounters, shocks and the dormant variant are not represented.
- **Dyad reduction** is numerical: the quasi-steady state of the fast variables is
  found by relaxation. Fixed points come from batched Newton iterations with
  finite-difference Jacobians, because no closed form exists.
- **Variants.** Guilt multiplies the invitee's x_ji by (1 − guilt) on cancellation.
  Soft capacity scales the closeness gain by 1/(1 + cost·max(0, n_c − K_c)/K_c).
  A dormant tie keeps its decayed r and o, and is revived at x0 + revival_bonus.
  `exploration: ties` draws the ε-target uniformly among the existing ties. An agent
  with no tie then issues nothing.
- **Embedded dyad** (`asym.meanfield.embedded`). It is the dyad analysis inside a
  population, because an isolated dyad always ends in friendship. Each focal agent
  sits in a clique with M background partners (by default of its own archetype),
  and the focal tie bridges the two cliques. The whole system of 2 + 2M agents is
  integrated with the mean-field solver. Bistability is detected as an outcome that
  depends on the focal start x0.

## 12. Open points

- Exact forms of `g`, `h` and the per-circle δ ladder.
- Whether circles add an allocation priority bonus on top of x^β.
- Calibration of archetype centres and noise levels. A first calibration towards
  Dunbar-like ratios is in `docs/experiments/02-calibrated-layering-scaling.md`. It holds
  at N ≈ 100, but the outer ratio grows with N: open question of what caps the
  acquaintance layer.
- Mapping the arbitrary time unit to days/weeks.
