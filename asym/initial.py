"""Initial conditions (docs/model-spec.md §8): empty | random | file."""
from __future__ import annotations

from asym.config import Config, ConfigError

TIE_KEYS = {"i", "j", "x", "r", "o", "circle"}


def initial_ties(cfg: Config, rng) -> dict:
    """Return {(i, j): {x, r, o, circle}} with agent indices."""
    mode = cfg.init["mode"]
    if mode == "empty":
        return {}
    if mode == "file":
        return _ties_from_records(cfg, cfg.init.get("ties") or [])
    raise ConfigError(f"init.mode {mode!r} is not supported yet")


def _ties_from_records(cfg: Config, records) -> dict:
    index = {aid: k for k, aid in enumerate(cfg.agent_ids)}
    out = {}
    for rec in records:
        unknown = set(rec) - TIE_KEYS
        if unknown:
            raise ConfigError(f"unknown tie field(s) {sorted(unknown)}")
        try:
            i, j = index[rec["i"]], index[rec["j"]]
        except KeyError as e:
            raise ConfigError(f"tie refers to unknown agent {e.args[0]!r}") from None
        if i == j:
            raise ConfigError(f"self tie for agent {rec['i']!r}")
        if (i, j) in out:
            raise ConfigError(f"duplicate tie {rec['i']!r} -> {rec['j']!r}")
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
