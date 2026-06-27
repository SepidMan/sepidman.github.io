"""File and data helpers for the resume pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from .errors import ResumePipelineError
from .types import JsonDict, JsonValue


def assert_condition(condition: bool, message: str) -> None:
    """Raise a pipeline error when a required condition is false."""
    if not condition:
        raise ResumePipelineError(message)


def read_json(path: Path) -> JsonDict:
    """Read a JSON object from disk."""
    with path.open("r", encoding="utf8") as handle:
        data = json.load(handle)

    assert_condition(isinstance(data, dict), f"Expected a JSON object in {path}.")
    return data


def read_yaml(path: Path) -> JsonDict:
    """Read a YAML object from disk."""
    with path.open("r", encoding="utf8") as handle:
        data = yaml.safe_load(handle)

    assert_condition(isinstance(data, dict), f"Expected a YAML object in {path}.")
    return data


def write_yaml(path: Path, data: JsonDict) -> None:
    """Write a YAML object to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)


def deep_merge(target: JsonValue, source: JsonValue) -> JsonValue:
    """Recursively merge dict-like values, replacing scalars and lists."""
    if not isinstance(source, dict):
        return source

    result = dict(target) if isinstance(target, dict) else {}
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def clone(data: JsonDict) -> JsonDict:
    """Deep-copy JSON-shaped data."""
    return json.loads(json.dumps(data))


def ensure_readable(path: Path, label: str) -> None:
    """Ensure a required file exists."""
    if not path.is_file():
        raise ResumePipelineError(f"{label} is missing or unreadable: {path}")
