"""Helpers for naming public resume assets."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .paths import WEBSITE_ASSETS_DIR

if TYPE_CHECKING:
    from pathlib import Path

    from .types import JsonDict


def resume_slug(resume: JsonDict) -> str:
    """Build a filesystem-safe slug from the resume owner's name."""
    basics = resume.get("basics")
    name = basics.get("name") if isinstance(basics, dict) else ""
    if not isinstance(name, str) or not name.strip():
        return "resume"
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
    return slug.strip("-") or "resume"


def public_jsonresume_output_path(resume: JsonDict) -> Path:
    """Return the published JSON Resume asset path."""
    return WEBSITE_ASSETS_DIR / f"{resume_slug(resume)}-jsonresume.json"
