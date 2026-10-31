"""Ticket 12: experiment harness and the layering experiment."""
import json
from pathlib import Path

import pytest
import yaml

from asym.experiments import load_experiment, load_run, run_experiment

REPO = Path(__file__).resolve().parent.parent


def _tiny_experiment(tmp_path):
    spec = {
        "name": "tiny_layering",
        "description": "small version of experiment 01",
        "base": {
            "population": {"composition": {"butterfly": 6, "loyal_few": 6, "transactional": 4, "avoidant": 4},
                           "noise": 0.1, "seed": 0},
            "globals": {"gamma": 0.5, "a0": 1.0},
            "simulation": {"horizon": 30.0, "burn_in": 10.0, "sample_interval": 5.0, "record_events": False},
        },
        "seeds": {"range": [0, 3]},
        "conditions": {"empty": {"init": {"mode": "empty"}},
                       "random": {"init": {"mode": "random", "density": 0.2}}},
        "analysis": ["layering"],
    }
    path = tmp_path / "tiny.yaml"
    path.write_text(yaml.safe_dump(spec))
    return path


def test_run_stores_results_manifest_and_analysis(tmp_path):
    run_dir = run_experiment(_tiny_experiment(tmp_path), tmp_path / "out")
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["seeds"] == [0, 1, 2]
    assert set(manifest["configs"]) == {"empty", "random"}
    assert "git_commit" in manifest["code"] and manifest["experiment"]["name"] == "tiny_layering"
    assert len(manifest["results"]) == 6
    runs = load_run(run_dir)
    assert [r.seed for r in runs["empty"]] == [0, 1, 2]
    report = json.loads((run_dir / "analysis.json").read_text())["layering"]
    for cond in ("empty", "random"):
        sizes = report["conditions"][cond]["layer_sizes"]
        assert len(sizes) == 4 and all(len(s["ci"]) == 2 for s in sizes)
        assert sizes[0]["mean"] <= sizes[3]["mean"]  # cumulative layers grow outwards
    assert len(report["comparisons"]["empty_vs_random"]) == 4


def test_rerun_is_identical(tmp_path):
    path = _tiny_experiment(tmp_path)
    a = json.loads((run_experiment(path, tmp_path / "a", analyse=False) / "manifest.json").read_text())
    b = json.loads((run_experiment(path, tmp_path / "b", workers=2, analyse=False) / "manifest.json").read_text())
    assert a["results"] == b["results"]


def test_shipped_experiment_files_are_valid():
    files = sorted((REPO / "experiments").glob("*.yaml"))
    assert files
    for f in files:
        spec = load_experiment(f)
        assert spec["seeds"]


def test_cli_runs(tmp_path, capsys):
    from asym.experiments import main
    main(["run", str(_tiny_experiment(tmp_path)), "--out", str(tmp_path / "cli")])
    out = capsys.readouterr().out
    assert "tiny_layering" in out and "layer_sizes" in out


def test_layering_by_archetype_analysis(tmp_path):
    from asym.experiments import analyse_run
    run_dir = run_experiment(_tiny_experiment(tmp_path), tmp_path / "out", analyse=False)
    report = analyse_run(run_dir, ["layering_by_archetype"])["layering_by_archetype"]
    groups = report["conditions"]["empty"]
    assert set(groups) == {"butterfly", "loyal_few", "transactional", "avoidant"}
    for g in groups.values():
        assert len(g["layer_sizes"]) == 4 and g["layer_sizes"][0]["n"] == 3


def test_layer_regime_analysis(tmp_path):
    from asym.experiments import analyse_run
    run_dir = run_experiment(_tiny_experiment(tmp_path), tmp_path / "out", analyse=False)
    rep = analyse_run(run_dir, ["layer_regime"])["layer_regime"]["conditions"]["empty"]
    assert len(rep["layer_counts"]) == 4 and rep["layer_counts"][0]["n"] == 3
    assert set(rep) >= {"layer_counts", "mu", "inverse_fraction", "by_archetype"}
    assert 0.0 <= rep["inverse_fraction"]["mean"] <= 1.0
    assert set(rep["by_archetype"]) == {"butterfly", "loyal_few", "transactional", "avoidant"}


def test_asymmetry_analysis(tmp_path):
    from asym.experiments import analyse_run
    run_dir = run_experiment(_tiny_experiment(tmp_path), tmp_path / "out", analyse=False)
    rep = analyse_run(run_dir, ["asymmetry"])["asymmetry"]["conditions"]["empty"]
    assert set(rep) >= {"unreciprocated", "correlation", "one_sided", "abs_asymmetry", "by_pair"}
    assert rep["unreciprocated"]["n"] == 3
    assert "butterfly->transactional" in rep["by_pair"]
    assert set(rep["by_pair"]["butterfly->transactional"]) == {"unreciprocated", "signed_asymmetry"}
