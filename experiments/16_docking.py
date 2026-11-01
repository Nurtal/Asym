"""Experiment 16: docking of the ABM with the mean-field ODE (data for the docking figure).

The dyad of ``tests/test_09_meanfield.py`` is scaled towards its fluid limit: budgets
× s, and jump sizes (η, investment unit, cancellation drop) / s. As s grows, the ABM
ensemble mean should converge to the mean-field trajectory, at rate O(s^-1/2) for
the fluctuations. Two regimes are checked:

- **sustained**: the dyad holds;
- **decaying**: the dyad fades.

For each s, n seeds are run. The output stores the ABM mean and SD of x_ab(t) and
x_ba(t), the mean-field trajectory, and the maximum absolute error. A sampling
floor, 2·SD/√n, is stored alongside.

    python experiments/16_docking.py [--seeds 200] [--workers 4]
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

SCALES = [1, 2, 4, 8, 16, 32, 64]
OUT = Path("results/16_docking.json")


def _cfg(s, regime):
    from test_09_meanfield import _scaled
    return _scaled(s, regime)


def _abm(args):
    from asym import simulate
    s, regime, seed = args
    r = simulate(_cfg(s, regime), seed=seed)
    return r.trajectory("a", "b")["x"].tolist(), r.trajectory("b", "a")["x"].tolist()


def main():
    from asym import solve_meanfield
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    out = []
    with ProcessPoolExecutor(a.workers) as ex:
        for regime in ("sustained", "decaying"):
            for s in SCALES:
                mf = solve_meanfield(_cfg(s, regime))
                runs = list(ex.map(_abm, [(s, regime, k) for k in range(a.seeds)]))
                row = {"regime": regime, "s": s, "t": mf.trajectory("a", "b")["t"].tolist(), "n": a.seeds}
                err, floor = 0.0, 0.0
                for d, (i, j) in enumerate((("a", "b"), ("b", "a"))):
                    X = np.array([r[d] for r in runs])
                    m, sd = X.mean(axis=0), X.std(axis=0, ddof=1)
                    f = mf.trajectory(i, j)["x"]
                    row[f"abm_mean_{i}{j}"], row[f"abm_sd_{i}{j}"], row[f"mf_{i}{j}"] = m.tolist(), sd.tolist(), f.tolist()
                    err = max(err, float(np.abs(m - f).max()))
                    floor = max(floor, float((2 * sd / np.sqrt(a.seeds)).max()))
                row["max_error"], row["sampling_floor"] = err, floor
                out.append(row)
                print(f"{regime} s={s}: max error {err:.4f} (sampling floor {floor:.4f})", flush=True)
    OUT.write_text(json.dumps(out))


if __name__ == "__main__":
    main()
