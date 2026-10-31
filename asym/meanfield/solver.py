"""Deterministic mean-field solver (docs/model-spec.md §9, ADR-0001).

Every stochastic channel of the PDMP engine is replaced by its expected rate. State
per ordered pair (i, j), stored as N×N arrays:

- ``x, r, o``: closeness, perceived reciprocity, own investment
- ``Pu, Ps``: expected numbers of pending invitations i→j that are still unanswered
  (``Pu``) or have been met with silence (``Ps``)
- ``Wu, Ws``: summed waiting ages of those invitations. Exits are memoryless, so
  dW/dt = P − (exit rate)·W holds exactly in expectation. These sums give the
  expected cancellation drop on r.
- ``circle, since``: the hybrid discrete part, updated after every step with the same
  hysteresis / dwell / forgetting rules as the engine

Interactions in progress follow the engine's deterministic duration d. The count of
interactions in progress in dyad {i, j} is the accepted-interaction rate integrated
over the last d time units (a delay term), held at its start-of-step value within
each RK4 step.

Not represented: encounters (ν) and shocks, which are pure noise sources; a warning
is issued if they are enabled. A tie that does not exist has x = 0 and is not a
target of non-exploration invitations, as in the engine. A tie that receives
interactions grows continuously from 0 rather than jumping to x0.
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass

import numpy as np

from asym.config import Config, load_config
from asym.initial import initial_ties
from asym.model import forms


@dataclass
class Trajectory:
    agent_ids: list
    times: np.ndarray  # (T,)
    x: np.ndarray  # (T, N, N)
    r: np.ndarray
    o: np.ndarray
    circle: np.ndarray  # (T, N, N) int, 0 where the tie does not exist
    pending: np.ndarray  # (T, N, N) Pu + Ps
    budget: np.ndarray  # (T, N) expected committed budget U_i
    accept_rate: np.ndarray  # (T, N, N) expected accepted interactions i→j per unit time

    def index(self, agent_id) -> int:
        return self.agent_ids.index(agent_id)

    def trajectory(self, i, j) -> dict:
        ii, jj = self.index(i), self.index(j)
        return {"t": self.times, "x": self.x[:, ii, jj], "r": self.r[:, ii, jj], "o": self.o[:, ii, jj],
                "circle": self.circle[:, ii, jj]}


class MeanField:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        g, var = cfg.globals, cfg.variants
        A = cfg.agents
        self.N = N = cfg.n_agents
        if g["shock_rate"] > 0 or any(a["nu"] > 0 for a in A):
            warnings.warn("mean-field solver ignores encounters (nu) and shocks", stacklevel=3)
        if cfg.variants["dormant"]:
            warnings.warn("mean-field solver ignores the dormant variant (forgotten ties are deleted)", stacklevel=3)
        col = lambda k: np.array([a[k] for a in A], dtype=float)[:, None]  # noqa: E731  (per inviter i, broadcast over j)
        self.B, self.beta, self.eps = col("B")[:, 0], col("beta"), col("epsilon")
        self.kappa, self.ell, self.rho, self.lam = col("kappa"), col("ell"), col("rho_star"), col("lam")
        self.tau, self.w, self.m, self.pi = col("tau"), col("w"), col("m"), col("pi")
        self.alpha_j = np.array([a["alpha"] for a in A], dtype=float)[None, :]  # invitee j
        self.delta = np.array([a["delta"] for a in A], dtype=float)  # (N, 4)
        self.g, self.var = g, var
        self.offdiag = ~np.eye(N, dtype=bool)
        self.perc = forms.mean_perception(self.pi, g["sigma_p"]) * g["inv_unit"]  # (N, 1)

        x = np.zeros((N, N))
        r = np.zeros((N, N))
        o = np.zeros((N, N))
        circle = np.zeros((N, N), dtype=int)
        for (i, j), v in initial_ties(cfg, np.random.default_rng(0)).items():
            x[i, j], r[i, j], o[i, j] = v["x"], v["r"], v["o"]
            circle[i, j] = v["circle"] or forms.initial_circle(v["x"], g["thresholds"])
        self.circle = circle
        self.since = np.zeros((N, N))
        z = np.zeros((N, N))
        # continuous state vector: x, r, o, Pu, Ps, Wu, Ws
        self.y = np.stack([x, r, o, z, z, z, z])

    # ------------------------------------------------------------------ rates
    def _delta_c(self):
        idx = np.clip(self.circle, 1, 4) - 1
        return np.take_along_axis(self.delta, idx, axis=1)

    def rates(self, y, n_inter):
        """Derivative of the continuous state, plus diagnostics."""
        g = self.g
        x, r, o, Pu, Ps, Wu, Ws = y
        exists = (self.circle > 0) & self.offdiag
        q = forms.reciprocity_ratio(r, o, g["o0"])
        gq = forms.reciprocity_weight(q, self.rho)  # (N,N), rho per inviter row

        U = n_inter.sum(axis=1) + g["c_wait"] * (Pu + Ps).sum(axis=1)
        F = np.maximum(0.0, self.B - U)
        # target choice
        wts = np.where(exists, np.where(x > 0, x, 0.0) ** self.beta * gq, 0.0)
        wsum = wts.sum(axis=1, keepdims=True)
        share = np.where(wsum > 0, wts / np.where(wsum > 0, wsum, 1.0), 0.0)
        explore = np.where(self.offdiag, 1.0 / max(self.N - 1, 1), 0.0)
        Iss = g["gamma"] * F[:, None] * (self.eps * explore + (1.0 - self.eps) * share)

        # acceptance by j of an invitation from i uses j's view of i: transpose
        gq_T = gq.T  # gq_T[i, j] = g(q_ji) with rho of j
        xT = x.T
        load = (U / self.B)[None, :]
        P = forms.acceptance_probability(xT, gq_T, load, g["a0"], g["a"], g["b"], g["c"])
        P = np.where(self.offdiag, P, 0.0)
        c = forms.cancellation_hazard(self.tau, g["h1"], x)

        acc = g["omega"] * Pu * P + g["zeta"] * Ps * P  # accepted i→j invitations per unit time
        A = acc + acc.T  # interactions in dyad {i, j}
        dec = g["omega"] * Pu * (1.0 - P) * (1.0 - self.alpha_j)
        to_silent = g["omega"] * Pu * (1.0 - P) * self.alpha_j

        dPu = Iss - (g["omega"] + c) * Pu
        dPs = to_silent - (g["zeta"] * P + c) * Ps
        dWu = Pu - (g["omega"] + c) * Wu
        dWs = Ps + g["omega"] * (1.0 - P) * self.alpha_j * Wu - (g["zeta"] * P + c) * Ws

        delta_c = self._delta_c()
        eta = g["eta"]
        K, cost = self.var["circle_capacity"], self.var["capacity_cost"]
        if K is not None and cost:
            counts = np.stack([(self.circle == c).sum(axis=1) for c in range(1, 5)], axis=1)  # (N, 4)
            ci = np.clip(self.circle, 1, 4) - 1
            n_c = np.take_along_axis(counts, ci, axis=1)
            eta = eta * forms.capacity_factor(n_c, np.asarray(K)[ci], cost)
        dx = eta * (1.0 - x) * A + forms.closeness_drift(
            x, q, delta_c, self.kappa, self.ell, self.rho, self.var["surplus_boost"])
        if self.var["guilt"]:
            dx = dx - self.var["guilt"] * x * (c * (Pu + Ps)).T  # cancellations of i→j hit x_ji
        dr = A * self.perc - self.lam * r - g["psi"] * (1.0 - self.ell * x) * c * (Wu + Ws)
        do = A * g["inv_unit"] + g["c_rej"] * g["inv_unit"] * dec * exists - self.lam * o
        d = np.stack([dx, dr, do, dPu, dPs, dWu, dWs])
        d[:, ~self.offdiag] = 0.0
        return d, A, U, acc

    # ------------------------------------------------------------------- run
    def run(self) -> Trajectory:
        sim, g = self.cfg.simulation, self.g
        h = float(sim["mf_step"])
        horizon, burn_in, dt_s = sim["horizon"], sim["burn_in"], sim["sample_interval"]
        n_samples = int(math.floor((horizon - burn_in) / dt_s + 1e-9)) + 1
        sample_times = burn_in + dt_s * np.arange(n_samples)
        lag = max(1, int(round(g["d"] / h)))
        history = np.zeros((lag, self.N, self.N))  # accepted-interaction rate over the last d
        hpos = 0
        out = {k: [] for k in ("x", "r", "o", "circle", "pending", "budget", "accept_rate")}
        t, k_s = 0.0, 0
        n_steps = int(math.ceil(horizon / h - 1e-9))
        for step in range(n_steps + 1):
            n_inter = history.sum(axis=0) * h
            while k_s < n_samples and sample_times[k_s] <= t + 1e-9:
                _, _, U, acc = self.rates(self.y, n_inter)
                self._record(out, U, acc)
                k_s += 1
            if step == n_steps:
                break
            y = self.y
            k1, A1, _, _ = self.rates(y, n_inter)
            k2, _, _, _ = self.rates(y + 0.5 * h * k1, n_inter)
            k3, _, _, _ = self.rates(y + 0.5 * h * k2, n_inter)
            k4, _, _, _ = self.rates(y + h * k3, n_inter)
            self.y = y + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
            self.y[0] = np.clip(self.y[0], 0.0, 1.0)
            self.y[1:] = np.maximum(self.y[1:], 0.0)
            _, A_new, _, _ = self.rates(self.y, n_inter)
            history[hpos] = 0.5 * (A1 + A_new)
            hpos = (hpos + 1) % lag
            t = (step + 1) * h
            self._hybrid(t)
        return Trajectory(
            agent_ids=list(self.cfg.agent_ids), times=sample_times,
            **{k: np.array(v) for k, v in out.items()},
        )

    def _record(self, out, U, acc):
        x, r, o, Pu, Ps, _, _ = self.y
        out["x"].append(x.copy())
        out["r"].append(r.copy())
        out["o"].append(o.copy())
        out["circle"].append(self.circle.copy())
        out["pending"].append(Pu + Ps)
        out["budget"].append(U.copy())
        out["accept_rate"].append(acc.copy())

    def _hybrid(self, t):
        """Ties come into existence, circle transitions (hysteresis + dwell), forgetting."""
        g = self.g
        x = self.y[0]
        th = g["thresholds"]
        born = (self.circle == 0) & self.offdiag & (x >= g["x_min"]) & (x > 0)
        if born.any():
            self.circle[born] = 1
            self.since[born] = t
        for i, j in zip(*np.nonzero(self.circle > 0)):
            if x[i, j] < g["x_min"]:
                self.circle[i, j] = 0
                self.y[0:3, i, j] = 0.0
                continue
            if t - self.since[i, j] < self.m[i, 0] - 1e-9:
                continue
            new = forms.circle_transition(int(self.circle[i, j]), x[i, j], th, self.w[i, 0])
            if new != self.circle[i, j]:
                self.circle[i, j] = new
                self.since[i, j] = t


def solve_meanfield(config) -> Trajectory:
    """Integrate the deterministic mean-field system for a config accepted by ``simulate``."""
    return MeanField(load_config(config)).run()
