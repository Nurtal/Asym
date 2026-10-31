"""Embedded dyad: the focal dyad competes with background partners (mean-field)."""
import numpy as np
import pytest

from asym.config import load_config
from asym.meanfield.dyad import OUTCOMES, archetype_pairs
from asym.meanfield.embedded import embedded_dyad_config, embedded_outcome, embedded_pairs, embedded_sweep

G = {"gamma": 0.5, "a0": 0.5}


def test_config_structure():
    raw = embedded_dyad_config("loyal_few", "butterfly", n_background=3, x0=(0.2, 0.7), x_bg=0.4)
    cfg = load_config(raw)
    assert cfg.agent_ids == ["A", "B", "a1", "a2", "a3", "b1", "b2", "b3"]
    assert [a["archetype"] for a in cfg.agents[:3]] == ["loyal_few", "butterfly", "loyal_few"]
    assert cfg.agents[5]["archetype"] == "butterfly"
    ties = {(t["i"], t["j"]): t["x"] for t in raw["init"]["ties"]}
    assert len(ties) == 2 + 2 * 4 * 3  # focal pair + two directed 4-cliques
    assert ties[("A", "B")] == 0.2 and ties[("B", "A")] == 0.7 and ties[("a1", "a3")] == 0.4
    assert ("a1", "b1") not in ties and ("A", "b1") not in ties


def test_no_background_reduces_to_isolated_dyad():
    iso = archetype_pairs(["loyal_few", "transactional"], x0=(0.5, 0.5), horizon=300.0, globals_=G)
    emb = embedded_outcome("loyal_few", "transactional", starts=[(0.5, 0.5)], n_background=0, globals_=G,
                           horizon=300.0)[0]
    ref = iso[("loyal_few", "transactional")]
    assert emb["x_ab"] == pytest.approx(ref["x_ab"], abs=1e-9) and emb["x_ba"] == pytest.approx(ref["x_ba"], abs=1e-9)


@pytest.mark.slow
def test_competition_produces_breakup_and_bistability():
    out = embedded_outcome("loyal_few", "loyal_few", n_background=4, globals_=G)
    assert out[0]["outcome"] == "breakup" and out[-1]["outcome"] == "friendship"  # start-dependent


@pytest.mark.slow
def test_competition_produces_asymmetry():
    out = embedded_outcome("butterfly", "transactional", starts=[(0.5, 0.5)], n_background=4, globals_=G)[0]
    assert out["outcome"] == "asymmetric" and out["x_ab"] > out["x_ba"]


def test_sweep_shapes_and_bistability_mask():
    res = embedded_sweep("loyal_few", "loyal_few", {"globals.a0": [0.5, 3.0]}, n_background=2, globals_=G,
                         horizon=200.0)
    assert res["outcome"].shape == (2, 2) and res["x_ab"].shape == (2, 2) and res["bistable"].shape == (2,)
    assert set(res["outcome"].ravel()) <= set(OUTCOMES)
    assert res["bistable"][0] == (res["outcome"][0, 0] != res["outcome"][1, 0])
    # background parameters only touch the partners
    from asym.meanfield.embedded import _set
    raw = embedded_dyad_config("loyal_few", "loyal_few", n_background=2)
    _set(raw, "background.1.B", 9.0, 2)
    assert [a["B"] for a in raw["agents"]] == [4.0, 4.0, 4.0, 4.0, 9.0, 9.0]


def test_pairs_table():
    tab = embedded_pairs(["loyal_few", "avoidant"], starts=[(0.5, 0.5)], n_background=2, globals_=G, horizon=100.0)
    assert set(tab) == {(a, b) for a in ("loyal_few", "avoidant") for b in ("loyal_few", "avoidant")}
    for v in tab.values():
        assert len(v) == 1 and v[0]["outcome"] in OUTCOMES
