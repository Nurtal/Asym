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
