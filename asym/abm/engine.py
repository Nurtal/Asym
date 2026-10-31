"""PDMP event engine (docs/model-spec.md, ADR-0001).

Between events, every tie follows the deterministic flow (``forms.advance_tie_flow``).
Ties are advanced lazily, only when they are read or modified, and all of them are
advanced at housekeeping checks and sample times. Stochastic events are drawn by
thinning against constant upper bounds of their rates, so the simulation is exact
for the PDMP. Circle transitions and forgetting are checked after events on the ties
those events touch, and at every housekeeping check (``simulation.check_interval``).
"""
from __future__ import annotations

import heapq
import math

import numpy as np

from asym.config import Config, load_config
from asym.initial import initial_ties
from asym.model import forms
from asym.result import SimulationResult


class Tie:
    __slots__ = ("x", "r", "o", "circle", "since", "t")

    def __init__(self, x, r, o, circle, since, t):
        self.x, self.r, self.o, self.circle, self.since, self.t = x, r, o, circle, since, t


class Engine:
    def __init__(self, cfg: Config, seed: int):
        self.cfg = cfg
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.g = cfg.globals
        self.sim = cfg.simulation
        self.var = cfg.variants
        self.N = cfg.n_agents
        self.ids = cfg.agent_ids
        self.agents = cfg.agents
        self.record = bool(self.sim["record_events"])

        self.ties: dict[tuple[int, int], Tie] = {}
        self.out: list[dict[int, Tie]] = [dict() for _ in range(self.N)]
        self.B = np.array([a["B"] for a in self.agents], dtype=float)  # effective capacity
        self.U = np.zeros(self.N)  # committed budget
        self.U_pending = np.zeros(self.N)  # part of U held by pending invitations
        self.events: list[dict] = []
        self.scheduled: list = []  # heap of (time, seq, kind, payload)
        self._seq = 0
        self.t = 0.0

        for (i, j), vals in initial_ties(cfg, self.rng).items():
            self._create_tie(i, j, **vals, log=False)

    # ----------------------------------------------------------------- helpers
    def log(self, kind, **data):
        if self.record:
            ev = {"t": self.t, "type": kind}
            for k, v in data.items():
                ev[k] = self.ids[v] if k in ("i", "j", "k") else v
            self.events.append(ev)

    def schedule(self, time, kind, payload):
        self._seq += 1
        heapq.heappush(self.scheduled, (time, self._seq, kind, payload))

    def _create_tie(self, i, j, x, r=0.0, o=0.0, circle=None, log=True):
        if circle is None:
            circle = forms.initial_circle(x, self.g["thresholds"])
        tie = Tie(float(x), float(r), float(o), int(circle), self.t, self.t)
        self.ties[(i, j)] = tie
        self.out[i][j] = tie
        return tie

    def _delete_tie(self, i, j):
        del self.ties[(i, j)]
        del self.out[i][j]

    def advance(self, i, tie: Tie):
        """Bring one tie of agent i up to the current time with the flow."""
        dt = self.t - tie.t
        if dt <= 0:
            return tie
        a = self.agents[i]
        tie.x, tie.r, tie.o = forms.advance_tie_flow(
            tie.x, tie.r, tie.o, dt,
            delta=a["delta"][tie.circle - 1], kappa=a["kappa"], ell=a["ell"], rho_star=a["rho_star"],
            lam=a["lam"], o0=self.g["o0"], mu_s=self.var["surplus_boost"], max_step=self.sim["ode_step"],
        )
        tie.t = self.t
        return tie

    def advance_all(self):
        for (i, _j), tie in self.ties.items():
            self.advance(i, tie)

    # --------------------------------------------------------------- run loop
    def _rate_components(self):
        """Return (bounds, handlers) for stochastic event channels. Overridden by mechanisms."""
        return [], []

    def run(self) -> SimulationResult:
        horizon = self.sim["horizon"]
        burn_in, dt_s = self.sim["burn_in"], self.sim["sample_interval"]
        dt_c = self.sim["check_interval"]
        n_samples = int(math.floor((horizon - burn_in) / dt_s + 1e-9)) + 1
        sample_times = burn_in + dt_s * np.arange(n_samples)
        samples = []
        k_sample, k_check = 0, 1

        while True:
            t_sample = sample_times[k_sample] if k_sample < n_samples else math.inf
            t_check = k_check * dt_c
            t_heap = self.scheduled[0][0] if self.scheduled else math.inf
            t_sched = min(t_sample, t_check, t_heap)
            if t_sched > horizon + 1e-9:
                break
            bounds, handlers = self._rate_components()
            total = float(sum(bounds)) if bounds else 0.0
            if total > 0:
                t_next = self.t + self.rng.exponential(1.0 / total)
                if t_next < t_sched:
                    self.t = t_next
                    k = _pick(self.rng, bounds, total)
                    handlers[k]()
                    continue
            self.t = t_sched
            if t_sched == t_heap:
                _, _, kind, payload = heapq.heappop(self.scheduled)
                self.handle_scheduled(kind, payload)
            elif t_sched == t_sample:
                self.advance_all()
                self.housekeeping()
                samples.append(self._snapshot())
                k_sample += 1
            else:
                self.advance_all()
                self.housekeeping()
                k_check += 1

        return self._result(sample_times, samples)

    def handle_scheduled(self, kind, payload):
        raise NotImplementedError(kind)

    def housekeeping(self):
        """Circle transitions and forgetting on every tie (overridden by mechanisms)."""

    # ----------------------------------------------------------------- output
    def _snapshot(self):
        rows = [(self.t, i, j, tie.x, tie.r, tie.o, tie.circle) for (i, j), tie in self.ties.items()]
        return rows, self.U.copy(), self.U_pending.copy(), self.B.copy()

    def _result(self, sample_times, samples) -> SimulationResult:
        rows = [r for s in samples for r in s[0]]
        cols = list(zip(*rows)) if rows else [[]] * 7
        ties = {
            "t": np.array(cols[0], dtype=float),
            "i": np.array(cols[1], dtype=np.int32),
            "j": np.array(cols[2], dtype=np.int32),
            "x": np.array(cols[3], dtype=float),
            "r": np.array(cols[4], dtype=float),
            "o": np.array(cols[5], dtype=float),
            "circle": np.array(cols[6], dtype=np.int8),
        }
        n = self.N

        def stack(k):
            return np.array([s[k] for s in samples], dtype=float).reshape(len(samples), n)

        return SimulationResult(
            config=self.cfg.to_dict(),
            seed=self.seed,
            agent_ids=list(self.ids),
            times=np.asarray(sample_times, dtype=float),
            ties=ties,
            budget=stack(1),
            pending_budget=stack(2),
            capacity=stack(3),
            events=self.events,
        )


def _pick(rng, weights, total):
    u = rng.random() * total
    acc = 0.0
    for k, w in enumerate(weights):
        acc += w
        if u < acc:
            return k
    return len(weights) - 1


def simulate(config, seed: int = 0) -> SimulationResult:
    """Run one PDMP simulation. ``config``: mapping, YAML path or Config."""
    cfg = load_config(config)
    return Engine(cfg, int(seed)).run()
