"""Experiment 11: do layer sizes depend on budget B, gain η and decay δ only through Q = η·B/δ?

Same base as experiment 10 (calibrated model of experiment 06, N = 100, random
start, horizon 600, burn-in 300). Q is scaled by q ∈ {0.5, 0.71, 1, 1.41, 2} along
four routes: B alone, η alone, δ alone (δ × 1/q), and mixed (B × √q, δ × 1/√q). If
the layers depend only on Q, the four routes give the same layers at the same q.

    python experiments/11_maintenance_collapse.py [--seeds 2] [--workers 8] > results/11_maintenance_collapse.md
"""
import argparse
import importlib.util
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from asym import metrics
from asym.abm.engine import simulate
from asym.experiments import _agent_counts
from asym.sensitivity import Factor, apply_factors

_spec = importlib.util.spec_from_file_location("morris", Path(__file__).with_name("10_morris.py"))
_morris = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_morris)

QS = [0.5, 2 ** -0.5, 1.0, 2 ** 0.5, 2.0]
ETA0 = 0.09


def routes(q):
    s = math.sqrt(q)
    return {"B": {"B": q, "delta": 1.0, "eta": ETA0}, "eta": {"B": 1.0, "delta": 1.0, "eta": ETA0 * q},
            "delta": {"B": 1.0, "delta": 1.0 / q, "eta": ETA0}, "mixed": {"B": s, "delta": 1.0 / s, "eta": ETA0}}


def config(m):
    facs = [Factor("B", "archetypes.B", m["B"], m["B"]), Factor("delta", "archetypes.delta", m["delta"], m["delta"]),
            Factor("eta", "globals.eta", m["eta"], m["eta"])]
    return apply_factors(_morris.base_config(), facs, [0.0, 0.0, 0.0])


def run(args):
    q, route, m, seed = args
    res = simulate(config(m), seed=seed)
    K = len(res.times)
    L = np.mean([metrics.layering(res, at=k)["mean_layer_sizes"] for k in range(K)], axis=0)
    mu = metrics.layer_exponent(_agent_counts(res).mean(axis=0))
    hi = np.mean([np.mean(res.snapshot(k)["x"] >= 0.75) for k in range(K)])
    return {"q": q, "route": route, "seed": seed, "L": L.tolist(), "mu": mu, "high": float(hi)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    jobs = []
    for q in QS:
        for route, m in routes(q).items():
            if q == 1.0 and route != "B":
                continue  # all routes coincide at q = 1
            jobs += [(q, route, m, s) for s in range(a.seeds)]
    with ProcessPoolExecutor(a.workers) as ex:
        out = list(ex.map(run, jobs))
    Path("results").mkdir(exist_ok=True)
    Path("results/11_maintenance_collapse.json").write_text(json.dumps(out, indent=1))
    names = ["inner", "+close", "+friends", "all", "μ", "high-mode share"]
    for k, name in enumerate(names):
        print(f"\n### {name}\n\n| q | " + " | ".join(routes(1)) + " | spread (max/min) |\n|---|---|---|---|---|---|")
        for q in QS:
            cells, vals = [], []
            for route in routes(q):
                rs = [r for r in out if r["q"] == q and (r["route"] == route or q == 1.0)]
                v = np.mean([(r["L"][k] if k < 4 else r["mu"] if k == 4 else r["high"]) for r in rs])
                cells.append(f"{v:.3g}")
                vals.append(v)
            vals = np.array(vals)
            spread = f"{vals.max() / vals.min():.2f}" if np.all(vals > 0) else f"Δ={vals.max() - vals.min():.2f}"
            print(f"| {q:.2f} | " + " | ".join(cells) + f" | {spread} |")


if __name__ == "__main__":
    main()
