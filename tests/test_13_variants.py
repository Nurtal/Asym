"""Ticket 13: model variants as config switches."""
import numpy as np
import pytest

from asym import simulate, solve_meanfield

from conftest import make_config

OFF = {"surplus_boost": 0.0, "guilt": 0.0, "circle_capacity": None, "capacity_cost": 0.0, "dormant": False,
       "revival_bonus": 0.0}


def _interacting(variants=None, **sim):
    agents = [{"id": k, "B": 3.0, "nu": 0.05, "epsilon": 0.1} for k in range(8)]
    ties = [{"i": i, "j": (i + 1) % 8, "x": 0.5} for i in range(8)] + [{"i": (i + 1) % 8, "j": i, "x": 0.4} for i in range(8)]
    return make_config(agents=agents, ties=ties, variants=variants,
                       globals_={"gamma": 0.6, "a0": 0.5, "shock_rate": 0.05},
                       simulation={"horizon": 60.0, **sim})


def test_all_variants_off_equals_baseline():
    assert simulate(_interacting(OFF), seed=3).equals(simulate(_interacting(), seed=3))


def test_surplus_boost_strengthens_overreciprocated_ties():
    agents = [{"id": "a", "delta": 0.05, "lam": 0.0, "rho_star": 0.5}, {"id": "b"}]
    ties = [{"i": "a", "j": "b", "x": 0.5, "r": 10.0, "o": 1.0}]  # q ≈ 7 > ρ*
    base = simulate(make_config(agents=agents, ties=ties), seed=0).trajectory("a", "b")["x"]
    boosted = simulate(make_config(agents=agents, ties=ties, variants={"surplus_boost": 0.1}), seed=0).trajectory("a", "b")["x"]
    assert np.all(boosted[1:] > base[1:])
    mf = solve_meanfield(make_config(agents=agents, ties=ties, variants={"surplus_boost": 0.1})).trajectory("a", "b")["x"]
    np.testing.assert_allclose(mf, boosted, rtol=1e-3)


def test_guilt_lowers_the_invitee_closeness_on_cancellation():
    agents = [{"id": "a", "tau": 0.5, "delta": 0.0}, {"id": "b", "B": 0.5, "alpha": 1.0, "delta": 0.0}]
    ties = [{"i": "a", "j": "b", "x": 0.5}, {"i": "b", "j": "a", "x": 0.8}]
    glob = {"gamma": 1.0, "a0": -50.0}
    base = simulate(make_config(agents=agents, ties=ties, globals_=glob), seed=0)
    guilty = simulate(make_config(agents=agents, ties=ties, globals_=glob, variants={"guilt": 0.05}), seed=0)
    assert base.trajectory("b", "a")["x"][-1] == pytest.approx(0.8)
    events = guilty.events_of("guilt")
    assert events and all(e["x_after"] == pytest.approx(0.95 * e["x_before"]) for e in events)
    xb = guilty.trajectory("b", "a")["x"]
    assert len(xb) == 0 or xb[-1] < 0.8


def test_soft_capacity_limits_crowded_circles():
    def friends(variants):
        agents = [{"id": "hub", "B": 20.0, "beta": 0.0, "epsilon": 0.0}] + [{"id": k, "B": 3.0} for k in range(12)]
        ties = [{"i": "hub", "j": k, "x": 0.35} for k in range(12)] + [{"i": k, "j": "hub", "x": 0.35} for k in range(12)]
        raw = make_config(agents=agents, ties=ties, variants=variants, globals_={"gamma": 0.5, "a0": 2.0},
                          simulation={"horizon": 80.0, "burn_in": 40.0, "sample_interval": 2.0})
        res = simulate(raw, seed=1)
        x = res.ties["x"][res.ties["i"] == 0]
        return x.mean()
    free = friends(None)
    capped = friends({"circle_capacity": [50, 2, 2, 2], "capacity_cost": 5.0})
    assert capped < free - 0.05


def test_dormant_ties_can_be_revived_with_bonus():
    agents = [{"id": "a", "delta": 0.3, "nu": 0.5, "epsilon": 0.0}, {"id": "b", "delta": 0.3}]
    ties = [{"i": "a", "j": "b", "x": 0.3}, {"i": "b", "j": "a", "x": 0.3}]
    raw = make_config(agents=agents, ties=ties, variants={"dormant": True, "revival_bonus": 0.2},
                      globals_={"gamma": 0.0, "mu_tri": 0.0}, simulation={"horizon": 60.0})
    res = simulate(raw, seed=0)
    assert any(e.get("dormant") for e in res.events_of("forget"))
    revivals = res.events_of("revive")
    assert revivals and all(e["x"] == pytest.approx(0.3) for e in revivals)
    # without the variant, the same meetings start from scratch
    raw["variants"] = {}
    assert not simulate(raw, seed=0).events_of("revive")


def test_variants_combine():
    v = {"surplus_boost": 0.05, "guilt": 0.1, "circle_capacity": [20, 5, 3, 2], "capacity_cost": 1.0,
         "dormant": True, "revival_bonus": 0.1}
    res = simulate(_interacting(v), seed=0)
    assert res.events
    assert not res.equals(simulate(_interacting(), seed=0))
