"""Experiment 18: do the main results survive finer interactions (k = 3), once recalibrated?

Experiment 17 found that finer interactions (B × k; η, investment unit and cancellation
drop / k, at the same Q = ηB/δ) reduce the turnover mismatch, but move the layers away
from the calibration. This experiment recalibrates at k = 3, towards the layers of k = 1
measured on the same draw, start and window as experiment 15, and reruns the main results.
k = 1 stays the reference model; this is a sensitivity test.

Knobs of the recalibration: the circle thresholds t1, t2, t3 and a factor snu on openness
ν. Thresholds cannot move the outer layer, which is set by exposure (experiment 10).

Blocks, on the blocks of experiment 15 (one seed; compared with its runs of the same
draws and seed):

- ``layers``: N = 100 and 200, 3 draws, plus the closeness histogram;
- ``asymmetry``: 5 counterfactuals, 3 draws;
- ``collapse``: routes B, η, δ at q = 0.5 and 2, and q = 1, 2 draws;
- ``pairing``: the mixed population at B × 1 and × 0.3, 2 draws;
- ``inverse``: N = 12, 24, 48, 3 draws (experiment 09 is the comparison);
- ``reference``: one k = 1 run for the closeness histogram;
- ``time``: the measures of experiment 17 at k = 1 and k = 3, 2 seeds, in a late window.

Everything runs one job at a time in this process, appending to a log, and a rerun skips
what is done.

    python experiments/18_k3_sensitivity.py calibrate --n 12 [--points '[{...}]']
    python experiments/18_k3_sensitivity.py diagnose
    python experiments/18_k3_sensitivity.py long
    python experiments/18_k3_sensitivity.py run
    python experiments/18_k3_sensitivity.py report > results/18_k3_sensitivity/report.md
"""
import argparse
import copy
import importlib.util
import json
import math
import time
from pathlib import Path

import numpy as np
from scipy import stats

OUT = Path("results/18_k3_sensitivity")
RUNS = OUT / "runs.jsonl"
CALIB = OUT / "calibration.jsonl"
LONG = OUT / "long.jsonl"
ROBUST = Path("results/15_robustness/runs.jsonl")
HERE = Path(__file__).parent

K = 3.0
# Layers at k = 1 from experiment 15: draw 0, mean of 3 seeds, empty start, window 1000-1500.
TARGET = [2.11, 5.51, 15.27, 41.69]
RANGES = {"t1": (0.26, 0.38), "t2": (0.48, 0.62), "t3": (0.70, 0.86), "snu": (0.25, 0.60)}
# k = 3 is still drifting over 300-700 (cmd_diagnose), so time is measured later.
TIME_WINDOW = (1000.0, 1500.0)
# Chosen from the calibration log; see docs/experiments/18-k3-sensitivity.md.
CHOSEN = {"t1": 0.315, "t2": 0.58, "t3": 0.822, "snu": 0.39}
# Best point of the first search, whose protocol differed from the control runs.
DIAGNOSED = {"t1": 0.30, "t2": 0.60, "t3": 0.80, "snu": 0.62}
BINS = np.linspace(0.0, 1.0, 21)


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


m15 = _load("m15", "15_robustness.py")
m17 = _load("m17", "17_time_mapping.py")
calib = _load("calib", "calibrate_layering.py")


def recalibrated(raw, point=None):
    """k = 3 version of a k = 1 config, with the thresholds and openness of ``point``."""
    return m17.scale_interactions(calib.apply(raw, point or CHOSEN), K)


def score(L):
    if np.any(~np.isfinite(L)) or np.any(np.asarray(L) <= 0):
        return 99.0
    return float(np.sum(np.log(np.asarray(L) / np.asarray(TARGET)) ** 2))


# ------------------------------------------------------------------ calibration
def cmd_calibrate(a):
    from asym.abm.engine import simulate
    from asym.experiments import layering_per_run
    OUT.mkdir(parents=True, exist_ok=True)
    if a.points:
        points = json.loads(a.points)
    else:
        rng = np.random.default_rng(a.seed)
        points = [{k: float(rng.uniform(*r)) for k, r in RANGES.items()} for _ in range(a.n)]
    done = [json.loads(line)["point"] for line in CALIB.read_text().splitlines()] if CALIB.exists() else []
    base = m15.build_config({"block": "layers", "cond": "n100", "pop": 0, "seed": 0})
    base["simulation"].update(record_events=False)
    for n, p in enumerate(points):
        if p in done:
            continue
        t = time.time()
        res = simulate(recalibrated(base, p), seed=0)
        L = layering_per_run(res).tolist()
        with CALIB.open("a") as fh:
            fh.write(json.dumps({"point": p, "L": L, "score": score(L), "sec": time.time() - t}) + "\n")
        print(f"{n + 1}/{len(points)} score={score(L):.3f} L={np.round(L, 2).tolist()} {time.time() - t:.0f}s", flush=True)


# ------------------------------------------------------------------ jobs
def job_list():
    out = [{"block": "reference", "cond": "n100", "pop": 0, "seed": 0}]
    out += [{"block": "layers", "cond": n, "pop": p, "seed": 0} for n in ("n100", "n200") for p in range(3)]
    for c in ("no_deficit", "same_decay", "same_allocation", "average_only", "misperception_centred"):
        out += [{"block": "asymmetry", "cond": c, "pop": p, "seed": 0} for p in range(3)]
    for q, route in [(1.0, "B")] + [(q, r) for q in (0.5, 2.0) for r in ("B", "eta", "delta")]:
        out += [{"block": "collapse", "cond": f"{route}@{q:.3f}", "q": q, "route": route, "pop": p, "seed": 0}
                for p in range(2)]
    for m in (1.0, 0.3):
        out += [{"block": "pairing", "cond": f"mixed_B{m}", "kind": "mixed", "beta": None, "b_mult": m,
                 "pop": p, "seed": 0} for p in range(2)]
    out += [{"block": "inverse", "cond": f"n{n}", "n": n, "pop": p, "seed": 0} for n in (12, 24, 48) for p in range(3)]
    return out


def job_key(j):
    return f"{j['block']}|{j['cond']}|{j['pop']}|{j['seed']}"


def histogram(res, out):
    hist = np.zeros(len(BINS) - 1)
    for k in range(len(res.times)):
        hist += np.histogram(res.snapshot(k)["x"], BINS)[0]
    out["hist"] = hist.tolist()


def run_one(j):
    if j["block"] == "reference":
        return {**m15.run_job({**j, "block": "layers"}, extra=histogram), **j}
    if j["block"] == "inverse":
        layers = {**j, "block": "layers", "cond": "n100"}

        def size(raw):
            raw["population"]["size"] = j["n"]
            return recalibrated(raw)
        return {**m15.run_job(layers, transform=size), **j}
    if j["block"] in ("collapse", "pairing"):
        # Experiment 15 measures these over 300-600, where k = 3 is still drifting.
        def late(raw):
            raw = recalibrated(raw)
            raw["simulation"].update(horizon=TIME_WINDOW[1], burn_in=TIME_WINDOW[0])
            return raw
        return m15.run_job(j, transform=late)
    extra = histogram if j["block"] == "layers" else None
    return m15.run_job(j, transform=recalibrated, extra=extra)


def cmd_diagnose(_):
    """Random start, run up to the horizon of experiment 15. Compared with its empty
    start, this separates a slow transient from a dependence on the initial state."""
    from asym import metrics
    from asym.abm.engine import simulate
    raw = m17.base_config(1.0)
    raw["simulation"].update(horizon=1500.0, burn_in=300.0, sample_interval=25.0, record_events=False)
    res = simulate(recalibrated(raw, DIAGNOSED), seed=0)
    t = np.asarray(res.times)
    L = np.array([metrics.layering(res, at=k)["mean_layer_sizes"] for k in range(len(t))])
    out = {f"{a}-{b}": L[(t >= a) & (t <= b)].mean(axis=0).tolist()
           for a, b in [(300, 700), (700, 1000), (1000, 1500)]}
    (OUT / "diagnose.json").write_text(json.dumps({"point": DIAGNOSED, "windows": out}))
    print(json.dumps(out), flush=True)


def cmd_long(_):
    """Both starts up to t = 3000 at k = 1 and k = 3: does the start stop mattering?"""
    from asym import metrics
    from asym.abm.engine import simulate
    random_start = {"mode": "random", "density": 0.2, "x_range": [0.05, 0.3]}
    done = {(r["k"], r["start"]) for r in _rows(LONG)} if LONG.exists() else set()
    for k in (1, 3):
        for start in ("empty", "random"):
            if (k, start) in done:
                continue
            t0 = time.time()
            raw = m15.build_config({"block": "layers", "cond": "n100", "pop": 0, "seed": 0})
            raw["simulation"].update(horizon=3000.0, burn_in=500.0, sample_interval=25.0, record_events=False)
            if start == "random":
                raw["init"] = copy.deepcopy(random_start)
            if k == 3:
                raw = recalibrated(raw)
            res = simulate(raw, seed=0)
            t = np.asarray(res.times)
            L = np.array([metrics.layering(res, at=i)["mean_layer_sizes"] for i in range(len(t))])
            windows = {f"{a}-{a + 500}": L[(t >= a) & (t < a + 500)].mean(axis=0).tolist() for a in range(500, 3000, 500)}
            with LONG.open("a") as fh:
                fh.write(json.dumps({"k": k, "start": start, "windows": windows}) + "\n")
            print(k, start, json.dumps(windows), f"{time.time() - t0:.0f}s", flush=True)


def cmd_run(_):
    assert CHOSEN is not None, "set CHOSEN from the calibration log first"
    OUT.mkdir(parents=True, exist_ok=True)
    done = {job_key(json.loads(line)) for line in RUNS.read_text().splitlines() if line.strip()} if RUNS.exists() else set()
    jobs = [j for j in job_list() if job_key(j) not in done]
    print(f"{len(jobs)} jobs to run ({len(done)} done)", flush=True)
    for n, j in enumerate(jobs):
        t = time.time()
        r = run_one(j)
        with RUNS.open("a") as fh:
            fh.write(json.dumps(r) + "\n")
        print(f"{n + 1}/{len(jobs)} {job_key(j)} {time.time() - t:.0f}s", flush=True)
    m17.WINDOW = TIME_WINDOW
    for path, args in ((OUT / "time_k1.json", (1.0,)), (OUT / "time.json", (K, lambda raw: calib.apply(raw, CHOSEN)))):
        if not path.exists():
            t = time.time()
            path.write_text(json.dumps([m17.measure((s, *args)) for s in range(2)]))
            print(f"{path.name} {time.time() - t:.0f}s", flush=True)


# ------------------------------------------------------------------ report
def _rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _draws(rows, get):
    by = {}
    for r in rows:
        by.setdefault(r["pop"], []).append(get(r))
    return {p: float(np.mean(v)) for p, v in by.items()}


def _paired(a, b):
    d = np.array([a[p] - b[p] for p in sorted(a) if p in b])
    half = float(stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else math.nan
    return float(d.mean()), half


def cmd_report(_):
    names = ["inner", "+close", "+friends", "all"]
    calibration = sorted(_rows(CALIB), key=lambda r: r["score"])
    print("# Experiment 18: main results at k = 3, recalibrated\n")
    print(f"## Calibration ({len(calibration)} points)\n\nTarget layers (k = 1): {TARGET}. Best points:\n")
    print("| score | t1 | t2 | t3 | snu | layers |\n|---|---|---|---|---|---|")
    for r in calibration[:5]:
        p = r["point"]
        print(f"| {r['score']:.3f} | {p['t1']:.3f} | {p['t2']:.3f} | {p['t3']:.3f} | {p['snu']:.3f} | "
              + " / ".join(f"{v:.2f}" for v in r["L"]) + " |")
    print(f"\nChosen: {CHOSEN}\n")

    rows, ref = _rows(RUNS), _rows(ROBUST)

    def k3(block, cond):
        return [r for r in rows if r["block"] == block and r["cond"] == cond]

    def k1(block, cond, pops):
        return [r for r in ref if r["block"] == block and r["cond"] == cond and r["seed"] == 0 and r["pop"] in pops]

    print("## 1. Layers (same draws, seed 0)\n")
    print("| N | k | " + " | ".join(names) + " | μ | unreciprocated | correlation |\n|---|---|---|---|---|---|---|---|---|")
    for c in ("n100", "n200"):
        a = k3("layers", c)
        for lab, rs in (("1", k1("layers", c, {r["pop"] for r in a})), ("3", a)):
            cells = [f"{np.mean([r['layers'][i] for r in rs]):.2f}" for i in range(4)]
            print(f"| {c} | {lab} | " + " | ".join(cells) + f" | {np.mean([r['mu'] for r in rs]):.3f} | "
                  f"{np.mean([r['unreciprocated'] for r in rs]):.3f} | {np.mean([r['correlation'] for r in rs]):.3f} |")
    print()

    print("Paired differences k = 3 − k = 1 over the 3 draws (t-interval):\n")
    print("| N | " + " | ".join(names) + " | μ | unreciprocated |\n|---|---|---|---|---|---|---|")
    for c in ("n100", "n200"):
        a = k3("layers", c)
        b = k1("layers", c, {r["pop"] for r in a})
        gets = [(lambda r, i=i: r["layers"][i]) for i in range(4)] + [lambda r: r["mu"], lambda r: r["unreciprocated"]]
        cells = ["{:+.3f} ± {:.3f}".format(*_paired(_draws(a, g), _draws(b, g))) for g in gets]
        print(f"| {c} | " + " | ".join(cells) + " |")
    print()

    if LONG.exists():
        print("## 1b. Does the start stop mattering? (draw 0, seed 0, N = 100)\n")
        print("| k | start | window | " + " | ".join(names) + " |\n|---|---|---|---|---|---|---|")
        for r in _rows(LONG):
            for w, v in r["windows"].items():
                print(f"| {r['k']} | {r['start']} | {w} | " + " | ".join(f"{x:.2f}" for x in v) + " |")
        print()

    print("## 2. Closeness histogram (share of ties per band, N = 100)\n")
    h1 = np.array(k3("reference", "n100")[0]["hist"])
    h3 = np.sum([r["hist"] for r in k3("layers", "n100")], axis=0)
    print("| band | k = 1 | k = 3 |\n|---|---|---|")
    for i in range(len(h1)):
        print(f"| {BINS[i]:.2f}–{BINS[i + 1]:.2f} | {h1[i] / h1.sum():.3f} | {h3[i] / h3.sum():.3f} |")
    print()

    print("## 3. Asymmetry: unreciprocated share, difference from the baseline paired by draw\n")
    print("| condition | k = 1 share | k = 1 difference | k = 3 share | k = 3 difference |\n|---|---|---|---|---|")
    get = lambda r: r["unreciprocated"]  # noqa: E731
    base3 = _draws(k3("layers", "n100"), get)
    pops = set(base3)
    base1 = _draws(k1("layers", "n100", pops), get)
    print(f"| baseline | {np.mean(list(base1.values())):.3f} | | {np.mean(list(base3.values())):.3f} | |")
    for c in ("no_deficit", "same_decay", "same_allocation", "average_only", "misperception_centred"):
        d3 = _draws(k3("asymmetry", c), get)
        d1 = _draws(k1("asymmetry", c, pops), get)
        m1, h1_ = _paired(d1, base1)
        m3, h3_ = _paired(d3, base3)
        print(f"| {c} | {np.mean(list(d1.values())):.3f} | {m1:+.3f} ± {h1_:.3f} | "
              f"{np.mean(list(d3.values())):.3f} | {m3:+.3f} ± {h3_:.3f} |")
    print()
    pairs = ["butterfly_c->transactional_c", "loyal_few_c->transactional_c", "butterfly_c->avoidant_c"]
    def pair_share(rs, p):
        v = [r["pairs"].get(p) for r in rs]
        v = [x for x in v if x is not None]
        return f"{np.mean(v):.3f}" if v else "n/a"

    print("Unreciprocated share by pair (k = 1 / k = 3):\n")
    print("| condition | " + " | ".join(p.replace("_c", "") for p in pairs) + " |\n|---|---|---|---|")
    for c in ("baseline", "no_deficit", "same_decay"):
        a3 = k3("layers", "n100") if c == "baseline" else k3("asymmetry", c)
        a1 = k1("layers", "n100", pops) if c == "baseline" else k1("asymmetry", c, pops)
        print(f"| {c} | " + " | ".join(f"{pair_share(a1, p)} / {pair_share(a3, p)}" for p in pairs) + " |")
    print()

    print("## 4. Collapse (draws 0, 1)\n")
    col = [r for r in rows if r["block"] == "collapse"]
    print("| q | route | " + " | ".join(names) + " | high-mode share |\n|---|---|---|---|---|---|---|")
    for q, route in [(0.5, "B"), (0.5, "delta"), (0.5, "eta"), (1.0, "B"), (2.0, "B"), (2.0, "delta"), (2.0, "eta")]:
        rs = [r for r in col if r["q"] == q and r["route"] == route]
        print(f"| {q:g} | {route} | " + " | ".join(f"{np.mean([r['layers'][i] for r in rs]):.2f}" for i in range(4))
              + f" | {np.mean([r['high'] for r in rs]):.3f} |")
    print("\nShare of the variance of log(layer) explained by q on the B and δ routes:\n")
    print("| layer | k = 3 | k = 1 (same cells) |\n|---|---|---|")
    keep = lambda rs: [r for r in rs if r["route"] in ("B", "delta") and r["q"] in (0.5, 1.0, 2.0)]  # noqa: E731
    r1 = [r for r in ref if r["block"] == "collapse" and r["seed"] == 0 and abs(r["q"] - round(r["q"], 1)) < 1e-9]
    for i, nm in enumerate(names):
        cells = []
        for rs in (keep(col), keep(r1)):
            rs = [r for r in rs if r["layers"][i] > 0]
            y = np.log([r["layers"][i] for r in rs])
            qs = np.array([r["q"] for r in rs])
            cells.append(sum((qs == q).sum() * (y[qs == q].mean() - y.mean()) ** 2 for q in np.unique(qs)) / len(y) / y.var())
        print(f"| {nm} | {cells[0]:.3f} | {cells[1]:.3f} |")
    print("\nlog(layer under δ / layer under B), draw 0, draw 1:\n")
    print("| k | q | " + " | ".join(names) + " |\n|---|---|---|---|---|---|")
    one = lambda rs, q, route, p: next(r for r in rs if r["q"] == q and r["route"] == route and r["pop"] == p)  # noqa: E731
    for lab, rs in (("1", r1), ("3", col)):
        for q in (0.5, 2.0):
            cells = [", ".join(f"{math.log(one(rs, q, 'delta', p)['layers'][i] / one(rs, q, 'B', p)['layers'][i]):+.2f}"
                               for p in (0, 1)) for i in range(4)]
            print(f"| {lab} | {q:g} | " + " | ".join(cells) + " |")
    held = total = 0
    for p in (0, 1):
        for q, sign in ((0.5, -1), (2.0, 1)):
            e = one(col, q, "eta", p)
            for other in ("B", "delta"):
                o = one(col, q, other, p)
                for got, want in ((e["layers"][0] - o["layers"][0], sign), (e["layers"][3] - o["layers"][3], -sign),
                                  (e["high"] - o["high"], sign)):
                    total += 1
                    held += bool(got * want > 0)
    print(f"\nProposition 2 at k = 3: {held} of {total} signs of the η route hold (both draws).\n")

    print("## 5. Pairing: share of agents in an exclusive pair\n")
    print("| budget | profile | k = 1 | k = 3 |\n|---|---|---|---|")
    for c in ("mixed_B1.0", "mixed_B0.3"):
        a = k3("pairing", c)
        b = k1("pairing", c, {r["pop"] for r in a})
        for g in sorted(a[0]["pairing"]):
            print(f"| {c} | {g.replace('_c', '')} | {np.mean([r['pairing'][g]['exclusive'] for r in b]):.3f} | "
                  f"{np.mean([r['pairing'][g]['exclusive'] for r in a]):.3f} |")
    print()

    print("## 6. Inverse regime: μ (k = 1 from experiment 09: −0.34, −0.12, +0.42)\n")
    print("| N | μ per draw | mean |\n|---|---|---|")
    for n in (12, 24, 48):
        v = [r["mu"] for r in rows if r["block"] == "inverse" and r["n"] == n]
        print(f"| {n} | " + ", ".join(f"{x:+.2f}" for x in v) + f" | {np.mean(v):+.2f} |")
    print()

    print(f"## 7. Time mapping (window {TIME_WINDOW[0]:.0f}-{TIME_WINDOW[1]:.0f}, random start)\n")
    wpy = 365.25 / 7
    for lab, name in (("k = 1", "time_k1.json"), ("k = 3", "time.json")):
        t = json.loads((OUT / name).read_text())
        p10 = {n: np.percentile(np.concatenate([o["layer_rates"][n] for o in t]), 10) for n in ("close+", "friend+")}
        h = {}
        for n in ("close+", "friend+"):
            a = sum(o["retention"][n][0] for o in t)
            b = sum(o["retention"][n][1] for o in t)
            h[n] = -math.log(b / a) / 50.0
        uc, ut = 1.0 / p10["close+"], -math.log(0.98) / h["close+"] / wpy
        v = [x for o in t for x in o["reach"]["2"]]
        nf, tf = np.median([x[0] for x in v]), np.median([x[1] for x in v])
        rate = np.mean([o["per_agent_rate"] for o in t])
        lt = np.concatenate([o["lifetimes"] for o in t])
        print(f"### {lab}\n")
        print(f"- Layers: {np.round(np.mean([o['layers'] for o in t], axis=0), 2).tolist()}")
        print(f"- Mismatch contact / close+ turnover: {uc / ut:.0f}× ({uc:.2f} vs {ut:.3f} units per week)")
        print(f"- close+ loss per year at the contact mapping: {1 - math.exp(-h['close+'] * uc * wpy):.0%}")
        print(f"- Hazard close+ / friend+: {h['close+'] / h['friend+']:.2f}; contact ratio: {p10['close+'] / p10['friend+']:.2f}")
        print(f"- Interactions to friend: {nf:.0f}; time {tf:.0f} units, {tf / uc:.0f} weeks at the contact mapping")
        print(f"- Hours per interaction (Hall 90 h): {90 / nf:.2f}; social h/week: {rate * 90 / nf * uc:.0f}")
        print(f"- New ties gone within 200 units: {np.mean((lt >= 0) & (lt <= 200)):.2f}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["calibrate", "diagnose", "long", "run", "report"])
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--points", default=None)
    a = ap.parse_args()
    {"calibrate": cmd_calibrate, "diagnose": cmd_diagnose, "long": cmd_long, "run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
