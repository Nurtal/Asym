"""Mean-field scaling law (docs/theory/maintenance-scaling.md, Proposition 1).

Without deficit erosion, the stationary state depends on η and δ only through η/δ:
the η × 2 and δ / 2 routes reach the same closeness. Budget enters as a scale, so
B × 2 also agrees once the reciprocity prior o0 is negligible.
"""
import itertools
import warnings

import numpy as np

from asym.meanfield.solver import solve_meanfield
from asym.model.archetypes import archetype_centre, archetype_table


def _clique(mB=1.0, meta=1.0, mdelta=1.0, o0=0.5, kappa=0.0, horizon=1500.0):
    table = archetype_table()
    agents = []
    for k, name in enumerate(["butterfly", "loyal_few", "transactional"]):
        a = archetype_centre(name, table)
        a.update(id=f"a{k}", nu=0.0, kappa=kappa, B=a["B"] * mB, delta=[d * mdelta for d in a["delta"]])
        agents.append(a)
    rng = np.random.default_rng(0)
    ties = [{"i": f"a{i}", "j": f"a{j}", "x": float(rng.uniform(0.3, 0.7)), "r": 1.0, "o": 1.0}
            for i, j in itertools.permutations(range(3), 2)]
    return {"agents": agents, "globals": {"eta": 0.1 * meta, "o0": o0}, "init": {"mode": "file", "ties": ties},
            "variants": {"exploration": "ties"},
            "simulation": {"horizon": horizon, "burn_in": 0.0, "sample_interval": horizon, "mf_step": 0.1}}


def _final(cfgs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tr = solve_meanfield(cfgs, occupancy="exponential")
    off = ~np.eye(3, dtype=bool)
    return [tr.x[-1, k][off] for k in range(len(cfgs))]


def test_eta_and_delta_routes_coincide_without_deficit():
    x_eta, x_delta, x_base = _final([_clique(meta=2.0), _clique(mdelta=0.5, horizon=3000.0), _clique()])
    assert np.allclose(x_eta, x_delta, atol=1e-6)
    assert np.all(x_eta > x_base)  # doubling Q raises every tie


def test_budget_route_coincides_when_prior_is_negligible():
    x_eta, x_B = _final([_clique(meta=2.0, o0=1e-3), _clique(mB=2.0, o0=1e-3)])
    assert np.allclose(x_eta, x_B, atol=1e-3)


def test_deficit_erosion_breaks_the_delta_route():
    x_eta, x_delta = _final([_clique(meta=2.0, kappa=1.0), _clique(mdelta=0.5, kappa=1.0, horizon=3000.0)])
    assert np.max(np.abs(x_eta - x_delta)) > 1e-3  # K = κ/δ doubles on the δ route
