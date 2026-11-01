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
ODD description: [`docs/odd.md`](docs/odd.md). Decisions: [`docs/adr/`](docs/adr/).
Literature: [`docs/research/literature-review.md`](docs/research/literature-review.md).
Scaling theory (why layers collapse on B/δ): [`docs/theory/maintenance-scaling.md`](docs/theory/maintenance-scaling.md).

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

Experiment reports (`docs/experiments/`):

| # | Topic |
|---|---|
| 01, 01b | Layering from empty vs random start; long-horizon rerun |
| 02 | First calibration; layer scaling with N (baseline exploration) |
| 03 | Isolated dyads by archetype pair (mean-field) |
| 04 | Embedded dyads: focal dyad bridging two cliques (mean-field) |
| 05 | Encounter-only tie formation makes layering independent of N |
| 06 | Dunbar-calibrated thresholds; scaling check |
| 07 | Noise-induced switching of embedded dyads (stochastic ABM) |
| 08, 09 | Tamarit's inverse regime; robustness across population draws |
| 10 | Morris sensitivity screening |
| 11 | Collapse of layer sizes on the maintenance ratio B/δ (and η) |
| 12 | Population-level asymmetry and its mechanisms (counterfactuals) |
| 13 | Checks of the scaling theory (`docs/theory/maintenance-scaling.md`) |
| 14 | Pairing race in the full population: gap condition, scarcity regime |

Scripts without the YAML harness: `experiments/03_…py`, `04_…py`, `07_…py`, `09_aggregate.py`,
`10_morris.py`, `11_…py`, `13_…py`, `14_…py`, and the calibration tool `experiments/calibrate_layering.py`.

## Benchmark

```bash
python benchmarks/bench_engine.py --n 1000 --horizon 50 [--profile]
```
