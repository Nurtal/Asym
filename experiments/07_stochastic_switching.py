"""Experiment 07: noise-induced switching of embedded dyads in the stochastic ABM.

Same set-up as experiment 04 (focal dyad bridging two cliques of M = 4 background
partners of the focal agents' archetypes, built-in archetypes, γ 0.5, a0 0.5), now
simulated with the ABM (``variants.exploration: ties``, no encounters, so a
forgotten tie stays broken). For each pair and focal start x0, many seeds are run
and the dyad closeness (mean of both directions) is read as a two-state signal with
hysteresis bands low = 0.15 / high = 0.6 (``metrics.dyad_switching``).

Reported per (pair, x0):
- P(high), P(broken) at the horizon, and the mean-field prediction from that start
- for runs that reach the high state: P(still high) at t = 250, 500, 1000
- number of high→low and low→high switches per run

    python experiments/07_stochastic_switching.py [--seeds 40] [--workers 8] > results/07_stochastic_switching.md
"""
import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from asym import metrics
from asym.abm.engine import simulate
from asym.meanfield.embedded import embedded_dyad_config, embedded_outcome

PAIRS = [("loyal_few", "loyal_few"), ("avoidant", "avoidant"), ("transactional", "transactional"),
         ("butterfly", "butterfly"), ("butterfly", "transactional")]
STARTS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
LOW, HIGH, M, HORIZON = 0.15, 0.6, 4, 1000.0
G = {"gamma": 0.5, "a0": 0.5}
CHECKS = (250.0, 500.0, 1000.0)


def config(pair, x0):
    raw = embedded_dyad_config(*pair, n_background=M, x0=(x0, x0), globals_=G, horizon=HORIZON)
    raw["variants"] = {"exploration": "ties"}
    raw["simulation"].update(sample_interval=1.0, record_events=False)
    return raw


def run(args):
    pair, x0, seed = args
    sw = metrics.dyad_switching(simulate(config(pair, x0), seed=seed), "A", "B", LOW, HIGH)
    st = sw["state"]
    t = sw["t"]
    reached = bool(np.any(st == "high"))
    still = {}
    if reached:
        k0 = int(np.argmax(st == "high"))
        for c in CHECKS:
            k = int(np.searchsorted(t, c, side="right")) - 1
            still[c] = bool(np.all(st[k0:k + 1] == "high"))  # stayed high without interruption since first reaching it
    n_down = sum(1 for _, a, b in sw["switches"] if a == "high" and b in ("low", "broken"))
    n_up = sum(1 for _, a, b in sw["switches"] if a in ("low", "mid") and b == "high")
    return {"pair": pair, "x0": x0, "seed": seed, "final": sw["final"], "reached_high": reached, "still": still,
            "n_down": n_down, "n_up": n_up, "breakup_time": sw["breakup_time"]}


def mf_prediction(pair):
    out = embedded_outcome(*pair, starts=[(s, s) for s in STARTS], n_background=M, globals_=G, horizon=HORIZON)
    return {s: 0.5 * (d["x_ab"] + d["x_ba"]) for s, d in zip(STARTS, out)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=40)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--json", default="results/07_stochastic_switching.json")
    a = ap.parse_args()
    jobs = [(p, x0, s) for p in PAIRS for x0 in STARTS for s in range(a.seeds)]
    with ProcessPoolExecutor(a.workers) as ex:
        runs = list(ex.map(run, jobs, chunksize=4))
        mf = dict(zip(PAIRS, ex.map(mf_prediction, PAIRS)))
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps({"runs": runs, "mf": {f"{p[0]}-{p[1]}": v for p, v in mf.items()}},
                                       indent=1, default=str))
    for p in PAIRS:
        print(f"### {p[0]} ↔ {p[1]}\n")
        print("| x0 | MF closeness | P(high) end | P(broken) end | P(stay high ≥250 / 500 / 1000 \\| reached) "
              "| mean breakup time | down / up switches per run |")
        print("|---|---|---|---|---|---|---|")
        for x0 in STARTS:
            rs = [r for r in runs if r["pair"] == p and r["x0"] == x0]
            n = len(rs)
            hi = sum(r["final"] == "high" for r in rs) / n
            br = sum(r["final"] == "broken" for r in rs) / n
            reached = [r for r in rs if r["reached_high"]]
            stay = " / ".join(f"{np.mean([r['still'][c] for r in reached]):.2f}" for c in CHECKS) if reached else "–"
            bt = [r["breakup_time"] for r in rs if r["breakup_time"] is not None]
            bts = f"{np.mean(bt):.0f}" if bt else "–"
            print(f"| {x0} | {mf[p][x0]:.2f} | {hi:.2f} | {br:.2f} | {stay} | {bts} | "
                  f"{np.mean([r['n_down'] for r in rs]):.2f} / {np.mean([r['n_up'] for r in rs]):.2f} |")
        print()


if __name__ == "__main__":
    main()
