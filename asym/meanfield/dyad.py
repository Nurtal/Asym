"""Dyad analysis: 2-D reduction, fixed points, stability, outcome sweeps.

Research question 1 (docs/model-spec.md §10): for an isolated dyad {i, j}, which
regions of (x_ij, x_ji) lead to a stable friendship, a breakup or an asymmetric
state, and where do the bifurcations lie?

**Reduction.** The mean-field dyad has 13 continuous variables: x, r, o, Pu, Ps, Wu
and Ws in each direction, plus the interaction occupancy. Away from the slow
closeness dynamics, all of them except the two closenesses relax quickly (memories
at rate λ, invitations at rates ω and 1/τ, occupancy at rate 1/d). The reduced
system ``dx/dt = F(x_ij, x_ji)`` sets every fast variable to its quasi-steady state
for frozen (x_ij, x_ji). That state is found numerically by relaxing the
fast subsystem (``MeanField`` with x held fixed), so the reduced field reuses
exactly the same rates as the full solver. The reduction is valid when λ, ω, 1/τ and
1/d are large compared with δ and η·A. Circles are taken from x without hysteresis
in the reduced field (``forms.initial_circle``).

The quasi-steady state has no closed form, because of the sigmoid acceptance, the
load term and the ratio q. Fixed points and Jacobians are therefore computed
numerically (batched Newton iterations, central differences) rather than with SymPy.
"""
from __future__ import annotations

import copy
import itertools
from dataclasses import dataclass

import numpy as np

from asym.config import ConfigError, load_config
from asym.meanfield.solver import MeanField, solve_meanfield
from asym.model import forms
from asym.model.archetypes import archetype_centre, archetype_table

OUTCOMES = ("breakup", "acquaintance", "asymmetric", "friendship")


@dataclass
class FixedPoint:
    x: tuple  # (x_ij, x_ji)
    jacobian: np.ndarray
    eigenvalues: np.ndarray
    stability: str  # "stable", "saddle", "unstable"
    kind: str  # "node", "focus", "degenerate"


def classify_outcome(x_ij, x_ji, thresholds, x_min):
    """Outcome label of a long-run dyad state.

    - ``friendship``: both ties are at least friend level
    - ``asymmetric``: exactly one tie is
    - ``breakup``: both ties are below x_min (forgotten)
    - ``acquaintance``: otherwise
    """
    f = thresholds[0]
    a, b = np.asarray(x_ij), np.asarray(x_ji)
    out = np.full(np.broadcast(a, b).shape, "acquaintance", dtype=object)
    out[(a >= f) & (b >= f)] = "friendship"
    out[(a >= f) ^ (b >= f)] = "asymmetric"
    out[(a < x_min) & (b < x_min)] = "breakup"
    return out if out.shape else out.item()


class DyadAnalysis:
    """Reduced 2-D analysis of a two-agent config (agents in config order: i, j)."""

    def __init__(self, config, relax_step: float = 0.05, relax_tol: float = 1e-10, relax_max: int = 20000):
        self.cfg = load_config(config)
        if self.cfg.n_agents != 2:
            raise ConfigError("DyadAnalysis needs a config with exactly two agents")
        self.h, self.tol, self.max_iter = relax_step, relax_tol, relax_max
        self.thresholds = self.cfg.globals["thresholds"]

    # ------------------------------------------------------- reduced field
    def _batch(self, X):
        mf = MeanField([self.cfg] * len(X), occupancy="exponential")
        mf.y[:] = 0.0
        mf.y[0, :, 0, 1], mf.y[0, :, 1, 0] = X[:, 0], X[:, 1]
        circ = np.zeros((len(X), 2, 2), dtype=int)
        for k, (a, b) in enumerate(X):
            circ[k, 0, 1] = forms.initial_circle(a, self.thresholds)
            circ[k, 1, 0] = forms.initial_circle(b, self.thresholds)
        mf.circle = circ
        return mf

    def field(self, X):
        """Reduced vector field F at points X, shape (M, 2) → (M, 2)."""
        X = np.clip(np.atleast_2d(np.asarray(X, dtype=float)), 0.0, 1.0)
        mf = self._batch(X)
        n = np.zeros((len(X), 2, 2))
        d_int = mf.g["d"]
        for _ in range(self.max_iter):
            d, A, _, _ = mf.rates(mf.y, n)
            fast = np.where((mf.y[1:] <= 0.0) & (d[1:] < 0.0), 0.0, d[1:])  # clamped at 0: settled
            mf.y[1:] = np.maximum(mf.y[1:] + self.h * fast, 0.0)
            dn = A - n / d_int
            n = n + self.h * dn
            if max(np.abs(fast).max(), np.abs(dn).max()) < self.tol:
                break
        d, _, _, _ = mf.rates(mf.y, n)
        return np.stack([d[0, :, 0, 1], d[0, :, 1, 0]], axis=1)

    def grid(self, n: int = 41, lo: float = 0.0, hi: float = 1.0):
        """Reduced field on an n×n grid: (xs, U, V) with U[a, b] = F_ij(xs[a], xs[b])."""
        xs = np.linspace(lo, hi, n)
        P = np.array(list(itertools.product(xs, xs)))
        F = self.field(P)
        return xs, F[:, 0].reshape(n, n), F[:, 1].reshape(n, n)

    def jacobian(self, p, eps: float = 1e-5):
        p = np.asarray(p, dtype=float)
        pts = np.array([p + [eps, 0], p - [eps, 0], p + [0, eps], p - [0, eps]])
        F = self.field(pts)
        return np.column_stack([(F[0] - F[1]) / (2 * eps), (F[2] - F[3]) / (2 * eps)])

    # ------------------------------------------------------- fixed points
    def fixed_points(self, n_grid: int = 25, newton_iter: int = 30, tol: float = 1e-10):
        """Fixed points of the reduced field with their linear stability."""
        xs, U, V = self.grid(n_grid)
        seeds = []
        for a in range(n_grid - 1):
            for b in range(n_grid - 1):
                cu, cv = U[a:a + 2, b:b + 2], V[a:a + 2, b:b + 2]
                if cu.min() <= 0 <= cu.max() and cv.min() <= 0 <= cv.max():
                    seeds.append(((xs[a] + xs[a + 1]) / 2, (xs[b] + xs[b + 1]) / 2))
        found = []
        for s in seeds:
            p = self._newton(np.array(s), newton_iter, tol)
            if p is None or any(np.allclose(p, f.x, atol=1e-4) for f in found):
                continue
            J = self.jacobian(p)
            ev = np.linalg.eigvals(J)
            re = ev.real
            stability = "stable" if np.all(re < 0) else "unstable" if np.all(re > 0) else "saddle"
            kind = "focus" if np.any(np.abs(ev.imag) > 1e-9) else ("degenerate" if np.any(np.abs(re) < 1e-9) else "node")
            found.append(FixedPoint(tuple(float(v) for v in p), J, ev, stability, kind))
        return sorted(found, key=lambda f: f.x)

    def _newton(self, p, n_iter, tol):
        for _ in range(n_iter):
            F = self.field(p)[0]
            if np.abs(F).max() < tol:
                return p
            J = self.jacobian(p)
            try:
                step = np.linalg.solve(J, -F)
            except np.linalg.LinAlgError:
                return None
            lam = 1.0
            while lam > 1e-3:
                cand = np.clip(p + lam * step, 0.0, 1.0)
                if np.abs(self.field(cand)[0]).max() < np.abs(F).max():
                    break
                lam /= 2
            p = cand
        return p if np.abs(self.field(p)[0]).max() < 1e-7 else None

    def is_bistable(self, **kw) -> bool:
        return sum(f.stability == "stable" for f in self.fixed_points(**kw)) >= 2

    # ------------------------------------------------------- forward runs
    def integrate(self, x0, horizon: float = 300.0, step: float = 0.05):
        """Integrate the full mean-field dyad (exponential occupancy) from closeness x0."""
        raw = _with_initial(self.cfg.to_dict(), x0)
        raw["simulation"].update({"horizon": horizon, "burn_in": 0.0, "sample_interval": horizon, "mf_step": step})
        tr = solve_meanfield(raw, occupancy="exponential")
        return np.array([tr.x[-1, 0, 1], tr.x[-1, 1, 0]])


# ------------------------------------------------------------- sweeps / tables
def _with_initial(raw: dict, x0, r0=None, o0=None):
    raw = copy.deepcopy(raw)
    ids = [a["id"] for a in raw["agents"]]
    r0 = (1.0, 1.0) if r0 is None else r0
    o0 = (1.0, 1.0) if o0 is None else o0
    raw["init"] = {"mode": "file", "ties": [
        {"i": ids[0], "j": ids[1], "x": float(x0[0]), "r": r0[0], "o": o0[0]},
        {"i": ids[1], "j": ids[0], "x": float(x0[1]), "r": r0[1], "o": o0[1]},
    ]}
    return raw


def _set_path(raw: dict, path: str, value):
    parts = path.split(".")
    if parts[0] == "agents":
        targets = raw["agents"] if parts[1] == "*" else [raw["agents"][int(parts[1])]]
        for a in targets:
            a[parts[2]] = value
    else:
        node = raw.setdefault(parts[0], {})
        for p in parts[1:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = value


def sweep(config, axes: dict, x0=(0.5, 0.5), horizon: float = 300.0, step: float = 0.05):
    """Long-run dyad outcome over a parameter grid (batched mean-field integration).

    ``axes`` maps a parameter path to its values. A path is ``globals.<key>``,
    ``variants.<key>``, ``agents.<k>.<param>`` or ``agents.*.<param>`` (both agents).
    Returns {"axes", "x_ij", "x_ji", "outcome"}; each grid has one dimension per axis.
    """
    base = load_config(config).to_dict()
    names = list(axes)
    values = [list(axes[k]) for k in names]
    configs = []
    for combo in itertools.product(*values):
        raw = _with_initial(base, x0)
        for path, v in zip(names, combo):
            _set_path(raw, path, v)
        raw["simulation"].update({"horizon": horizon, "burn_in": 0.0, "sample_interval": horizon, "mf_step": step})
        configs.append(raw)
    tr = solve_meanfield(configs, occupancy="exponential")
    shape = tuple(len(v) for v in values)
    xij = tr.x[-1, :, 0, 1].reshape(shape)
    xji = tr.x[-1, :, 1, 0].reshape(shape)
    g = load_config(configs[0]).globals
    return {"axes": dict(zip(names, values)), "x_ij": xij, "x_ji": xji,
            "outcome": classify_outcome(xij, xji, g["thresholds"], g["x_min"])}


def archetype_pairs(names=None, x0=(0.5, 0.5), horizon: float = 300.0, globals_=None, archetypes=None,
                    step: float = 0.05):
    """Long-run outcome of every ordered archetype pair, from archetype centres.

    Returns {(A, B): {"outcome", "x_ab", "x_ba"}}.
    """
    table = archetype_table(archetypes)
    names = list(names or table)
    configs, pairs = [], []
    for a, b in itertools.product(names, names):
        ca, cb = archetype_centre(a, table), archetype_centre(b, table)
        raw = {"agents": [{**ca, "id": "A", "nu": 0.0}, {**cb, "id": "B", "nu": 0.0}],
               "globals": dict(globals_ or {}),
               "simulation": {"horizon": horizon, "sample_interval": horizon, "mf_step": step}}
        configs.append(_with_initial(raw, x0))
        pairs.append((a, b))
    tr = solve_meanfield(configs, occupancy="exponential")
    g = load_config(configs[0]).globals
    out = {}
    for k, pair in enumerate(pairs):
        xab, xba = float(tr.x[-1, k, 0, 1]), float(tr.x[-1, k, 1, 0])
        out[pair] = {"outcome": classify_outcome(xab, xba, g["thresholds"], g["x_min"]), "x_ab": xab, "x_ba": xba}
    return out
