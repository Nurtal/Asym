# ADR-0006: Arbitrary model time unit

**Status:** Accepted

## Decision

All rates and durations use an arbitrary model time unit. They are mapped to real
time (days or weeks) later, once the dynamics are understood, by calibrating against
stylised facts such as the half-life of an unmaintained friendship.

## Consequences

- Parameters should be reported in dimensionless or ratio form where possible.
- Configs carry no real-time units.
- Simulation horizon and burn-in are expressed in model units.

## Update: mapping attempted, unit kept arbitrary

Experiment 17 (`docs/experiments/17-time-mapping.md`) tried the mapping against contact
frequency, turnover and hours to friendship. The anchors disagree by a factor of 70 at the
calibrated point, and finer interactions improve turnover only by worsening time to
friendship. The unit therefore stays arbitrary, and results are not quoted in real time.
Experiment 18 (`docs/experiments/18-k3-sensitivity.md`) finds the same trade-off after
recalibrating at k = 3.
