"""Ticket 06: encounters (random / triadic closure) and init.mode = empty."""
import networkx as nx
import numpy as np
import pytest

from asym import simulate

from conftest import make_config


def _population(n=30, nu=0.2, mu_rand=1.0, mu_tri=1.0, init=None, horizon=60.0, ties=None, epsilon=0.05):
    agents = [{"id": k, "nu": nu, "B": 3.0, "epsilon": epsilon} for k in range(n)]
    return make_config(agents=agents, ties=ties, init=init or {"mode": "empty"},
                       globals_={"gamma": 0.5, "a0": 1.0, "mu_rand": mu_rand, "mu_tri": mu_tri},
                       simulation={"horizon": horizon, "sample_interval": 5.0})


def test_empty_init_then_ties_appear():
    res = simulate(_population(), seed=0)
    assert res.snapshot(0)["i"].size == 0
    assert res.snapshot(len(res.times) - 1)["i"].size > 0


def test_encounters_are_logged_with_kind():
    res = simulate(_population(), seed=1)
    enc = res.events_of("encounter")
    assert enc
    assert {e["kind"] for e in enc} == {"random", "triadic"}
    assert all("via" in e for e in enc if e["kind"] == "triadic")


def test_triadic_only_never_starts_from_empty():
    # no exploration either: nobody can ever meet anybody
    res = simulate(_population(mu_rand=0.0, epsilon=0.0), seed=0)
    assert not res.events_of("encounter")
    assert res.snapshot(len(res.times) - 1)["i"].size == 0


def test_triadic_only_closes_triangles():
    ties = [{"i": u, "j": v, "x": 0.6} for u, v in [(0, 1), (1, 0), (1, 2), (2, 1)]]
    raw = _population(n=3, mu_rand=0.0, init={"mode": "file", "ties": ties}, horizon=30.0)
    raw["globals"]["gamma"] = 0.0
    res = simulate(raw, seed=0)
    enc = res.events_of("encounter")
    assert enc
    assert all(e["kind"] == "triadic" and e["via"] == 1 for e in enc)
    assert {frozenset((e["i"], e["j"])) for e in enc} == {frozenset((0, 2))}


def _clustering(mu_tri, seeds=range(3), n=60):
    # sparse regime: acquaintances are forgotten unless maintained
    vals = []
    for seed in seeds:
        res = simulate(_population(n=n, nu=0.08, mu_tri=mu_tri, horizon=100.0, epsilon=0.0), seed=seed)
        snap = res.snapshot(len(res.times) - 1)
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(zip(snap["i"].tolist(), snap["j"].tolist()))
        vals.append(nx.average_clustering(G))
    return float(np.mean(vals))


@pytest.mark.slow
def test_triadic_closure_raises_clustering():
    assert _clustering(8.0) > _clustering(0.0) + 0.15


@pytest.mark.parametrize("seed", range(3))
def test_no_duplicate_or_self_ties(seed):
    res = simulate(_population(), seed=seed)
    for k in range(len(res.times)):
        snap = res.snapshot(k)
        pairs = list(zip(snap["i"].tolist(), snap["j"].tolist()))
        assert len(pairs) == len(set(pairs))
        assert all(i != j for i, j in pairs)
