"""Transform canonical resume data into RenderCV-ready structures."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from .errors import ResumePipelineError
from .io_utils import deep_merge

if TYPE_CHECKING:
    from .types import GeneratedVariantPaths, JsonDict, JsonValue


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


def _string_values(item: JsonDict, keys: tuple[str, ...]) -> list[str]:
    return [
        value
        for key in keys
        if isinstance((value := item.get(key)), str) and value
    ]


def build_rendercv_data(
    resume: JsonDict,
    converted_seed: JsonDict,
    theme_config: JsonDict,
    paths: GeneratedVariantPaths,
) -> JsonDict:
    """Merge RenderCV seed output, theme config, and transformed resume data."""
    basics = resume.get("basics")
    if not isinstance(basics, dict):
        msg = "Resume basics must be an object before generating RenderCV data."
        raise ResumePipelineError(msg)

    output_folder = paths.render_output_dir.relative_to(paths.output_path.parent)
    pdf_path = paths.rendered_pdf_path.relative_to(paths.output_path.parent)
    typst_path = pdf_path.with_suffix(".typ")

    seed_cv = converted_seed.get("cv")
    cv = dict(seed_cv) if isinstance(seed_cv, dict) else {}
    cv.update(
        {
            "name": basics.get("name"),
            "headline": (
                basics.get("label") if isinstance(basics.get("label"), str) else ""
            ),
            "location": _format_location(basics.get("location")),
            "email": (
                basics.get("email") if isinstance(basics.get("email"), str) else ""
            ),
            "phone": (
                basics.get("phone") if isinstance(basics.get("phone"), str) else ""
            ),
            "website": (
                basics.get("url") if isinstance(basics.get("url"), str) else ""
            ),
            "social_networks": [
                {"network": profile.get("network"), "username": _pick_username(profile)}
                for profile in basics.get("profiles", [])
                if isinstance(profile, dict)
            ],
            "sections": build_sections(resume),
        },
    )

    return deep_merge(
        theme_config,
        {
            "cv": cv,
            "settings": {
                "current_date": "today",
                "render_command": {
                    "output_folder": str(output_folder),
                    "pdf_path": str(pdf_path),
                    "typst_path": str(typst_path),
                    "dont_generate_markdown": True,
                    "dont_generate_html": True,
                    "dont_generate_png": True,
                },
            },
        },
    )
