"""Ticket 05: circles — hysteresis, dwell time, circle-dependent decay, forgetting."""
import numpy as np
import pytest

from asym import simulate

from conftest import make_config

TH = [0.3, 0.55, 0.8]


def test_loaded_ties_start_in_matching_circle():
    agents = [{"id": k} for k in "abcde"]
    ties = [{"i": "a", "j": j, "x": x} for j, x in zip("bcde", (0.2, 0.4, 0.6, 0.9))] + \
           [{"i": "b", "j": "a", "x": 0.2, "circle": 3}]
    res = simulate(make_config(agents=agents, ties=ties, simulation={"horizon": 1.0}), seed=0)
    assert [res.trajectory("a", j)["circle"][0] for j in "bcde"] == [1, 2, 3, 4]
    assert res.trajectory("b", "a")["circle"][0] == 3


def test_decaying_tie_walks_down_then_is_forgotten():
    agents = [{"id": "a", "delta": 0.1, "m": 0.1}, {"id": "b"}]
    raw = make_config(agents=agents, ties=[{"i": "a", "j": "b", "x": 0.95}],
                      simulation={"horizon": 60.0, "sample_interval": 0.5})
    res = simulate(raw, seed=0)
    steps = [(e["type"], e.get("from"), e.get("to")) for e in res.events if e["type"] in ("promote", "demote", "forget")]
    assert steps == [("demote", 4, 3), ("demote", 3, 2), ("demote", 2, 1), ("forget", 1, None)]
    t_forget = res.events_of("forget")[0]["t"]
    tr = res.trajectory("a", "b")
    assert tr["t"].max() < t_forget
    assert np.exp(-0.1 * t_forget) * 0.95 == pytest.approx(0.02, abs=0.01)


@pytest.mark.parametrize("seed", range(6))
def test_transitions_respect_hysteresis_and_dwell(seed):
    rng = np.random.default_rng(seed)
    n = 6
    agents = [{"id": k, "w": float(rng.uniform(0, 0.2)), "m": float(rng.uniform(0, 3)), "B": 3.0} for k in range(n)]
    ties = [{"i": i, "j": j, "x": float(rng.uniform(0.1, 0.9))} for i in range(n) for j in range(n) if i != j]
    raw = make_config(agents=agents, ties=ties, globals_={"gamma": 1.0, "a0": 0.0, "eta": 0.15},
                      simulation={"horizon": 60.0})
    res = simulate(raw, seed=seed)
    w = {a["id"]: a["w"] for a in agents}
    m = {a["id"]: a["m"] for a in agents}
    last = {}
    moves = res.events_of("promote", "demote")
    assert moves
    for e in moves:
        key = (e["i"], e["j"])
        if e["type"] == "promote":
            assert e["x"] >= TH[e["from"] - 1] + w[e["i"]] / 2 - 1e-12
        else:
            assert e["x"] < TH[e["from"] - 2] - w[e["i"]] / 2 + 1e-12
        assert e["t"] - last.get(key, 0.0) >= m[e["i"]] - 1e-9
        last[key] = e["t"]


def _n_transitions(w):
    total = 0
    for seed in range(8):
        agents = [{"id": "a", "w": w, "m": 0.0, "delta": 0.3}, {"id": "b", "w": w, "m": 0.0, "delta": 0.3}]
        ties = [{"i": "a", "j": "b", "x": 0.3}, {"i": "b", "j": "a", "x": 0.3}]
        raw = make_config(agents=agents, ties=ties, globals_={"gamma": 0.6, "a0": 2.0, "eta": 0.1},
                          simulation={"horizon": 80.0})
        total += len(simulate(raw, seed=seed).events_of("promote", "demote"))
    return total


def test_wider_hysteresis_means_fewer_transitions():
    narrow, wide = _n_transitions(0.0), _n_transitions(0.15)
    assert narrow > 20
    assert wide < 0.6 * narrow


def test_inner_ties_decay_slower():
    agents = [{"id": "a", "delta": [0.2, 0.1, 0.05, 0.01], "m": 1e9}, {"id": "b"}, {"id": "c"}]
    ties = [{"i": "a", "j": "b", "x": 0.9}, {"i": "a", "j": "c", "x": 0.29}]
    res = simulate(make_config(agents=agents, ties=ties, simulation={"horizon": 5.0}), seed=0)
    inner, outer = res.trajectory("a", "b"), res.trajectory("a", "c")
    np.testing.assert_allclose(inner["x"], 0.9 * np.exp(-0.01 * inner["t"]), rtol=1e-6)
    np.testing.assert_allclose(outer["x"], 0.29 * np.exp(-0.2 * outer["t"]), rtol=1e-6)
