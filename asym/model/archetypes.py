"""Agents, archetypes and population sampling."""
from __future__ import annotations

import copy

from asym.config import AGENT_DEFAULTS, ConfigError, validate_agent

AGENT_KEYS = set(AGENT_DEFAULTS) | {"id", "archetype"}


def resolve_agent(spec: dict, base: dict | None = None) -> dict:
    """Resolve one agent spec into a full θ dict (defaults <- base <- overrides)."""
    unknown = set(spec) - AGENT_KEYS
    if unknown:
        raise ConfigError(f"unknown agent parameter(s) {sorted(unknown)} for agent {spec.get('id')!r}")
    agent = copy.deepcopy(AGENT_DEFAULTS)
    if base:
        agent.update(copy.deepcopy(base))
    agent.update(copy.deepcopy(spec))
    return validate_agent(agent)


def build_population(agents_raw, population, archetypes) -> list[dict]:
    if population is not None:
        raise ConfigError("'population' is not supported yet")
    agents = [resolve_agent(dict(a)) for a in agents_raw]
    ids = [a.get("id") for a in agents]
    if any(i is None for i in ids):
        raise ConfigError("every explicit agent needs an 'id'")
    if len(set(ids)) != len(ids):
        raise ConfigError("agent ids must be unique")
    return agents
