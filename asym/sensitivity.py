"""Global sensitivity analysis: Morris elementary-effects screening.

Factors are defined on ranges and mapped from the unit cube. Each factor addresses a
part of a raw config:

- ``globals.<key>``: a global parameter, set to the value
- ``thresholds.<k>``: circle threshold k (0, 1, 2), set to the value
- ``archetypes.<param>``: a *multiplier* on that parameter of every archetype used by
  the population. A list such as the δ ladder is scaled elementwise. Parameters in
  [0, 1] are clipped.

Design (Morris 1991; Campolongo et al. 2007): ``r`` random one-at-a-time trajectories
on a ``levels``-grid of the unit cube, with step Δ = levels / (2 (levels − 1)). Each
trajectory changes one factor at a time, so k factors cost r (k + 1) runs. Indices,
per factor and per output, are computed on the unit-cube scale so that factors with
different units can be compared:

- μ: mean elementary effect
- μ*: mean absolute elementary effect (importance)
- σ: standard deviation of the elementary effects (non-linearity or interactions)
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass

import numpy as np

from asym.config import AGENT_DEFAULTS, GLOBAL_DEFAULTS, UNIT_INTERVAL_AGENT_PARAMS, ConfigError
from asym.model.archetypes import archetype_table


@dataclass(frozen=True)
class Factor:
    name: str
    path: str
    low: float
    high: float
    log: bool = False

    def value(self, u: float) -> float:
        if self.log:
            return float(math.exp(math.log(self.low) + u * (math.log(self.high) - math.log(self.low))))
        return float(self.low + u * (self.high - self.low))


def morris_design(k: int, r: int, levels: int = 4, seed: int = 0) -> np.ndarray:
    """(r, k + 1, k) array of unit-cube points: r trajectories of k + 1 points each."""
    if levels < 2 or levels % 2:
        raise ValueError("levels must be an even integer >= 2")
    rng = np.random.default_rng(seed)
    delta = levels / (2 * (levels - 1))
    grid = np.arange(levels // 2) / (levels - 1)  # starting values from which +Δ stays in [0, 1]
    out = np.empty((r, k + 1, k))
    for t in range(r):
        x = rng.choice(grid, size=k)
        sign = rng.choice([-1.0, 1.0], size=k)
        x = np.where(sign < 0, x + delta, x)  # a negative step starts from the upper half
        order = rng.permutation(k)
        out[t, 0] = x
        for s, f in enumerate(order):
            x = x.copy()
            x[f] += sign[f] * delta
            out[t, s + 1] = x
    return out


def morris_indices(design: np.ndarray, outputs: np.ndarray) -> dict:
    """Morris indices from a design (r, k+1, k) and outputs (r, k+1) or (r, k+1, n_out).

    Returns {"mu", "mu_star", "sigma", "n"}, each of shape (k,) or (k, n_out); ``n`` counts
    the finite elementary effects per factor (non-finite outputs are skipped).
    """
    Y = np.asarray(outputs, dtype=float)
    squeeze = Y.ndim == 2
    if squeeze:
        Y = Y[..., None]
    r, kp1, k = design.shape
    ee = [[] for _ in range(k)]
    for t in range(r):
        for s in range(k):
            dx = design[t, s + 1] - design[t, s]
            f = int(np.flatnonzero(dx)[0])
            ee[f].append((Y[t, s + 1] - Y[t, s]) / dx[f])
    n_out = Y.shape[-1]
    mu, mu_star, sigma, n = (np.full((k, n_out), np.nan) for _ in range(4))
    for f in range(k):
        E = np.array(ee[f])  # (r, n_out)
        for o in range(n_out):
            e = E[:, o][np.isfinite(E[:, o])]
            n[f, o] = e.size
            if e.size:
                mu[f, o], mu_star[f, o] = e.mean(), np.abs(e).mean()
                sigma[f, o] = e.std(ddof=1) if e.size > 1 else 0.0
    res = {"mu": mu, "mu_star": mu_star, "sigma": sigma, "n": n}
    return {key: v[:, 0] for key, v in res.items()} if squeeze else res


def apply_factors(raw: dict, factors, u) -> dict:
    """Copy of ``raw`` with every factor set from its unit-cube coordinate in ``u``."""
    raw = copy.deepcopy(raw)
    table = archetype_table(raw.get("archetypes"))
    names = list((raw.get("population") or {}).get("composition", {}))
    for fac, ui in zip(factors, u):
        v = fac.value(float(ui))
        head, _, key = fac.path.partition(".")
        if head == "globals":
            raw.setdefault("globals", {})[key] = v
        elif head == "thresholds":
            g = raw.setdefault("globals", {})
            th = list(g.get("thresholds", GLOBAL_DEFAULTS["thresholds"]))
            th[int(key)] = v
            g["thresholds"] = th
        elif head == "archetypes":
            if not names:
                raise ConfigError("archetype factors need a population composition")
            arch = raw.setdefault("archetypes", {})
            for nm in names:
                centre = copy.deepcopy(AGENT_DEFAULTS)
                centre.update(table[nm])
                centre.update(arch.get(nm, {}))
                base = centre[key]
                if isinstance(base, (list, tuple)):
                    new = [float(b) * v for b in base]
                else:
                    new = float(base) * v
                    if key in UNIT_INTERVAL_AGENT_PARAMS or key == "ell":
                        new = min(1.0, max(0.0, new))
                spec = arch.setdefault(nm, {})
                if "base" not in spec and nm in table and nm not in (raw.get("archetypes") or {}):
                    spec["base"] = nm
                spec[key] = new
        else:
            raise ConfigError(f"unknown factor path {fac.path!r}")
    if "thresholds" in raw.get("globals", {}):
        th = raw["globals"]["thresholds"]
        if any(b <= a for a, b in zip(th, th[1:])):
            raise ConfigError(f"factor values give non-increasing thresholds {th}")
    return raw
