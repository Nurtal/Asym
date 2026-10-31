"""Configuration schema, defaults and validation.

A config is a nested mapping (usually loaded from YAML) with sections:

- ``simulation``: horizon, burn-in, sampling, numerical settings
- ``globals``: global model parameters (see docs/model-spec.md §2.2)
- ``agents``: explicit list of agents, each ``{id, archetype?, <θ overrides>}``
- ``population``: archetype-based population (alternative to ``agents``)
- ``archetypes``: user-defined archetypes (merged with built-ins)
- ``init``: initial condition (``mode``: empty | random | file)
- ``variants``: switches for non-baseline mechanisms
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml


class ConfigError(ValueError):
    """Raised when a configuration or initial-condition input is invalid."""


N_CIRCLES = 4
CIRCLE_NAMES = ("acquaintance", "friend", "close_friend", "inner_circle")

# Per-agent behavioural parameters θ_i (docs/model-spec.md §2.1).
AGENT_DEFAULTS: dict[str, Any] = {
    "B": 5.0,  # budget (interaction slots)
    "beta": 1.0,  # concentration of allocation
    "epsilon": 0.05,  # exploration share
    "delta": [0.08, 0.05, 0.03, 0.015],  # closeness decay per circle (outer -> inner)
    "rho_star": 0.8,  # reciprocity expectation
    "kappa": 0.0,  # reciprocity-deficit sensitivity
    "lam": 0.1,  # memory rate of r and o
    "w": 0.05,  # hysteresis width
    "m": 1.0,  # minimum dwell time in a circle
    "nu": 0.0,  # openness (encounter rate)
    "pi": 0.0,  # perception log-bias
    "tau": 5.0,  # base patience
    "ell": 0.0,  # loyalty in [0, 1]
    "alpha": 0.5,  # conflict avoidance: P(silence | not accepting)
}

UNIT_INTERVAL_AGENT_PARAMS = {"epsilon", "ell", "alpha"}
POSITIVE_AGENT_PARAMS = {"B", "tau"}
NONNEGATIVE_AGENT_PARAMS = {"beta", "rho_star", "kappa", "lam", "w", "m", "nu"}

GLOBAL_DEFAULTS: dict[str, Any] = {
    "eta": 0.1,  # closeness gain per accepted interaction
    "d": 1.0,  # interaction duration (slot occupancy)
    "c_wait": 0.5,  # slot fraction held by a pending invitation
    "c_rej": 0.5,  # own-investment cost of a declined invitation (in investment units)
    "inv_unit": 1.0,  # size of one investment increment in r / o
    "gamma": 0.5,  # invitation issuing rate per free slot
    "omega": 1.0,  # invitee response rate
    "zeta": 0.2,  # late-acceptance rate for silent invitees
    "a0": 0.0,  # acceptance intercept
    "a": 4.0,  # acceptance weight on own closeness
    "b": 2.0,  # acceptance weight on reciprocity
    "c": 2.0,  # acceptance weight on load
    "psi": 0.1,  # cancellation drop per unit waiting time
    "h1": 1.0,  # slope of patience in closeness
    "o0": 0.5,  # prior pseudo-count of the reciprocity ratio
    "thresholds": [0.3, 0.55, 0.8],  # lower bounds of friend, close friend, inner circle
    "x_min": 0.02,  # forgetting threshold
    "x0": 0.1,  # closeness at first encounter
    "sigma_p": 0.0,  # perception noise
    "mu_rand": 1.0,  # weight of random encounters
    "mu_tri": 1.0,  # weight of triadic-closure encounters
    "shock_rate": 0.0,  # global shock rate
    "shock_tie_prob": 0.5,  # P(tie shock | shock), else budget shock
    "shock_phi": [0.3, 0.8],  # range of the tie-shock factor
    "shock_budget_phi": [0.2, 0.6],  # range of the budget-shock factor
    "shock_budget_duration": 10.0,  # mean duration of a budget shock
}

SIMULATION_DEFAULTS: dict[str, Any] = {
    "horizon": 100.0,
    "burn_in": 0.0,
    "sample_interval": 1.0,
    "check_interval": 0.25,  # housekeeping period for circle transitions / forgetting
    "ode_step": 0.05,  # max RK4 sub-step for the closeness flow
    "record_events": True,
}

VARIANT_DEFAULTS: dict[str, Any] = {
    "surplus_boost": 0.0,  # μ_s; 0 = baseline (surplus neutral)
    "guilt": 0.0,  # closeness drop of the invitee when an invitation to it is cancelled
    "circle_capacity": None,  # list of K_c targets per circle, or None
    "capacity_cost": 0.0,  # strength of the soft capacity cost
    "dormant": False,  # dormant state instead of deletion
    "revival_bonus": 0.0,  # closeness bonus when a dormant tie is revived
}

INIT_KEYS = {"mode", "ties", "ties_path", "agents_path", "path", "density", "x_range", "base_dir"}
SECTIONS = {"simulation", "globals", "agents", "population", "archetypes", "init", "variants", "name", "description", "_base_dir"}


@dataclass
class Config:
    simulation: dict
    globals: dict
    agents: list  # list of fully-resolved agent dicts (id + every θ param)
    init: dict
    variants: dict
    raw: dict = field(repr=False)

    @property
    def n_agents(self) -> int:
        return len(self.agents)

    @property
    def agent_ids(self) -> list:
        return [a["id"] for a in self.agents]

    def to_dict(self) -> dict:
        """Fully-resolved, JSON-serialisable view of the config."""
        return {
            "simulation": copy.deepcopy(self.simulation),
            "globals": copy.deepcopy(self.globals),
            "agents": copy.deepcopy(self.agents),
            "init": copy.deepcopy(self.init),
            "variants": copy.deepcopy(self.variants),
        }


def _check_keys(section: str, given: Mapping, allowed) -> None:
    unknown = set(given) - set(allowed)
    if unknown:
        raise ConfigError(f"unknown key(s) in '{section}': {sorted(unknown)}")


def _merge(section: str, defaults: dict, given: Mapping | None) -> dict:
    given = dict(given or {})
    _check_keys(section, given, defaults)
    out = copy.deepcopy(defaults)
    out.update(copy.deepcopy(given))
    return out


def _as_delta(value, who) -> list[float]:
    if isinstance(value, (int, float)):
        return [float(value)] * N_CIRCLES
    value = [float(v) for v in value]
    if len(value) != N_CIRCLES:
        raise ConfigError(f"{who}: 'delta' must be a scalar or a list of {N_CIRCLES} values")
    return value


def validate_agent(agent: dict) -> dict:
    who = f"agent {agent.get('id')!r}"
    agent["delta"] = _as_delta(agent["delta"], who)
    if any(v < 0 for v in agent["delta"]):
        raise ConfigError(f"{who}: 'delta' must be non-negative")
    for k in UNIT_INTERVAL_AGENT_PARAMS:
        if not 0.0 <= float(agent[k]) <= 1.0:
            raise ConfigError(f"{who}: '{k}' must lie in [0, 1]")
    for k in POSITIVE_AGENT_PARAMS:
        if float(agent[k]) <= 0:
            raise ConfigError(f"{who}: '{k}' must be > 0")
    for k in NONNEGATIVE_AGENT_PARAMS:
        if float(agent[k]) < 0:
            raise ConfigError(f"{who}: '{k}' must be >= 0")
    for k, v in agent.items():
        if k not in ("id", "archetype", "delta"):
            agent[k] = float(v)
    return agent


def _resolve_agents(raw: dict, init: dict, base_dir) -> list[dict]:
    from asym.io import read_table  # local imports: avoid cycles
    from asym.model.archetypes import build_population

    agents_raw = raw.get("agents")
    population = raw.get("population")
    archetypes = raw.get("archetypes")
    file_agents = None
    if init["mode"] == "file" and init.get("agents_path"):
        file_agents = read_table(init["agents_path"], base_dir)
    elif init["mode"] == "file" and init.get("path"):
        file_agents = read_table(init["path"], base_dir, key="agents") or None
    sources = [s for s in (agents_raw, population, file_agents) if s is not None]
    if len(sources) > 1:
        raise ConfigError("agents must come from exactly one of 'agents', 'population' or the init file")
    if not sources:
        raise ConfigError("config needs 'agents', 'population' or an init file with agents")
    return build_population(agents_raw if population is None else None, population, archetypes) \
        if file_agents is None else build_population(file_agents, None, archetypes)


def load_config(source) -> Config:
    """Load and validate a config from a mapping, a YAML file path, or a Config."""
    if isinstance(source, Config):
        return source
    base_dir = None
    if isinstance(source, (str, Path)):
        path = Path(source)
        base_dir = path.parent
        with open(path) as fh:
            raw = yaml.safe_load(fh)
    elif isinstance(source, Mapping):
        raw = copy.deepcopy(dict(source))
    else:
        raise ConfigError(f"cannot load config from {type(source).__name__}")
    if not isinstance(raw, Mapping):
        raise ConfigError("config root must be a mapping")
    _check_keys("config", raw, SECTIONS)

    sim = _merge("simulation", SIMULATION_DEFAULTS, raw.get("simulation"))
    glob = _merge("globals", GLOBAL_DEFAULTS, raw.get("globals"))
    variants = _merge("variants", VARIANT_DEFAULTS, raw.get("variants"))
    init = dict(raw.get("init") or {"mode": "empty"})
    _check_keys("init", init, INIT_KEYS)
    init.setdefault("mode", "empty")
    if init["mode"] not in ("empty", "random", "file"):
        raise ConfigError(f"init.mode must be empty | random | file, got {init['mode']!r}")

    if sim["horizon"] <= 0 or sim["sample_interval"] <= 0 or sim["check_interval"] <= 0:
        raise ConfigError("horizon, sample_interval and check_interval must be > 0")
    if not 0 <= sim["burn_in"] <= sim["horizon"]:
        raise ConfigError("burn_in must lie in [0, horizon]")
    th = [float(v) for v in glob["thresholds"]]
    if len(th) != N_CIRCLES - 1 or any(b <= a for a, b in zip(th, th[1:])):
        raise ConfigError(f"globals.thresholds must be {N_CIRCLES - 1} increasing values")
    glob["thresholds"] = th
    if not 0 <= glob["x_min"] < th[0]:
        raise ConfigError("globals.x_min must lie in [0, thresholds[0])")
    if not 0 <= glob["c_wait"] <= 1:
        raise ConfigError("globals.c_wait must lie in [0, 1]")
    if glob["d"] <= 0:
        raise ConfigError("globals.d must be > 0")
    if not 0 <= glob["eta"] <= 1:
        raise ConfigError("globals.eta must lie in [0, 1]")

    base_dir = init.pop("base_dir", None) or base_dir or raw.get("_base_dir")
    agents = _resolve_agents(raw, init, base_dir)
    if base_dir is not None:
        init["base_dir"] = str(base_dir)
    return Config(simulation=sim, globals=glob, agents=agents, init=init, variants=variants, raw=raw)
