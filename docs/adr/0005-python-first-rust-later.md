# ADR-0005: Python first, Rust only for profiled hot paths

**Status:** Accepted

## Decision

- Implementation in Python: NumPy/SciPy, SymPy for analysis, numba for hot loops,
  networkx for network metrics.
- Layout: `asym/model` (θ, archetypes, pure functional forms), `asym/meanfield`,
  `asym/abm` (PDMP event engine), `asym/metrics`, `experiments/` (YAML config + seed
  per experiment).
- The ABM engine exposes a stable Python interface. It is ported to Rust
  (PyO3/maturin) **only once profiling shows** it is the bottleneck, and the port
  must not require changes to experiments or metrics.
- Development is test-first (TDD) for model components.

## Alternatives rejected

Julia (DifferentialEquations.jl / JumpProcesses.jl) is a good fit technically, but
the user prefers Python.
