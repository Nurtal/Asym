"""Ticket 07: archetypes, parameter sampling, init.mode = random | file."""
import json

import numpy as np
import pytest
import yaml

from asym import ConfigError, load_config, simulate
from asym.config import AGENT_DEFAULTS
from asym.model.archetypes import BUILTIN_ARCHETYPES


def _pop(composition, size=None, noise=0.1, seed=0, archetypes=None, overrides=None):
    raw = {"population": {"composition": composition, "noise": noise, "seed": seed},
           "simulation": {"horizon": 1.0}, "globals": {"gamma": 0.0}}
    if size is not None:
        raw["population"]["size"] = size
    if archetypes:
        raw["archetypes"] = archetypes
    if overrides:
        raw["population"]["overrides"] = overrides
    return raw


def test_builtin_archetypes_exist():
    assert {"butterfly", "loyal_few", "transactional", "avoidant"} <= set(BUILTIN_ARCHETYPES)


def test_sampled_parameters_stay_in_domain():
    cfg = load_config(_pop({"butterfly": 100, "loyal_few": 100, "transactional": 100, "avoidant": 100}, noise=1.0))
    for a in cfg.agents:
        for k in ("epsilon", "ell", "alpha"):
            assert 0.0 <= a[k] <= 1.0
        for k in ("B", "tau"):
            assert a[k] > 0
        for k in ("beta", "rho_star", "kappa", "lam", "w", "m", "nu"):
            assert a[k] >= 0
        assert all(d >= 0 for d in a["delta"])


def test_sample_means_converge_to_centres():
    cfg = load_config(_pop({"loyal_few": 4000}, noise=0.2))
    centre = {**AGENT_DEFAULTS, **BUILTIN_ARCHETYPES["loyal_few"]}
    for k in ("B", "beta", "tau", "w", "lam"):
        assert np.mean([a[k] for a in cfg.agents]) == pytest.approx(centre[k], rel=0.02)
    for k in ("ell", "alpha", "epsilon"):  # logit-normal: median = centre
        assert np.median([a[k] for a in cfg.agents]) == pytest.approx(centre[k], rel=0.03)


def test_zero_noise_reproduces_centre():
    cfg = load_config(_pop({"transactional": 3}, noise=0.0))
    centre = {**AGENT_DEFAULTS, **BUILTIN_ARCHETYPES["transactional"]}
    for a in cfg.agents:
        assert a["kappa"] == centre["kappa"] and a["tau"] == centre["tau"]
        assert a["archetype"] == "transactional"


def test_composition_counts_and_proportions():
    cfg = load_config(_pop({"butterfly": 3, "avoidant": 2}))
    assert [a["archetype"] for a in cfg.agents] == ["butterfly"] * 3 + ["avoidant"] * 2
    cfg = load_config(_pop({"butterfly": 0.25, "loyal_few": 0.75}, size=10))
    names = [a["archetype"] for a in cfg.agents]
    assert len(names) == 10
    assert names.count("loyal_few") in (7, 8)
    with pytest.raises(ConfigError):
        load_config(_pop({"butterfly": 0.5, "avoidant": 0.5}))  # proportions need size


def test_user_archetypes_and_overrides():
    cfg = load_config(_pop({"hermit": 2}, noise=0.0,
                           archetypes={"hermit": {"base": "avoidant", "nu": 0.0, "B": 1.5}},
                           overrides={1: {"B": 9.0}}))
    assert cfg.agents[0]["B"] == 1.5 and cfg.agents[0]["alpha"] == 0.9
    assert cfg.agents[1]["B"] == 9.0
    with pytest.raises(ConfigError):
        load_config(_pop({"nobody": 2}))


def test_explicit_agent_with_archetype():
    cfg = load_config({"agents": [{"id": "x", "archetype": "butterfly", "B": 2.0}], "simulation": {"horizon": 1.0}})
    assert cfg.agents[0]["B"] == 2.0
    assert cfg.agents[0]["beta"] == BUILTIN_ARCHETYPES["butterfly"]["beta"]


def test_random_init_density():
    raw = _pop({"butterfly": 60}, noise=0.0)
    raw["init"] = {"mode": "random", "density": 0.2, "x_range": [0.2, 0.7]}
    res = simulate(raw, seed=0)
    snap = res.snapshot(0)
    n_pairs = 60 * 59 / 2
    assert snap["i"].size / 2 / n_pairs == pytest.approx(0.2, abs=0.03)
    assert snap["x"].min() >= 0.2 - 1e-9 and snap["x"].max() <= 0.7


def _write_files(tmp_path, kind):
    agents = [{"id": "ann", "archetype": "loyal_few"}, {"id": "bob", "B": 3.0}, {"id": "cy"}]
    ties = [{"i": "ann", "j": "bob", "x": 0.7, "r": 1.0, "o": 2.0, "circle": 3},
            {"i": "bob", "j": "ann", "x": 0.2}, {"i": "cy", "j": "ann", "x": 0.5}]
    if kind == "json":
        (tmp_path / "state.json").write_text(json.dumps({"agents": agents, "ties": ties}))
        init = {"mode": "file", "path": "state.json"}
    else:
        (tmp_path / "agents.csv").write_text("id,archetype,B\nann,loyal_few,\nbob,,3.0\ncy,,\n")
        (tmp_path / "ties.csv").write_text("i,j,x,r,o,circle\nann,bob,0.7,1.0,2.0,3\nbob,ann,0.2,,,\ncy,ann,0.5,,,\n")
        init = {"mode": "file", "agents_path": "agents.csv", "ties_path": "ties.csv"}
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(yaml.safe_dump({"init": init, "simulation": {"horizon": 1.0}, "globals": {"gamma": 0.0}}))
    return cfg_path


@pytest.mark.parametrize("kind", ["json", "csv"])
def test_file_init_reproduces_loaded_state(tmp_path, kind):
    res = simulate(_write_files(tmp_path, kind), seed=0)
    assert res.agent_ids == ["ann", "bob", "cy"]
    assert res.config["agents"][0]["archetype"] == "loyal_few"
    assert res.config["agents"][1]["B"] == 3.0
    ab = res.trajectory("ann", "bob")
    assert (ab["x"][0], ab["r"][0], ab["o"][0], ab["circle"][0]) == (0.7, 1.0, 2.0, 3)
    assert res.trajectory("bob", "ann")["x"][0] == 0.2
    assert res.snapshot(0)["i"].size == 3


@pytest.mark.parametrize("bad_tie, msg", [
    ({"i": "a", "j": "zed", "x": 0.5}, "unknown agent"),
    ({"i": "a", "j": "b", "x": 1.5}, "x must lie"),
    ({"i": "a", "j": "a", "x": 0.5}, "self tie"),
    ({"i": "b", "j": "a", "x": 0.5}, "duplicate"),
])
def test_malformed_ties_raise(bad_tie, msg):
    raw = {"agents": [{"id": "a"}, {"id": "b"}], "simulation": {"horizon": 1.0},
           "init": {"mode": "file", "ties": [{"i": "b", "j": "a", "x": 0.3}, bad_tie]}}
    with pytest.raises(ConfigError, match=msg):
        simulate(raw, seed=0)


def test_unknown_archetype_in_file_raises(tmp_path):
    (tmp_path / "s.json").write_text(json.dumps({"agents": [{"id": 1, "archetype": "ghost"}], "ties": []}))
    with pytest.raises(ConfigError, match="unknown archetype"):
        load_config({"init": {"mode": "file", "path": str(tmp_path / "s.json")}})


def test_missing_file_raises():
    with pytest.raises(ConfigError, match="not found"):
        load_config({"init": {"mode": "file", "path": "/nonexistent/s.json"}})
