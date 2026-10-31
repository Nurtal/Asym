# Asym

A mathematical and computational framework for modelling **asymmetric interpersonal
relationship dynamics** with heterogeneous multi-agent systems. Agents hold directed
ties (closeness, perceived reciprocity, own investment) and sort them into social
circles: acquaintance, friend, close friend, inner circle. They spend a finite budget
on invitations that the other side may accept, decline or ignore.

The model has two levels of description:

- **`simulate(config, seed)`**: an exact stochastic simulation (a piecewise-deterministic
  Markov process, PDMP) of the agent population
- **`solve_meanfield(config)`**: the deterministic mean-field limit, used for analysis.
  Ensemble averages of `simulate` converge to it.

Domain vocabulary: [`CONTEXT.md`](CONTEXT.md). Equations: [`docs/model-spec.md`](docs/model-spec.md).
Decisions: [`docs/adr/`](docs/adr/).

## Install

```bash
python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -m "not slow"     # fast suite; drop the marker for the statistical tests
```

## Quick start

```python
from asym import simulate, solve_meanfield
from asym import metrics

config = {
    "population": {"composition": {"butterfly": 10, "loyal_few": 10, "transactional": 10, "avoidant": 10}},
    "init": {"mode": "empty"},
    "simulation": {"horizon": 200.0, "burn_in": 100.0, "sample_interval": 10.0},
}
res = simulate(config, seed=0)
print(metrics.layering(res)["mean_layer_sizes"])   # inner circle → all ties
print(metrics.network_metrics(res))
res.save("run.npz")
```

Dyad analysis (research question 1):

```python
from asym.meanfield.dyad import DyadAnalysis, sweep, archetype_pairs

da = DyadAnalysis(two_agent_config)
for fp in da.fixed_points():
    print(fp.x, fp.stability, fp.kind)
grid = sweep(two_agent_config, {"globals.a0": [-6, -3, 0], "agents.*.kappa": [0.0, 0.5, 1.0]})
table = archetype_pairs()
```

## Experiments

Every experiment is a versioned YAML file under `experiments/`, run as a seed ensemble:

```bash
python -m asym.experiments run experiments/01_layering_empty_vs_random.yaml --workers 6
python -m asym.experiments analyse results/layering_empty_vs_random
```

Each run directory holds one `.npz` per (condition, seed), plus a `manifest.json`
(resolved configs, seeds, git commit, result hashes) and an `analysis.json`.

## Benchmark

```bash
python benchmarks/bench_engine.py --n 1000 --horizon 50 [--profile]
```
