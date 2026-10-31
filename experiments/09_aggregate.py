"""Aggregate experiment 09 with population draws as the statistical unit.

For each N, the per-archetype exponent μ is averaged over the simulation seeds of
each population draw, then summarised across the draws (mean, 95% t-interval,
number of draws with μ < 0). A paired contrast compares transactional agents with
the loyal_few and avoidant agents of the same population (butterfly μ is extreme or
undefined at small N, so it is left out of the contrast).

    python experiments/09_aggregate.py results/inverse_regime_populations
"""
import re
import sys
from collections import defaultdict

import numpy as np

from asym.experiments import _ci, analyse_layer_regime, load_run

ARCH = ["butterfly_c", "loyal_few_c", "transactional_c", "avoidant_c"]


def main(run_dir):
    runs = load_run(run_dir)
    rep = analyse_layer_regime(runs)["conditions"]
    by_n = defaultdict(list)
    for cond, v in rep.items():
        n = int(re.match(r"n(\d+)_p\d+", cond).group(1))
        mu = {g: v["by_archetype"].get(g, {"mu": {"mean": np.nan}})["mu"]["mean"] for g in ARCH}
        by_n[n].append({"all": v["mu"]["mean"], "inv": v["inverse_fraction"]["mean"], **mu})
    print("| N | all agents μ | inverse fraction | " + " | ".join(a[:-2] for a in ARCH)
          + " | transactional − mean(loyal_few, avoidant), paired |")
    print("|---|---|---|" + "---|" * len(ARCH) + "---|")
    for n in sorted(by_n):
        rows = by_n[n]

        def cell(key):
            vals = [r[key] for r in rows if np.isfinite(r[key])]
            if not vals:
                return "–"
            c = _ci(vals)
            neg = sum(v < 0 for v in vals)
            return f"{c['mean']:+.2f} [{c['ci'][0]:+.2f}, {c['ci'][1]:+.2f}] ({neg}/{len(vals)} <0)"

        diffs = []
        for r in rows:
            others = [r[a] for a in ("loyal_few_c", "avoidant_c") if np.isfinite(r[a])]
            if np.isfinite(r["transactional_c"]) and others:
                diffs.append(r["transactional_c"] - np.mean(others))
        d = _ci(diffs) if diffs else None
        dcell = f"{d['mean']:+.2f} [{d['ci'][0]:+.2f}, {d['ci'][1]:+.2f}] (n={d['n']})" if d else "–"
        inv = _ci([r["inv"] for r in rows])
        print(f"| {n} | {cell('all')} | {inv['mean']:.2f} | " + " | ".join(cell(a) for a in ARCH) + f" | {dcell} |")


if __name__ == "__main__":
    main(sys.argv[1])
