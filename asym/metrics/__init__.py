"""Research observables computed from a ``SimulationResult`` (pure functions).

All metrics use only post-burn-in data. Samples start at the burn-in by
construction, and events are filtered to ``t >= burn_in``. ``at`` selects a sample
index; the default is the last one.
"""
from __future__ import annotations

import math

import networkx as nx
import numpy as np

from asym.result import SimulationResult

N_CIRCLES = 4


def _events(res: SimulationResult, *types):
    b = res.burn_in
    return [e for e in res.events if e["type"] in types and e["t"] >= b - 1e-12]


def _snap(res, at):
    if len(res.times) == 0:
        return {k: np.array([]) for k in ("t", "i", "j", "x", "r", "o", "circle")}
    return res.snapshot(at if at >= 0 else len(res.times) + at)


# ------------------------------------------------------------------ layering
def circle_sizes(res: SimulationResult, at: int = -1) -> np.ndarray:
    """(N, 4) number of ties of each agent in each circle (column 0 = acquaintance)."""
    n = len(res.agent_ids)
    out = np.zeros((n, N_CIRCLES), dtype=int)
    s = _snap(res, at)
    if s["i"].size:
        np.add.at(out, (s["i"].astype(int), s["circle"].astype(int) - 1), 1)
    return out


def layer_sizes(res: SimulationResult, at: int = -1) -> np.ndarray:
    """(N, 4) cumulative layer sizes, from the inner circle outwards.

    Column 0 = inner circle, 1 = inner + close friends, 2 = … + friends, 3 = all ties.
    This is the Dunbar convention, where each layer includes the inner ones.
    """
    return np.cumsum(circle_sizes(res, at)[:, ::-1], axis=1)


def layering(res: SimulationResult, at: int = -1) -> dict:
    """Mean cumulative layer sizes and the ratios between consecutive layers."""
    L = layer_sizes(res, at)
    mean = L.mean(axis=0) if L.size else np.zeros(N_CIRCLES)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = np.where(mean[:-1] > 0, mean[1:] / np.where(mean[:-1] > 0, mean[:-1], 1), np.nan)
    return {"mean_layer_sizes": mean, "ratios": ratios}


def layering_by_archetype(res: SimulationResult, at: int = -1) -> dict:
    """{archetype: mean cumulative layer sizes (4,)} over the agents of each archetype.

    Agents without an archetype are grouped under ``None``.
    """
    agents = {a["id"]: a.get("archetype") for a in res.config.get("agents", [])}
    groups = [agents.get(a) for a in res.agent_ids]
    L = layer_sizes(res, at)
    return {g: L[[k for k, gk in enumerate(groups) if gk == g]].mean(axis=0) for g in dict.fromkeys(groups)}


def dyad_switching(res: SimulationResult, i, j, low: float, high: float) -> dict:
    """Two-state (hysteretic) reading of a dyad's sampled closeness, and its switches.

    The dyad closeness is the mean of x_ij and x_ji, with a missing tie counted as 0.
    The state is ``high`` once the closeness reaches ``high``, and ``low`` once it
    falls to ``low`` or below. In between, the previous state is kept (``mid`` before
    either band is reached). ``broken`` means both ties are gone; it is absorbing in a
    population without encounters, but a later sample can leave it if the ties
    reform. Returns {"t", "closeness", "state", "switches": [(t, from, to)],
    "breakup_time", "final"}.
    """
    ii, jj = res.index(i), res.index(j)
    T = len(res.times)
    tidx = {t: k for k, t in enumerate(res.times)}
    xij, xji = np.zeros(T), np.zeros(T)
    present = np.zeros(T, dtype=bool)
    for a, b, arr in ((ii, jj, xij), (jj, ii, xji)):
        m = (res.ties["i"] == a) & (res.ties["j"] == b)
        for t, x in zip(res.ties["t"][m], res.ties["x"][m]):
            arr[tidx[t]] = x
            present[tidx[t]] = True
    closeness = 0.5 * (xij + xji)
    states, switches, cur = [], [], "mid"
    for k in range(T):
        if not present[k]:
            new = "broken"
        elif closeness[k] >= high:
            new = "high"
        elif closeness[k] <= low:
            new = "low"
        else:
            new = cur if cur != "broken" else "mid"
        if new != cur and k > 0:
            switches.append((float(res.times[k]), cur, new))
        cur = new
        states.append(cur)
    broken = [float(res.times[k]) for k in range(T) if not present[k]]
    return {"t": res.times.copy(), "closeness": closeness, "state": np.array(states, dtype=object),
            "switches": switches, "breakup_time": broken[0] if broken else None,
            "final": states[-1] if states else None}


# ----------------------------------------------------------------- asymmetry
def asymmetry(res: SimulationResult, at: int = -1) -> dict:
    """Asymmetry of the dyads present at sample ``at``.

    - ``abs_diff``: |x_ij − x_ji| for each mutual dyad
    - ``circle_mismatch``: fraction of mutual dyads whose two ties sit in different circles
    - ``one_sided``: fraction of dyads where only one direction exists
    """
    s = _snap(res, at)
    ties = {(int(i), int(j)): (float(x), int(c)) for i, j, x, c in zip(s["i"], s["j"], s["x"], s["circle"])}
    diffs, mismatch, one_sided, seen = [], 0, 0, set()
    for (i, j), (x, c) in ties.items():
        key = (min(i, j), max(i, j))
        if key in seen:
            continue
        seen.add(key)
        other = ties.get((j, i))
        if other is None:
            one_sided += 1
            continue
        diffs.append(abs(x - other[0]))
        mismatch += c != other[1]
    n_mutual = len(diffs)
    return {
        "abs_diff": np.array(diffs),
        "circle_mismatch": mismatch / n_mutual if n_mutual else math.nan,
        "one_sided": one_sided / len(seen) if seen else math.nan,
        "n_dyads": len(seen),
    }


def reciprocity_ratios(res: SimulationResult, at: int = -1, o0: float | None = None) -> np.ndarray:
    """Perceived reciprocity ratio q = (r + o0)/(o + o0) of every tie present."""
    o0 = o0 if o0 is not None else res.config.get("globals", {}).get("o0", 0.5)
    s = _snap(res, at)
    return (s["r"] + o0) / (s["o"] + o0)


# -------------------------------------------------------------------- churn
def tie_lifetimes(res: SimulationResult) -> dict:
    """Lifetimes of directed ties: ``completed`` (created then forgotten) and ``censored``.

    Ties present at t = 0 count as created at 0. Censored ties are still alive at the
    last sample and are measured up to it.
    """
    t_end = float(res.times[-1]) if len(res.times) else 0.0
    born = {}
    if len(res.times) and res.times[0] == 0.0:
        s = res.snapshot(0)
        born = {(int(i), int(j)): 0.0 for i, j in zip(s["i"], s["j"])}
    completed = []
    idx = {a: k for k, a in enumerate(res.agent_ids)}
    for e in res.events:
        if e["type"] not in ("tie_created", "forget"):
            continue
        key = (idx[e["i"]], idx[e["j"]])
        if e["type"] == "tie_created":
            born[key] = e["t"]
        elif key in born:
            completed.append(e["t"] - born.pop(key))
    censored = [t_end - t0 for t0 in born.values()]
    return {"completed": np.array(completed), "censored": np.array(censored)}


def churn(res: SimulationResult) -> dict:
    """Forgetting and circle-transition rates per existing tie per unit time (post burn-in)."""
    if len(res.times) < 2:
        return {"forget_rate": math.nan, "transition_rate": math.nan, "creation_rate": math.nan}
    span = float(res.times[-1] - res.times[0])
    n_ties = np.mean([np.sum(res.ties["t"] == t) for t in res.times])
    exposure = n_ties * span
    count = lambda *types: len([e for e in _events(res, *types) if e["t"] <= res.times[-1]])  # noqa: E731
    if exposure <= 0:
        return {"forget_rate": math.nan, "transition_rate": math.nan, "creation_rate": math.nan}
    return {
        "forget_rate": count("forget") / exposure,
        "transition_rate": count("promote", "demote") / exposure,
        "creation_rate": count("tie_created") / span / max(len(res.agent_ids), 1),
    }


# --------------------------------------------------------------- resilience
def shock_resilience(res: SimulationResult) -> dict:
    """Recovery after tie shocks.

    - ``recovery_times``: per shock, the time until the tie's closeness first returns
      to its pre-shock level at a sample (NaN if it never does or the tie is forgotten)
    - ``drop_probability``: fraction of shocks followed by a demotion or by forgetting
      of the shocked tie before it recovers
    """
    shocks = _events(res, "shock_tie")
    rec, drops = [], 0
    moves = [e for e in res.events if e["type"] in ("demote", "forget")]
    for sh in shocks:
        tr = res.trajectory(sh["i"], sh["j"])
        later = tr["t"] > sh["t"]
        ok = np.nonzero(later & (tr["x"] >= sh["x_before"] - 1e-12))[0]
        t_rec = float(tr["t"][ok[0]]) if ok.size else math.inf
        rec.append(t_rec - sh["t"] if ok.size else math.nan)
        if any(m["i"] == sh["i"] and m["j"] == sh["j"] and sh["t"] <= m["t"] < t_rec for m in moves):
            drops += 1
    return {
        "recovery_times": np.array(rec),
        "drop_probability": drops / len(shocks) if shocks else math.nan,
        "n_shocks": len(shocks),
    }


# ----------------------------------------------------------- isolation trap
def locked_budget_fraction(res: SimulationResult) -> np.ndarray:
    """(S, N) fraction of each agent's capacity locked in pending invitations."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(res.capacity > 0, res.pending_budget / res.capacity, 0.0)


def isolation_trap(res: SimulationResult, threshold: float = 0.5) -> np.ndarray:
    """(S,) fraction of agents trapped at each sample.

    An agent is trapped when at least ``threshold`` of its capacity is locked in
    pending invitations and less than one free slot remains.
    """
    if res.budget.size == 0:
        return np.zeros(len(res.times))
    locked = locked_budget_fraction(res) >= threshold
    no_slot = (res.capacity - res.budget) < 1.0 - 1e-9
    return (locked & no_slot).mean(axis=1)


# ------------------------------------------------------------------ network
def gini(values) -> float:
    v = np.sort(np.asarray(values, dtype=float))
    n = v.size
    if n == 0 or v.sum() == 0:
        return 0.0
    return float((2 * np.arange(1, n + 1) - n - 1).dot(v) / (n * v.sum()))


def social_graph(res: SimulationResult, at: int = -1, min_circle: int = 1, mutual: bool = False) -> nx.Graph:
    """Undirected graph of ties with circle ≥ min_circle (both directions required if ``mutual``)."""
    s = _snap(res, at)
    G = nx.Graph()
    G.add_nodes_from(range(len(res.agent_ids)))
    directed = {(int(i), int(j)) for i, j, c in zip(s["i"], s["j"], s["circle"]) if c >= min_circle}
    for i, j in directed:
        if not mutual or (j, i) in directed:
            G.add_edge(i, j)
    return G


def network_metrics(res: SimulationResult, at: int = -1) -> dict:
    """Clustering, modularity (greedy), and inequality of close-tie degree."""
    G = social_graph(res, at)
    n_edges = G.number_of_edges()
    clustering = nx.average_clustering(G) if G.number_of_nodes() else math.nan
    if n_edges:
        comms = nx.community.greedy_modularity_communities(G)
        modularity = nx.community.modularity(G, comms)
    else:
        comms, modularity = [], math.nan
    close = circle_sizes(res, at)[:, 2:].sum(axis=1)  # close friends + inner circle
    return {
        "n_edges": n_edges,
        "mean_degree": 2 * n_edges / G.number_of_nodes() if G.number_of_nodes() else math.nan,
        "clustering": clustering,
        "modularity": modularity,
        "n_communities": len(comms),
        "close_degree_gini": gini(close),
    }


__all__ = [
    "circle_sizes", "layer_sizes", "layering", "asymmetry", "reciprocity_ratios", "tie_lifetimes", "churn",
    "shock_resilience", "locked_budget_fraction", "isolation_trap", "gini", "social_graph", "network_metrics",
]
