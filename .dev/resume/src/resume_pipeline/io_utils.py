"""File and data helpers for the resume pipeline."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import yaml

from .errors import ResumePipelineError

if TYPE_CHECKING:
    from pathlib import Path

    from .types import JsonDict, JsonValue


class _NoDatesSafeLoader(yaml.SafeLoader):
    """Safe YAML loader that keeps timestamp-like scalars as strings."""


for _key, _resolvers in list(_NoDatesSafeLoader.yaml_implicit_resolvers.items()):
    _NoDatesSafeLoader.yaml_implicit_resolvers[_key] = [
        (tag, regexp)
        for tag, regexp in _resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]


def assert_condition(*, condition: bool, message: str) -> None:
    """Raise a pipeline error when a required condition is false."""
    if not condition:
        raise ResumePipelineError(message)


def read_json(path: Path) -> JsonDict:
    """Read a JSON object from disk."""
    with path.open("r", encoding="utf8") as handle:
        data = json.load(handle)

    message = f"Expected a JSON object in {path}."
    assert_condition(condition=isinstance(data, dict), message=message)
    return data


def write_json(path: Path, data: JsonDict) -> None:
    """Write a JSON object to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def read_yaml(path: Path) -> JsonDict:
    """Read a YAML object from disk."""
    with path.open("r", encoding="utf8") as handle:
        data = yaml.load(handle, Loader=_NoDatesSafeLoader)  # noqa: S506

    message = f"Expected a YAML object in {path}."
    assert_condition(condition=isinstance(data, dict), message=message)
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
        msg = f"{label} is missing or unreadable: {path}"
        raise ResumePipelineError(msg)
