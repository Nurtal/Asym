# ADR-0002: Social circles are discrete hybrid states with hysteresis

**Status:** Accepted

## Context

Circles (acquaintance, friend, close friend, inner circle) could be mere labels on
continuous closeness. In that case the "discrete transitions" part of the project
would be cosmetic, and there would be no genuine threshold effects.

## Decision

- Circles are discrete states of each directed tie.
- Promotion and demotion thresholds are separated by a per-agent **hysteresis
  width**, and transitions require a per-agent **minimum dwell time**. Together these
  define relationship stability.
- The circle feeds back into the continuous dynamics (circle-dependent decay rate).
- Threshold *positions* are global, and only the widths vary per agent, to limit the
  parameter count.
- A tie below `x_min` is forgotten (deleted). A dormant state is a later variant.

## Consequences

The mean-field system is piecewise-smooth with memory (hybrid). Deleting ties keeps
the graph sparse, which matters for N ≈ 1000 and a later Rust engine.
