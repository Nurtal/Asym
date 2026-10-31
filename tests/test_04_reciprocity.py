"""Ticket 04: reciprocity deficit and perception bias (seam: simulate)."""
import math

import numpy as np
import pytest

from asym import simulate

from conftest import make_config


def _eroding(kappa=0.0, rho_star=0.8, ell=0.0, x0=0.5):
    # b never reciprocated: r = 0, o = 10 -> q = 0.5 / 10.5; memories frozen (lam = 0)
    agents = [{"id": "a", "delta": 0.02, "kappa": kappa, "rho_star": rho_star, "ell": ell, "lam": 0.0},
              {"id": "b"}]
    ties = [{"i": "a", "j": "b", "x": x0, "r": 0.0, "o": 10.0}]
    raw = make_config(agents=agents, ties=ties, globals_={"x_min": 0.0},
                      simulation={"horizon": 20.0, "sample_interval": 0.5})
    return simulate(raw, seed=0).trajectory("a", "b")


def test_deficit_erodes_faster_than_decay_and_matches_closed_form():
    q = 0.5 / 10.5
    pure = _eroding(kappa=0.0)
    eroded = _eroding(kappa=0.3)
    assert np.all(eroded["x"][1:] < pure["x"][1:])
    expected = 0.5 * np.exp(-(0.02 + 0.3 * (0.8 - q)) * eroded["t"])
    np.testing.assert_allclose(eroded["x"], expected, rtol=1e-6)


def test_erosion_grows_with_kappa_and_rho_star():
    assert _eroding(kappa=0.6)["x"][-1] < _eroding(kappa=0.3)["x"][-1]
    assert _eroding(kappa=0.3, rho_star=1.5)["x"][-1] < _eroding(kappa=0.3, rho_star=0.8)["x"][-1]


def test_no_erosion_without_deficit():
    agents = [{"id": "a", "delta": 0.02, "kappa": 1.0, "lam": 0.0}, {"id": "b"}]
    ties = [{"i": "a", "j": "b", "x": 0.5, "r": 10.0, "o": 10.0}]  # q = 1 > rho* = 0.8
    tr = simulate(make_config(agents=agents, ties=ties), seed=0).trajectory("a", "b")
    np.testing.assert_allclose(tr["x"], 0.5 * np.exp(-0.02 * tr["t"]), rtol=1e-6)


def test_loyalty_protects_close_ties():
    assert _eroding(kappa=0.5, ell=0.9, x0=0.9)["x"][-1] > _eroding(kappa=0.5, ell=0.0, x0=0.9)["x"][-1]


def test_perception_bias_scales_reciprocity_increments():
    agents = [{"id": "a", "pi": 0.5, "lam": 0.0, "delta": 0.0}, {"id": "b", "lam": 0.0, "delta": 0.0}]
    raw = make_config(agents=agents, globals_={"gamma": 0.5, "a0": 50.0, "psi": 0.0}, simulation={"horizon": 5.0})
    res = simulate(raw, seed=0)
    n = len(res.events_of("accept"))
    assert n >= 1
    assert res.trajectory("a", "b")["r"][-1] == pytest.approx(2.0 + n * math.exp(0.5))
    assert res.trajectory("b", "a")["r"][-1] == pytest.approx(1.0 + n)


@pytest.mark.slow
def test_perception_bias_alone_creates_asymmetry():
    common = {"kappa": 0.5, "rho_star": 0.9, "lam": 0.2, "B": 3.0}
    agents = [{"id": "a", **common, "pi": -1.0}, {"id": "b", **common}]
    ties = [{"i": "a", "j": "b", "x": 0.5}, {"i": "b", "j": "a", "x": 0.5}]
    raw = make_config(agents=agents, ties=ties, globals_={"gamma": 0.4, "a0": -1.0},
                      simulation={"horizon": 150.0, "burn_in": 50.0, "sample_interval": 5.0})
    diffs = []
    for seed in range(20):
        res = simulate(raw, seed=seed)
        xa, xb = res.trajectory("a", "b")["x"], res.trajectory("b", "a")["x"]
        n = min(len(xa), len(xb))
        diffs.append(np.mean(xb[:n] - xa[:n]) if n else 0.0)
    diffs = np.array(diffs)
    t_stat = diffs.mean() / (diffs.std(ddof=1) / math.sqrt(len(diffs)))
    assert diffs.mean() > 0.02
    assert t_stat > 3.0
