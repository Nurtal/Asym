"""Ticket 08: exogenous tie and budget shocks."""
import numpy as np
import pytest

from asym import simulate

from conftest import make_config


def _cfg(rate, tie_prob=0.5, horizon=200.0, gamma=0.0, n=5, sample_interval=1.0):
    agents = [{"id": k, "delta": 0.0, "B": 4.0} for k in range(n)]
    ties = [{"i": i, "j": j, "x": 0.6} for i in range(n) for j in range(n) if i != j]
    return make_config(agents=agents, ties=ties,
                       globals_={"shock_rate": rate, "shock_tie_prob": tie_prob, "gamma": gamma, "a0": 1.0},
                       simulation={"horizon": horizon, "sample_interval": sample_interval})


def test_no_shocks_at_zero_rate():
    res = simulate(_cfg(0.0), seed=0)
    assert not res.events_of("shock_tie", "shock_budget")


def test_shock_count_matches_rate():
    res = simulate(_cfg(0.5, tie_prob=0.0, horizon=2000.0, sample_interval=100.0), seed=0)
    n = len(res.events_of("shock_tie", "shock_budget"))
    assert n == pytest.approx(1000, abs=4 * np.sqrt(1000))


def test_tie_shock_scales_closeness():
    res = simulate(_cfg(0.2, tie_prob=1.0, horizon=100.0), seed=1)
    shocks = res.events_of("shock_tie")
    assert len(shocks) > 5
    for e in shocks:
        assert 0.3 <= e["phi"] <= 0.8
        assert e["x_after"] == pytest.approx(e["phi"] * e["x_before"])
    first = shocks[0]
    tr = res.trajectory(first["i"], first["j"])
    after = tr["t"] >= first["t"]
    assert tr["x"][after][0] == pytest.approx(first["x_after"])


def test_budget_shock_caps_new_commitments_and_restores():
    res = simulate(_cfg(0.1, tie_prob=0.0, horizon=300.0, gamma=1.0, sample_interval=0.5), seed=2)
    shocks, restores = res.events_of("shock_budget"), res.events_of("budget_restore")
    assert len(shocks) > 10 and restores
    for e in res.events_of("invite", "accept", "late_accept"):
        assert e["U_i"] <= e["B_i"] + 1e-9
        if "U_j" in e:
            assert e["U_j"] <= e["B_j"] + 1e-9
    # capacity is reduced during the shock and restored once every shock ended
    for e in shocks:
        k = np.searchsorted(res.times, e["t"])
        if k < len(res.times) and e["t"] + e["duration"] > res.times[k]:
            assert res.capacity[k, res.index(e["i"])] < 4.0
    assert np.all(res.capacity <= 4.0 + 1e-12)
    last_restore = {}
    for e in restores:
        last_restore[e["i"]] = e
    for aid, e in last_restore.items():
        if e["active"] == 0:
            k = np.searchsorted(res.times, e["t"])
            if k < len(res.times):
                assert res.capacity[k, res.index(aid)] == pytest.approx(4.0)
