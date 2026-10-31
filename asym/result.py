"""SimulationResult: the structured, serialisable output of ``simulate``."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

TIE_COLUMNS = ("t", "i", "j", "x", "r", "o", "circle")


@dataclass
class SimulationResult:
    config: dict  # fully-resolved config (Config.to_dict())
    seed: int
    agent_ids: list
    times: np.ndarray  # (S,) sample times
    ties: dict  # columnar arrays, one row per (sample, existing directed tie)
    budget: np.ndarray  # (S, N) committed budget U_i
    pending_budget: np.ndarray  # (S, N) part of U_i held by pending invitations
    capacity: np.ndarray  # (S, N) effective budget B_i (reduced during budget shocks)
    events: list = field(default_factory=list)  # dicts: {"t", "type", ...}

    @classmethod
    def build(cls, agent_ids, times, rows, budget=None, pending_budget=None, capacity=None, events=None,
              config=None, seed=0):
        """Assemble a result by hand from rows ``(t, i, j, x, r, o, circle)`` (agent ids or indices)."""
        ids = list(agent_ids)
        idx = {a: k for k, a in enumerate(ids)}
        conv = lambda a: idx[a] if a in idx else int(a)  # noqa: E731
        rows = list(rows)
        cols = list(zip(*rows)) if rows else [[]] * 7
        ties = {
            "t": np.array(cols[0], dtype=float), "i": np.array([conv(a) for a in cols[1]], dtype=np.int32),
            "j": np.array([conv(a) for a in cols[2]], dtype=np.int32), "x": np.array(cols[3], dtype=float),
            "r": np.array(cols[4], dtype=float), "o": np.array(cols[5], dtype=float),
            "circle": np.array(cols[6], dtype=np.int8),
        }
        times = np.asarray(times, dtype=float)
        shape = (len(times), len(ids))
        zero = np.zeros(shape)
        return cls(config=config or {}, seed=seed, agent_ids=ids, times=times, ties=ties,
                   budget=zero if budget is None else np.asarray(budget, float),
                   pending_budget=zero.copy() if pending_budget is None else np.asarray(pending_budget, float),
                   capacity=np.ones(shape) if capacity is None else np.asarray(capacity, float),
                   events=list(events or []))

    @property
    def burn_in(self) -> float:
        return float(self.config.get("simulation", {}).get("burn_in", self.times[0] if len(self.times) else 0.0))

    # ------------------------------------------------------------------ queries
    def index(self, agent_id) -> int:
        return self.agent_ids.index(agent_id)

    def trajectory(self, i, j) -> dict:
        """Sampled trajectory of the directed tie i→j (only samples where it existed)."""
        ii, jj = self.index(i), self.index(j)
        mask = (self.ties["i"] == ii) & (self.ties["j"] == jj)
        return {k: self.ties[k][mask] for k in ("t", "x", "r", "o", "circle")}

    def events_of(self, *types) -> list:
        return [e for e in self.events if e["type"] in types]

    def snapshot(self, time_index: int) -> dict:
        """Ties present at sample ``time_index`` as columnar arrays."""
        mask = self.ties["t"] == self.times[time_index]
        return {k: v[mask] for k, v in self.ties.items()}

    # --------------------------------------------------------------- comparison
    def equals(self, other: "SimulationResult") -> bool:
        if self.seed != other.seed or self.agent_ids != other.agent_ids:
            return False
        if not np.array_equal(self.times, other.times):
            return False
        for k in TIE_COLUMNS:
            if not np.array_equal(self.ties[k], other.ties[k]):
                return False
        for a, b in ((self.budget, other.budget), (self.pending_budget, other.pending_budget), (self.capacity, other.capacity)):
            if not np.array_equal(a, b):
                return False
        return _norm(self.events) == _norm(other.events)

    # ---------------------------------------------------------- serialisation
    def save(self, path) -> None:
        path = Path(path)
        meta = {"config": self.config, "seed": self.seed, "agent_ids": self.agent_ids, "events": self.events}
        arrays = {f"tie_{k}": v for k, v in self.ties.items()}
        np.savez_compressed(
            path,
            meta=np.array(json.dumps(meta, default=_json_default)),
            times=self.times,
            budget=self.budget,
            pending_budget=self.pending_budget,
            capacity=self.capacity,
            **arrays,
        )

    @classmethod
    def load(cls, path) -> "SimulationResult":
        with np.load(Path(path), allow_pickle=False) as data:
            meta = json.loads(str(data["meta"]))
            ties = {k: data[f"tie_{k}"] for k in TIE_COLUMNS}
            return cls(
                config=meta["config"],
                seed=meta["seed"],
                agent_ids=meta["agent_ids"],
                times=data["times"],
                ties=ties,
                budget=data["budget"],
                pending_budget=data["pending_budget"],
                capacity=data["capacity"],
                events=meta["events"],
            )


def _json_default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def _norm(events):
    return json.loads(json.dumps(events, default=_json_default))
