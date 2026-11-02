"""Tie lifetimes of experiment 17, on hand-built event logs (no simulation)."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "time_mapping", Path(__file__).parent.parent / "experiments" / "17_time_mapping.py"
)
tm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tm)


def ev(kind, t, i="a", j="b"):
    return {"type": kind, "t": t, "i": i, "j": j}


def test_forgotten_tie_has_finite_lifetime():
    log = [ev("tie_created", 310.0), ev("forget", 340.0)]
    assert tm.tie_lifetimes(log, 300.0, 500.0) == [30.0]


def test_surviving_tie_is_censored():
    assert tm.tie_lifetimes([ev("tie_created", 310.0)], 300.0, 500.0) == [-1]


def test_recreated_tie_is_not_censored_by_its_earlier_forget():
    log = [ev("tie_created", 100.0), ev("forget", 150.0), ev("tie_created", 310.0), ev("forget", 360.0)]
    assert tm.tie_lifetimes(log, 300.0, 500.0) == [50.0]


def test_each_creation_in_the_window_counts():
    log = [ev("tie_created", 310.0), ev("forget", 320.0), ev("tie_created", 330.0), ev("forget", 370.0)]
    assert sorted(tm.tie_lifetimes(log, 300.0, 500.0)) == [10.0, 40.0]


def test_directions_are_separate_and_window_is_half_open():
    log = [ev("tie_created", 310.0), ev("tie_created", 310.0, "b", "a"), ev("forget", 320.0, "b", "a"),
           ev("tie_created", 500.0, "c", "d"), ev("tie_created", 299.0, "e", "f")]
    assert sorted(tm.tie_lifetimes(log, 300.0, 500.0)) == [-1, 10.0]
