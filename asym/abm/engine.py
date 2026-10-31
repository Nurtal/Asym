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


class Invitation:
    __slots__ = ("id", "i", "j", "t_issue", "silent")

    def __init__(self, inv_id, i, j, t_issue):
        self.id, self.i, self.j, self.t_issue, self.silent = inv_id, i, j, t_issue, False


EPS = 1e-9


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
        self.pending: dict[int, Invitation] = {}
        self._inv_seq = 0
        self.tau = np.array([a["tau"] for a in self.agents], dtype=float)

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
    def free(self, i) -> float:
        return self.B[i] - self.U[i]

    def _rate_components(self):
        """Upper bounds of every stochastic channel, and the handler firing each one.

        Handlers receive no argument; they draw the concrete actor themselves and
        perform the thinning acceptance step where the true rate is state dependent.
        """
        g = self.g
        bounds, handlers = [], []
        free = self.B - self.U
        issue = np.where(free >= 1.0 - EPS, free, 0.0) * g["gamma"]
        total_issue = float(issue.sum())
        if total_issue > 0:
            bounds.append(total_issue)
            handlers.append(lambda w=issue, tot=total_issue: self.issue(_pick(self.rng, w, tot)))
        if self.pending:
            invs = list(self.pending.values())
            new = [inv for inv in invs if not inv.silent]
            silent = [inv for inv in invs if inv.silent]
            if new and g["omega"] > 0:
                bounds.append(g["omega"] * len(new))
                handlers.append(lambda new=new: self.respond(new[int(self.rng.integers(len(new)))]))
            if silent and g["zeta"] > 0:
                bounds.append(g["zeta"] * len(silent))
                handlers.append(lambda silent=silent: self.late_response(silent[int(self.rng.integers(len(silent)))]))
            cancel = [1.0 / self.tau[inv.i] for inv in invs]
            total_cancel = float(sum(cancel))
            bounds.append(total_cancel)
            handlers.append(lambda invs=invs, w=cancel, tot=total_cancel: self.maybe_cancel(invs[_pick(self.rng, w, tot)]))
        return bounds, handlers

    # ------------------------------------------------------------ invitations
    def choose_target(self, i) -> int:
        a = self.agents[i]
        candidates = list(self.out[i].items())
        weights = []
        if candidates and self.rng.random() >= a["epsilon"]:
            for _j, tie in candidates:
                self.advance(i, tie)
                q = forms.reciprocity_ratio(tie.r, tie.o, self.g["o0"])
                weights.append(tie.x ** a["beta"] * forms.reciprocity_weight(q, a["rho_star"]))
            total = float(sum(weights))
            if total > 0:
                return candidates[_pick(self.rng, weights, total)][0]
        j = int(self.rng.integers(self.N - 1))
        return j + 1 if j >= i else j

    def issue(self, i):
        if self.N < 2:
            return
        j = self.choose_target(i)
        self._inv_seq += 1
        inv = Invitation(self._inv_seq, i, j, self.t)
        self.pending[inv.id] = inv
        cw = self.g["c_wait"]
        self.U[i] += cw
        self.U_pending[i] += cw
        self.log("invite", i=i, j=j, inv=inv.id)

    def _release_pending(self, inv):
        del self.pending[inv.id]
        cw = self.g["c_wait"]
        self.U[inv.i] -= cw
        self.U_pending[inv.i] -= cw

    def acceptance(self, inv) -> float:
        """Probability that the invitee accepts now (0 if either side cannot honour it)."""
        i, j, g = inv.i, inv.j, self.g
        if self.free(j) < 1.0 - EPS or self.free(i) + g["c_wait"] < 1.0 - EPS:
            return 0.0
        tie = self.out[j].get(i)
        if tie is not None:
            self.advance(j, tie)
            x, q = tie.x, forms.reciprocity_ratio(tie.r, tie.o, g["o0"])
        else:
            x, q = 0.0, 1.0
        gj = forms.reciprocity_weight(q, self.agents[j]["rho_star"])
        load = self.U[j] / self.B[j]
        return float(forms.acceptance_probability(x, gj, load, g["a0"], g["a"], g["b"], g["c"]))

    def respond(self, inv):
        if self.rng.random() < self.acceptance(inv):
            self.accept(inv, "accept")
        else:
            self.not_accepted(inv)

    def not_accepted(self, inv):
        if self.rng.random() < self.agents[inv.j]["alpha"]:
            inv.silent = True
            self.log("silence", i=inv.i, j=inv.j, inv=inv.id)
            return
        self._release_pending(inv)
        tie = self.out[inv.i].get(inv.j)
        if tie is not None:
            self.advance(inv.i, tie)
            tie.o += self.g["c_rej"] * self.g["inv_unit"]
        self.log("decline", i=inv.i, j=inv.j, inv=inv.id)

    def late_response(self, inv):
        # thinning: true rate ζ·P_acc against bound ζ
        if self.rng.random() < self.acceptance(inv):
            self.accept(inv, "late_accept")

    def maybe_cancel(self, inv):
        i, j, g = inv.i, inv.j, self.g
        tie = self.out[i].get(j)
        x = self.advance(i, tie).x if tie is not None else 0.0
        # thinning: true hazard 1/(τ(1+h1·x)) against bound 1/τ
        if self.rng.random() >= 1.0 / (1.0 + g["h1"] * x):
            return
        self._release_pending(inv)
        wait = self.t - inv.t_issue
        dr = 0.0
        if tie is not None:
            r_new = float(forms.cancellation_drop(tie.r, g["psi"], self.agents[i]["ell"], tie.x, wait))
            dr, tie.r = tie.r - r_new, r_new
        self.log("cancel", i=i, j=j, inv=inv.id, wait=wait, dr=dr)
        self.on_cancel(inv)
        if tie is not None:
            self.check_tie(i, j)

    def on_cancel(self, inv):
        """Hook for the invitee-side effect of a cancellation (guilt variant)."""

    def _ensure_tie(self, i, j):
        tie = self.out[i].get(j)
        if tie is None:
            tie = self._create_tie(i, j, self.g["x0"])
        return self.advance(i, tie)

    def _perceived(self, i) -> float:
        a, g = self.agents[i], self.g
        xi = self.rng.normal(0.0, g["sigma_p"]) if g["sigma_p"] > 0 else 0.0
        return g["inv_unit"] * math.exp(a["pi"] + xi)

    def accept(self, inv, kind):
        i, j, g = inv.i, inv.j, self.g
        self._release_pending(inv)
        self.U[i] += 1.0
        self.U[j] += 1.0
        self.schedule(self.t + g["d"], "interaction_end", (i, j))
        for u, v in ((i, j), (j, i)):
            tie = self._ensure_tie(u, v)
            tie.x = forms.interaction_jump(tie.x, g["eta"])
            tie.o += g["inv_unit"]
            tie.r += self._perceived(u)
        self.log(kind, i=i, j=j, inv=inv.id, wait=self.t - inv.t_issue)
        self.check_tie(i, j)
        self.check_tie(j, i)

    def handle_scheduled(self, kind, payload):
        if kind == "interaction_end":
            i, j = payload
            self.U[i] -= 1.0
            self.U[j] -= 1.0
            self.log("interaction_end", i=i, j=j)
        else:
            raise NotImplementedError(kind)

    def check_tie(self, i, j):
        """Forgetting and (dwell-gated, hysteretic) circle transition of one tie."""
        tie = self.out[i].get(j)
        if tie is None:
            return
        self.advance(i, tie)
        a = self.agents[i]
        if tie.x < self.g["x_min"]:
            self.forget(i, j, tie)
            return
        if self.t - tie.since < a["m"] - EPS:
            return
        new = forms.circle_transition(tie.circle, tie.x, self.g["thresholds"], a["w"])
        if new != tie.circle:
            kind = "promote" if new > tie.circle else "demote"
            self.log(kind, i=i, j=j, x=tie.x, **{"from": tie.circle, "to": new})
            tie.circle, tie.since = new, self.t

    def forget(self, i, j, tie):
        self._delete_tie(i, j)
        self.log("forget", i=i, j=j, x=tie.x, **{"from": tie.circle})

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

    def housekeeping(self):
        """Circle transitions and forgetting on every tie."""
        for i, j in list(self.ties):
            self.check_tie(i, j)

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
