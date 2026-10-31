import copy

import pytest


def make_config(agents=None, ties=None, simulation=None, globals_=None, init=None, variants=None):
    """Build a minimal config dict: a dyad of agents 'a' and 'b' by default."""
    cfg = {
        "simulation": {"horizon": 10.0, "burn_in": 0.0, "sample_interval": 1.0},
        "globals": {"gamma": 0.0},
        "agents": agents if agents is not None else [{"id": "a"}, {"id": "b"}],
        "init": init if init is not None else {
            "mode": "file",
            "ties": ties if ties is not None else [
                {"i": "a", "j": "b", "x": 0.6, "r": 2.0, "o": 2.0},
                {"i": "b", "j": "a", "x": 0.4, "r": 1.0, "o": 1.0},
            ],
        },
    }
    if simulation:
        cfg["simulation"].update(simulation)
    if globals_:
        cfg["globals"].update(globals_)
    if variants:
        cfg["variants"] = variants
    return copy.deepcopy(cfg)


@pytest.fixture
def cfg_factory():
    return make_config
