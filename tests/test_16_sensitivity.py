"""Morris screening: design, indices and factor application."""
import numpy as np
import pytest

from asym.config import load_config
from asym.sensitivity import Factor, apply_factors, morris_design, morris_indices


def test_design_is_one_at_a_time_on_the_grid():
    D = morris_design(k=5, r=7, levels=4, seed=1)
    assert D.shape == (7, 6, 5)
    assert D.min() >= 0 and D.max() <= 1
    for t in range(7):
        steps = np.diff(D[t], axis=0)
        assert np.all((steps != 0).sum(axis=1) == 1)  # one factor per step
        assert sorted(np.flatnonzero(s)[0] for s in steps) == list(range(5))  # each factor once
        assert np.allclose(np.abs(steps[steps != 0]), 4 / 6)


def test_indices_recover_linear_and_interaction_effects():
    D = morris_design(k=3, r=30, seed=2)
    Y = 2 * D[..., 0] - 0 * D[..., 1] + 3 * D[..., 0] * D[..., 2]  # factor 2 only acts through x0
    idx = morris_indices(D, Y)
    assert idx["mu_star"][1] == pytest.approx(0.0)
    assert idx["mu_star"][0] > idx["mu_star"][2] > 0
    assert idx["sigma"][2] > 0 and idx["sigma"][0] > 0  # interaction → spread of effects
    multi = morris_indices(D, np.stack([Y, -Y], axis=-1))
    assert multi["mu"].shape == (3, 2) and multi["mu"][0, 1] == pytest.approx(-multi["mu"][0, 0])


def test_factor_values_and_application():
    f = Factor("B", "archetypes.B", 0.5, 2.0, log=True)
    assert f.value(0) == pytest.approx(0.5) and f.value(1) == pytest.approx(2.0) and f.value(0.5) == pytest.approx(1.0)
    raw = {"archetypes": {"bf": {"base": "butterfly", "B": 20.0}},
           "population": {"composition": {"bf": 3, "loyal_few": 3}, "seed": 0}, "init": {"mode": "empty"}}
    facs = [f, Factor("delta", "archetypes.delta", 0.5, 2.0, log=True), Factor("ell", "archetypes.ell", 0.5, 2.0),
            Factor("eta", "globals.eta", 0.05, 0.2), Factor("t3", "thresholds.2", 0.7, 0.9)]
    out = apply_factors(raw, facs, [1.0, 0.0, 1.0, 0.0, 1.0])
    assert out["archetypes"]["bf"]["B"] == pytest.approx(40.0)
    assert out["archetypes"]["loyal_few"]["B"] == pytest.approx(8.0)  # built-in 4.0 × 2
    assert out["archetypes"]["loyal_few"]["ell"] == 1.0  # 0.8 × 2 clipped to [0, 1]
    assert out["archetypes"]["loyal_few"]["delta"] == pytest.approx([0.04, 0.025, 0.015, 0.0075])
    assert out["globals"]["eta"] == pytest.approx(0.05) and out["globals"]["thresholds"][2] == pytest.approx(0.9)
    cfg = load_config(out)
    assert {a["archetype"] for a in cfg.agents} == {"bf", "loyal_few"}
    assert raw["archetypes"] == {"bf": {"base": "butterfly", "B": 20.0}}  # input untouched
