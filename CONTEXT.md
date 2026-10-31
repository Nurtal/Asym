# Asym — Domain Context

Asym is a mathematical and computational framework for modelling the dynamics of
human interpersonal relationships with heterogeneous multi-agent systems. Its
primary deliverable is a **research paper / thesis**; the code supports the paper
and is kept clean enough to be reused later.

The model is **theoretical**: it is not fitted to a dataset, but validated against
**stylised facts** (Dunbar-like layering, decay of unmaintained ties, reciprocity
distributions, churn rates).

See `docs/model-spec.md` for equations and `docs/adr/` for structural decisions.

## Glossary

**Agent** — An individual, characterised by a behavioural parameter vector θ_i.
Agents evaluate their relationships independently of each other.

**Archetype** — A named behavioural profile (e.g. *butterfly*, *loyal-few*,
*transactional*, *avoidant*). Each archetype is a cluster centre in parameter space;
agents are sampled around it with noise.

**Tie** — The *directed* relationship i→j, as held by agent i. The tie j→i is a
distinct object. A tie exists from the first encounter until it is forgotten.

**Dyad** — The unordered pair {i, j}, i.e. the two ties i→j and j→i together.

**Closeness (x_ij)** — i's continuous valuation of the tie i→j, in [0, 1].

**Perceived reciprocity (r_ij)** — i's decaying memory of how much j invests in the
relationship, as *perceived* by i (subject to i's perception bias).

**Own investment (o_ij)** — i's decaying memory of how much i has invested in j.
Used as the denominator of the reciprocity ratio.

**Reciprocity ratio (q_ij)** — r_ij / o_ij: perceived return on own investment.

**Reciprocity expectation (ρ*_i)** — The reciprocity ratio agent i expects. Falling
below it is a **reciprocity deficit**, which erodes closeness.

**Asymmetry** — Any difference between i→j and j→i (closeness, circle, investment).
Asymmetry is the central object of study, not noise.

**Circle** — A discrete level a tie occupies, from outer to inner:
*acquaintance*, *friend*, *close friend*, *inner circle*. Circles are genuine hybrid
states: they change the continuous dynamics (decay rate, allocation priority).

**Promotion / Demotion** — Moving a tie one circle inward / outward when closeness
crosses a threshold, subject to hysteresis and minimum dwell time.

**Hysteresis width** — Per-agent gap between promotion and demotion thresholds.
Together with **dwell time** it defines an agent's **relationship stability**.

**Forgotten tie** — A tie whose closeness has fallen below x_min. It is deleted.

**Budget (B_i)** — Agent i's finite capacity for social engagement, measured in
interaction slots. Varies across agents. Accepted interactions and pending
invitations consume it.

**Committed budget** — The part of B_i currently in use. It may never exceed B_i.

**Concentration (β_i)** — How strongly i concentrates budget on its closest ties.

**Exploration (ε_i)** — The fraction of budget i spends on uniformly random targets
(strangers or dormant-ish ties).

**Invitation** — An interaction attempt from an inviter i to an invitee j. Lifecycle:
*pending* → *accepted* | *declined* | *cancelled*. A silent invitee leaves it pending.

**Silence** — The invitee does not respond. The invitation stays pending and keeps
costing the inviter `c_wait` (≈ 0.5) of an interaction's slot.

**Late acceptance** — A silent invitee accepting a still-pending invitation later.

**Patience (τ_i)** — i's base willingness to wait. The effective patience for a
given invitation grows with closeness: T_ij = τ_i · h(x_ij).

**Cancellation** — The inviter withdrawing a pending invitation (hazard 1/T_ij).
It produces a perceived-reciprocity drop proportional to the time waited.

**Loyalty (ℓ_i)** — Protection that close ties get against negative signals.
It dampens the reciprocity-deficit erosion and the cancellation drop, more strongly
the closer the tie: effective sensitivity = κ_i · (1 − ℓ_i · x_ij).

**Conflict avoidance (α_j)** — The probability that an invitee who does not accept
stays silent rather than declining explicitly.

**Perception bias (π_i)** — Systematic over/under-perception of what others invest.

**Openness (ν_i)** — Rate at which i forms new ties through encounters.

**Encounter** — The first meeting that creates a tie. Either *random* or by
*triadic closure* (meeting a friend of a friend).

**Shock** — Exogenous random life event that suddenly changes a tie's closeness or
an agent's budget. Used as an experimental probe of stability.

**Isolation trap** — An emergent state in which an agent's budget is locked up in
pending invitations to silent contacts, so it cannot invest in new ties.

**Mean-field model** — The deterministic ODE obtained by replacing event rates with
their expectations. It is used for analysis (fixed points, bifurcations).

**PDMP / ABM** — The stochastic piecewise-deterministic Markov process that is
simulated as an agent-based model. The mean-field model is its large-rate limit.

**Initial condition mode** — How a simulation starts: `empty` (nobody knows anyone),
`random` (random initial network), or `file` (a specific situation loaded from
JSON/CSV).

**Time unit** — Arbitrary model time unit. Mapping to days/weeks comes later.
