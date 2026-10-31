"""Ticket 10: dyad analysis — 2-D reduction, fixed points, phase diagrams."""
import numpy as np
import pytest

from asym.meanfield.dyad import OUTCOMES, DyadAnalysis, archetype_pairs, classify_outcome, sweep

from conftest import make_config

FAST = {"lam": 3.0, "tau": 0.5, "B": 3.0, "delta": 0.05, "epsilon": 0.0}


def _bistable(a=8.0, a0=-5.0, **glob):
    return make_config(agents=[{"id": "a", **FAST}, {"id": "b", **FAST}],
                       globals_={"gamma": 0.5, "a": a, "a0": a0, "b": 0.0, "c": 0.0, "omega": 5.0, "zeta": 0.0,
                                 "eta": 0.1, "x_min": 0.0, **glob})


@pytest.fixture(scope="module")
def bistable_fps():
    return DyadAnalysis(_bistable()).fixed_points(n_grid=21)


def test_classify_outcome():
    th, xm = [0.3, 0.55, 0.8], 0.02
    assert classify_outcome(0.6, 0.4, th, xm) == "friendship"
    assert classify_outcome(0.6, 0.1, th, xm) == "asymmetric"
    assert classify_outcome(0.1, 0.2, th, xm) == "acquaintance"
    assert classify_outcome(0.01, 0.0, th, xm) == "breakup"


@pytest.mark.slow
def test_fixed_points_and_bistability(bistable_fps):
    stab = [f.stability for f in bistable_fps]
    assert stab.count("stable") == 2 and "saddle" in stab
    low, high = bistable_fps[0], bistable_fps[-1]
    assert low.x[0] < 0.1 and high.x[0] > 0.55
    for f in bistable_fps:
        assert f.eigenvalues.shape == (2,) and f.jacobian.shape == (2, 2)


@pytest.mark.slow
def test_reduced_fixed_points_match_full_mean_field(bistable_fps):
    da = DyadAnalysis(_bistable())
    low, high = bistable_fps[0], bistable_fps[-1]
    np.testing.assert_allclose(da.integrate((0.7, 0.65), horizon=400.0), high.x, atol=5e-3)
    np.testing.assert_allclose(da.integrate((0.2, 0.25), horizon=400.0), low.x, atol=5e-3)


@pytest.mark.slow
def test_stability_agrees_with_forward_integration(bistable_fps):
    da = DyadAnalysis(_bistable())
    for f in bistable_fps:
        p = np.array(f.x)
        if f.stability == "stable":
            np.testing.assert_allclose(da.integrate(p + [0.03, -0.02], horizon=400.0), p, atol=5e-3)
        elif f.stability == "saddle":
            up = da.integrate(np.clip(p + 0.03, 0, 1), horizon=400.0)
            down = da.integrate(np.clip(p - 0.03, 0, 1), horizon=400.0)
            assert up.min() > p.max() + 0.03 and down.max() < p.min() - 0.03


@pytest.mark.slow
def test_monostable_regime_is_not_bistable():
    assert not DyadAnalysis(_bistable(a=0.0, a0=3.0)).is_bistable(n_grid=15)


def test_two_parameter_sweep_gives_outcome_grid():
    res = sweep(_bistable(), {"globals.a0": [-8.0, -5.0, 0.0], "agents.*.delta": [0.02, 0.05]}, x0=(0.6, 0.6),
                horizon=200.0)
    assert res["outcome"].shape == (3, 2) and res["x_ij"].shape == (3, 2)
    assert set(res["outcome"].ravel()) <= set(OUTCOMES)
    assert res["outcome"][2, 0] == "friendship"
    assert res["x_ij"][0, 1] < res["x_ij"][2, 1]  # higher acceptance keeps the dyad closer


def test_archetype_pair_table():
    names = ["butterfly", "loyal_few", "transactional", "avoidant"]
    table = archetype_pairs(names, horizon=100.0)
    assert set(table) == {(a, b) for a in names for b in names}
    for v in table.values():
        assert v["outcome"] in OUTCOMES
        assert 0.0 <= v["x_ab"] <= 1.0 and 0.0 <= v["x_ba"] <= 1.0
