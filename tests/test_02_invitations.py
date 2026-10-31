"""Ticket 02: accepted invitations and the budget (seam: simulate)."""
from collections import Counter

import numpy as np
import pytest

from asym import simulate

from conftest import make_config

ALWAYS_ACCEPT = {"gamma": 0.5, "a0": 50.0}


def test_interacting_dyad_stays_alive():
    decaying = simulate(make_config(simulation={"horizon": 100.0}), seed=0)
    alive = simulate(make_config(simulation={"horizon": 100.0}, globals_=ALWAYS_ACCEPT), seed=0)
    x_dead = decaying.trajectory("a", "b")["x"][-1]
    x_alive = alive.trajectory("a", "b")["x"][-40:]
    assert x_dead < 0.05
    assert x_alive.mean() > 0.3


@pytest.mark.parametrize("seed", range(15))
def test_committed_budget_never_exceeds_capacity(seed):
    rng = np.random.default_rng(seed)
    n = 6
    agents = [{"id": k, "B": float(rng.uniform(1, 4)), "epsilon": 0.3} for k in range(n)]
    ties = [{"i": i, "j": j, "x": float(rng.uniform(0.1, 0.9))} for i in range(n) for j in range(n) if i != j and rng.random() < 0.5]
    raw = make_config(
        agents=agents, ties=ties,
        simulation={"horizon": 30.0, "sample_interval": 0.05},
        globals_={"gamma": 2.0, "a0": float(rng.uniform(-2, 4)), "d": float(rng.uniform(0.5, 3))},
    )
    res = simulate(raw, seed=seed)
    assert np.all(res.budget <= res.capacity + 1e-9)
    assert np.all(res.budget >= -1e-9)
    assert len(res.events_of("accept")) > 0


def test_fully_committed_agent_issues_no_invitation():
    raw = make_config(agents=[{"id": "a", "B": 1.5}, {"id": "b", "B": 1.5}],
                      globals_={**ALWAYS_ACCEPT, "d": 1000.0}, simulation={"horizon": 50.0})
    res = simulate(raw, seed=3)
    accepts = res.events_of("accept")
    assert len(accepts) == 1
    t_acc = accepts[0]["t"]
    assert not [e for e in res.events_of("invite") if e["t"] > t_acc]


def _target_shares(beta, seed=0):
    agents = [{"id": "a", "beta": beta, "epsilon": 0.0, "delta": 0.0, "B": 3.0}] + \
             [{"id": k, "B": 0.5, "delta": 0.0} for k in ("b", "c", "d")]  # B < 1: others never invite
    ties = [{"i": "a", "j": "b", "x": 0.8}, {"i": "a", "j": "c", "x": 0.4}, {"i": "a", "j": "d", "x": 0.2}]
    raw = make_config(agents=agents, ties=ties, globals_={"gamma": 1.0, "eta": 0.0, "a0": -50.0, "inv_unit": 0.0},
                      simulation={"horizon": 400.0})
    res = simulate(raw, seed=seed)
    counts = Counter(e["j"] for e in res.events_of("invite") if e["i"] == "a")
    total = sum(counts.values())
    return {k: counts[k] / total for k in ("b", "c", "d")}, total


def test_beta_concentrates_invitations_on_closest_ties():
    flat, n0 = _target_shares(0.0)
    peaked, n4 = _target_shares(4.0)
    assert n0 > 300 and n4 > 300
    for k in "bcd":
        assert abs(flat[k] - 1 / 3) < 0.07
    w = np.array([0.8, 0.4, 0.2]) ** 4
    expected = w / w.sum()
    np.testing.assert_allclose([peaked[k] for k in "bcd"], expected, atol=0.06)
    assert peaked["b"] > flat["b"] + 0.3


def test_exploration_reaches_strangers():
    agents = [{"id": "a", "epsilon": 0.5}] + [{"id": k, "B": 0.5} for k in ("b", "c", "d")]
    raw = make_config(agents=agents, ties=[{"i": "a", "j": "b", "x": 0.8}],
                      globals_={"gamma": 1.0, "a0": -50.0}, simulation={"horizon": 100.0})
    res = simulate(raw, seed=1)
    targets = Counter(e["j"] for e in res.events_of("invite"))
    assert targets["c"] > 0 and targets["d"] > 0


def test_invitation_events_are_logged():
    res = simulate(make_config(globals_=ALWAYS_ACCEPT, simulation={"horizon": 20.0}), seed=0)
    types = {e["type"] for e in res.events}
    assert {"invite", "accept", "interaction_end"} <= types
    inv = res.events_of("invite")[0]
    assert {"t", "i", "j", "inv"} <= set(inv)


def test_accepted_interaction_updates_both_sides():
    raw = make_config(globals_={**ALWAYS_ACCEPT, "eta": 0.2, "psi": 0.0}, simulation={"horizon": 3.0, "sample_interval": 0.01},
                      agents=[{"id": "a", "delta": 0.0, "lam": 0.0}, {"id": "b", "delta": 0.0, "lam": 0.0}])
    res = simulate(raw, seed=0)
    ab, ba = res.trajectory("a", "b"), res.trajectory("b", "a")
    n_acc = len(res.events_of("accept"))
    assert n_acc >= 1
    assert ab["x"][-1] == pytest.approx(1 - 0.4 * 0.8**n_acc)
    assert ba["x"][-1] == pytest.approx(1 - 0.6 * 0.8**n_acc)
    assert ab["o"][-1] == pytest.approx(2.0 + n_acc)
    assert ba["r"][-1] == pytest.approx(1.0 + n_acc)
