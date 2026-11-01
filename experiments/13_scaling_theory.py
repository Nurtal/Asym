"""Experiment 13: checks of the analytical scaling theory of maintained ties.

Theory: docs/theory/maintenance-scaling.md. Four checks, one per sub-command:

- ``meanfield``: the mean-field steady state depends on B, η and δ only through
  Q = ηB/δ, up to two named corrections (κ/δ and o0/B). A clique of 8 calibrated
  agents is integrated under the three routes (B × 2, η × 2, δ / 2), with and
  without those corrections.
- ``shotnoise``: linear-noise prediction for one tie, Var x = (η/2) x (1 − x)² /
  (1 − β(1 − x)), checked by exact simulation of a single tie.
- ``abm``: the same prediction inside the full ABM (N = 100, calibrated model):
  per-tie temporal variance under the B, η and δ routes at q = 2.
- ``pairing``: the instability criterion β_eff (1 − x) > 1 for equal sharing,
  checked on mean-field cliques of M identical agents.

    python experiments/13_scaling_theory.py meanfield
    python experiments/13_scaling_theory.py shotnoise
    python experiments/13_scaling_theory.py abm [--seeds 2] [--workers 8]
    python experiments/13_scaling_theory.py pairing
"""
import argparse
import copy
import importlib.util
import itertools
import json
import math
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from asym.config import load_config
from asym.experiments import condition_configs, load_experiment
from asym.meanfield.solver import solve_meanfield
from asym.model import forms
from asym.model.archetypes import archetype_centre, archetype_table

warnings.filterwarnings("ignore", message="mean-field solver ignores")
OUT = Path("results/13_scaling_theory")
ROUTES = {"base": (1.0, 1.0, 1.0), "B": (2.0, 1.0, 1.0), "eta": (1.0, 2.0, 1.0), "delta": (1.0, 1.0, 0.5)}


def calibrated():
    raw = condition_configs(load_experiment("experiments/06_dunbar_calibrated_scaling.yaml"))["n100"]
    return raw, archetype_table(raw["archetypes"])


# ---------------------------------------------------------------- mean-field
def clique_config(agents, x_init, globals_, horizon, step=0.1):
    ids = [a["id"] for a in agents]
    ties = [{"i": ids[i], "j": ids[j], "x": float(x_init[i, j]), "r": 1.0, "o": 1.0}
            for i, j in itertools.permutations(range(len(ids)), 2)]
    return {"agents": agents, "globals": dict(globals_), "init": {"mode": "file", "ties": ties},
            "variants": {"exploration": "ties"},
            "simulation": {"horizon": float(horizon), "burn_in": 0.0, "sample_interval": float(horizon),
                           "mf_step": step}}


def route_agents(base_agents, mB, mdelta, kappa_off):
    out = []
    for a in base_agents:
        a = copy.deepcopy(a)
        a["B"] = a["B"] * mB
        a["delta"] = [d * mdelta for d in a["delta"]]
        if kappa_off:
            a["kappa"] = 0.0
        out.append(a)
    return out


def cmd_meanfield(_):
    raw, table = calibrated()
    names = ["butterfly_c", "loyal_few_c", "transactional_c", "avoidant_c"] * 2
    base_agents = []
    for k, nm in enumerate(names):
        a = archetype_centre(nm, table)
        a.update(id=f"a{k}", nu=0.0)
        a.pop("archetype", None)
        base_agents.append(a)
    x_init = np.random.default_rng(1).uniform(0.2, 0.8, (8, 8))
    g0 = dict(raw["globals"])
    rows = []
    for kappa_off, o0 in itertools.product([False, True], [0.5, 0.005]):
        cfgs = []
        for route, (mB, meta, md) in ROUTES.items():
            g = dict(g0, eta=g0["eta"] * meta, o0=o0)
            cfgs.append(clique_config(route_agents(base_agents, mB, md, kappa_off), x_init, g, horizon=4000.0))
        tr = solve_meanfield(cfgs, occupancy="exponential")
        X = tr.x[-1]  # (routes, N, N)
        off = ~np.eye(8, dtype=bool)
        ref = X[2][off]  # η route: the pure-Q route
        row = {"kappa": "off" if kappa_off else "on", "o0": o0,
               "x_eta_mean": float(ref.mean()), "x_base_mean": float(X[0][off].mean())}
        for k, route in enumerate(ROUTES):
            if route in ("B", "delta"):
                d = np.abs(X[k][off] - ref)
                row[f"{route}_vs_eta_max"] = float(d.max())
                row[f"{route}_vs_eta_mean"] = float(d.mean())
        rows.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "meanfield.json").write_text(json.dumps(rows, indent=1))
    print("| κ | o0 | mean x (base) | mean x (η route) | B vs η: mean / max abs diff | δ vs η: mean / max abs diff |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['kappa']} | {r['o0']} | {r['x_base_mean']:.3f} | {r['x_eta_mean']:.3f} | "
              f"{r['B_vs_eta_mean']:.2g} / {r['B_vs_eta_max']:.2g} | {r['delta_vs_eta_mean']:.2g} / {r['delta_vs_eta_max']:.2g} |")


# ---------------------------------------------------------------- shot noise
def single_tie(eta, c, delta, beta, T, seed, dt_sample=1.0, burn=2000.0):
    """Exact simulation of one tie: decay δ, interactions at rate c·x^β, jumps η(1 − x)."""
    rng = np.random.default_rng(seed)
    x, t = 0.5, 0.0
    samples = []
    next_s = burn
    while t < T:
        # thinning against the bound c (x ≤ 1)
        w = rng.exponential(1.0 / c)
        while next_s < t + w and next_s < T:
            samples.append(x * math.exp(-delta * (next_s - t)))
            next_s += dt_sample
        x *= math.exp(-delta * w)
        t += w
        if rng.random() < x ** beta:
            x += eta * (1.0 - x)
    return np.array(samples)


def lna_var(eta, x, beta):
    return 0.5 * eta * x * (1 - x) ** 2 / (1 - beta * (1 - x))


def cmd_shotnoise(_):
    rows = []
    eta0, delta0 = 0.09, 0.0115
    for beta, x_target in [(0.0, 0.5), (0.0, 0.8), (0.5, 0.8), (1.5, 0.8)]:
        # base rate c such that the mean-field fixed point is x_target: η c x^β (1 − x) = δ x
        c0 = delta0 * x_target ** (1 - beta) / (eta0 * (1 - x_target))
        for route, (mB, meta, md) in ROUTES.items():
            if route == "base":
                continue
            eta, c, delta = eta0 * meta, c0 * mB, delta0 * md
            # fixed point of the route (same for all three: Q doubled)
            xs = np.linspace(1e-4, 1 - 1e-4, 200001)
            f = eta * c * xs ** beta * (1 - xs) - delta * xs
            idx = np.flatnonzero(np.diff(np.sign(f)))
            x_mf = float(xs[idx[-1]])
            s = single_tie(eta, c, delta, beta, T=2.0e6 if route == "delta" else 1.0e6, seed=7)
            rows.append({"beta": beta, "route": route, "x_mf": x_mf, "mean": float(s.mean()), "var": float(s.var()),
                         "lna": float(lna_var(eta, x_mf, beta))})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "shotnoise.json").write_text(json.dumps(rows, indent=1))
    print("| β | route | mean-field x* | simulated mean | simulated var | LNA var | ratio |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['beta']} | {r['route']} | {r['x_mf']:.3f} | {r['mean']:.3f} | {r['var']:.2e} | {r['lna']:.2e} | "
              f"{r['var'] / r['lna']:.2f} |")


# ----------------------------------------------------------------------- ABM
def _abm_run(args):
    route, seed = args
    from asym.abm.engine import simulate
    from asym.sensitivity import Factor, apply_factors
    spec = importlib.util.spec_from_file_location("morris", Path(__file__).with_name("10_morris.py"))
    morris = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(morris)
    mB, meta, md = ROUTES[route]
    facs = [Factor("B", "archetypes.B", mB, mB), Factor("delta", "archetypes.delta", md, md),
            Factor("eta", "globals.eta", 0.09 * meta, 0.09 * meta)]
    raw = apply_factors(morris.base_config(), facs, [0.0, 0.0, 0.0])
    raw["simulation"].update(horizon=1100.0, burn_in=300.0, sample_interval=5.0)
    res = simulate(raw, seed=seed)
    T = res.ties
    K = len(res.times)
    key = T["i"].astype(np.int64) * 100000 + T["j"].astype(np.int64)
    uk, inv, counts = np.unique(key, return_inverse=True, return_counts=True)
    full = counts == K  # ties alive at every sample
    sel = full[inv]
    order = np.argsort(inv[sel] * K + np.searchsorted(res.times, T["t"][sel]))
    xs = T["x"][sel][order].reshape(-1, K)
    n_agents = len(res.agent_ids)
    th = float(raw["globals"]["thresholds"][2])
    return {"route": route, "seed": seed, "mean": xs.mean(axis=1).tolist(), "var": xs.var(axis=1).tolist(),
            "x": xs.tolist() if route == "B" else None,
            "above_inner": float(np.mean([(res.snapshot(k)["x"] >= th).sum() for k in range(K)]) / n_agents),
            "theta4": th, "n_agents": n_agents}


def cmd_abm(a):
    jobs = [(r, s) for r in ("base", "B", "eta", "delta") for s in range(a.seeds)]
    with ProcessPoolExecutor(a.workers) as ex:
        out = list(ex.map(_abm_run, jobs))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "abm.json").write_text(json.dumps([{k: v for k, v in r.items() if k != "x"} for r in out]))
    bins = [0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95]
    print("Normalised per-tie temporal variance, Var x / (x (1 − x)²), median per bin of mean x "
          "(ties alive over the whole window):\n")
    print("| mean x | " + " | ".join(ROUTES) + " | η / B |\n|---|---|---|---|---|---|")
    for lo, hi in zip(bins, bins[1:]):
        cells, vals = [], {}
        for route in ROUTES:
            m = np.concatenate([np.array(r["mean"]) for r in out if r["route"] == route])
            v = np.concatenate([np.array(r["var"]) for r in out if r["route"] == route])
            k = (m >= lo) & (m < hi)
            z = np.median(v[k] / (m[k] * (1 - m[k]) ** 2)) if k.sum() >= 5 else np.nan
            vals[route] = z
            cells.append(f"{z:.3g} (n={k.sum()})")
        print(f"| {lo:.2f}–{hi:.2f} | " + " | ".join(cells) + f" | {vals['eta'] / vals['B']:.2f} |")
    # tail prediction: widen the B-route fluctuations by √2 around each tie's mean
    print("\nTies at or above the inner threshold per agent (snapshot count, not circle membership):\n")
    print("| route | observed |\n|---|---|")
    for route in ROUTES:
        print(f"| {route} | {np.mean([r['above_inner'] for r in out if r['route'] == route]):.2f} |")
    preds = []
    for r in out:
        if r["route"] != "B":
            continue
        xs = np.array(r["x"])
        m = xs.mean(axis=1, keepdims=True)
        widened = m + math.sqrt(2.0) * (xs - m)
        # ties that are not alive over the whole window are counted as in the observation
        extra = (widened >= r["theta4"]).mean(axis=1).sum() - (xs >= r["theta4"]).mean(axis=1).sum()
        preds.append(r["above_inner"] + extra / r["n_agents"])
    print(f"| η route predicted from B route (fluctuations × √2) | {np.mean(preds):.2f} |")


# ------------------------------------------------------------------- pairing
BETAS = [0.5, 1.0, 1.5, 2.0, 3.0]


def _pairing_batch(args):
    arch, M, b_mult = args
    raw, table = calibrated()
    g = dict(raw["globals"])
    cfgs, agent_sets = [], []
    for beta in BETAS:
        agents = []
        for k in range(M):
            a = archetype_centre(arch, table)
            a.update(id=f"a{k}", nu=0.0, beta=beta, kappa=0.0)
            a["B"] = a["B"] * b_mult
            a.pop("archetype", None)
            a["delta"] = [a["delta"][2]] * 4  # flat ladder: no circle feedback on decay
            agents.append(a)
        sym = np.full((M, M), 0.5)
        pert = sym + np.random.default_rng(M * 10 + int(beta * 10)).uniform(-0.02, 0.02, (M, M))
        pert = 0.5 * (pert + pert.T)
        cfgs += [clique_config(agents, sym, g, 3000.0, step=0.2), clique_config(agents, pert, g, 3000.0, step=0.2)]
        agent_sets.append(agents)
    tr = solve_meanfield(cfgs, occupancy="exponential")
    ga = load_config(cfgs[0]).globals
    off = ~np.eye(M, dtype=bool)
    rows = []
    for b, (beta, agents) in enumerate(zip(BETAS, agent_sets)):
        xs, xp = tr.x[-1, 2 * b][off], tr.x[-1, 2 * b + 1][off]
        x_sym = float(xs.mean())
        # elasticity of the dyad interaction rate in x at the symmetric state
        q = forms.reciprocity_ratio(tr.r[-1, 2 * b][off].mean(), tr.o[-1, 2 * b][off].mean(), ga["o0"])
        gq = forms.reciprocity_weight(q, agents[0]["rho_star"])
        load = float(tr.budget[-1, 2 * b].mean() / agents[0]["B"])
        P = float(forms.acceptance_probability(x_sym, gq, load, ga["a0"], ga["a"], ga["b"], ga["c"]))
        beta_eff = (1 - agents[0]["epsilon"]) * beta + ga["a"] * x_sym * (1 - P)
        crit = beta_eff * (1 - x_sym)
        rows.append({"archetype": arch, "M": M, "B": agents[0]["B"], "beta": beta, "x_sym": x_sym, "P": P, "beta_eff": beta_eff,
                     "criterion": crit, "predicted_split": bool(crit > 1),
                     "spread_after": float(xp.std()), "max_after": float(xp.max()), "min_after": float(xp.min())})
    return rows


def cmd_pairing(a):
    jobs = list(itertools.product(["transactional_c", "loyal_few_c"], [8], [1.0, 0.3, 0.15, 0.08]))
    with ProcessPoolExecutor(a.workers) as ex:
        rows = [r for batch in ex.map(_pairing_batch, jobs) for r in batch]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pairing.json").write_text(json.dumps(rows, indent=1))
    print("| archetype | M | B | β | x_sym | β_eff | β_eff (1 − x_sym) | predicted | spread after perturbation | min–max x |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['archetype']} | {r['M']} | {r['B']:.2g} | {r['beta']} | {r['x_sym']:.3f} | {r['beta_eff']:.2f} | "
              f"{r['criterion']:.2f} | {'split' if r['predicted_split'] else 'equal'} | {r['spread_after']:.3f} | "
              f"{r['min_after']:.2f}–{r['max_after']:.2f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["meanfield", "shotnoise", "abm", "pairing"])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    {"meanfield": cmd_meanfield, "shotnoise": cmd_shotnoise, "abm": cmd_abm, "pairing": cmd_pairing}[a.cmd](a)


if __name__ == "__main__":
    main()
