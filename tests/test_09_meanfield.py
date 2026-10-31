"""Ticket 09: mean-field solver (seam: solve_meanfield) and ABM <-> mean-field convergence."""
import numpy as np
import pytest

from asym import simulate, solve_meanfield
from asym.model import forms

from conftest import make_config


def _scaled(s, regime="sustained", horizon=30.0):
    """Dyad config at scale s: budgets × s, jump sizes / s (fluid limit as s → ∞)."""
    common = {"B": 3.0 * s, "kappa": 0.3, "rho_star": 0.9, "lam": 0.2, "delta": 0.08, "tau": 3.0, "alpha": 0.5}
    agents = [{"id": "a", **common, "pi": -0.3}, {"id": "b", **common, "ell": 0.5}]
    ties = [{"i": "a", "j": "b", "x": 0.5, "r": 1.0, "o": 1.0}, {"i": "b", "j": "a", "x": 0.3, "r": 1.0, "o": 1.0}]
    gamma, a0 = (0.6, 1.5) if regime == "sustained" else (0.3, -0.5)
    return make_config(
        agents=agents, ties=ties,
        globals_={"gamma": gamma, "a0": a0, "eta": 0.1 / s, "inv_unit": 1.0 / s, "psi": 0.1 / s,
                  "sigma_p": 0.3, "x_min": 0.0, "zeta": 0.3},
        simulation={"horizon": horizon, "sample_interval": 1.0, "record_events": False})


def test_returns_trajectory_for_dyad_and_small_population():
    tr = solve_meanfield(_scaled(1, horizon=5.0))
    ab = tr.trajectory("a", "b")
    assert set(ab) >= {"t", "x", "r", "o", "circle"}
    assert len(ab["t"]) == 6
    agents = [{"id": k, "B": 3.0} for k in range(5)]
    ties = [{"i": i, "j": (i + 1) % 5, "x": 0.5} for i in range(5)]
    tr = solve_meanfield(make_config(agents=agents, ties=ties, globals_={"gamma": 0.5}, simulation={"horizon": 5.0}))
    assert tr.x.shape == (6, 5, 5)
    assert np.all((tr.x >= 0) & (tr.x <= 1))
    assert np.all(tr.budget <= np.array([3.0] * 5) + 1e-9)


def test_no_interaction_is_pure_decay():
    agents = [{"id": "a", "delta": 0.1, "lam": 0.3}, {"id": "b", "delta": 0.2, "lam": 0.05}]
    tr = solve_meanfield(make_config(agents=agents))
    ab = tr.trajectory("a", "b")
    np.testing.assert_allclose(ab["x"], 0.6 * np.exp(-0.1 * ab["t"]), rtol=1e-6)
    np.testing.assert_allclose(ab["r"], 2.0 * np.exp(-0.3 * ab["t"]), rtol=1e-6)
    np.testing.assert_allclose(tr.trajectory("b", "a")["x"], 0.4 * np.exp(-0.2 * ab["t"]), rtol=1e-6)


def test_mean_field_matches_simple_steady_state():
    """Always-accepting dyad without memory effects: x* solves η(1−x)A = δx with A from Little's law."""
    agents = [{"id": k, "delta": 0.05, "B": 2.0, "epsilon": 0.0, "tau": 1e9} for k in "ab"]
    raw = make_config(agents=agents, globals_={"gamma": 1.0, "a0": 60.0, "omega": 5.0, "c_wait": 0.0, "d": 1.0},
                      simulation={"horizon": 200.0, "sample_interval": 10.0})
    tr = solve_meanfield(raw)
    U = tr.budget[-1]
    A = 2 * (1.0 * (2.0 - U[0]))  # both agents issue γ·F; every invitation is accepted
    x_star = 0.1 * A / (0.1 * A + 0.05)
    assert tr.x[-1, 0, 1] == pytest.approx(x_star, rel=1e-3)
    assert U[0] == pytest.approx(A * 1.0, rel=1e-3)  # Little: U = A·d


def test_functional_forms_are_shared(monkeypatch):
    monkeypatch.setattr(forms, "acceptance_probability", lambda *a, **k: 0.0 * a[0])
    raw = make_config(globals_={"gamma": 1.0, "a0": 60.0}, simulation={"horizon": 20.0})
    assert not simulate(raw, seed=0).events_of("accept", "late_accept")
    assert np.all(solve_meanfield(raw).accept_rate == 0.0)


@pytest.mark.slow
@pytest.mark.parametrize("regime", ["sustained", "decaying"])
def test_abm_ensemble_converges_to_mean_field(regime):
    errors = []
    for s in (1, 4, 16):
        mf = solve_meanfield(_scaled(s, regime))
        runs = [simulate(_scaled(s, regime), seed=k) for k in range(20)]
        err = 0.0
        for i, j in (("a", "b"), ("b", "a")):
            mean_x = np.mean([r.trajectory(i, j)["x"] for r in runs], axis=0)
            err = max(err, float(np.abs(mean_x - mf.trajectory(i, j)["x"]).max()))
        errors.append(err)
    assert errors[0] > errors[1] > errors[2]
    assert errors[2] < 0.012
