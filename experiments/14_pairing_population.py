"""Experiment 14: the pairing race in the full population (ABM).

Criterion (docs/theory/maintenance-scaling.md §3): equal sharing between ties at
closeness x is unstable iff β_eff (1 − x) > 1, with β_eff ≈ (1 − ε) β (+ acceptance
feedback). In a population this predicts two things:

1. **Gap.** No maintained tie can rest below x_c = 1 − 1/β_eff. The closeness
   distribution should be depleted under x_c, and the high mode should start near
   it.
2. **Pairing.** When the closeness that equal sharing would give, x_ref, falls
   below x_c, agents concentrate on few partners. Their effective number of
   friends drops, and best friends become mutual.

Design: a homogeneous population of N = 100 calibrated transactional agents with
κ = 0, so there is no deficit erosion. Encounters and tie-only exploration are on,
as in experiment 06. Grid: β ∈ {0.5, 1, 1.5, 2, 3} × budget B ∈ {12.5, 3.75, 1.9,
1.0}, 2 seeds; random start, horizon 600, burn-in 300. x_ref(B) is read from the
β = 0.5 run, which is stable everywhere (β_eff < 1). It is the mean closeness of
maintained ties (x ≥ θ_friend).

A second part runs the calibrated mixed population of experiment 10 at B × 1 and
B × 0.3, analysed by profile.

    python experiments/14_pairing_population.py run [--seeds 2] [--workers 8]
    python experiments/14_pairing_population.py report > results/14_pairing_population.md
"""
import argparse
import copy
import importlib.util
import itertools
import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

OUT = Path("results/14_pairing_population.json")
BETAS = [0.5, 1.0, 1.5, 2.0, 3.0]
B_MULTS = [1.0, 0.3, 0.15, 0.08]
EPS = 0.05  # exploration share of the transactional profile
BINS = np.linspace(0.0, 1.0, 51)


def _morris():
    spec = importlib.util.spec_from_file_location("morris", Path(__file__).with_name("10_morris.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def config(kind, beta, b_mult):
    raw = _morris().base_config()
    arch = raw["archetypes"]
    if kind == "homogeneous":
        raw["population"]["composition"] = {"transactional_c": 1.0}
        arch["transactional_c"].update(beta=beta, kappa=0.0, B=arch["transactional_c"]["B"] * b_mult)
    else:
        for spec in arch.values():
            spec["B"] = spec["B"] * b_mult
    return raw


def pairing_metrics(res, theta_friend, theta_strong=0.6):
    """Per-snapshot pairing statistics, averaged over snapshots, by profile."""
    groups = {a["id"]: a.get("archetype") for a in res.config.get("agents", [])}
    gid = [groups.get(a) for a in res.agent_ids]
    N = len(res.agent_ids)
    acc = defaultdict(lambda: defaultdict(list))
    hist = np.zeros(len(BINS) - 1)
    for k in range(len(res.times)):
        s = res.snapshot(k)
        i, j, x = s["i"].astype(int), s["j"].astype(int), s["x"]
        hist += np.histogram(x, BINS)[0]
        top = np.full(N, -1)
        best = np.full(N, -1.0)
        for a, b, v in zip(i, j, x):
            if v > best[a]:
                best[a], top[a] = v, b
        per = defaultdict(list)
        for a, v in zip(i, x):
            per[a].append(v)
        for a in range(N):
            v = np.array(per.get(a, []))
            m = v[v >= theta_friend]
            row = acc[gid[a]]
            row["n_friend"].append(len(m))
            row["n_strong"].append(int((v >= theta_strong).sum()))
            row["n_eff"].append(m.sum() ** 2 / (m ** 2).sum() if len(m) else 0.0)
            row["x_maint"].extend(m.tolist())
            if top[a] >= 0 and best[a] >= theta_friend:
                row["mutual_top"].append(float(top[top[a]] == a))
                row["exclusive"].append(float(top[top[a]] == a and (v >= theta_strong).sum() == 1))
                row["top_share"].append(best[a] / m.sum())
    out = {}
    for g, row in acc.items():
        out[g] = {k: float(np.mean(v)) if len(v) else float("nan") for k, v in row.items()}
    return out, (hist / hist.sum()).tolist()


def _run(job):
    from asym.abm.engine import simulate
    kind, beta, b_mult, seed = job
    raw = config(kind, beta, b_mult)
    res = simulate(raw, seed=seed)
    th = raw["globals"]["thresholds"][0]
    by_group, hist = pairing_metrics(res, th)
    return {"kind": kind, "beta": beta, "b_mult": b_mult, "seed": seed, "by_group": by_group, "hist": hist}


def cmd_run(a):
    jobs = [("homogeneous", b, m, s) for b, m, s in itertools.product(BETAS, B_MULTS, range(a.seeds))]
    jobs += [("mixed", None, m, s) for m, s in itertools.product([1.0, 0.3], range(a.seeds))]
    with ProcessPoolExecutor(a.workers) as ex:
        out = list(ex.map(_run, jobs))
    OUT.write_text(json.dumps(out))


def _mean(rows, key, group):
    return float(np.nanmean([r["by_group"][group][key] for r in rows if group in r["by_group"]]))


def _antimode(h):
    """Location of the minimum of the smoothed density between its low peak and its
    high peak (x > 0.4), or None when there is no interior minimum."""
    d = np.convolve(h, np.ones(3) / 3, mode="same")
    c = 0.5 * (BINS[1:] + BINS[:-1])
    hi = np.flatnonzero(c > 0.4)
    k_hi = hi[np.argmax(d[hi])]
    lo = np.flatnonzero((c > 0.06) & (c < c[k_hi]))
    if not len(lo):
        return None
    k_min = lo[np.argmin(d[lo])]
    return float(c[k_min]) if d[k_min] < 0.8 * d[k_hi] else None


def cmd_report(_):
    out = json.loads(OUT.read_text())
    hom = [r for r in out if r["kind"] == "homogeneous"]
    g = "transactional_c"
    print("## Homogeneous population (transactional, κ = 0, N = 100)\n")
    print("x_ref = mean closeness of maintained ties (x ≥ θ_friend) at β = 0.5. The criterion uses "
          "β_eff = (1 − ε)β, a lower bound that leaves out the acceptance feedback.\n")
    print("| B | β | x_ref | (1−ε)β(1−x_ref) | predicted | friends/agent | strong/agent | effective friends | "
          "top share | mutual best friends | exclusive pairs | x_c = 1 − 1/β_eff | antimode |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for m in B_MULTS:
        ref = [r for r in hom if r["b_mult"] == m and r["beta"] == 0.5]
        x_ref = _mean(ref, "x_maint", g)
        for b in BETAS:
            rs = [r for r in hom if r["b_mult"] == m and r["beta"] == b]
            be = (1 - EPS) * b
            crit = be * (1 - x_ref)
            h = np.mean([r["hist"] for r in rs], axis=0)
            am = _antimode(h)
            xc = 1 - 1 / be if be > 1 else None
            print(f"| {12.5 * m:.3g} | {b} | {x_ref:.2f} | {crit:.2f} | {'pair' if crit > 1 else 'share'} | "
                  f"{_mean(rs, 'n_friend', g):.1f} | {_mean(rs, 'n_strong', g):.1f} | {_mean(rs, 'n_eff', g):.2f} | "
                  f"{_mean(rs, 'top_share', g):.2f} | {_mean(rs, 'mutual_top', g):.2f} | {_mean(rs, 'exclusive', g):.2f} | "
                  f"{'—' if xc is None else f'{xc:.2f}'} | {'—' if am is None else f'{am:.2f}'} |")
    print("\n## Closeness distributions (share of ties per 0.1 bin, pooled snapshots)\n")
    print("| B | β | " + " | ".join(f"{k / 10:.1f}" for k in range(10)) + " |\n|---|---|" + "---|" * 10)
    for m, b in itertools.product(B_MULTS, BETAS):
        h = np.mean([r["hist"] for r in hom if r["b_mult"] == m and r["beta"] == b], axis=0)
        h10 = h.reshape(10, 5).sum(axis=1)
        print(f"| {12.5 * m:.3g} | {b} | " + " | ".join(f"{v:.3f}" for v in h10) + " |")
    mix = [r for r in out if r["kind"] == "mixed"]
    print("\n## Calibrated mixed population (experiment 10 base), by profile\n")
    print("| B × | profile | friends/agent | strong/agent | effective friends | top share | mutual best friends | "
          "exclusive pairs | mean x maintained |")
    print("|---|---|---|---|---|---|---|---|---|")
    for m in (1.0, 0.3):
        rs = [r for r in mix if r["b_mult"] == m]
        for grp in sorted(rs[0]["by_group"]):
            print(f"| {m} | {grp.replace('_c', '')} | {_mean(rs, 'n_friend', grp):.1f} | {_mean(rs, 'n_strong', grp):.1f} | "
                  f"{_mean(rs, 'n_eff', grp):.2f} | {_mean(rs, 'top_share', grp):.2f} | "
                  f"{_mean(rs, 'mutual_top', grp):.2f} | {_mean(rs, 'exclusive', grp):.2f} | "
                  f"{_mean(rs, 'x_maint', grp):.2f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    {"run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
