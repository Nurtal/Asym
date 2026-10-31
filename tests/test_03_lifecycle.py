"""Ticket 03: decline, silence, late acceptance and cancellation (seam: simulate)."""
import numpy as np
import pytest

from asym import simulate

from conftest import make_config

NEVER = {"gamma": 1.0, "a0": -50.0}


def _dyad(alpha, glob=None, a=None, b=None, horizon=200.0, ties=None, sample_interval=1.0):
    agents = [{"id": "a", **(a or {})}, {"id": "b", "alpha": alpha, "B": 0.5, **(b or {})}]
    return make_config(agents=agents, ties=ties, globals_={**NEVER, **(glob or {})},
                       simulation={"horizon": horizon, "sample_interval": sample_interval})


@pytest.mark.parametrize("alpha, kind", [(0.0, "silence"), (1.0, "decline")])
def test_extreme_alpha_gives_single_outcome(alpha, kind):
    res = simulate(_dyad(alpha), seed=0)
    assert len(res.events_of("decline", "silence")) > 50
    assert not res.events_of(kind)


def test_silence_fraction_converges_to_alpha():
    res = simulate(_dyad(0.3, a={"delta": 0.0}, horizon=1500.0), seed=1)
    n_sil, n_dec = len(res.events_of("silence")), len(res.events_of("decline"))
    assert n_sil + n_dec > 1000
    assert n_sil / (n_sil + n_dec) == pytest.approx(0.3, abs=0.04)


def test_pending_invitations_hold_c_wait():
    raw = _dyad(0.6, glob={"c_wait": 0.25}, horizon=60.0, sample_interval=0.1)
    res = simulate(raw, seed=2)
    a = res.index("a")
    opened = {}
    for e in res.events:
        if e["type"] == "invite" and e["i"] == "a":
            opened[e["inv"]] = e["t"]
    closed = {e["inv"]: e["t"] for e in res.events if e["type"] in ("decline", "cancel", "accept", "late_accept") and e["i"] == "a"}
    for k, t in enumerate(res.times):
        n_open = sum(1 for inv, t0 in opened.items() if t0 <= t and closed.get(inv, np.inf) > t)
        assert res.pending_budget[k, a] == pytest.approx(0.25 * n_open)
    assert res.pending_budget[:, a].max() > 0


def test_late_acceptances_occur():
    res = simulate(_dyad(1.0, glob={"a0": -1.0, "zeta": 0.5}, b={"B": 3.0}), seed=0)
    assert res.events_of("late_accept")


def _cancel_drops(ell, x, seed=0):
    raw = _dyad(1.0, glob={"psi": 0.05, "h1": 0.0, "zeta": 0.0},
                a={"ell": ell, "delta": 0.0, "lam": 0.0, "tau": 2.0},
                ties=[{"i": "a", "j": "b", "x": x, "r": 1e6, "o": 0.0}], horizon=100.0)
    res = simulate(raw, seed=seed)
    cancels = res.events_of("cancel")
    assert len(cancels) > 30
    return cancels


@pytest.mark.parametrize("ell, x", [(0.0, 0.5), (0.8, 0.5), (0.8, 0.9)])
def test_cancellation_drop_is_proportional_to_wait_and_damped_by_loyalty(ell, x):
    for e in _cancel_drops(ell, x):
        assert e["dr"] == pytest.approx(0.05 * (1 - ell * x) * e["wait"], rel=1e-6)


def test_more_loyal_and_closer_gives_smaller_drop():
    def per_wait(ell, x):
        c = _cancel_drops(ell, x)
        return sum(e["dr"] for e in c) / sum(e["wait"] for e in c)
    assert per_wait(0.8, 0.5) < per_wait(0.0, 0.5)
    assert per_wait(0.8, 0.9) < per_wait(0.8, 0.5)


@pytest.mark.parametrize("tau, x", [(2.0, 0.1), (2.0, 0.9), (6.0, 0.1)])
def test_mean_wait_before_cancellation(tau, x):
    raw = _dyad(1.0, glob={"h1": 1.0, "zeta": 0.0}, a={"tau": tau, "delta": 0.0, "B": 2.0},
                ties=[{"i": "a", "j": "b", "x": x}], horizon=3000.0)
    waits = [e["wait"] for e in simulate(raw, seed=4).events_of("cancel")]
    assert len(waits) > 200
    assert np.mean(waits) == pytest.approx(tau * (1 + x), rel=0.12)


def test_isolation_trap():
    contacts = [f"c{k}" for k in range(10)]
    agents = [{"id": "a", "B": 2.0, "tau": 1e6, "epsilon": 0.0}] + [{"id": c, "B": 0.5, "alpha": 1.0} for c in contacts]
    ties = [{"i": "a", "j": c, "x": 0.5} for c in contacts]
    raw = make_config(agents=agents, ties=ties, globals_={"gamma": 1.0, "zeta": 0.0},
                      simulation={"horizon": 200.0})
    res = simulate(raw, seed=0)
    a = res.index("a")
    assert res.pending_budget[-1, a] == pytest.approx(1.5)
    assert res.capacity[-1, a] - res.budget[-1, a] < 1.0
    invites = [e["t"] for e in res.events_of("invite") if e["i"] == "a"]
    assert len(invites) == 3
    assert max(invites) < 50.0
