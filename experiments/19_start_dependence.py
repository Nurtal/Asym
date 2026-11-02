"""Experiment 19: does the calibrated model (k = 1) depend on its initial state?

Experiment 18 found, on one draw and one seed, an inner circle of 2.16 from an empty start
and 1.93 from a random start at t = 3000. This reruns the layers block of experiment 15
(N = 100, 5 draws, 3 seeds, window 1000-1500) from the random start of experiments 10, 11,
14 and 17, and compares it with the empty-start runs of experiment 15, paired by draw.

Runs one job at a time, appending to a log, and a rerun skips what is done.

    python experiments/19_start_dependence.py run
    python experiments/19_start_dependence.py report > results/19_start_dependence/report.md
"""
import argparse
import importlib.util
import json
import math
import time
from pathlib import Path

import numpy as np
from scipy import stats

OUT = Path("results/19_start_dependence")
RUNS = OUT / "runs.jsonl"
ROBUST = Path("results/15_robustness/runs.jsonl")
HERE = Path(__file__).parent
RANDOM_START = {"mode": "random", "density": 0.2, "x_range": [0.05, 0.3]}
DRAWS, SEEDS = range(5), range(3)


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def random_start(raw):
    raw["init"] = dict(RANDOM_START)
    return raw


def cmd_run(_):
    m15 = _load("m15", "15_robustness.py")
    OUT.mkdir(parents=True, exist_ok=True)
    done = {(r["pop"], r["seed"]) for r in _rows(RUNS)} if RUNS.exists() else set()
    for p in DRAWS:
        for s in SEEDS:
            if (p, s) in done:
                continue
            t = time.time()
            r = m15.run_job({"block": "layers", "cond": "n100", "pop": p, "seed": s}, transform=random_start)
            with RUNS.open("a") as fh:
                fh.write(json.dumps(r) + "\n")
            print(f"draw {p} seed {s} {np.round(r['layers'], 2).tolist()} {time.time() - t:.0f}s", flush=True)


def _by_draw(rows, get):
    by = {}
    for r in rows:
        by.setdefault(r["pop"], []).append(get(r))
    return {p: float(np.mean(v)) for p, v in by.items()}


def cmd_report(_):
    rand = _rows(RUNS)
    empty = [r for r in _rows(ROBUST) if r["block"] == "layers" and r["cond"] == "n100"]
    gets = {"inner": lambda r: r["layers"][0], "+close": lambda r: r["layers"][1],
            "+friends": lambda r: r["layers"][2], "all": lambda r: r["layers"][3],
            "mu": lambda r: r["mu"], "unreciprocated": lambda r: r["unreciprocated"]}
    print("# Experiment 19: start dependence at k = 1\n")
    print(f"{len(rand)} random-start runs, {len(empty)} empty-start runs. Differences are random − empty, "
          "paired by draw, with 95% t-intervals over draws.\n")
    print("| measure | empty | random | difference | relative | p |\n|---|---|---|---|---|---|")
    for name, g in gets.items():
        a, b = _by_draw(rand, g), _by_draw(empty, g)
        d = np.array([a[p] - b[p] for p in sorted(a)])
        half = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / math.sqrt(len(d))
        mb = np.mean(list(b.values()))
        print(f"| {name} | {mb:.3f} | {np.mean(list(a.values())):.3f} | {d.mean():+.3f} ± {half:.3f} | "
              f"{d.mean() / mb:+.1%} | {stats.ttest_1samp(d, 0).pvalue:.2g} |")
    print("\nInner circle by draw:\n\n| draw | empty | random |\n|---|---|---|")
    a, b = _by_draw(rand, gets["inner"]), _by_draw(empty, gets["inner"])
    for p in sorted(a):
        print(f"| {p} | {b[p]:.2f} | {a[p]:.2f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    a = ap.parse_args()
    {"run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
