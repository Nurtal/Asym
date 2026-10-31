# ADR-0003: Circle capacity emerges from a finite, heterogeneous budget

**Status:** Accepted

## Context

Real relationships compete for finite time. Without such a coupling, ties evolve
independently and the population reduces to independent dyads, with no
displacement and no layered structure.

## Decision

- Each agent has its own finite budget `B_i`, which varies by profile.
- Allocation is proportional to `x^β_i · g(reciprocity)`, plus a small exploration
  fraction `ε_i` sent to random targets.
- **No circle sizes are imposed** in the baseline. Whether Dunbar-like layering
  (~5/15/50/150) emerges from budget scarcity + β + hysteresis is a headline research
  question.
- Explicit per-circle capacity costs are a variant, used for comparison.

## Consequences

Budget accounting is a hard invariant (committed ≤ B_i) and must be tested. Pending
invitations also consume budget (see ADR-0004).
