# Asym: ODD description

This description follows the ODD protocol, second update (Grimm et al. 2020,
*JASSS* 23(2):7, doi:10.18564/jasss.4259). It describes the agent-based model as
implemented in `asym/abm/engine.py` (commit at the time of writing: see `git log`).
The mean-field counterpart (`asym/meanfield/`) is described in §7.4 as a
submodel used for analysis and docking. Equations and implementation decisions are
detailed in `docs/model-spec.md`; where the two differ, the code and §11 of the spec
are authoritative.

---

## 1. Purpose and patterns

**Purpose.** The model explains how heterogeneity in individual social behaviour
produces asymmetric relationships, layered personal networks and history-dependent
relationship outcomes. Agents differ in four respects:

- how much time they have;
- how they concentrate it;
- what reciprocity they expect;
- how fast their ties erode.

The model is a *theoretical* model, meant for understanding rather than for
prediction.

**Patterns used to evaluate the model** (pattern-oriented modelling):

1. **Layered ego networks.** Cumulative layer sizes grow outwards with a roughly
   constant ratio of about 3 (Hill & Dunbar 2003; Zhou et al. 2005; Dunbar et al.
   2015). This pattern was used for calibration (experiment 06).
2. **Regime change with resources per alter.** Tamarit et al. (2018) find an
   *inverse regime*, where the inner layers are the most populated, when the
   resources per available alter are high. This pattern was **not** used for
   calibration (experiments 08–09).
3. **Independence of the start.** The steady-state layering does not depend on the
   initial network (experiments 01, 01b).
4. **Asymmetric and unreciprocated ties.** A large share of friendships are
   perceived differently at the two ends (Almaatouq et al. 2016).
5. **Early fate of ties.** A tie's lifetime is largely decided early on (Hidd et al.
   2023; Burt 2000).

---

## 2. Entities, state variables and scales

**Agents** (i = 1 … N, closed population). Each agent carries the behavioural
parameters θ_i in Table 1, fixed over a run, plus two dynamic state variables:

- the committed budget U_i, which counts ongoing interactions (1 slot each) and
  pending invitations (c_wait slots each);
- the set of its pending outgoing invitations, with issue times and status
  (unanswered or silent).

**Directed ties** i→j are entities in their own right, owned by i. Their state:

| Variable | Range | Meaning |
|---|---|---|
| x_ij | [0, 1] | closeness, as perceived and valued by i |
| r_ij | ≥ 0 | memory of perceived investment received from j |
| o_ij | ≥ 0 | memory of i's own investment in j |
| c_ij | {1, 2, 3, 4} | circle: acquaintance, friend, close friend, inner circle |
| s_ij | ≥ 0 | time since the last circle transition |

Ties are directed, and x_ij ≠ x_ji in general: **asymmetry is a state of the
model, not an output measure only.** A tie exists from its creation (an encounter,
or an accepted exploration invitation to a stranger) until it is forgotten.

**Invitations** are short-lived entities: inviter, invitee, issue time, status.

**Environment.** There is no space. The population is closed and unstructured
apart from the tie network itself.

**Global variables.** Table 2 lists the global parameters. There is also an
optional shock process.

**Scales.** Time is continuous, in an **arbitrary unit** (ADR-0006); one unit is
the default duration d of an interaction. Typical runs have horizon 1500 with a
burn-in of 1000. Populations range from 8 to 400 agents (performance: about 10⁴
events per second, `docs/performance.md`).

**Table 1. Agent parameters θ_i.** Baseline defaults, and the calibrated archetype
centres of experiments 06–09 (B, β and δ were rescaled by the calibration).

| Symbol | Name | Default | butterfly | loyal_few | transactional | avoidant |
|---|---|---|---|---|---|---|
| B | budget (slots) | 5 | 20 | 10 | 12.5 | 12.5 |
| β | concentration of allocation | 1 | 0.6 | 3.0 | 1.2 | 1.2 |
| ε | exploration share | 0.05 | 0.15 | 0.05 | 0.05 | 0.05 |
| δ_c | decay per circle (outer→inner) | 0.08, 0.05, 0.03, 0.015 | 0.024, 0.017, 0.012, 0.007 | same as butterfly | same as butterfly | 0.045, 0.033, 0.023, 0.014 |
| ρ* | reciprocity expectation | 0.8 | 0.8 | 0.8 | 1.1 | 0.8 |
| κ | deficit sensitivity | 0 | 0 | 0 | 1.0 | 0 |
| λ | memory rate of r, o | 0.1 | 0.1 | 0.1 | 0.1 | 0.1 |
| w | hysteresis width | 0.05 | 0.05 | 0.15 | 0.05 | 0.05 |
| m | minimum dwell time | 1 | 1 | 1 | 1 | 1 |
| ν | encounter rate (openness) | 0 | 0.15 | 0.03 | 0.06 | 0.02 |
| π | perception log-bias | 0 | 0 | 0 | 0 | 0 |
| τ | base patience | 5 | 5 | 12 | 2.5 | 5 |
| ℓ | loyalty | 0 | 0 | 0.8 | 0.1 | 0 |
| α | P(silence \| not accepting) | 0.5 | 0.5 | 0.5 | 0.5 | 0.9 |

**Table 2. Global parameters.** Defaults; values that differ in experiments 06–09
are in brackets.

| Symbol | Role | Value |
|---|---|---|
| η | closeness gain per accepted interaction | 0.1 [0.09] |
| d | interaction duration | 1 |
| c_wait | slots held by a pending invitation | 0.5 |
| c_rej | own-investment cost of a decline | 0.5 |
| inv_unit | investment increment | 1 |
| γ | issuing rate per free slot | 0.5 [0.85] |
| ω | response rate | 1 |
| ζ | late-acceptance rate of silent invitees | 0.2 |
| a0, a, b, c | acceptance intercept and weights | 0, 4, 2, 2 [a0 = 0.5] |
| ψ | cancellation drop per unit waiting time | 0.1 |
| h1 | slope of patience in closeness | 1 |
| o0 | prior pseudo-count of the reciprocity ratio | 0.5 |
| θ_2, θ_3, θ_4 | lower bounds of friend, close friend, inner circle | 0.3, 0.55, 0.8 [0.31, 0.60, 0.82] |
| x_min | forgetting threshold | 0.02 |
| x0 | closeness at first encounter | 0.1 |
| σ_p | perception noise | 0 |
| μ_rand, μ_tri | random / triadic encounter weights | 1, 1 |
| Λ_s | shock rate | 0 |

---

## 3. Process overview and scheduling

The model is a **piecewise-deterministic Markov process** (ADR-0001). Between
events, every tie follows a deterministic flow (closeness decay and erosion,
memory decay; §7.1). Events occur in continuous time:

| Event | Rate |
|---|---|
| issue an invitation (agent i) | γ·(B_i − U_i), while at least one full slot is free |
| invitee response | ω per unanswered invitation |
| late acceptance | ζ·P_acc per silent invitation |
| cancellation | 1/(τ_i (1 + h1·x_ij)) per pending invitation |
| encounter (agent i) | ν_i |
| shock | Λ_s |
| end of an interaction | scheduled, after d |
| end of a budget shock | scheduled |

**Scheduling.** The next stochastic event is drawn by *thinning* against constant
upper bounds of the channel rates, so the process is simulated exactly. Scheduled
events (interaction ends, budget restorations) are kept in a time-ordered heap.

Ties are advanced *lazily*: a tie's flow is integrated up to the current time only
when the tie is used by an event or by housekeeping. The flow has a closed form
when there is no deficit, and is otherwise integrated with RK4 at a step ≤ 0.2.

After every event the ties concerned are checked for circle transitions and
forgetting. Every `check_interval` (0.25) all ties are advanced and checked
(housekeeping). State is sampled every `sample_interval` after the burn-in.

---

## 4. Design concepts

- **Basic principles.**
  - **Time is a finite, concurrent resource:** the budget is a stock of slots. No
    capacity of any circle is imposed (ADR-0003), so layering must emerge from
    budget scarcity, allocation concentration and circle-dependent decay.
  - **Relationships are directed perceptions.** Each side evaluates the tie
    through its own expectations, with a negativity bias: a reciprocity deficit
    erodes closeness, while a surplus is neutral.
  - **Circles are hybrid states** (ADR-0002). Discrete labels with hysteresis
    and dwell time feed back on the continuous dynamics: decay is slower in inner
    circles.
- **Emergence:**
  - layer sizes and their ratios;
  - the regime of the layer populations (normal versus inverse);
  - the bimodal closeness distribution;
  - asymmetry and unreciprocated ties;
  - pair formation within neighbourhoods;
  - tie lifetimes and switching between the high and low relationship states.
- **Adaptation.** Agents adapt their allocation to their current ties: targets are
  drawn ∝ x^β·g(q), where g(q) = q/(q + ρ*) rewards perceived reciprocity. Responses
  depend on the invitee's own view of the tie and on its current load.
- **Objectives.** None explicit; behaviour is rule-based. The model does not
  optimise. This is the main difference from Tamarit et al. (2018), whose layers
  result from entropy maximisation under a resource constraint.
- **Learning.** None beyond the memories r and o, which decay at rate λ.
- **Prediction.** None.
- **Sensing.** An agent knows its own ties (x, r, o, circle), its budget, and
  whether its invitations are answered. Investment received is perceived with a
  log-bias π and noise σ_p. Agents do not observe the other side's closeness.
- **Interaction.** Interaction is direct and pairwise, through invitations:
  - accepted invitations raise closeness on both sides;
  - declines raise the inviter's unreturned investment;
  - silences hold the inviter's budget until a late acceptance or a cancellation.

  Encounters create ties at random or by triadic closure.
- **Stochasticity.** These are random:
  - event times;
  - target choice and exploration;
  - acceptance, decline and silence;
  - cancellations;
  - encounter partners;
  - perception noise;
  - shocks;
  - agent parameters (sampled around archetype centres);
  - the initial network in `random` mode.

  Population sampling uses `population.seed`, independent of the simulation seed,
  so seed ensembles share one population.
- **Collectives.** None imposed. Circles are per-agent categories of ties, not
  groups. Pairs and cliques can emerge.
- **Observation.** The full tie table is sampled at regular times after the
  burn-in. Event logs are optional. Metrics (`asym/metrics`) include:
  - circle and cumulative layer sizes, layer ratios and the exponent μ;
  - asymmetry (|x_ij − x_ji|, circle mismatch, one-sided ties);
  - reciprocity ratios;
  - tie lifetimes and churn;
  - shock resilience and the isolation trap (budget locked in pending invitations);
  - network metrics (clustering, modularity, Gini);
  - two-state dyad switching.

---

## 5. Initialisation

The initial network is a parameter (`init.mode`):

- **empty**: nobody knows anybody;
- **random**: an undirected G(N, density) random graph, with both directions
  created and x ~ U(x_range);
- **file**: a specified situation (agents and ties from JSON or CSV).

Initial ties get the circle that matches their x, with r = o given or 0. Agents
come either from an explicit list or from a population specification: a
composition by archetype (counts or proportions), a size, a noise level s
(default 0.15) and a seed. Each parameter is drawn around its archetype centre:

| Parameter type | Distribution |
|---|---|
| positive | mean-preserving log-normal |
| parameters in [0, 1] | logit-normal |
| π | normal |
| δ ladder | one shared log-normal factor, preserving the order |

Experiments 05–09 start from `empty` and discard a burn-in of 1000 time units.
This is justified by stationarity checks: first and last parts of the measurement
window differ by less than 3%.

---

## 6. Input data

None. The model uses no external time series.

---

## 7. Submodels

### 7.1 Deterministic flow of a tie

```
q_ij   = (r_ij + o0) / (o_ij + o0)                (reciprocity ratio, neutral prior q = 1)
D_ij   = max(0, ρ*_i − q_ij)                      (deficit)
dx/dt  = − δ_{i,c_ij} x_ij − κ_i (1 − ℓ_i x_ij) D_ij x_ij
dr/dt  = − λ_i r_ij ,   do/dt = − λ_i o_ij
```

### 7.2 Invitations

**Issuing.** An agent with at least one full free slot issues at rate γ·(B_i − U_i).
Each invitation holds c_wait slots. Its target is:

- with probability ε_i, an exploration target: a uniform other agent in the
  baseline, or a uniform existing tie under `variants.exploration: ties`;
- otherwise, a tie drawn ∝ x_ij^β_i · g(q_ij).

An agent with no weighted tie issues nothing on the second branch.

**Response** at rate ω. The invitee j accepts with probability

```
P_acc = σ(a0 + a·x_ji + b·g(q_ji) − c·U_j/B_j)
```

provided j has a free slot and the inviter can still turn its c_wait into a full
slot. A stranger is evaluated with x = 0 and q = 1. If j does not accept, it stays
silent with probability α_j, and otherwise declines.

**Late acceptance** of a silent invitation happens at rate ζ·P_acc, re-evaluated on
the current state. **Cancellation** has hazard 1/(τ_i(1 + h1·x_ij)), so patience
grows with closeness.

**Effects:**

- **Accepted:** both sides occupy 1 slot for d; x ← x + η(1 − x) on both sides;
  o ← o + inv_unit and r ← r + inv_unit·e^{π + ξ} on both sides. An accepted
  exploration invitation to a stranger first creates both ties at x0.
- **Declined:** the inviter's o_ij grows by c_rej·inv_unit.
- **Cancelled after a wait t_w:** r_ij ← max(0, r_ij − ψ(1 − ℓ_i x_ij) t_w).
  The (1 − ℓ x) factor means loyalty protects close ties.

### 7.3 Circles, forgetting, encounters, shocks

Circles use 3 thresholds θ_2 < θ_3 < θ_4; acquaintance is the floor of every
existing tie. Transitions apply only once s_ij ≥ m_i, one step at a time:

- **promotion** when x ≥ θ_{c+1} + w_i/2;
- **demotion** when x < θ_c − w_i/2;
- **forgetting** (tie deleted) when x < x_min.

**Encounters** happen at rate ν_i. With weight μ_rand the partner is a uniform
stranger. With weight μ_tri it is reached by triadic closure: a friend k drawn
∝ x_ik, then k's partner j drawn ∝ x_kj, with j not yet known. An encounter
creates both ties at x0.

**Shocks**, when enabled, are either a tie shock (x ← φx) or a budget shock
(B ← φ_B·B for an exponential duration).

Variants, all off by default:

- surplus boost;
- guilt;
- soft circle capacity;
- dormant ties with revival;
- `exploration: ties`.

### 7.4 Mean-field submodel (analysis and docking)

Replacing each event by its expected rate gives a deterministic ODE system over
all directed pairs. Its state is x, r and o, the pending invitations (unanswered
and silent), and their waiting-age masses, which carry the expected cancellation
drop. Interaction occupancy is a delay of length d, or exponential for the dyad
reduction. Circles enter as hybrid states with the same hysteresis. Encounters,
shocks and dormant ties are not represented. The solver uses fixed-step RK4, batched
over many configurations.

**Docking.** As rates are scaled up, ABM ensemble means converge to the
mean-field. The trajectory error falls from 0.038 to 0.015 to 0.006 as the scale
goes from 1 to 4 to 16 (`tests/test_09_meanfield.py`). With 200 runs per scale (experiment 16), the error drops from 0.047 at s = 1 to 0.004 at s = 4. Beyond that it stays at the sampling floor, while the ABM's own spread falls as s^−1/2. The *embedded-dyad*
analysis applies the mean-field to a focal dyad bridging two cliques of background
partners (`asym/meanfield/embedded.py`). It gives the deterministic thresholds that
the stochastic ABM turns into probabilities (experiment 07).

---

## References

- Almaatouq, A. et al. (2016) PLOS ONE 11(3):e0151588, doi:10.1371/journal.pone.0151588
- Burt, R. S. (2000) Social Networks 22(1):1–28, doi:10.1016/S0378-8733(99)00015-5
- Dunbar, R. I. M., Arnaboldi, V., Conti, M., Passarella, A. (2015) Social Networks 43:39–47, doi:10.1016/j.socnet.2015.04.005
- Grimm, V. et al. (2020) JASSS 23(2):7, doi:10.18564/jasss.4259
- Hill, R. A., Dunbar, R. I. M. (2003) Human Nature 14(1):53–72, doi:10.1007/s12110-003-1016-y
- Hidd, V. V. et al. (2023) Scientific Reports 13:6120, doi:10.1038/s41598-023-32206-2
- Tamarit, I., Cuesta, J. A., Dunbar, R. I. M., Sánchez, A. (2018) PNAS 115(33):8316–8321, doi:10.1073/pnas.1719233115
- Zhou, W.-X., Sornette, D., Hill, R. A., Dunbar, R. I. M. (2005) Proc. R. Soc. B 272:439–444, doi:10.1098/rspb.2004.2970

Full verified reference list: `docs/research/literature-review.md`.
