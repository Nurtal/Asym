"""Experiment 15: robustness of the main claims across simulation seeds and population draws.

The unit of replication is the **population draw** (population.seed): each draw
samples new individual parameters around the archetype centres. Several simulation
seeds are run per draw. The report gives, per claim:

- the mean over draws (each draw averaged over its seeds) and its 95% t-interval;
- the within-draw seed SD;
- the share of variance due to draws.

Blocks:

- ``layers``: calibrated layering (exp 06) at N = 100 and 200, 5 draws × 3 seeds,
  with the asymmetry metrics of exp 12 computed on the same runs.
- ``asymmetry``: the exp 12 counterfactuals, 4 draws × 2 seeds, plus
  ``misperception_centred``. That condition uses σ_p = 0.5 with π = −σ_p²/2 for
  every agent, so that the perceived investment keeps mean 1. It removes the
  confound of exp 12.
- ``collapse``: the exp 11 routes, 2 draws × 3 seeds.
- ``pairing``: key cells of exp 14, the mixed population with 4 draws × 2 seeds and
  the homogeneous cells with 2 draws × 2 seeds.

    python experiments/15_robustness.py run [--blocks layers asymmetry collapse pairing] [--workers 1]
    python experiments/15_robustness.py report > results/15_robustness/report.md

Runs are appended to ``results/15_robustness/runs.jsonl`` as they finish. A rerun
skips the jobs already there.
"""
import argparse
import copy
import importlib.util
import itertools
import json
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from scipy import stats

OUT = Path("results/15_robustness")
RUNS = OUT / "runs.jsonl"
HERE = Path(__file__).parent
PAIRS = ["butterfly_c->transactional_c", "butterfly_c->avoidant_c", "loyal_few_c->transactional_c",
         "transactional_c->butterfly_c"]


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ jobs
def jobs_for(block):
    out = []
    if block == "layers":
        for n, p, s in itertools.product([200, 100], range(5), range(3)):
            out.append({"block": block, "cond": f"n{n}", "pop": p, "seed": s})
    elif block == "asymmetry":
        conds = ["no_deficit", "same_allocation", "same_decay", "average_only", "misperception",
                 "misperception_centred"]
        for c, p, s in itertools.product(conds, range(4), range(2)):
            out.append({"block": block, "cond": c, "pop": p, "seed": s})
    elif block == "collapse":
        m11 = _load("m11", "11_maintenance_collapse.py")
        for q in m11.QS:
            for route in m11.routes(q):
                if q == 1.0 and route != "B":
                    continue
                for p, s in itertools.product(range(2), range(3)):
                    out.append({"block": block, "cond": f"{route}@{q:.3f}", "q": q, "route": route, "pop": p, "seed": s})
    elif block == "pairing":
        for m, p, s in itertools.product([1.0, 0.3], range(4), range(2)):
            out.append({"block": block, "cond": f"mixed_B{m}", "kind": "mixed", "beta": None, "b_mult": m,
                        "pop": p, "seed": s})
        for (m, b), p, s in itertools.product([(1.0, 3.0), (0.3, 3.0), (0.15, 0.5), (0.15, 1.5), (0.15, 3.0)],
                                              range(2), range(2)):
            out.append({"block": block, "cond": f"homog_B{m}_beta{b}", "kind": "homogeneous", "beta": b,
                        "b_mult": m, "pop": p, "seed": s})
    return out


def job_key(j):
    return f"{j['block']}|{j['cond']}|{j['pop']}|{j['seed']}"


def build_config(j):
    from asym.experiments import condition_configs, load_experiment
    b = j["block"]
    if b == "layers":
        raw = condition_configs(load_experiment(HERE / "06_dunbar_calibrated_scaling.yaml"))[j["cond"]]
    elif b == "asymmetry":
        conds = condition_configs(load_experiment(HERE / "12_asymmetry_mechanisms.yaml"))
        if j["cond"] == "misperception_centred":
            raw = copy.deepcopy(conds["misperception"])
            for spec in raw["archetypes"].values():
                spec["pi"] = -0.5 * 0.5 ** 2
        else:
            raw = conds[j["cond"]]
    elif b == "collapse":
        m11 = _load("m11", "11_maintenance_collapse.py")
        raw = m11.config(m11.routes(j["q"])[j["route"]])
    else:
        raw = _load("m14", "14_pairing_population.py").config(j["kind"], j["beta"], j["b_mult"])
    raw = copy.deepcopy(raw)
    raw["population"]["seed"] = j["pop"]
    return raw


# ------------------------------------------------------------------ one run
def run_job(j, transform=None, extra=None):
    """Run one job. ``transform(raw)`` changes the config before the run, and
    ``extra(res, out)`` adds measures to the result."""
    from asym import metrics
    from asym.abm.engine import simulate
    from asym.experiments import _agent_counts, layering_per_run
    raw = build_config(j)
    if transform is not None:
        raw = transform(raw)
    res = simulate(raw, seed=j["seed"])
    out = dict(j)
    K = len(res.times)
    L = layering_per_run(res)
    out["layers"] = L.tolist()
    out["mu"] = float(metrics.layer_exponent(_agent_counts(res).mean(axis=0)))
    if j["block"] in ("layers", "asymmetry"):
        fr = [metrics.friendship_reciprocity(res, at=k) for k in range(K)]
        out["unreciprocated"] = float(np.nanmean([f["unreciprocated"] for f in fr]))
        out["correlation"] = float(np.nanmean([f["correlation"] for f in fr]))
        pairs = {}
        for f in fr:
            for (ga, gb), d in f["by_pair"].items():
                pairs.setdefault(f"{ga}->{gb}", []).append(d["unreciprocated"])
        out["pairs"] = {k: float(np.nanmean(v)) if np.isfinite(v).any() else None
                        for k, v in pairs.items() if k in PAIRS}
        by = {}
        for k in range(K):
            for g, v in metrics.layering_by_archetype(res, at=k).items():
                by.setdefault(str(g), []).append(v)
        out["by_archetype"] = {g: np.mean(v, axis=0).tolist() for g, v in by.items()}
    if j["block"] == "collapse":
        out["high"] = float(np.mean([np.mean(res.snapshot(k)["x"] >= 0.75) for k in range(K)]))
    if j["block"] == "pairing":
        m14 = _load("m14", "14_pairing_population.py")
        by_group, _ = m14.pairing_metrics(res, raw["globals"]["thresholds"][0])
        out["pairing"] = by_group
    if extra is not None:
        extra(res, out)
    return out


def cmd_run(a):
    OUT.mkdir(parents=True, exist_ok=True)
    done = set()
    if RUNS.exists():
        done = {job_key(json.loads(line)) for line in RUNS.read_text().splitlines() if line.strip()}
    jobs = [j for b in a.blocks for j in jobs_for(b) if job_key(j) not in done]
    # large populations first, for load balancing
    jobs.sort(key=lambda j: j["cond"] != "n200")
    print(f"{len(jobs)} jobs to run ({len(done)} already done)", flush=True)
    with ProcessPoolExecutor(a.workers) as ex, RUNS.open("a") as fh:
        futs = {ex.submit(run_job, j): j for j in jobs}
        for k, f in enumerate(as_completed(futs)):
            try:
                fh.write(json.dumps(f.result()) + "\n")
                fh.flush()
            except Exception as e:  # keep going; the job stays undone and a rerun retries it
                print(f"failed {job_key(futs[f])}: {e!r}", flush=True)
            if (k + 1) % 10 == 0:
                print(f"{k + 1}/{len(jobs)}", flush=True)


# ------------------------------------------------------------------ report
def summarise(rows, get):
    """Draw-level summary of a scalar: mean, 95% CI over draws, within-draw seed SD,
    share of variance between draws."""
    by_pop = {}
    for r in rows:
        v = get(r)
        if v is not None and np.isfinite(v):
            by_pop.setdefault(r["pop"], []).append(float(v))
    means = np.array([np.mean(v) for v in by_pop.values()])
    n = len(means)
    if n == 0:
        return None
    mean = float(means.mean())
    half = float(stats.t.ppf(0.975, n - 1) * means.std(ddof=1) / math.sqrt(n)) if n > 1 else math.nan
    within = [np.var(v, ddof=1) for v in by_pop.values() if len(v) > 1]
    w = float(np.mean(within)) if within else math.nan
    k = np.mean([len(v) for v in by_pop.values()])
    between = max(0.0, float(means.var(ddof=1)) - w / k) if n > 1 and np.isfinite(w) else math.nan
    share = between / (between + w) if np.isfinite(between) and (between + w) > 0 else math.nan
    return {"mean": mean, "half": half, "n_pop": n, "seed_sd": math.sqrt(w) if np.isfinite(w) else math.nan,
            "pop_share": share, "draws": means.tolist()}


def fmt(s, digits=3):
    """Mean ± 95% half-width. With two draws the t-interval is uninformative
    (t = 12.7), so the two draw means are shown instead."""
    if s is None:
        return "—"
    if s["n_pop"] == 2:
        a, b = s["draws"]
        return f"{s['mean']:.{digits}g} [{a:.{digits}g}, {b:.{digits}g}]"
    return f"{s['mean']:.{digits}g} ± {s['half']:.2g}"


def fmt_full(s, digits=3):
    if s is None:
        return "— | — | —"
    return f"{fmt(s, digits)} | {s['seed_sd']:.2g} | {s['pop_share']:.2f}"


def paired_difference(rows, rows_base, get):
    """Per-draw difference from the baseline over the draws they share: mean, 95%
    half-width, p of a one-sample t-test."""
    def draws(rs):
        by = {}
        for r in rs:
            by.setdefault(r["pop"], []).append(get(r))
        return {p: float(np.mean(v)) for p, v in by.items()}
    a, b = draws(rows), draws(rows_base)
    d = np.array([a[p] - b[p] for p in sorted(a) if p in b])
    half = float(stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / math.sqrt(len(d)))
    return float(d.mean()), half, float(stats.ttest_1samp(d, 0.0).pvalue)


def cmd_report(_):
    rows = [json.loads(line) for line in RUNS.read_text().splitlines() if line.strip()]
    by = lambda b, c: [r for r in rows if r["block"] == b and r["cond"] == c]  # noqa: E731
    names = ["inner", "+close", "+friends", "all"]

    print("# Experiment 15: robustness across seeds and population draws\n")
    print("Mean ± half-width of the 95% t-interval over population draws (each draw averaged over its seeds); "
          "seed SD = within-draw SD; draw share = share of the variance due to the population draw.\n")

    print("## 1. Calibrated layering (exp 06)\n")
    for c in ("n100", "n200"):
        rs = by("layers", c)
        if not rs:
            continue
        print(f"### {c} ({len({r['pop'] for r in rs})} draws, {len(rs)} runs)\n")
        print("| quantity | mean ± CI | seed SD | draw share |\n|---|---|---|---|")
        for k, nm in enumerate(names):
            print(f"| {nm} | {fmt_full(summarise(rs, lambda r: r['layers'][k]))} |")
        for k in range(3):
            print(f"| ratio {k + 1} | {fmt_full(summarise(rs, lambda r: r['layers'][k + 1] / r['layers'][k] if r['layers'][k] > 0 else None))} |")
        print(f"| μ | {fmt_full(summarise(rs, lambda r: r['mu']))} |")
        print(f"| unreciprocated friendships | {fmt_full(summarise(rs, lambda r: r['unreciprocated']))} |")
        print(f"| correlation x_ij, x_ji | {fmt_full(summarise(rs, lambda r: r['correlation']))} |")
        print()
        groups = sorted({g for r in rs for g in r["by_archetype"]})
        print("Cumulative layers by profile:\n")
        print("| profile | " + " | ".join(names) + " |\n|---|---|---|---|---|")
        for g in groups:
            cells = [fmt(summarise(rs, lambda r: r["by_archetype"].get(g, [None] * 4)[k])) for k in range(4)]
            print(f"| {g.replace('_c', '')} | " + " | ".join(cells) + " |")
        print()
    a = by("layers", "n100")
    if a:
        print("N-independence (n200 − n100), Welch test on draw means:\n")
        print("| layer | n100 | n200 | p |\n|---|---|---|---|")
        for k, nm in enumerate(names):
            m1 = [np.mean([r["layers"][k] for r in by("layers", "n100") if r["pop"] == p]) for p in range(5)]
            m2 = [np.mean([r["layers"][k] for r in by("layers", "n200") if r["pop"] == p]) for p in range(5)]
            m1 = [v for v in m1 if np.isfinite(v)]
            m2 = [v for v in m2 if np.isfinite(v)]
            if len(m1) > 1 and len(m2) > 1:
                p = stats.ttest_ind(m1, m2, equal_var=False).pvalue
                print(f"| {nm} | {np.mean(m1):.3g} | {np.mean(m2):.3g} | {p:.2g} |")
        print()

    print("## 2. Asymmetry counterfactuals (exp 12), N = 100\n")
    print("Baseline = the n100 runs of block 1.\n")
    print("| condition | unreciprocated | seed SD | draw share | correlation | " +
          " | ".join(p.replace("_c", "") for p in PAIRS) + " |")
    print("|---|---|---|---|---|" + "---|" * len(PAIRS))
    for c in ["baseline", "no_deficit", "same_allocation", "same_decay", "average_only", "misperception",
              "misperception_centred"]:
        rs = by("layers", "n100") if c == "baseline" else by("asymmetry", c)
        if not rs:
            continue
        pcells = [fmt(summarise(rs, lambda r: (r.get("pairs") or {}).get(p))) for p in PAIRS]
        print(f"| {c} | {fmt_full(summarise(rs, lambda r: r['unreciprocated']))} | "
              f"{fmt(summarise(rs, lambda r: r['correlation']))} | " + " | ".join(pcells) + " |")
    print()
    base = by("layers", "n100")
    conds = [c for c in ["no_deficit", "same_allocation", "same_decay", "average_only", "misperception",
                         "misperception_centred"] if by("asymmetry", c)]
    if base and conds:
        print("Unreciprocated share, difference from the baseline paired by population draw:\n")
        print("| condition | difference ± CI | p |\n|---|---|---|")
        for c in conds:
            m, h, p = paired_difference(by("asymmetry", c), base, lambda r: r["unreciprocated"])
            print(f"| {c} | {m:+.3f} ± {h:.3f} | {p:.2g} |")
        print()

    m11 = _load("m11", "11_maintenance_collapse.py")
    col = [r for r in rows if r["block"] == "collapse"]
    if col:
        print("## 3. Maintenance collapse (exp 11)\n")
        print("Two draws: each cell gives the mean and, in brackets, the mean of each draw.\n")
        outs = [("inner", lambda r: r["layers"][0]), ("+close", lambda r: r["layers"][1]),
                ("+friends", lambda r: r["layers"][2]), ("all", lambda r: r["layers"][3]),
                ("μ", lambda r: r["mu"]), ("high-mode share", lambda r: r["high"])]
        routes = list(m11.routes(1.0))
        for nm, get in outs:
            print(f"### {nm}\n\n| q | " + " | ".join(routes) + " |\n|---|" + "---|" * len(routes))
            for q in m11.QS:
                cells = []
                for route in routes:
                    rs = [r for r in col if abs(r["q"] - q) < 1e-9 and (r["route"] == route or q == 1.0)]
                    cells.append(fmt(summarise(rs, get)))
                print(f"| {q:.2f} | " + " | ".join(cells) + " |")
            print()
        print("Share of the variance of log(layer) explained by q (between-q over total, all runs):\n")
        print("| layer | all four routes | B, δ, mixed |\n|---|---|---|")
        for k, nm in enumerate(names):
            cells = []
            for keep in (routes, ["B", "delta", "mixed"]):
                rs = [r for r in col if (r["route"] in keep or r["q"] == 1.0) and r["layers"][k] > 0]
                y = np.log([r["layers"][k] for r in rs])
                qs = np.array([r["q"] for r in rs])
                tot = y.var()
                bet = sum((qs == q).sum() * (y[qs == q].mean() - y.mean()) ** 2 for q in np.unique(qs)) / len(y)
                cells.append(f"{bet / tot:.3f}")
            print(f"| {nm} | " + " | ".join(cells) + " |")
        print()
        print("Exchangeability of the routes: log(layer under route / layer under B), per draw "
              "(draw 0, draw 1). R² hides these gaps, which are systematic.\n")
        for route in ("delta", "eta"):
            print(f"### {route} against B\n\n| q | " + " | ".join(names) + " |\n|---|" + "---|" * len(names))
            for q in m11.QS:
                if q == 1.0:
                    continue
                cells = []
                for k in range(len(names)):
                    logs = []
                    for p in (0, 1):
                        val = lambda rt: np.mean([r["layers"][k] for r in col  # noqa: E731, B023
                                                  if abs(r["q"] - q) < 1e-9 and r["route"] == rt and r["pop"] == p])
                        logs.append(math.log(val(route) / val("B")))
                    cells.append(f"{logs[0]:+.2f}, {logs[1]:+.2f}")
                print(f"| {q:.2f} | " + " | ".join(cells) + " |")
            print()

    pr = [r for r in rows if r["block"] == "pairing"]
    if pr:
        print("## 4. Pairing (exp 14)\n")
        print("| condition | profile | strong ties/agent | effective friends | exclusive pairs |\n|---|---|---|---|---|")
        for c in dict.fromkeys(r["cond"] for r in pr):
            rs = [r for r in pr if r["cond"] == c]
            for g in sorted(rs[0]["pairing"]):
                cells = [fmt(summarise(rs, lambda r: r["pairing"].get(g, {}).get(k))) for k in
                         ("n_strong", "n_eff", "exclusive")]
                print(f"| {c} | {g.replace('_c', '')} | " + " | ".join(cells) + " |")
        print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--blocks", nargs="+", default=["layers", "asymmetry", "collapse", "pairing"])
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args()
    {"run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
