"""Deterministic mean-field solver (docs/model-spec.md §9, ADR-0001).

Every stochastic channel of the PDMP engine is replaced by its expected rate. State
per ordered pair (i, j), stored as arrays of shape (K, N, N) for a batch of K
systems that share the same N (a single config has K = 1):

- ``x, r, o``: closeness, perceived reciprocity, own investment
- ``Pu, Ps``: expected numbers of pending invitations i→j that are still unanswered
  (``Pu``) or have been met with silence (``Ps``)
- ``Wu, Ws``: summed waiting ages of those invitations. Exits are memoryless, so
  dW/dt = P − (exit rate)·W holds exactly in expectation. These sums give the
  expected cancellation drop on r.
- ``circle, since``: the hybrid discrete part, updated after every step with the same
  hysteresis / dwell / forgetting rule as the engine (``forms.circle_transition_array``)

Interactions in progress follow the engine's deterministic duration d by default
(``occupancy="delay"``). The count in dyad {i, j} is the accepted-interaction rate
integrated over the last d time units, held at its start-of-step value within each
RK4 step. ``occupancy="exponential"`` instead uses dn/dt = A − n/d, which has the
same steady state; the dyad analysis uses this form.

Batching: ``MeanField([cfg_1, …, cfg_K])`` integrates K systems at once. Per-agent
parameters and numeric globals may differ across the batch; list-valued globals
(thresholds …) must agree.

Not represented: encounters (ν), shocks and the dormant variant, which are pure noise
sources; a warning is issued if they are enabled. A tie that does not exist has
x = 0 and is not a target of non-exploration invitations, as in the engine. A tie
that receives interactions grows continuously from 0 rather than jumping to x0.
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass

import numpy as np

from asym.config import Config, ConfigError, load_config
from asym.initial import initial_ties
from asym.model import forms

AGENT_ROW = ("B", "beta", "epsilon", "kappa", "ell", "rho_star", "lam", "tau", "w", "m", "pi")
LIST_GLOBALS = ("thresholds", "shock_phi", "shock_budget_phi")


def _swap(a):
    return np.swapaxes(a, -1, -2)


@dataclass
class Trajectory:
    agent_ids: list
    times: np.ndarray  # (T,)
    x: np.ndarray  # (T, N, N)  — or (T, K, N, N) for a batch
    r: np.ndarray
    o: np.ndarray
    circle: np.ndarray  # int, 0 where the tie does not exist
    pending: np.ndarray  # Pu + Ps
    budget: np.ndarray  # (T, N) / (T, K, N) expected committed budget U_i
    accept_rate: np.ndarray  # expected accepted invitations i→j per unit time

    def index(self, agent_id) -> int:
        return self.agent_ids.index(agent_id)

    def trajectory(self, i, j) -> dict:
        ii, jj = self.index(i), self.index(j)
        return {"t": self.times, "x": self.x[..., ii, jj], "r": self.r[..., ii, jj], "o": self.o[..., ii, jj],
                "circle": self.circle[..., ii, jj]}


class MeanField:
    def __init__(self, cfgs, occupancy: str = "delay"):
        single = isinstance(cfgs, Config) or not isinstance(cfgs, (list, tuple))
        cfgs = [load_config(cfgs)] if single else [load_config(c) for c in cfgs]
        self.single = single
        self.cfgs = cfgs
        self.cfg = cfg = cfgs[0]
        self.K, self.N = K, N = len(cfgs), cfg.n_agents
        if any(c.n_agents != N for c in cfgs):
            raise ConfigError("all configs of a mean-field batch need the same number of agents")
        if occupancy not in ("delay", "exponential"):
            raise ConfigError("occupancy must be 'delay' or 'exponential'")
        self.occupancy = occupancy
        for c in cfgs:
            if c.globals["shock_rate"] > 0 or any(a["nu"] > 0 for a in c.agents):
                warnings.warn("mean-field solver ignores encounters (nu) and shocks", stacklevel=3)
                break
        if any(c.variants["dormant"] for c in cfgs):
            warnings.warn("mean-field solver ignores the dormant variant (forgotten ties are deleted)", stacklevel=3)

        # per-agent parameters: (K, N, 1) for the inviter row i, alpha as (K, 1, N) for invitee j
        def agent_param(k):
            return np.array([[a[k] for a in c.agents] for c in cfgs], dtype=float)[:, :, None]

        for k in AGENT_ROW:
            setattr(self, "p_" + k, agent_param(k))
        self.B = self.p_B[:, :, 0]  # (K, N)
        self.alpha_j = np.array([[a["alpha"] for a in c.agents] for c in cfgs], dtype=float)[:, None, :]
        self.delta = np.array([[a["delta"] for a in c.agents] for c in cfgs], dtype=float)  # (K, N, 4)

        # globals: scalar when shared by the whole batch, else a (K, 1, 1) array
        self.g = {}
        for key, val in cfg.globals.items():
            vals = [c.globals[key] for c in cfgs]
            if key in LIST_GLOBALS or isinstance(val, (list, tuple)):
                if any(v != val for v in vals):
                    raise ConfigError(f"globals.{key} must agree across a mean-field batch")
                self.g[key] = val
            elif all(v == val for v in vals):
                self.g[key] = float(val)
            else:
                self.g[key] = np.array(vals, dtype=float)[:, None, None]
        self.var = dict(cfg.variants)
        for key in ("surplus_boost", "guilt", "capacity_cost"):
            vals = [c.variants[key] for c in cfgs]
            self.var[key] = float(vals[0]) if all(v == vals[0] for v in vals) else np.array(vals, float)[:, None, None]
        if any(c.variants["circle_capacity"] != cfg.variants["circle_capacity"] for c in cfgs):
            raise ConfigError("variants.circle_capacity must agree across a mean-field batch")

        self.offdiag = ~np.eye(N, dtype=bool)
        self.perc = forms.mean_perception(self.p_pi, self.g["sigma_p"]) * self.g["inv_unit"]  # (K, N, 1)

        x = np.zeros((K, N, N))
        r = np.zeros((K, N, N))
        o = np.zeros((K, N, N))
        circle = np.zeros((K, N, N), dtype=int)
        for b, c in enumerate(cfgs):
            for (i, j), v in initial_ties(c, np.random.default_rng(0)).items():
                x[b, i, j], r[b, i, j], o[b, i, j] = v["x"], v["r"], v["o"]
                circle[b, i, j] = v["circle"] or forms.initial_circle(v["x"], self.g["thresholds"])
        self.circle = circle
        self.since = np.zeros((K, N, N))
        z = np.zeros((K, N, N))
        self.y = np.stack([x, r, o, z, z, z, z])  # (7, K, N, N)

    # ------------------------------------------------------------------ rates
    def _delta_c(self, circle):
        idx = np.clip(circle, 1, 4) - 1
        return np.take_along_axis(self.delta, idx, axis=-1)

    def rates(self, y, n_inter, circle=None):
        """Time derivative of the continuous state (7, K, N, N), plus diagnostics."""
        g = self.g
        circle = self.circle if circle is None else circle
        x, r, o, Pu, Ps, Wu, Ws = y
        exists = (circle > 0) & self.offdiag
        q = forms.reciprocity_ratio(r, o, g["o0"])
        gq = forms.reciprocity_weight(q, self.p_rho_star)  # ρ* of the row agent

        U = n_inter.sum(axis=-1) + g["c_wait"] * (Pu + Ps).sum(axis=-1)  # (K, N)
        F = np.maximum(0.0, self.B - U)
        wts = np.where(exists, np.where(x > 0, x, 0.0) ** self.p_beta * gq, 0.0)
        wsum = wts.sum(axis=-1, keepdims=True)
        share = np.where(wsum > 0, wts / np.where(wsum > 0, wsum, 1.0), 0.0)
        explore = np.where(self.offdiag, 1.0 / max(self.N - 1, 1), 0.0)
        Iss = g["gamma"] * F[..., None] * (self.p_epsilon * explore + (1.0 - self.p_epsilon) * share)

        # acceptance by j of an invitation from i uses j's view of i: swap the last two axes
        load = (U / self.B)[..., None, :]
        P = forms.acceptance_probability(_swap(x), _swap(gq), load, g["a0"], g["a"], g["b"], g["c"])
        P = np.where(self.offdiag, P, 0.0)
        c = forms.cancellation_hazard(self.p_tau, g["h1"], x)

        acc = g["omega"] * Pu * P + g["zeta"] * Ps * P  # accepted i→j invitations per unit time
        A = acc + _swap(acc)  # interactions in dyad {i, j}
        dec = g["omega"] * Pu * (1.0 - P) * (1.0 - self.alpha_j)
        to_silent = g["omega"] * Pu * (1.0 - P) * self.alpha_j

        dPu = Iss - (g["omega"] + c) * Pu
        dPs = to_silent - (g["zeta"] * P + c) * Ps
        dWu = Pu - (g["omega"] + c) * Wu
        dWs = Ps + g["omega"] * (1.0 - P) * self.alpha_j * Wu - (g["zeta"] * P + c) * Ws

        eta = g["eta"]
        K_c, cost = self.var["circle_capacity"], self.var["capacity_cost"]
        if K_c is not None and np.any(cost):
            counts = np.stack([(circle == k).sum(axis=-1) for k in range(1, 5)], axis=-1)  # (K, N, 4)
            ci = np.clip(circle, 1, 4) - 1
            n_c = np.take_along_axis(counts, ci, axis=-1)
            eta = eta * forms.capacity_factor(n_c, np.asarray(K_c)[ci], cost)
        dx = eta * (1.0 - x) * A + forms.closeness_drift(
            x, q, self._delta_c(circle), self.p_kappa, self.p_ell, self.p_rho_star, self.var["surplus_boost"])
        if np.any(self.var["guilt"]):
            dx = dx - self.var["guilt"] * x * _swap(c * (Pu + Ps))  # cancellations of i→j hit x_ji
        dr = A * self.perc - self.p_lam * r - g["psi"] * (1.0 - self.p_ell * x) * c * (Wu + Ws)
        do = A * g["inv_unit"] + g["c_rej"] * g["inv_unit"] * dec * exists - self.p_lam * o
        d = np.stack([dx, dr, do, dPu, dPs, dWu, dWs])
        d[..., ~self.offdiag] = 0.0
        return d, A, U, acc

    # ------------------------------------------------------------------- run
    def step(self, h, n_inter):
        """One RK4 step of the continuous state; returns the start/end interaction rates."""
        y = self.y
        k1, A1, _, _ = self.rates(y, n_inter)
        k2, _, _, _ = self.rates(y + 0.5 * h * k1, n_inter)
        k3, _, _, _ = self.rates(y + 0.5 * h * k2, n_inter)
        k4, _, _, _ = self.rates(y + h * k3, n_inter)
        self.y = y + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        self.y[0] = np.clip(self.y[0], 0.0, 1.0)
        self.y[1:] = np.maximum(self.y[1:], 0.0)
        return A1

    def run(self) -> Trajectory:
        sim, g = self.cfg.simulation, self.g
        h = float(sim["mf_step"])
        horizon, burn_in, dt_s = sim["horizon"], sim["burn_in"], sim["sample_interval"]
        n_samples = int(math.floor((horizon - burn_in) / dt_s + 1e-9)) + 1
        sample_times = burn_in + dt_s * np.arange(n_samples)
        d_scalar = float(np.max(g["d"]))
        lag = max(1, int(round(d_scalar / h)))
        shape = (self.K, self.N, self.N)
        history = np.zeros((lag,) + shape)
        n_exp = np.zeros(shape)
        hpos = 0
        out = {k: [] for k in ("x", "r", "o", "circle", "pending", "budget", "accept_rate")}
        t, k_s = 0.0, 0
        n_steps = int(math.ceil(horizon / h - 1e-9))
        for step in range(n_steps + 1):
            n_inter = history.sum(axis=0) * h if self.occupancy == "delay" else n_exp
            while k_s < n_samples and sample_times[k_s] <= t + 1e-9:
                _, _, U, acc = self.rates(self.y, n_inter)
                self._record(out, U, acc)
                k_s += 1
            if step == n_steps:
                break
            A1 = self.step(h, n_inter)
            _, A_new, _, _ = self.rates(self.y, n_inter)
            if self.occupancy == "delay":
                history[hpos] = 0.5 * (A1 + A_new)
                hpos = (hpos + 1) % lag
            else:
                n_exp = n_exp + h * (0.5 * (A1 + A_new) - n_exp / g["d"])
            t = (step + 1) * h
            self.hybrid(t)
        arrays = {k: np.array(v) for k, v in out.items()}
        if self.single:
            arrays = {k: v[:, 0] for k, v in arrays.items()}
        return Trajectory(agent_ids=list(self.cfg.agent_ids), times=sample_times, **arrays)

    def _record(self, out, U, acc):
        x, r, o, Pu, Ps, _, _ = self.y
        out["x"].append(x.copy())
        out["r"].append(r.copy())
        out["o"].append(o.copy())
        out["circle"].append(self.circle.copy())
        out["pending"].append(Pu + Ps)
        out["budget"].append(U.copy())
        out["accept_rate"].append(acc.copy())

    def hybrid(self, t):
        """Ties come into existence, forgetting, circle transitions (hysteresis + dwell)."""
        g = self.g
        x = self.y[0]
        born = (self.circle == 0) & self.offdiag & (x >= g["x_min"]) & (x > 0)
        self.circle = np.where(born, 1, self.circle)
        self.since = np.where(born, t, self.since)
        forgotten = (self.circle > 0) & (x < g["x_min"])
        if forgotten.any():
            self.circle = np.where(forgotten, 0, self.circle)
            self.y[0:3] = np.where(forgotten, 0.0, self.y[0:3])
        ready = (self.circle > 0) & (t - self.since >= self.p_m - 1e-9)
        new = forms.circle_transition_array(self.circle, x, g["thresholds"], self.p_w)
        moved = ready & (new != self.circle)
        self.circle = np.where(moved, new, self.circle)
        self.since = np.where(moved, t, self.since)


def solve_meanfield(config, occupancy: str = "delay") -> Trajectory:
    """Integrate the deterministic mean-field system for a config accepted by ``simulate``.

    ``config`` may also be a list of configs with the same number of agents; they are
    integrated together as a batch, and the arrays get an extra batch axis after time.
    """
    return MeanField(config, occupancy=occupancy).run()
