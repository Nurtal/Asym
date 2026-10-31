"""Experiment 10: Morris screening of the calibrated model (experiment 06 base, N = 100).

18 factors (archetype multipliers and global parameters) × r trajectories, so
r · 19 ABM runs. To shorten the transient each run starts from a random
acquaintance network (density 0.2, x ~ U(0.05, 0.3)), with horizon 600 and burn-in
300. Results go to ``results/morris/`` (design, outputs, indices).

    python experiments/10_morris.py run [--r 10] [--workers 8]
    python experiments/10_morris.py report > results/morris/report.md
"""
import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from asym import metrics
from asym.abm.engine import simulate
from asym.experiments import _agent_counts, condition_configs, load_experiment
from asym.sensitivity import Factor, apply_factors, morris_design, morris_indices

OUT = Path("results/morris")
FACTORS = [
    Factor("budget B", "archetypes.B", 0.5, 2.0, log=True),
    Factor("decay δ", "archetypes.delta", 0.5, 2.0, log=True),
    Factor("concentration β", "archetypes.beta", 0.5, 2.0, log=True),
    Factor("encounter rate ν", "archetypes.nu", 0.5, 2.0, log=True),
    Factor("exploration ε", "archetypes.epsilon", 0.5, 2.0, log=True),
    Factor("deficit sensitivity κ", "archetypes.kappa", 0.5, 2.0, log=True),
    Factor("reciprocity expectation ρ*", "archetypes.rho_star", 0.85, 1.15),
    Factor("loyalty ℓ", "archetypes.ell", 0.5, 1.25),
    Factor("patience τ", "archetypes.tau", 0.5, 2.0, log=True),
    Factor("hysteresis w", "archetypes.w", 0.5, 2.0, log=True),
    Factor("memory rate λ", "archetypes.lam", 0.5, 2.0, log=True),
    Factor("gain η", "globals.eta", 0.045, 0.18, log=True),
    Factor("issuing rate γ", "globals.gamma", 0.425, 1.7, log=True),
    Factor("acceptance intercept a0", "globals.a0", -0.5, 1.5),
    Factor("acceptance weight a", "globals.a", 2.0, 6.0),
    Factor("forgetting x_min", "globals.x_min", 0.01, 0.04, log=True),
    Factor("first closeness x0", "globals.x0", 0.05, 0.2, log=True),
    Factor("inner threshold θ4", "thresholds.2", 0.76, 0.88),
]
OUTPUTS = ["inner", "+close", "+friends", "all", "ratio 1", "ratio 2", "ratio 3", "mu", "abs asymmetry",
           "one-sided", "high-mode share"]


def base_config():
    raw = condition_configs(load_experiment("experiments/06_dunbar_calibrated_scaling.yaml"))["n100"]
    raw["init"] = {"mode": "random", "density": 0.2, "x_range": [0.05, 0.3]}
    raw["simulation"].update(horizon=600.0, burn_in=300.0, sample_interval=25.0, record_events=False)
    return raw


def outputs(res):
    K = len(res.times)
    L = np.mean([metrics.layering(res, at=k)["mean_layer_sizes"] for k in range(K)], axis=0)
    ratios = L[1:] / np.where(L[:-1] > 0, L[:-1], np.nan)
    mu = metrics.layer_exponent(_agent_counts(res).mean(axis=0))
    late = range(max(0, K - 3), K)
    asy = [metrics.asymmetry(res, at=k) for k in late]
    absd = np.mean([np.mean(a["abs_diff"]) if len(a["abs_diff"]) else np.nan for a in asy])
    one = np.mean([a["one_sided"] for a in asy])
    hi = np.mean([np.mean(res.snapshot(k)["x"] >= 0.75) if len(res.snapshot(k)["x"]) else np.nan for k in range(K)])
    return [*L, *ratios, mu, absd, one, hi]


def _run(u):
    t = time.time()
    try:
        y = outputs(simulate(apply_factors(base_config(), FACTORS, u), seed=0))
    except Exception as e:  # keep the design complete; a failed point becomes NaN
        print(f"failed at {u}: {e!r}", file=sys.stderr)
        y = [np.nan] * len(OUTPUTS)
    return y, time.time() - t


def run(r, workers, seed):
    OUT.mkdir(parents=True, exist_ok=True)
    D = morris_design(len(FACTORS), r, levels=4, seed=seed)
    pts = D.reshape(-1, len(FACTORS))
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(_run, pts))
    Y = np.array([y for y, _ in res], dtype=float).reshape(r, len(FACTORS) + 1, len(OUTPUTS))
    np.savez(OUT / "morris.npz", design=D, outputs=Y, seconds=np.array([s for _, s in res]))
    idx = morris_indices(D, Y)
    (OUT / "indices.json").write_text(json.dumps({
        "factors": [f.name for f in FACTORS], "outputs": OUTPUTS, "r": r, "seed": seed,
        **{k: v.tolist() for k, v in idx.items()}}, indent=1))
    print(f"done: {len(pts)} runs, mean {np.mean([s for _, s in res]):.0f}s per run")


def report():
    J = json.loads((OUT / "indices.json").read_text())
    F, O = J["factors"], J["outputs"]
    ms, sg = np.array(J["mu_star"]), np.array(J["sigma"])
    D = np.load(OUT / "morris.npz")
    Y = D["outputs"].reshape(-1, len(O))
    print(f"Morris screening, r = {J['r']} trajectories, {Y.shape[0]} runs.\n")
    print("Output ranges over the design (min / median / max):\n")
    for o, col in zip(O, Y.T):
        c = col[np.isfinite(col)]
        print(f"- {o}: {c.min():.3g} / {np.median(c):.3g} / {c.max():.3g}")
    for o_i, o in enumerate(O):
        order = np.argsort(-np.nan_to_num(ms[:, o_i], nan=-1))
        print(f"\n### {o}\n\n| factor | μ* | μ | σ |\n|---|---|---|---|")
        mu = np.array(J["mu"])
        for f in order:
            print(f"| {F[f]} | {ms[f, o_i]:.3g} | {mu[f, o_i]:+.3g} | {sg[f, o_i]:.3g} |")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--r", type=int, default=10)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    run(a.r, a.workers, a.seed) if a.cmd == "run" else report()
