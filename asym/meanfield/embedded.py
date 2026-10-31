"""Embedded dyad: a focal dyad competing with background partners (mean-field).

An isolated dyad always ends in friendship, because the two agents have nobody else
to spend their budget on (docs/experiments/03-dyad-archetype-pairs.md). The embedded
dyad gives each focal agent a neighbourhood of ``M`` background partners:

    A — a_1 … a_M      (clique: A and its partners are all tied to each other)
    B — b_1 … b_M      (clique)
    A ↔ B              (the focal tie, bridging the two neighbourhoods)

Every agent, focal or background, therefore spreads its budget over several ties, and
the focal tie must hold its own against the background ties. The whole system
(N = 2 + 2M agents) is integrated with the batched mean-field solver; the focal
outcome is read off at the horizon. Bistability shows up as an outcome that depends
on the focal start x0.

Agent order in the generated config: A, B, a_1 … a_M, b_1 … b_M.
"""
from __future__ import annotations

import copy
import itertools

import numpy as np

from asym.config import ConfigError, load_config
from asym.meanfield.dyad import classify_outcome
from asym.meanfield.solver import solve_meanfield
from asym.model.archetypes import archetype_centre, archetype_table


def _agent(spec, table, agent_id):
    if isinstance(spec, str):
        agent = archetype_centre(spec, table)
        agent["archetype"] = spec
    else:
        agent = copy.deepcopy(dict(spec))
    agent["id"] = agent_id
    agent["nu"] = 0.0  # the mean-field ignores encounters
    return agent


def embedded_dyad_config(a, b, n_background: int = 4, background=None, x0=(0.5, 0.5), x_bg: float = 0.5,
                         globals_=None, archetypes=None, horizon: float = 600.0, step: float = 0.05,
                         variants=None) -> dict:
    """Raw config of an embedded dyad.

    ``a`` and ``b`` are archetype names or agent dicts. ``background`` is the archetype
    (or agent dict) of the background partners, or a pair ``(for_a, for_b)``; by
    default each focal agent's partners share its archetype. Background ties start at
    ``x_bg``, the focal ties at ``x0``; every tie starts with r = o = 1.
    ``variants`` defaults to ``{"exploration": "ties"}`` so that exploration cannot
    create ties outside the two cliques (the topology stays fixed).
    """
    if n_background < 0:
        raise ConfigError("n_background must be >= 0")
    table = archetype_table(archetypes)
    if background is None:
        background = (a, b)
    elif isinstance(background, (str, dict)):
        background = (background, background)
    agents = [_agent(a, table, "A"), _agent(b, table, "B")]
    agents += [_agent(background[0], table, f"a{k + 1}") for k in range(n_background)]
    agents += [_agent(background[1], table, f"b{k + 1}") for k in range(n_background)]

    def tie(i, j, x):
        return {"i": i, "j": j, "x": float(x), "r": 1.0, "o": 1.0}

    ties = [tie("A", "B", x0[0]), tie("B", "A", x0[1])]
    for focal, side in (("A", "a"), ("B", "b")):
        group = [focal] + [f"{side}{k + 1}" for k in range(n_background)]
        ties += [tie(i, j, x_bg) for i, j in itertools.permutations(group, 2)]
    return {
        "agents": agents,
        "globals": dict(globals_ or {}),
        "init": {"mode": "file", "ties": ties},
        "variants": dict({"exploration": "ties"}, **(variants or {})),
        "simulation": {"horizon": float(horizon), "burn_in": 0.0, "sample_interval": float(horizon), "mf_step": step},
    }


def _set(raw: dict, path: str, value, n_background: int):
    """Set a parameter by path: globals.<k>, variants.<k>, focal.<0|1|*>.<p>,
    background.<0|1|*>.<p> (0 = A's partners, 1 = B's) or agents.*.<p>."""
    parts = path.split(".")
    head = parts[0]
    if head in ("globals", "variants"):
        raw.setdefault(head, {})[parts[1]] = value
        return
    if len(parts) != 3:
        raise ConfigError(f"bad parameter path {path!r}")
    sel, param = parts[1], parts[2]
    M = n_background
    if head == "focal":
        idx = [0, 1] if sel == "*" else [int(sel)]
    elif head == "background":
        sides = [0, 1] if sel == "*" else [int(sel)]
        idx = [2 + s * M + k for s in sides for k in range(M)]
    elif head == "agents" and sel == "*":
        idx = list(range(len(raw["agents"])))
    else:
        raise ConfigError(f"bad parameter path {path!r}")
    for k in idx:
        raw["agents"][k][param] = value


def _solve(configs):
    tr = solve_meanfield(configs, occupancy="exponential")
    g = load_config(configs[0]).globals
    xab, xba = tr.x[-1, :, 0, 1], tr.x[-1, :, 1, 0]
    return xab, xba, classify_outcome(xab, xba, g["thresholds"], g["x_min"])


def embedded_outcome(a, b, starts=((0.1, 0.1), (0.5, 0.5), (0.9, 0.9)), **kw) -> list:
    """Focal outcome from each start: [{"x0", "x_ab", "x_ba", "outcome"}, …]."""
    configs = [embedded_dyad_config(a, b, x0=s, **kw) for s in starts]
    xab, xba, out = _solve(configs)
    return [{"x0": tuple(s), "x_ab": float(xab[k]), "x_ba": float(xba[k]), "outcome": str(np.atleast_1d(out)[k])}
            for k, s in enumerate(starts)]


def embedded_sweep(a, b, axes: dict, starts=((0.1, 0.1), (0.9, 0.9)), **kw) -> dict:
    """Focal outcome over a parameter grid, from each start.

    Returns {"axes", "starts", "x_ab", "x_ba", "outcome", "bistable"}; the arrays have
    shape (len(starts), *grid) and ``bistable`` (shape grid) marks the grid points
    whose outcome depends on the start.
    """
    n_bg = kw.get("n_background", 4)
    names = list(axes)
    values = [list(axes[k]) for k in names]
    configs = []
    for s in starts:
        for combo in itertools.product(*values):
            raw = embedded_dyad_config(a, b, x0=s, **kw)
            for path, v in zip(names, combo):
                _set(raw, path, v, n_bg)
            configs.append(raw)
    xab, xba, out = _solve(configs)
    shape = (len(starts),) + tuple(len(v) for v in values)
    out = np.asarray(out, dtype=object).reshape(shape)
    return {"axes": dict(zip(names, values)), "starts": [tuple(s) for s in starts],
            "x_ab": xab.reshape(shape), "x_ba": xba.reshape(shape), "outcome": out,
            "bistable": np.any(out != out[:1], axis=0)}


def embedded_pairs(names=None, starts=((0.1, 0.1), (0.5, 0.5), (0.9, 0.9)), archetypes=None, **kw) -> dict:
    """Embedded-dyad outcomes for every ordered archetype pair: {(A, B): [per start]}."""
    table = archetype_table(archetypes)
    names = list(names or table)
    pairs = list(itertools.product(names, names))
    configs = [embedded_dyad_config(p, q, x0=s, archetypes=archetypes, **kw) for p, q in pairs for s in starts]
    xab, xba, out = _solve(configs)
    out = np.atleast_1d(out)
    res, k = {}, 0
    for pair in pairs:
        res[pair] = []
        for s in starts:
            res[pair].append({"x0": tuple(s), "x_ab": float(xab[k]), "x_ba": float(xba[k]), "outcome": str(out[k])})
            k += 1
    return res
