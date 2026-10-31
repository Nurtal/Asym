# ADR-0001: Two-level formalism — PDMP simulation with a mean-field ODE limit

**Status:** Accepted

## Context

The project combines ODEs, discrete state transitions and agent-based modelling. We
need analytical tractability (fixed points, bifurcations, thresholds), and we also
need stochasticity: a deterministic model can never show noise pushing a
relationship across a threshold.

## Decision

- Simulate populations as a **piecewise-deterministic Markov process**: discrete
  stochastic events (invitations, responses, cancellations, encounters, shocks),
  with deterministic ODE flow (decay, memory) between events.
- Analyse the **mean-field ODE** obtained by replacing event rates with their
  expectations.
- Enforce consistency with a convergence test: ABM ensemble averages must converge to
  the mean-field model in the high-rate limit.

## Alternatives rejected

- Pure deterministic hybrid ODE: cannot capture noise-induced threshold crossings.
- Discrete-time map: simpler, but loses the ODE framing needed for analysis.

## Consequences

Two code paths (`asym/meanfield`, `asym/abm`) share the same functional forms from
`asym/model`, so the forms must be pure functions.
