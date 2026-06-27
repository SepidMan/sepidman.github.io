"""File and data helpers for the resume pipeline."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, time
from typing import TYPE_CHECKING

from pyserials import read as serial_read
from pyserials import update as serial_update
from pyserials import write as serial_write

from .errors import ResumePipelineError

if TYPE_CHECKING:
    from pathlib import Path

    from .types import JsonDict, JsonValue


def assert_condition(*, condition: bool, message: str) -> None:
    """Raise a pipeline error when a required condition is false."""
    if not condition:
        raise ResumePipelineError(message)


def _normalize_serialized_value(value: object) -> JsonValue:
    """Convert parser-specific values into plain JSON-shaped Python data."""
    if isinstance(value, dict):
        return {
            str(key): _normalize_serialized_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_normalize_serialized_value(item) for item in value]
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    return value


def _read_object(path: Path, *, data_type: str) -> JsonDict:
    """Read and normalize a serialized object file."""
    data = _normalize_serialized_value(serial_read.from_file(path, data_type=data_type))
    message = f"Expected a {data_type.upper()} object in {path}."
    assert_condition(condition=isinstance(data, dict), message=message)
    return data


def read_json(path: Path) -> JsonDict:
    """Read a JSON object from disk."""
    return _read_object(path, data_type="json")


def write_json(path: Path, data: JsonDict) -> None:
    """Write a JSON object to disk."""
    serial_write.to_json_file(data, path, indent=2)


def read_yaml(path: Path) -> JsonDict:
    """Read a YAML object from disk."""
    return _read_object(path, data_type="yaml")


def write_yaml(path: Path, data: JsonDict) -> None:
    """Write a YAML object to disk."""
    serial_write.to_yaml_file(data, path)


def deep_merge(target: JsonValue, source: JsonValue) -> JsonValue:
    """Recursively merge dict-like values, replacing scalars and lists."""
    if not isinstance(source, dict):
        return deepcopy(source)

    result = dict(target) if isinstance(target, dict) else {}
    serial_update.recursive_update(
        result,
        source,
        types={list: "write"},
        undefined_existing="write",
        log_changes=False,
    )
    return result


def clone(data: JsonDict) -> JsonDict:
    """Deep-copy JSON-shaped data."""
    return deepcopy(data)


def ensure_readable(path: Path, label: str) -> None:
    """Ensure a required file exists."""
    if not path.is_file():
        msg = f"{label} is missing or unreadable: {path}"
        raise ResumePipelineError(msg)
