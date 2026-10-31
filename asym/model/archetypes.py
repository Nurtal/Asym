"""Agents, archetypes and population sampling (docs/model-spec.md §2.1).

An archetype is a vector of parameter centres (unspecified parameters fall back to
``AGENT_DEFAULTS``). A population draws each agent around its archetype centre:

- positive / non-negative parameters: mean-preserving log-normal,
  ``c · exp(s·Z − s²/2)`` (a centre of 0 stays 0)
- parameters in [0, 1]: logit-normal, ``logistic(logit(c) + s·Z)`` (median = c;
  a centre of 0 or 1 stays exact)
- the perception bias ``pi`` (real-valued): additive normal, ``c + s·Z``
- the decay ladder ``delta``: one log-normal factor shared by its four entries, so
  the ladder keeps its ordering

The population is sampled with ``population.seed`` (default 0), independently of the
simulation seed, so an ensemble of simulation seeds shares one population.
"""
from __future__ import annotations

import copy
import math

import numpy as np

from asym.config import AGENT_DEFAULTS, UNIT_INTERVAL_AGENT_PARAMS, ConfigError, validate_agent

AGENT_KEYS = set(AGENT_DEFAULTS) | {"id", "archetype"}
REAL_PARAMS = {"pi"}

BUILTIN_ARCHETYPES: dict[str, dict] = {
    # many shallow ties: large budget, low concentration, open, exploring
    "butterfly": {"B": 8.0, "beta": 0.5, "nu": 0.15, "epsilon": 0.15},
    # few deep ties: concentrated, loyal, patient, stable circles
    "loyal_few": {"B": 4.0, "beta": 2.5, "ell": 0.8, "tau": 12.0, "w": 0.15, "nu": 0.03},
    # reciprocity accountant: sensitive to deficits, high expectations, impatient
    "transactional": {"kappa": 1.0, "rho_star": 1.1, "ell": 0.1, "tau": 2.5, "nu": 0.06},
    # fast decay, conflict-avoidant (silence rather than decline), closed
    "avoidant": {"delta": [0.15, 0.1, 0.06, 0.03], "alpha": 0.9, "nu": 0.02},
}
ALIASES = {"loyal-few": "loyal_few"}
POPULATION_KEYS = {"composition", "size", "noise", "overrides", "seed"}


def archetype_table(user: dict | None = None) -> dict[str, dict]:
    """Built-in archetypes merged with user-defined ones (``base`` extends another)."""
    table = copy.deepcopy(BUILTIN_ARCHETYPES)
    for name, spec in (user or {}).items():
        spec = dict(spec)
        base = spec.pop("base", None)
        centre = copy.deepcopy(table[_canon(base, table)]) if base else {}
        unknown = set(spec) - set(AGENT_DEFAULTS)
        if unknown:
            raise ConfigError(f"archetype {name!r}: unknown parameter(s) {sorted(unknown)}")
        centre.update(spec)
        table[name] = centre
    return table


def _canon(name, table):
    name = ALIASES.get(name, name)
    if name not in table:
        raise ConfigError(f"unknown archetype {name!r}; known: {sorted(table)}")
    return name


def archetype_centre(name, table) -> dict:
    centre = copy.deepcopy(AGENT_DEFAULTS)
    centre.update(copy.deepcopy(table[_canon(name, table)]))
    return centre


def resolve_agent(spec: dict, table: dict | None = None) -> dict:
    """Resolve one agent spec: defaults <- archetype centre <- explicit overrides."""
    unknown = set(spec) - AGENT_KEYS
    if unknown:
        raise ConfigError(f"unknown agent parameter(s) {sorted(unknown)} for agent {spec.get('id')!r}")
    table = table if table is not None else archetype_table()
    if spec.get("archetype") is not None:
        agent = archetype_centre(spec["archetype"], table)
        agent["archetype"] = _canon(spec["archetype"], table)
    else:
        agent = copy.deepcopy(AGENT_DEFAULTS)
    agent.update({k: copy.deepcopy(v) for k, v in spec.items() if k != "archetype"})
    return validate_agent(agent)


def _logit(p):
    return math.log(p / (1.0 - p))


def sample_around(centre: dict, noise, rng) -> dict:
    """One noisy draw around an archetype centre (see module docstring)."""
    out = copy.deepcopy(centre)
    for k, c in centre.items():
        s = noise.get(k, noise.get("default", 0.0)) if isinstance(noise, dict) else float(noise)
        if not s:
            continue
        z = rng.standard_normal()
        if k == "delta":
            c = [c] * 4 if isinstance(c, (int, float)) else c
            factor = math.exp(s * z - 0.5 * s * s)
            out[k] = [float(v) * factor for v in c]
        elif k in REAL_PARAMS:
            out[k] = float(c) + s * z
        elif k in UNIT_INTERVAL_AGENT_PARAMS:
            c = float(c)
            out[k] = c if c in (0.0, 1.0) else 1.0 / (1.0 + math.exp(-(_logit(c) + s * z)))
        else:
            out[k] = float(c) * math.exp(s * z - 0.5 * s * s)
    return out


def _counts(composition: dict, size) -> dict:
    values = list(composition.values())
    if all(isinstance(v, int) and not isinstance(v, bool) for v in values):
        counts = dict(composition)
        if size is not None and sum(counts.values()) != size:
            raise ConfigError("population.size does not match the composition counts")
        return counts
    if size is None:
        raise ConfigError("population.size is required when the composition uses proportions")
    total = float(sum(values))
    if total <= 0:
        raise ConfigError("population composition must be positive")
    raw = {k: v / total * size for k, v in composition.items()}
    counts = {k: int(math.floor(v)) for k, v in raw.items()}
    remainder = size - sum(counts.values())
    for k in sorted(raw, key=lambda k: raw[k] - counts[k], reverse=True)[:remainder]:
        counts[k] += 1
    return counts


def build_population(agents_raw, population, archetypes) -> list[dict]:
    table = archetype_table(archetypes)
    if population is not None:
        population = dict(population)
        unknown = set(population) - POPULATION_KEYS
        if unknown:
            raise ConfigError(f"unknown key(s) in 'population': {sorted(unknown)}")
        counts = _counts(dict(population.get("composition") or {}), population.get("size"))
        noise = population.get("noise", 0.1)
        rng = np.random.default_rng(population.get("seed", 0))
        overrides = population.get("overrides") or {}
        agents, k = [], 0
        for name, n in counts.items():
            centre = archetype_centre(name, table)
            for _ in range(n):
                agent = sample_around(centre, noise, rng)
                agent["archetype"] = _canon(name, table)
                agent["id"] = k
                ov = overrides.get(k, overrides.get(str(k), {}))
                unknown = set(ov) - set(AGENT_DEFAULTS)
                if unknown:
                    raise ConfigError(f"unknown override parameter(s) {sorted(unknown)} for agent {k}")
                agent.update(copy.deepcopy(ov))
                agents.append(validate_agent(agent))
                k += 1
        return agents
    agents = [resolve_agent(dict(a), table) for a in agents_raw]
    ids = [a.get("id") for a in agents]
    if any(i is None for i in ids):
        raise ConfigError("every explicit agent needs an 'id'")
    if len(set(ids)) != len(ids):
        raise ConfigError("agent ids must be unique")
    return agents
