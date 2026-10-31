"""Reproducible engine benchmark (ticket 14).

    python benchmarks/bench_engine.py [--n 1000] [--horizon 50] [--seed 0] [--profile]

A mixed-archetype population (25% of each built-in archetype) starts from a random
acquaintance network. The script prints wall-clock time, events processed, events
per second and the network size at the end.
"""
from __future__ import annotations

import argparse
import cProfile
import io
import pstats
import time

from asym.abm.engine import Engine
from asym.config import load_config


def config(n: int, horizon: float) -> dict:
    return {
        "population": {"composition": {"butterfly": 0.25, "loyal_few": 0.25, "transactional": 0.25, "avoidant": 0.25},
                       "size": n, "noise": 0.15, "seed": 0},
        "globals": {"gamma": 0.5, "a0": 0.5},
        "init": {"mode": "random", "density": 10.0 / n, "x_range": [0.1, 0.5]},
        "simulation": {"horizon": horizon, "sample_interval": horizon / 5, "record_events": False},
    }


class CountingEngine(Engine):
    n_events = 0

    def _rate_components(self):
        bounds, handlers = super()._rate_components()
        self.n_events += 1
        return bounds, handlers


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--horizon", type=float, default=50.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--profile", action="store_true")
    args = ap.parse_args(argv)
    eng = CountingEngine(load_config(config(args.n, args.horizon)), args.seed)
    prof = cProfile.Profile() if args.profile else None
    t0 = time.perf_counter()
    if prof:
        prof.enable()
    res = eng.run()
    if prof:
        prof.disable()
    wall = time.perf_counter() - t0
    n_ties = res.snapshot(len(res.times) - 1)["i"].size
    print(f"N={args.n} horizon={args.horizon} seed={args.seed}")
    print(f"wall-clock: {wall:.2f} s | loop iterations (events + scheduled): {eng.n_events} "
          f"| events/s: {eng.n_events / wall:,.0f} | ties at end: {n_ties}")
    if prof:
        s = io.StringIO()
        pstats.Stats(prof, stream=s).sort_stats("tottime").print_stats(15)
        print(s.getvalue())


if __name__ == "__main__":
    main()
