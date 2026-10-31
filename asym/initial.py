"""Initial conditions (docs/model-spec.md §8): empty | random | file."""
from __future__ import annotations

from asym.config import Config, ConfigError
from asym.io import read_table

TIE_KEYS = {"i", "j", "x", "r", "o", "circle"}


def initial_ties(cfg: Config, rng) -> dict:
    """Return {(i, j): {x, r, o, circle}} with agent indices."""
    mode = cfg.init["mode"]
    if mode == "empty":
        return {}
    if mode == "file":
        init, base = cfg.init, cfg.init.get("base_dir")
        records = list(init.get("ties") or [])
        if init.get("ties_path"):
            records += read_table(init["ties_path"], base)
        if init.get("path"):
            records += read_table(init["path"], base, key="ties")
        return _ties_from_records(cfg, records)
    if mode == "random":
        return _random_ties(cfg, rng)
    raise ConfigError(f"unknown init.mode {mode!r}")


def _random_ties(cfg: Config, rng) -> dict:
    """Undirected random graph G(N, density); each direction gets its own x ~ U(x_range)."""
    density = float(cfg.init.get("density", 0.1))
    lo, hi = (float(v) for v in cfg.init.get("x_range", [cfg.globals["x0"], 0.9]))
    if not 0 <= density <= 1 or not 0 <= lo <= hi <= 1:
        raise ConfigError("init.density must lie in [0, 1] and init.x_range within [0, 1]")
    n = cfg.n_agents
    out = {}
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < density:
                for u, v in ((i, j), (j, i)):
                    out[(u, v)] = {"x": float(rng.uniform(lo, hi)), "r": 0.0, "o": 0.0, "circle": None}
    return out


def _ties_from_records(cfg: Config, records) -> dict:
    index = {aid: k for k, aid in enumerate(cfg.agent_ids)}
    index.update({str(aid): k for k, aid in enumerate(cfg.agent_ids) if str(aid) not in index})
    out = {}
    for rec in records:
        unknown = set(rec) - TIE_KEYS
        if unknown:
            raise ConfigError(f"unknown tie field(s) {sorted(unknown)}")
        try:
            i, j = index[rec["i"]], index[rec["j"]]
        except KeyError as e:
            if e.args[0] in ("i", "j"):
                raise ConfigError(f"tie record misses field {e.args[0]!r}") from None
            raise ConfigError(f"tie refers to unknown agent {e.args[0]!r}") from None
        if i == j:
            raise ConfigError(f"self tie for agent {rec['i']!r}")
        if (i, j) in out:
            raise ConfigError(f"duplicate tie {rec['i']!r} -> {rec['j']!r}")
        if "x" not in rec:
            raise ConfigError(f"tie {rec['i']!r} -> {rec['j']!r} misses 'x'")
        x = float(rec["x"])
        if not 0.0 <= x <= 1.0:
            raise ConfigError(f"tie {rec['i']!r} -> {rec['j']!r}: x must lie in [0, 1]")
        r, o = float(rec.get("r", 0.0)), float(rec.get("o", 0.0))
        if r < 0 or o < 0:
            raise ConfigError(f"tie {rec['i']!r} -> {rec['j']!r}: r and o must be >= 0")
        circle = rec.get("circle")
        if circle is not None:
            circle = int(circle)
            if not 1 <= circle <= 4:
                raise ConfigError("circle must lie in 1..4")
        out[(i, j)] = {"x": x, "r": r, "o": o, "circle": circle}
    return out
