"""Random-search calibration of the layer sizes towards a Dunbar-like scaling.

Starts from an experiment file (its base config) and scales parameters with common
factors, then scores each candidate by the squared log-distance of the three layer
ratios from ``--target`` (default 3), plus a weak pull of the inner circle towards
``--inner`` (default 4). Candidates run in parallel with one seed each.

Knobs (log-uniform ranges given as JSON, e.g. '{"sB": [0.8, 1.3]}'):
  sB     budget factor on every archetype
  sD     decay-ladder factor on every archetype
  t1..t3 circle thresholds (absolute values)
  snu    openness factor on every archetype

    python experiments/calibrate_layering.py experiments/05_tie_exploration_scaling.yaml \
        --condition n200 --n 24 --ranges '{"t2": [0.5, 0.7]}' --out results/calib.json
"""
from __future__ import annotations

import argparse
import copy
import json
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from asym.abm.engine import simulate
from asym.config import AGENT_DEFAULTS, GLOBAL_DEFAULTS
from asym.experiments import condition_configs, layering_per_run, load_experiment
from asym.model.archetypes import archetype_table


def apply(raw: dict, p: dict) -> dict:
    raw = copy.deepcopy(raw)
    table = archetype_table(raw.get("archetypes"))
    names = list((raw.get("population") or {}).get("composition", {}))
    arch = raw.setdefault("archetypes", {})
    for nm in names:
        c = copy.deepcopy(AGENT_DEFAULTS)
        c.update(table[nm])
        spec = arch.setdefault(nm, {})
        spec["B"] = c["B"] * p.get("sB", 1.0)
        spec["delta"] = (np.asarray(c["delta"], float) * p.get("sD", 1.0)).tolist()
        spec["nu"] = c["nu"] * p.get("snu", 1.0)
    th = list((raw.get("globals") or {}).get("thresholds", GLOBAL_DEFAULTS["thresholds"]))
    for k in range(3):
        th[k] = p.get(f"t{k + 1}", th[k])
    raw.setdefault("globals", {})["thresholds"] = sorted(th)
    return raw


def score(L, target, inner):
    if np.any(~np.isfinite(L)) or np.any(L <= 0):
        return 99.0
    r = L[1:] / L[:-1]
    return float(np.sum(np.log(r / target) ** 2) + 0.5 * np.log(L[0] / inner) ** 2)


def _run(args):
    raw, p, seed, target, inner = args
    t = time.time()
    res = simulate(apply(raw, p), seed=seed)
    L = layering_per_run(res)
    half = len(res.times) // 2
    early = np.mean([_lay(res, k) for k in range(half)], axis=0) if half else L
    late = np.mean([_lay(res, k) for k in range(half, len(res.times))], axis=0) if half else L
    return {**p, "L": L.tolist(), "ratios": (L[1:] / np.maximum(L[:-1], 1e-9)).tolist(),
            "drift": ((late - early) / np.maximum(L, 1e-9)).tolist(), "score": score(L, target, inner),
            "sec": time.time() - t}


def _lay(res, k):
    from asym import metrics
    return metrics.layering(res, at=k)["mean_layer_sizes"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment")
    ap.add_argument("--condition", default=None)
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--ranges", default="{}")
    ap.add_argument("--points", default=None, help="JSON list of explicit candidates (overrides --n/--ranges)")
    ap.add_argument("--target", type=float, default=3.0)
    ap.add_argument("--inner", type=float, default=4.0)
    ap.add_argument("--horizon", type=float, default=None)
    ap.add_argument("--burn-in", type=float, default=None)
    ap.add_argument("--init", default=None, help="JSON init override, e.g. a random start to shorten transients")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    spec = load_experiment(a.experiment)
    configs = condition_configs(spec)
    raw = configs[a.condition or next(iter(configs))]
    if a.horizon:
        raw["simulation"]["horizon"] = a.horizon
    if a.burn_in is not None:
        raw["simulation"]["burn_in"] = a.burn_in
    if a.init:
        raw["init"] = json.loads(a.init)
    raw["simulation"]["record_events"] = False
    if a.points:
        pts = json.loads(a.points)
    else:
        rng = np.random.default_rng(a.seed)
        R = json.loads(a.ranges)
        pts = [{k: float(np.exp(rng.uniform(np.log(lo), np.log(hi)))) for k, (lo, hi) in R.items()} for _ in range(a.n)]
    with ProcessPoolExecutor(a.workers) as ex:
        out = list(ex.map(_run, [(raw, p, 0, a.target, a.inner) for p in pts]))
    out.sort(key=lambda d: d["score"])
    if a.out:
        with open(a.out, "w") as f:
            json.dump(out, f, indent=1)
    for d in out:
        knobs = " ".join(f"{k}={d[k]:.3f}" for k in pts[0])
        print(f"{d['score']:.3f} {knobs} L={np.round(d['L'], 2).tolist()} r={np.round(d['ratios'], 2).tolist()} "
              f"drift={np.round(d['drift'], 3).tolist()} {d['sec']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
