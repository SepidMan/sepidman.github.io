"""Projection from canonical profile data to RenderCV input."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from .errors import ResumePipelineError
from .io_utils import deep_merge
from .paths import ROOT_DIR

if TYPE_CHECKING:
    from .types import GeneratedVariantPaths, JsonDict, JsonValue, RenderCVConfig


def _pick_username(profile: JsonDict) -> str:
    username = profile.get("username")
    if isinstance(username, str) and username:
        return username

    url = profile.get("url")
    if isinstance(url, str) and url:
        return urlparse(url).path.lstrip("/") or url

    return ""


def _format_location(location: JsonValue) -> str:
    if not isinstance(location, dict):
        return ""

    country = location.get("countryCode") or ""
    region = location.get("region") or ""
    city = location.get("city") or ""
    if region == city:
        region = ""

    parts = [part for part in (city, region, country) if isinstance(part, str) and part]
    return ", ".join(parts)


def _to_date_fields(start_date: JsonValue, end_date: JsonValue) -> JsonDict | None:
    fields: JsonDict = {}
    if isinstance(start_date, (str, int)):
        fields["start_date"] = start_date
    if isinstance(end_date, (str, int)):
        fields["end_date"] = end_date
    elif "start_date" in fields:
        fields["end_date"] = "present"
    return fields or None


def _with_summary_highlights(summary: JsonValue, highlights: JsonValue) -> list[str]:
    if isinstance(highlights, list):
        normalized = [item for item in highlights if isinstance(item, str) and item]
        if normalized:
            return normalized

    return [summary] if isinstance(summary, str) and summary else []


def _optional_string(value: JsonValue) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _resolve_photo(value: JsonValue, output_directory: str) -> str | None:
    photo = _optional_string(value)
    if photo is None:
        return None

    if photo.startswith(("http://", "https://")):
        parsed = urlparse(photo)
        if parsed.path.startswith("/assets/"):
            source_path = ROOT_DIR / "src" / parsed.path.lstrip("/")
            if source_path.is_file():
                return os.path.relpath(source_path, ROOT_DIR / output_directory)

    return photo


def _string_values(item: JsonDict, keys: tuple[str, ...]) -> list[str]:
    return [
        value
        for key in keys
        if isinstance((value := item.get(key)), str) and value
    ]


def _build_experience_entry(item: JsonDict) -> JsonDict:
    entry: JsonDict = {
        "company": item.get("name"),
        "position": item.get("position"),
        "highlights": _with_summary_highlights(
            item.get("summary"),
            item.get("highlights"),
        ),
    }
    if isinstance(item.get("location"), str) and item["location"]:
        entry["location"] = item["location"]
    if isinstance(item.get("summary"), str) and item["summary"]:
        entry["summary"] = item["summary"]
    dates = _to_date_fields(item.get("startDate"), item.get("endDate"))
    if dates is not None:
        entry.update(dates)
    return entry


def _build_education_entry(item: JsonDict) -> JsonDict:
    entry: JsonDict = {
        "institution": item.get("institution"),
        "area": item.get("area") if isinstance(item.get("area"), str) else "",
        "degree": (
            item.get("studyType") if isinstance(item.get("studyType"), str) else ""
        ),
    }
    if isinstance(item.get("location"), str) and item["location"]:
        entry["location"] = item["location"]
    if isinstance(item.get("summary"), str) and item["summary"]:
        entry["summary"] = item["summary"]
    dates = _to_date_fields(item.get("startDate"), item.get("endDate"))
    if dates is not None:
        entry.update(dates)
    return entry


def _build_project_entry(item: JsonDict) -> JsonDict:
    entry: JsonDict = {
        "name": item.get("name"),
        "highlights": _with_summary_highlights(
            item.get("description"),
            item.get("highlights"),
        ),
    }
    if isinstance(item.get("description"), str) and item["description"]:
        entry["summary"] = item["description"]
    dates = _to_date_fields(item.get("startDate"), item.get("endDate"))
    if dates is not None:
        entry.update(dates)
    return entry


def _build_labeled_entry(
    item: JsonDict,
    *,
    keyword_key: str,
    name_key: str,
) -> JsonDict:
    keywords = item.get(keyword_key)
    details = (
        ", ".join(value for value in keywords if isinstance(value, str))
        if isinstance(keywords, list)
        else ""
    )
    return {"label": item.get(name_key), "details": details}


def _build_detail_entry(
    item: JsonDict,
    *,
    name_key: str,
    detail_keys: tuple[str, ...],
) -> JsonDict:
    return {
        "label": item.get(name_key),
        "details": " | ".join(_string_values(item, detail_keys)),
    }


def build_sections(resume: JsonDict) -> JsonDict:
    """Build the RenderCV section payload for a profiled resume."""
    sections: JsonDict = {}
    basics = resume.get("basics")

    if isinstance(basics, dict):
        summary = basics.get("summary")
        if isinstance(summary, str) and summary:
            sections["summary"] = [summary]

    work_items = resume.get("work")
    if isinstance(work_items, list) and work_items:
        sections["experience"] = [
            _build_experience_entry(item)
            for item in work_items
            if isinstance(item, dict)
        ]

    education_items = resume.get("education")
    if isinstance(education_items, list) and education_items:
        sections["education"] = [
            _build_education_entry(item)
            for item in education_items
            if isinstance(item, dict)
        ]

    skills = resume.get("skills")
    if isinstance(skills, list) and skills:
        sections["skills"] = [
            _build_labeled_entry(item, keyword_key="keywords", name_key="name")
            for item in skills
            if isinstance(item, dict)
        ]

    projects = resume.get("projects")
    if isinstance(projects, list) and projects:
        sections["projects"] = [
            _build_project_entry(item) for item in projects if isinstance(item, dict)
        ]

    certificates = resume.get("certificates")
    if isinstance(certificates, list) and certificates:
        sections["certificates"] = [
            _build_detail_entry(item, name_key="name", detail_keys=("issuer", "date"))
            for item in certificates
            if isinstance(item, dict)
        ]

    languages = resume.get("languages")
    if isinstance(languages, list) and languages:
        sections["languages"] = [
            _build_detail_entry(item, name_key="language", detail_keys=("fluency",))
            for item in languages
            if isinstance(item, dict)
        ]

    awards = resume.get("awards")
    if isinstance(awards, list) and awards:
        sections["awards"] = [
            {
                "bullet": " | ".join(
                    part for part in _string_values(item, ("title", "awarder"))
                ),
            }
            for item in awards
            if isinstance(item, dict)
        ]

    return sections


def _build_custom_connections(basics: JsonDict) -> list[JsonDict]:
    connections = basics.get("connections")
    if not isinstance(connections, list):
        return []

    items: list[JsonDict] = []
    for item in connections:
        if not isinstance(item, dict):
            continue
        icon = item.get("icon")
        label = item.get("label")
        if not isinstance(label, str) or not label:
            continue

        fontawesome_icon: str | None = None
        if isinstance(icon, dict):
            if icon.get("kind") == "fontawesome" and isinstance(icon.get("name"), str):
                fontawesome_icon = icon["name"]
        elif isinstance(icon, str) and icon:
            fontawesome_icon = icon

        if fontawesome_icon is None:
            continue

        connection: JsonDict = {
            "placeholder": label,
            "fontawesome_icon": fontawesome_icon,
        }
        if isinstance(item.get("url"), str) and item["url"]:
            connection["url"] = item["url"]
        items.append(connection)

    return items


def build_rendercv_data(
    resume: JsonDict,
    theme_config: JsonDict,
    paths: GeneratedVariantPaths,
    rendercv_config: RenderCVConfig,
) -> JsonDict:
    """Merge theme config and transformed resume data into RenderCV input."""
    basics = resume.get("basics")
    if not isinstance(basics, dict):
        msg = "Resume basics must be an object before generating RenderCV data."
        raise ResumePipelineError(msg)

    output_folder = paths.render_output_dir.relative_to(paths.output_path.parent)
    pdf_path = paths.rendered_pdf_path.relative_to(paths.output_path.parent)
    typst_path = pdf_path.with_suffix(".typ")

    cv: JsonDict = {
        "name": basics.get("name"),
        "headline": basics.get("label") if isinstance(basics.get("label"), str) else "",
        "location": _format_location(basics.get("location")),
        "social_networks": [
            {"network": profile.get("network"), "username": _pick_username(profile)}
            for profile in basics.get("profiles", [])
            if isinstance(profile, dict)
        ],
        "sections": build_sections(resume),
    }
    if (email := _optional_string(basics.get("email"))) is not None:
        cv["email"] = email
    if (phone := _optional_string(basics.get("phone"))) is not None:
        cv["phone"] = phone
    if (website := _optional_string(basics.get("url"))) is not None:
        cv["website"] = website
    photo = _resolve_photo(
        basics.get("photo") or basics.get("image"),
        paths.output_path.parent.relative_to(ROOT_DIR).as_posix(),
    )
    if photo is not None:
        cv["photo"] = photo
    if (custom_connections := _build_custom_connections(basics)):
        cv["custom_connections"] = custom_connections

    rendercv_payload: JsonDict = {
        "cv": cv,
        "settings": {
            "current_date": rendercv_config.current_date,
            "render_command": {
                "output_folder": str(output_folder),
                "pdf_path": str(pdf_path),
                "typst_path": str(typst_path),
                "dont_generate_markdown": True,
                "dont_generate_html": True,
                "dont_generate_png": True,
            },
        },
    }
    if rendercv_config.bold_keywords:
        rendercv_payload["settings"]["bold_keywords"] = rendercv_config.bold_keywords
    if rendercv_config.pdf_title is not None:
        rendercv_payload["settings"]["pdf_title"] = rendercv_config.pdf_title
    if rendercv_config.locale_language is not None:
        rendercv_payload["locale"] = {"language": rendercv_config.locale_language}

    return deep_merge(theme_config, rendercv_payload)
