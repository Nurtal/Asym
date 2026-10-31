"""Reading agent / tie tables for ``init.mode = file`` (JSON or CSV)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from asym.config import ConfigError


def _convert(value: str):
    value = value.strip()
    if value == "":
        return None
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            pass
    if value.startswith("["):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    return value


def resolve_path(path, base_dir) -> Path:
    p = Path(path)
    if not p.is_absolute() and base_dir is not None:
        p = Path(base_dir) / p
    if not p.exists():
        raise ConfigError(f"initial-condition file not found: {p}")
    return p


def read_table(path, base_dir=None, key=None) -> list[dict]:
    """Records from a CSV file, a JSON list, or the ``key`` entry of a JSON object."""
    p = resolve_path(path, base_dir)
    if p.suffix.lower() == ".csv":
        with open(p, newline="") as fh:
            rows = list(csv.DictReader(fh))
        return [{k: v for k, v in ((k, _convert(v)) for k, v in row.items()) if v is not None} for row in rows]
    if p.suffix.lower() == ".json":
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            raise ConfigError(f"malformed JSON in {p}: {e}") from None
        if isinstance(data, dict):
            data = data.get(key, []) if key else data
        if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
            raise ConfigError(f"{p}: expected a list of records{f' under {key!r}' if key else ''}")
        return data
    raise ConfigError(f"unsupported initial-condition file type: {p.suffix} (use .csv or .json)")
