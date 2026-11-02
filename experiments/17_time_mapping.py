"""Experiment 17: mapping the model time unit to real time (ADR-0006).

Several independent empirical anchors are each turned into a conversion factor
(model units per week or per year), using quantities measured on the calibrated
population of experiment 06 (N = 100, random start as in experiment 10, window
300–700, events recorded). If the anchors agree, the mapping is credible; their
spread is the uncertainty.

Anchors (docs/experiments/17-time-mapping.md gives the sources and their status):

- **C. Minimum contact frequency per layer**: at least weekly for the 5-layer, monthly
  for the 15-layer. The model's cumulative layers are about 2 / 6 / 16 / 40, so the
  5-layer corresponds to close + inner and the 15-layer to friends and above. "Minimum"
  is read as the 10th percentile of the per-tie contact rate in that layer.
- **T. Turnover**:
  - inner layers, 1-4% of alters per year (Roy et al. 2022), 2% used here;
  - outer layers, at most 30% per year. This is a convention and an upper bound, so
    the mapping it gives is an upper bound too.
- **H. Hours to friendship** (Hall 2019): about 90 h together to become a friend. This
  maps interactions to *hours* of interaction, not calendar time. It is combined with
  the calendar mapping into a sanity check: weekly social hours per agent.
- **B. Liability of newness** (Burt 2002): about 90% of new bridge relations are gone
  within a year. This is a weak anchor, because bridges among colleagues are not the
  same as new acquaintances.

    python experiments/17_time_mapping.py run [--seeds 2]
    python experiments/17_time_mapping.py report > results/17_time_mapping.md
"""
import argparse
import importlib.util
import json
import math
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

OUT = Path("results/17_time_mapping.json")
HERE = Path(__file__).parent
WINDOW = (300.0, 700.0)
DT = 5.0


def base_config(k=1.0):
    """Calibrated config; k > 1 makes interactions finer at the same Q = ηB/δ:
    B × k, and η, investment unit and cancellation drop / k (Proposition 1)."""
    spec = importlib.util.spec_from_file_location("morris", HERE / "10_morris.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    raw = m.base_config()
    raw["simulation"].update(horizon=WINDOW[1], burn_in=WINDOW[0], sample_interval=DT, record_events=True)
    if k != 1.0:
        g = raw["globals"]
        g["eta"] = g.get("eta", 0.1) / k
        g["inv_unit"] = g.get("inv_unit", 1.0) / k
        g["psi"] = g.get("psi", 0.1) / k
        for spec in raw["archetypes"].values():
            spec["B"] = spec["B"] * k
    return raw


def measure(args):
    from asym.abm.engine import simulate
    from asym.experiments import layering_per_run
    seed, scale = args
    res = simulate(base_config(scale), seed=seed)
    ids = {a: k for k, a in enumerate(res.agent_ids)}
    N = len(ids)
    T0, T1 = WINDOW
    ev = res.events

    # interactions per dyad over time
    acc = [e for e in ev if e["type"] in ("accept", "late_accept")]
    acc_t = np.array([e["t"] for e in acc])
    acc_d = np.array([min(ids[e["i"]], ids[e["j"]]) * N + max(ids[e["i"]], ids[e["j"]]) for e in acc])
    win = (acc_t >= T0) & (acc_t < T1)
    per_agent_rate = 2 * win.sum() / N / (T1 - T0)  # each interaction involves 2 agents

    # circle of every directed tie at each sample; tie-time and dyad interactions per circle class
    times = res.times
    T = res.ties
    K = len(times)
    circ = defaultdict(lambda: np.zeros(K, dtype=int))
    for t, i, j, c in zip(T["t"], T["i"].astype(int), T["j"].astype(int), T["circle"].astype(int)):
        circ[(i, j)][np.searchsorted(times, t)] = c
    # interactions of each dyad in each sample interval [t_k, t_k + DT)
    bins = np.append(times, times[-1] + DT)
    counts = defaultdict(lambda: np.zeros(K))
    for t, d in zip(acc_t[win], acc_d[win]):
        k = np.searchsorted(bins, t, side="right") - 1
        if 0 <= k < K:
            counts[d][k] += 1
    layer_rates = {"close+": [], "friend+": []}
    retention = {"close+": [], "friend+": [], "inner": []}
    lag = int(round(50.0 / DT))
    for (i, j), cs in circ.items():
        d = min(i, j) * N + max(i, j)
        cnt = counts.get(d, np.zeros(K))
        for name, lo in (("close+", 3), ("friend+", 2)):
            mask = cs[:-1] >= lo
            if mask.sum() * DT >= 50.0:  # at least 50 units in the layer
                layer_rates[name].append(float(cnt[:-1][mask].sum() / (mask.sum() * DT)))
        for name, test in (("close+", lambda c: c >= 3), ("friend+", lambda c: c >= 2), ("inner", lambda c: c == 4)):
            a, b = test(cs[:-lag]), test(cs[lag:])
            retention[name].append((int(a.sum()), int((a & b).sum())))

    # Hall: interactions on a new tie before its first promotion to friend / close
    created = {}
    n_int = defaultdict(int)
    reach = {2: [], 3: []}
    seen = {2: set(), 3: set()}
    dyad_int = defaultdict(list)
    for e in acc:
        dyad_int[min(ids[e["i"]], ids[e["j"]]) * N + max(ids[e["i"]], ids[e["j"]])].append(e["t"])
    for e in ev:
        if e["type"] == "tie_created" and e["t"] >= T0 - 200:
            created[(ids[e["i"]], ids[e["j"]])] = e["t"]
        elif e["type"] == "promote" and e["to"] in (2, 3):
            key = (ids[e["i"]], ids[e["j"]])
            if key in created and key not in seen[e["to"]]:
                seen[e["to"]].add(key)
                d = min(key) * N + max(key)
                ts = np.array(dyad_int[d])
                k = int(((ts >= created[key]) & (ts <= e["t"])).sum())
                reach[e["to"]].append((k, e["t"] - created[key]))
    lifetimes = tie_lifetimes(ev, T0, T1 - 200)
    return {"seed": seed, "k": scale, "layers": layering_per_run(res).tolist(),
            "per_agent_rate": float(per_agent_rate), "layer_rates": layer_rates,
            "retention": {k: [sum(a for a, _ in v), sum(b for _, b in v)] for k, v in retention.items()},
            "reach": {str(k): v for k, v in reach.items()}, "lifetimes": lifetimes}


def tie_lifetimes(events, t0, t1):
    """Lifetime of every directed tie created in [t0, t1), -1 if it was still alive at
    the end of the log. A tie forgotten and met again counts as two ties. ``events`` is
    in chronological order."""
    alive = {}
    out = []
    for e in events:
        key = (e["i"], e["j"])
        if e["type"] == "tie_created":
            if t0 <= e["t"] < t1:
                alive[key] = len(out)
                out.append((e["t"], -1))
            else:
                alive.pop(key, None)
        elif e["type"] == "forget" and key in alive:
            n = alive.pop(key)
            out[n] = (out[n][0], e["t"] - out[n][0])
    return [life for _, life in out]


def cmd_run(a):
    path = OUT if a.k == 1.0 else OUT.with_name(f"17_time_mapping_k{a.k:g}.json")
    with ProcessPoolExecutor(a.workers) as ex:
        out = list(ex.map(measure, [(s, a.k) for s in range(a.seeds)]))
    path.write_text(json.dumps(out))


def cmd_report(_):
    out = json.loads(OUT.read_text())
    WEEKS_PER_YEAR = 365.25 / 7
    rows = []  # (anchor, units per week)
    print("# Experiment 17: time-unit mapping\n")
    rate = np.mean([o["per_agent_rate"] for o in out])
    print(f"Interactions per agent per model unit: {rate:.3f}\n")

    print("## C. Minimum contact frequency per layer\n")
    print("| layer (model ↔ Dunbar) | ties | median contacts / unit | 10th pct contacts / unit | empirical minimum | units per week |")
    print("|---|---|---|---|---|---|")
    p10 = {}
    for name, emp, per_week in (("close+", "weekly (5-layer)", 1.0), ("friend+", "monthly (15-layer)", 12 / 52.18)):
        v = np.concatenate([o["layer_rates"][name] for o in out])
        p10[name] = np.percentile(v, 10)
        upw = per_week / p10[name]  # model units per week such that the 10th-pct tie gets `per_week` contacts/week
        rows.append((f"C: {emp}", upw))
        print(f"| {name} ↔ {emp} | {len(v)} | {np.median(v):.3f} | {p10[name]:.3f} | {per_week:.2f} / week | {upw:.2f} |")
    print(f"\nUnit-free check: ratio of the 10th-percentile contact rates close+ / friend+ = "
          f"{p10['close+'] / p10['friend+']:.2f} (empirical weekly / monthly = {52.18 / 12:.2f}).\n")

    print("## T. Turnover (retention over 50 units)\n")
    print("| layer | members | retained after 50 units | loss hazard per unit | empirical loss per year | units per week |")
    print("|---|---|---|---|---|---|")
    for name, emp_label, emp in (("close+", "2% (Roy et al. 2022: 1-4%)", 0.02), ("friend+", "≤ 30% (convention, upper bound)", 0.30)):
        a = sum(o["retention"][name][0] for o in out)
        b = sum(o["retention"][name][1] for o in out)
        h = -math.log(b / a) / 50.0
        h_emp = -math.log(1 - emp)  # per year
        upw = h_emp / h / WEEKS_PER_YEAR
        rows.append((f"T: {name} turnover {emp_label}", upw))
        print(f"| {name} | {a} | {b / a:.3f} | {h:.2e} | {emp_label} | {upw:.2f} |")
    a = sum(o["retention"]["inner"][0] for o in out)
    b = sum(o["retention"]["inner"][1] for o in out)
    print(f"\n(Inner circle only: retained after 50 units {b / a:.3f}.)\n")

    print("## B. Liability of newness\n")
    lt = np.concatenate([o["lifetimes"] for o in out])
    lt = np.where(lt < 0, np.inf, lt)
    finite = np.isfinite(lt)
    t90 = np.percentile(lt, 90) if np.mean(finite) >= 0.9 else math.inf
    print(f"New ties created in the window: {len(lt)}; forgotten within 200 units: {np.mean(lt <= 200):.2f}; "
          f"median lifetime {np.median(lt):.0f} units; 90% gone after {t90:.0f} units.\n")
    if np.isfinite(t90):
        upw = t90 / WEEKS_PER_YEAR
        rows.append(("B: 90% of new bridges gone within a year", upw))
        print(f"If 90% are gone within one year: {upw:.2f} units per week.\n")

    print("## H. Interactions to friendship (Hall 2019)\n")
    print("| promotion | new ties reaching it | median interactions | median model time |")
    print("|---|---|---|---|")
    med = {}
    for k, lab in (("2", "acquaintance → friend"), ("3", "→ close friend")):
        v = [x for o in out for x in o["reach"][k]]
        if v:
            n = np.array([x[0] for x in v])
            t = np.array([x[1] for x in v])
            med[k] = (np.median(n), np.median(t))
            print(f"| {lab} | {len(v)} | {med[k][0]:.0f} | {med[k][1]:.0f} |")
    print()

    print("## Summary of anchors\n")
    print("| anchor | model units per week |\n|---|---|")
    for lab, u in rows:
        print(f"| {lab} | {u:.2f} |")
    print("\nThe friend+ turnover anchor is an upper bound on the mapping, so the anchors are not averaged.\n")
    contact = [u for lab, u in rows if lab.startswith("C:")]
    if "2" in med:
        h_per_int = 90.0 / med["2"][0]
        print(f"Hall: 90 h to friendship over a median of {med['2'][0]:.0f} interactions gives "
              f"{h_per_int:.1f} h per interaction.")
        print("Social hours per agent per week = "
              f"{rate:.3f} × {h_per_int:.1f} × units/week: "
              + ", ".join(f"{rate * h_per_int * u:.0f} h at {u:.2f} units/week" for u in contact) + ".")
    granularity_table()


def granularity_table():
    """Compare anchors across the granularity factor k (B × k, η / k)."""
    files = sorted(OUT.parent.glob("17_time_mapping_k*.json"), key=lambda f: float(f.stem.split("_k")[1]))
    sets = [(1.0, json.loads(OUT.read_text()))] + [(float(f.stem.split("_k")[1]), json.loads(f.read_text())) for f in files]
    WPY = 365.25 / 7
    print("\n## Granularity: finer interactions at the same Q (B × k, η / k)\n")
    print("| k | layers | contacts/agent/unit | units/week (contact, weekly) | units/week (close+ turnover 2%/yr) | "
          "mismatch | close+ loss per year at contact mapping | hazard close+ / friend+ | contact ratio close+ / friend+ | "
          "interactions to friend | time to friend (units) | weeks to friend at contact mapping | "
          "hours per interaction (Hall 90 h) | social h/week at contact mapping | new ties gone within 200 units |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, out in sets:
        layers = " / ".join(f"{v:.1f}" for v in np.mean([o["layers"] for o in out], axis=0))
        rate = np.mean([o["per_agent_rate"] for o in out])
        p10 = {n: np.percentile(np.concatenate([o["layer_rates"][n] for o in out]), 10) for n in ("close+", "friend+")}
        u_c = 1.0 / p10["close+"]
        hazard = {}
        for n in ("close+", "friend+"):
            a = sum(o["retention"][n][0] for o in out)
            b = sum(o["retention"][n][1] for o in out)
            hazard[n] = -math.log(b / a) / 50.0
        u_t = -math.log(0.98) / hazard["close+"] / WPY
        loss = 1 - math.exp(-hazard["close+"] * u_c * WPY)
        v = [x for o in out for x in o["reach"]["2"]]
        n_f = np.median([x[0] for x in v])
        t_f = np.median([x[1] for x in v])
        hpi = 90.0 / n_f
        lt = np.concatenate([o["lifetimes"] for o in out])
        gone = np.mean((lt >= 0) & (lt <= 200))
        print(f"| {k:g} | {layers} | {rate:.1f} | {u_c:.2f} | {u_t:.3f} | {u_c / u_t:.0f}× | {loss:.0%} | "
              f"{hazard['close+'] / hazard['friend+']:.2f} | {p10['close+'] / p10['friend+']:.2f} | {n_f:.0f} | "
              f"{t_f:.0f} | {t_f / u_c:.0f} | {hpi:.2f} | {rate * hpi * u_c:.0f} | {gone:.2f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--k", type=float, default=1.0, help="granularity factor (B × k, η / k)")
    ap.add_argument("--workers", type=int, default=1, help="event logs are held in memory: raise with care")
    a = ap.parse_args()
    {"run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
