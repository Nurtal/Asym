"""Ticket 11: metrics on SimulationResult, tested on hand-built results."""
import math

import numpy as np
import pytest

from asym import SimulationResult, simulate
from asym import metrics as M

from conftest import make_config

IDS = ["a", "b", "c", "d"]


def _result(rows, times=(0.0,), events=None, burn_in=0.0, **kw):
    return SimulationResult.build(IDS, times, rows, events=events,
                                  config={"simulation": {"burn_in": burn_in}, "globals": {"o0": 0.5}}, **kw)


def test_circle_and_layer_sizes():
    rows = [(0.0, "a", "b", 0.9, 0, 0, 4), (0.0, "a", "c", 0.6, 0, 0, 3), (0.0, "a", "d", 0.2, 0, 0, 1),
            (0.0, "b", "a", 0.9, 0, 0, 4)]
    res = _result(rows)
    np.testing.assert_array_equal(M.circle_sizes(res)[0], [1, 0, 1, 1])
    np.testing.assert_array_equal(M.layer_sizes(res)[0], [1, 2, 2, 3])
    lay = M.layering(res)
    np.testing.assert_allclose(lay["mean_layer_sizes"], [0.5, 0.75, 0.75, 1.0])
    np.testing.assert_allclose(lay["ratios"], [1.5, 1.0, 4 / 3])


def test_asymmetry():
    rows = [(0.0, "a", "b", 0.9, 0, 0, 4), (0.0, "b", "a", 0.5, 0, 0, 2),
            (0.0, "a", "c", 0.4, 0, 0, 2), (0.0, "c", "a", 0.3, 0, 0, 2),
            (0.0, "c", "d", 0.4, 0, 0, 2)]
    asym = M.asymmetry(_result(rows))
    np.testing.assert_allclose(sorted(asym["abs_diff"]), [0.1, 0.4])
    assert asym["circle_mismatch"] == 0.5
    assert asym["one_sided"] == pytest.approx(1 / 3)
    assert asym["n_dyads"] == 3


def test_reciprocity_ratios():
    rows = [(0.0, "a", "b", 0.5, 1.5, 0.5, 2), (0.0, "b", "a", 0.5, 0.0, 1.5, 2)]
    np.testing.assert_allclose(sorted(M.reciprocity_ratios(_result(rows))), [0.25, 2.0])


def test_lifetimes_and_churn():
    times = [0.0, 5.0, 10.0]
    rows = [(0.0, "a", "b", 0.5, 0, 0, 2), (0.0, "b", "a", 0.5, 0, 0, 2),
            (5.0, "b", "a", 0.4, 0, 0, 2), (5.0, "c", "d", 0.1, 0, 0, 1),
            (10.0, "b", "a", 0.3, 0, 0, 1), (10.0, "c", "d", 0.1, 0, 0, 1)]
    events = [{"t": 3.0, "type": "forget", "i": "a", "j": "b"},
              {"t": 4.0, "type": "tie_created", "i": "c", "j": "d"},
              {"t": 8.0, "type": "demote", "i": "b", "j": "a"}]
    res = _result(rows, times=times, events=events)
    lt = M.tie_lifetimes(res)
    np.testing.assert_allclose(lt["completed"], [3.0])
    np.testing.assert_allclose(sorted(lt["censored"]), [6.0, 10.0])
    ch = M.churn(res)
    assert ch["forget_rate"] == pytest.approx(1 / (2 * 10))
    assert ch["transition_rate"] == pytest.approx(1 / (2 * 10))


def test_metrics_ignore_pre_burn_in_events():
    times = [10.0, 20.0]
    rows = [(10.0, "a", "b", 0.5, 0, 0, 2), (20.0, "a", "b", 0.5, 0, 0, 2)]
    events = [{"t": 5.0, "type": "forget", "i": "c", "j": "d"}, {"t": 15.0, "type": "forget", "i": "d", "j": "c"}]
    assert M.churn(_result(rows, times=times, events=events, burn_in=10.0))["forget_rate"] == pytest.approx(0.1)


def test_shock_resilience():
    times = [0.0, 1.0, 2.0, 3.0]
    rows = [(t, "a", "b", x, 0, 0, c) for t, x, c in [(0, 0.6, 3), (1, 0.3, 3), (2, 0.5, 2), (3, 0.65, 3)]] + \
           [(t, "c", "d", 0.5, 0, 0, 2) for t in times]
    events = [{"t": 0.5, "type": "shock_tie", "i": "a", "j": "b", "x_before": 0.6, "x_after": 0.3},
              {"t": 1.5, "type": "demote", "i": "a", "j": "b"},
              {"t": 0.5, "type": "shock_tie", "i": "c", "j": "d", "x_before": 0.5, "x_after": 0.25}]
    out = M.shock_resilience(_result(rows, times=times, events=events))
    np.testing.assert_allclose(out["recovery_times"], [2.5, 0.5])
    assert out["drop_probability"] == 0.5


def test_isolation_trap_and_locked_fraction():
    times = [0.0, 1.0]
    budget = np.array([[0.0, 0.0, 0.0, 0.0], [1.5, 0.5, 0.0, 1.0]])
    pending = np.array([[0.0, 0.0, 0.0, 0.0], [1.5, 0.5, 0.0, 0.0]])
    cap = np.full((2, 4), 2.0)
    res = _result([], times=times, budget=budget, pending_budget=pending, capacity=cap)
    np.testing.assert_allclose(M.locked_budget_fraction(res)[1], [0.75, 0.25, 0.0, 0.0])
    np.testing.assert_allclose(M.isolation_trap(res), [0.0, 0.25])


def test_network_metrics():
    tri = [("a", "b"), ("b", "c"), ("c", "a")]
    rows = [(0.0, u, v, 0.9, 0, 0, 4) for u, v in tri] + [(0.0, v, u, 0.9, 0, 0, 4) for u, v in tri]
    net = M.network_metrics(_result(rows))
    assert net["n_edges"] == 3
    assert net["clustering"] == pytest.approx(0.75)  # three nodes at 1, the isolated node at 0
    assert net["close_degree_gini"] == pytest.approx(M.gini([2, 2, 2, 0]))
    assert M.gini([1, 1, 1]) == 0.0
    assert M.gini([0, 0, 0, 5]) == pytest.approx(0.75)


def test_graceful_on_empty_and_after_disk_round_trip(tmp_path):
    empty = _result([], times=[0.0, 1.0])
    assert M.circle_sizes(empty).sum() == 0
    assert math.isnan(M.asymmetry(empty)["circle_mismatch"])
    assert math.isnan(M.network_metrics(empty)["modularity"])
    assert M.tie_lifetimes(empty)["completed"].size == 0
    res = simulate(make_config(globals_={"gamma": 0.5, "a0": 1.0}, simulation={"horizon": 30.0}), seed=0)
    path = tmp_path / "r.npz"
    res.save(path)
    loaded = SimulationResult.load(path)
    np.testing.assert_array_equal(M.circle_sizes(loaded), M.circle_sizes(res))
    assert M.churn(loaded) == M.churn(res)


def test_layering_by_archetype():
    rows = [(0.0, "a", "b", 0.9, 0, 0, 4), (0.0, "a", "c", 0.6, 0, 0, 3), (0.0, "b", "a", 0.9, 0, 0, 4),
            (0.0, "c", "d", 0.2, 0, 0, 1)]
    agents = [{"id": "a", "archetype": "x"}, {"id": "b", "archetype": "y"}, {"id": "c", "archetype": "x"},
              {"id": "d"}]
    res = SimulationResult.build(IDS, (0.0,), rows, config={"agents": agents})
    by = M.layering_by_archetype(res)
    assert set(by) == {"x", "y", None}
    np.testing.assert_allclose(by["x"], [0.5, 1.0, 1.0, 1.5])  # a: [1,2,2,2], c: [0,0,0,1]
    np.testing.assert_allclose(by["y"], [1, 1, 1, 1])
    np.testing.assert_allclose(by[None], [0, 0, 0, 0])
