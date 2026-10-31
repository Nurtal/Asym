"""Experiment harness: versioned YAML experiment + seed list → stored ensemble results.

An experiment file looks like::

    name: layering_empty_vs_random
    description: ...
    base: {<a full simulation config>}
    seeds: [0, 1, 2]            # or {range: [0, 10]}
    conditions:                 # optional; named deep-merged overrides of ``base``
      empty:  {init: {mode: empty}}
      random: {init: {mode: random, density: 0.05}}
    analysis: [layering]        # optional; analyses run after the simulations

``run_experiment`` writes ``<out>/<name>/<condition>/seed_<k>.npz`` plus a
``manifest.json``. The manifest records the experiment file, the resolved configs,
the seeds, the code version (git commit, plus a dirty flag) and a content hash of
every result. Running the same experiment twice gives identical results.

Command line::

    python -m asym.experiments run experiments/01_layering_empty_vs_random.yaml [--out results] [--workers 4]
    python -m asym.experiments analyse results/layering_empty_vs_random
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import yaml
from scipy import stats

from asym import metrics
from asym.abm.engine import simulate
from asym.config import ConfigError, load_config
from asym.result import SimulationResult

EXPERIMENT_KEYS = {"name", "description", "base", "seeds", "conditions", "analysis"}


def deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_experiment(path) -> dict:
    path = Path(path)
    spec = yaml.safe_load(path.read_text())
    if not isinstance(spec, dict):
        raise ConfigError("experiment file must be a mapping")
    unknown = set(spec) - EXPERIMENT_KEYS
    if unknown:
        raise ConfigError(f"unknown experiment key(s) {sorted(unknown)}")
    for key in ("name", "base", "seeds"):
        if key not in spec:
            raise ConfigError(f"experiment needs '{key}'")
    seeds = spec["seeds"]
    if isinstance(seeds, dict):
        seeds = list(range(*seeds["range"]))
    spec["seeds"] = [int(s) for s in seeds]
    spec.setdefault("conditions", {"default": {}})
    spec.setdefault("analysis", [])
    spec["_path"] = str(path)
    spec["_base_dir"] = str(path.parent)
    return spec


def condition_configs(spec: dict) -> dict:
    """Resolved raw config per condition (file paths relative to the experiment file)."""
    out = {}
    for name, override in spec["conditions"].items():
        raw = deep_merge(spec["base"], override or {})
        raw.setdefault("init", {})
        raw["_base_dir"] = spec["_base_dir"]
        load_config(raw)  # validate early
        out[name] = raw
    return out


def code_version() -> dict:
    root = Path(__file__).resolve().parent.parent
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "asym"], cwd=root, capture_output=True,
                                    text=True, check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        rev, dirty = None, None
    from importlib.metadata import PackageNotFoundError, version
    try:
        pkg = version("asym")
    except PackageNotFoundError:
        pkg = None
    return {"git_commit": rev, "git_dirty": dirty, "package_version": pkg, "python": sys.version.split()[0]}


def result_hash(res: SimulationResult) -> str:
    h = hashlib.sha256()
    for arr in (res.times, res.budget, res.pending_budget, res.capacity, *(res.ties[k] for k in sorted(res.ties))):
        h.update(np.ascontiguousarray(arr).tobytes())
    h.update(json.dumps(res.events, sort_keys=True, default=float).encode())
    return h.hexdigest()


def _run_one(args):
    raw, seed, path = args
    res = simulate(raw, seed=seed)
    res.save(path)
    return str(path), result_hash(res)


def run_experiment(path, out_dir="results", workers: int = 1, analyse: bool = True) -> Path:
    """Run every (condition, seed) of an experiment and store the results; returns the run directory."""
    spec = load_experiment(path)
    configs = condition_configs(spec)
    version = code_version()  # captured before running: the code that produced the results
    run_dir = Path(out_dir) / spec["name"]
    jobs = []
    for cond, raw in configs.items():
        (run_dir / cond).mkdir(parents=True, exist_ok=True)
        jobs += [(raw, s, run_dir / cond / f"seed_{s}.npz") for s in spec["seeds"]]
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            done = list(ex.map(_run_one, jobs))
    else:
        done = [_run_one(j) for j in jobs]
    manifest = {
        "name": spec["name"],
        "description": spec.get("description", ""),
        "experiment_file": spec["_path"],
        "experiment": {k: v for k, v in spec.items() if not k.startswith("_")},
        "configs": {c: load_config(raw).to_dict() for c, raw in configs.items()},
        "seeds": spec["seeds"],
        "code": version,
        "results": {str(Path(p).relative_to(run_dir)): h for p, h in done},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=float))
    if analyse and spec["analysis"]:
        report = analyse_run(run_dir, spec["analysis"])
        (run_dir / "analysis.json").write_text(json.dumps(report, indent=2, default=_jsonable))
    return run_dir


def load_run(run_dir) -> dict:
    """{condition: [SimulationResult, …]} for a stored run, in seed order."""
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text())
    out = {}
    for cond in manifest["configs"]:
        out[cond] = [SimulationResult.load(run_dir / cond / f"seed_{s}.npz") for s in manifest["seeds"]]
    return out


# ------------------------------------------------------------------- analyses
def _ci(values, level=0.95):
    v = np.asarray(values, dtype=float)
    n = v.size
    mean = float(v.mean()) if n else math.nan
    if n < 2:
        return {"mean": mean, "ci": [math.nan, math.nan], "n": n}
    half = float(stats.t.ppf(0.5 + level / 2, n - 1) * v.std(ddof=1) / math.sqrt(n))
    return {"mean": mean, "ci": [mean - half, mean + half], "n": n}


def layering_per_run(res: SimulationResult) -> np.ndarray:
    """Time-averaged (post-burn-in) mean cumulative layer sizes of one run, shape (4,)."""
    if len(res.times) == 0:
        return np.full(4, math.nan)
    return np.mean([metrics.layering(res, at=k)["mean_layer_sizes"] for k in range(len(res.times))], axis=0)


def analyse_layering(runs: dict) -> dict:
    """Layer sizes and ratios per condition with 95% CIs, plus Welch tests between conditions."""
    per_cond = {c: np.array([layering_per_run(r) for r in rs]) for c, rs in runs.items()}
    report = {"conditions": {}, "comparisons": {}}
    for c, L in per_cond.items():
        with np.errstate(divide="ignore", invalid="ignore"):
            ratios = L[:, 1:] / L[:, :-1]
        report["conditions"][c] = {
            "layer_sizes": [_ci(L[:, k]) for k in range(4)],
            "layer_ratios": [_ci(ratios[:, k][np.isfinite(ratios[:, k])]) for k in range(3)],
        }
    names = list(per_cond)
    for a_i, a in enumerate(names):
        for b in names[a_i + 1:]:
            tests = []
            for k in range(4):
                xa, xb = per_cond[a][:, k], per_cond[b][:, k]
                t, p = stats.ttest_ind(xa, xb, equal_var=False) if len(xa) > 1 and len(xb) > 1 else (math.nan, math.nan)
                tests.append({"layer": k, "t": float(t), "p": float(p), "diff": float(xa.mean() - xb.mean())})
            report["comparisons"][f"{a}_vs_{b}"] = tests
    return report


ANALYSES = {"layering": analyse_layering}


def analyse_run(run_dir, names) -> dict:
    runs = load_run(run_dir)
    out = {}
    for n in names:
        if n not in ANALYSES:
            raise ConfigError(f"unknown analysis {n!r}; known: {sorted(ANALYSES)}")
        out[n] = ANALYSES[n](runs)
    return out


def _jsonable(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m asym.experiments")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run an experiment file")
    r.add_argument("experiment")
    r.add_argument("--out", default="results")
    r.add_argument("--workers", type=int, default=1)
    a = sub.add_parser("analyse", help="(re)analyse a stored run")
    a.add_argument("run_dir")
    a.add_argument("--analysis", nargs="*", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        run_dir = run_experiment(args.experiment, args.out, args.workers)
        print(run_dir)
        if (run_dir / "analysis.json").exists():
            print((run_dir / "analysis.json").read_text())
    else:
        manifest = json.loads((Path(args.run_dir) / "manifest.json").read_text())
        names = args.analysis or manifest["experiment"].get("analysis") or ["layering"]
        print(json.dumps(analyse_run(args.run_dir, names), indent=2, default=_jsonable))


if __name__ == "__main__":
    main()
