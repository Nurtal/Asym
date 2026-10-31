"""Ticket 01: config -> simulate -> result for a decaying dyad (seam: simulate)."""
import math

import numpy as np
import pytest
import yaml

from asym import ConfigError, SimulationResult, load_config, simulate


def test_yaml_config_loads_and_validates(tmp_path, cfg_factory):
    path = tmp_path / "dyad.yaml"
    path.write_text(yaml.safe_dump(cfg_factory()))
    cfg = load_config(path)
    assert [a["id"] for a in cfg.agents] == ["a", "b"]


def test_unknown_key_is_rejected(cfg_factory):
    raw = cfg_factory()
    raw["globals"]["etaa"] = 0.1
    with pytest.raises(ConfigError):
        load_config(raw)


def test_result_structure(cfg_factory):
    res = simulate(cfg_factory(), seed=1)
    assert isinstance(res, SimulationResult)
    assert res.seed == 1
    assert res.agent_ids == ["a", "b"]
    tr = res.trajectory("a", "b")
    for key in ("t", "x", "r", "o", "circle"):
        assert key in tr
    assert res.budget.shape == (len(res.times), 2)
    assert isinstance(res.events, list)


def test_pure_decay_matches_closed_form(cfg_factory):
    raw = cfg_factory(agents=[{"id": "a", "delta": 0.1, "lam": 0.3}, {"id": "b", "delta": 0.2, "lam": 0.05}])
    res = simulate(raw, seed=0)
    ab, ba = res.trajectory("a", "b"), res.trajectory("b", "a")
    np.testing.assert_allclose(ab["x"], 0.6 * np.exp(-0.1 * ab["t"]), rtol=1e-6)
    np.testing.assert_allclose(ab["r"], 2.0 * np.exp(-0.3 * ab["t"]), rtol=1e-6)
    np.testing.assert_allclose(ab["o"], 2.0 * np.exp(-0.3 * ab["t"]), rtol=1e-6)
    np.testing.assert_allclose(ba["x"], 0.4 * np.exp(-0.2 * ba["t"]), rtol=1e-6)
    np.testing.assert_allclose(ba["r"], 1.0 * np.exp(-0.05 * ba["t"]), rtol=1e-6)


def test_closeness_stays_in_unit_interval(cfg_factory):
    res = simulate(cfg_factory(simulation={"horizon": 50.0}), seed=0)
    for key in [("a", "b"), ("b", "a")]:
        x = res.trajectory(*key)["x"]
        assert np.all((x >= 0) & (x <= 1))


def test_horizon_burn_in_and_sampling(cfg_factory):
    res = simulate(cfg_factory(simulation={"horizon": 20.0, "burn_in": 5.0, "sample_interval": 2.5}), seed=0)
    np.testing.assert_allclose(res.times, np.arange(5.0, 20.0 + 1e-9, 2.5))


def test_determinism_and_disk_round_trip(tmp_path, cfg_factory):
    raw = cfg_factory()
    a, b = simulate(raw, seed=42), simulate(raw, seed=42)
    assert a.equals(b)
    path = tmp_path / "res.npz"
    a.save(path)
    loaded = SimulationResult.load(path)
    assert loaded.equals(a)
    assert loaded.seed == 42
    assert loaded.config == a.config
