"""Shared typed structures for the resume pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
type JsonDict = dict[str, JsonValue]


@dataclass(frozen=True)
class VariantConfig:
    """Definition of a named PDF variant."""

    name: str
    profile: str
    theme: str
    output: Path
    label: str | None = None
    summary: str | None = None


@dataclass(frozen=True)
class RenderCVConfig:
    """Canonical RenderCV export settings from the internal data model."""

    current_date: str = "today"
    bold_keywords: list[str] | None = None
    pdf_title: str | None = None
    locale_language: str | None = None


@dataclass(frozen=True)
class PipelineConfig:
    """Validated resume data and variant registry."""

    resume: JsonDict
    variants: dict[str, VariantConfig]
    rendercv: RenderCVConfig


@dataclass(frozen=True)
class GeneratedVariantPaths:
    """Generated and published file paths for a variant."""

    output_path: Path
    render_output_dir: Path
    rendered_pdf_path: Path
    public_pdf_output_path: Path


@dataclass(frozen=True)
class GeneratedVariant:
    """Complete result of preparing a variant for RenderCV."""

    variant: VariantConfig
    profile: JsonDict
    paths: GeneratedVariantPaths
