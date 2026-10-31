# ADR-0004: Interactions are invitations with a full lifecycle

**Status:** Accepted

## Context

Asymmetry needs a micro-mechanism through which the two sides of a relationship can
behave differently. Possible readings of an interaction:

- unilateral: only the initiator pays;
- joint: always symmetric;
- an invitation that the other side may accept, refuse or ignore.

## Decision

An interaction is an **invitation** from i to j:

- j may **accept** (probability depends on j's own closeness and reciprocity
  perception and on j's load), **decline** explicitly, or stay **silent**. The choice
  between declining and silence depends on j's conflict avoidance `α_j`.
- A silent invitation stays **pending** and costs i `c_wait` (≈ 0.5) of an interaction
  slot. j may still **accept late**.
- i **cancels** with hazard `1/T_ij`, where `T_ij = τ_i · h(x_ij)`: more patience for
  closer ties.
- On cancellation, i's perceived reciprocity drops in proportion to the time waited,
  damped by loyalty: factor `(1 − ℓ_i · x_ij)`. The same damping applies to the
  reciprocity-deficit erosion.
- Committed budget (interactions + pending invitations) may never exceed `B_i`.

## Consequences

- Unreciprocated bids generate divergent trajectories, and loyal agents keep
  investing in ties that the other side lets die.
- An emergent **isolation trap** becomes possible: budget locked in waiting on silent
  contacts.
- Cancellation hazards fit the Poisson event framework, so no timers are needed.
