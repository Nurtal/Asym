"""Experiment 04: embedded-dyad outcomes per archetype pair and neighbourhood size.

Each focal agent sits in a clique of M background partners of its own archetype
(ties at x_bg = 0.5); the focal tie starts at x0 = 0.1, 0.5 or 0.9. Built-in
archetypes, γ 0.5, a0 0.5, horizon 600. Prints Markdown tables.

    python experiments/04_embedded_dyad_pairs.py > results/04_embedded_dyad_pairs.md
"""
from asym.meanfield.embedded import embedded_pairs

NAMES = ["butterfly", "loyal_few", "transactional", "avoidant"]
STARTS = ((0.1, 0.1), (0.5, 0.5), (0.9, 0.9))
SHORT = {"breakup": "B", "acquaintance": "Q", "asymmetric": "A", "friendship": "F"}


def main():
    for M in (2, 4, 8):
        tab = embedded_pairs(NAMES, starts=STARTS, n_background=M, globals_={"gamma": 0.5, "a0": 0.5}, horizon=600.0)
        print(f"### M = {M} background partners\n")
        print("| A → B | " + " | ".join(f"x0={s[0]}" for s in STARTS) + " |")
        print("|---|" + "---|" * len(STARTS))
        for i, a in enumerate(NAMES):
            for b in NAMES[i:]:
                cells = [f"{SHORT[d['outcome']]} {d['x_ab']:.2f} / {d['x_ba']:.2f}" for d in tab[(a, b)]]
                print(f"| {a} → {b} | " + " | ".join(cells) + " |")
        print()


if __name__ == "__main__":
    main()
