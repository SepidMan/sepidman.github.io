"""Profile override handling for PDF variants."""

from __future__ import annotations

from .io_utils import clone
from .types import JsonDict


def apply_profile_overrides(resume: JsonDict, profile: JsonDict) -> JsonDict:
    """Apply repo-specific profile overrides to canonical resume data."""
    next_resume = clone(resume)

    summary = profile.get("summary")
    if isinstance(summary, str) and summary:
        basics = next_resume.setdefault("basics", {})
        if isinstance(basics, dict):
            basics["summary"] = summary

    sections = profile.get("sections")
    if isinstance(sections, dict):
        for section_name, config in sections.items():
            if not isinstance(section_name, str) or not isinstance(config, dict):
                continue

            if config.get("enabled") is False:
                next_resume[section_name] = []
                continue

            limit = config.get("limit")
            current_value = next_resume.get(section_name)
            if isinstance(limit, int) and isinstance(current_value, list):
                next_resume[section_name] = current_value[:limit]

    return next_resume
