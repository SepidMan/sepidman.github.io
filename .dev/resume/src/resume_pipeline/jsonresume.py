"""Projection from canonical profile data to JSON Resume output."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .io_utils import clone

if TYPE_CHECKING:
    from .types import JsonDict, JsonValue


JSONRESUME_SCHEMA_URL = (
    "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"
)


def _as_dict(value: JsonValue) -> JsonDict | None:
    if isinstance(value, dict):
        return value
    return None


def _as_list(value: JsonValue) -> list[JsonValue]:
    if isinstance(value, list):
        return value
    return []


def _pick_fields(item: JsonDict, field_names: tuple[str, ...]) -> JsonDict:
    return {field: clone(item[field]) for field in field_names if field in item}


def _project_basics(basics: JsonValue) -> JsonDict | None:
    basics_dict = _as_dict(basics)
    if basics_dict is None:
        return None

    projected = _pick_fields(
        basics_dict,
        (
            "name",
            "label",
            "image",
            "email",
            "phone",
            "url",
            "summary",
            "location",
        ),
    )

    profiles = [
        _pick_fields(profile, ("network", "username", "url"))
        for profile_value in _as_list(basics_dict.get("profiles"))
        if (profile := _as_dict(profile_value)) is not None
    ]
    if profiles:
        projected["profiles"] = profiles

    return projected


def _project_array(
    items: JsonValue,
    *,
    field_names: tuple[str, ...],
) -> list[JsonDict]:
    projected_items: list[JsonDict] = []
    for item_value in _as_list(items):
        item = _as_dict(item_value)
        if item is None:
            continue
        projected_items.append(_pick_fields(item, field_names))
    return projected_items


def build_jsonresume_data(profile: JsonDict) -> JsonDict:
    """Project canonical profile data into strict JSON Resume output."""
    jsonresume: JsonDict = {"$schema": JSONRESUME_SCHEMA_URL}

    if (meta := _as_dict(profile.get("meta"))) is not None:
        jsonresume["meta"] = clone(meta)

    if (basics := _project_basics(profile.get("basics"))) is not None:
        jsonresume["basics"] = basics

    sections: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "work",
            (
                "name",
                "description",
                "position",
                "url",
                "startDate",
                "endDate",
                "summary",
                "highlights",
                "location",
            ),
        ),
        (
            "volunteer",
            (
                "organization",
                "position",
                "url",
                "startDate",
                "endDate",
                "summary",
                "highlights",
            ),
        ),
        (
            "education",
            (
                "institution",
                "url",
                "area",
                "studyType",
                "startDate",
                "endDate",
                "score",
                "courses",
                "summary",
            ),
        ),
        (
            "awards",
            ("title", "date", "awarder", "summary"),
        ),
        (
            "certificates",
            ("name", "date", "issuer", "url", "summary"),
        ),
        (
            "publications",
            ("name", "publisher", "releaseDate", "url", "summary"),
        ),
        (
            "skills",
            ("name", "level", "keywords"),
        ),
        (
            "languages",
            ("language", "fluency"),
        ),
        (
            "interests",
            ("name", "keywords"),
        ),
        (
            "references",
            ("name", "reference"),
        ),
        (
            "projects",
            (
                "name",
                "description",
                "highlights",
                "keywords",
                "startDate",
                "endDate",
                "url",
                "roles",
                "entity",
                "type",
            ),
        ),
    )

    for section_name, field_names in sections:
        projected = _project_array(
            profile.get(section_name),
            field_names=field_names,
        )
        if projected:
            jsonresume[section_name] = projected

    return jsonresume
