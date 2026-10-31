"""Experiment 03: long-run outcome of an isolated dyad for every archetype pair.

Mean-field dyad (no encounters, no shocks) started at x_ab = x_ba = x0 for several
x0, for the built-in archetypes and for the calibrated set of experiment 02.
Prints a Markdown table of the steady closeness in both directions.

    python experiments/03_dyad_archetype_pairs.py > results/03_dyad_archetype_pairs.md
"""
from pathlib import Path

import yaml

from asym.meanfield.dyad import archetype_pairs

NAMES = ["butterfly", "loyal_few", "transactional", "avoidant"]
STARTS = (0.1, 0.5, 0.9)
HERE = Path(__file__).resolve().parent


def sets():
    cal = yaml.safe_load((HERE / "02_calibrated_layering_scaling.yaml").read_text())["base"]
    return [("built-in archetypes (γ 0.5, a0 0.5)", None, {"gamma": 0.5, "a0": 0.5}, NAMES),
            ("calibrated archetypes (experiment 02)", cal["archetypes"], cal["globals"], [n + "_c" for n in NAMES])]


def main():
    for label, arch, glob, names in sets():
        tabs = {x0: archetype_pairs(names, x0=(x0, x0), horizon=600.0, globals_=glob, archetypes=arch) for x0 in STARTS}
        print(f"### {label}\n")
        print("| A → B | " + " | ".join(f"x0={x0}: x_AB / x_BA (outcome)" for x0 in STARTS) + " |")
        print("|---|" + "---|" * len(STARTS))
        for i, a in enumerate(names):
            for b in names[i:]:
                cells = [f"{t[(a, b)]['x_ab']:.2f} / {t[(a, b)]['x_ba']:.2f} ({t[(a, b)]['outcome']})" for t in tabs.values()]
                print(f"| {a} → {b} | " + " | ".join(cells) + " |")
        print()


if __name__ == "__main__":
    main()
