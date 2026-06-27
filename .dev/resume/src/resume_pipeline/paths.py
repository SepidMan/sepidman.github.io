"""Workspace-relative paths used by the resume pipeline."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path.cwd()
CV_DIR = ROOT_DIR / "cv"
BUILD_DIR = ROOT_DIR / "build"
RESUME_PATH = CV_DIR / "resume.yaml"
RESUME_SCHEMA_PATH = CV_DIR / "resume_schema.json"
VARIANTS_PATH = CV_DIR / "rendercv" / "variants.yaml"
BASE_RENDER_CV_PATH = CV_DIR / "rendercv" / "base.yaml"
PIXI_BINARY = Path.home() / ".pixi" / "bin" / "pixi"


def profile_path(name: str) -> Path:
    """Return the path to a profile override file."""
    return CV_DIR / "profiles" / f"{name}.yaml"


def theme_path(name: str) -> Path:
    """Return the path to a RenderCV theme overlay file."""
    return CV_DIR / "rendercv" / "themes" / f"{name}.yaml"


def generated_yaml_path(variant: str, output: str | None = None) -> Path:
    """Return the generated YAML path for a variant."""
    return ROOT_DIR / (output or f"cv/generated/rendercv-{variant}.yaml")


def render_output_dir(variant: str) -> Path:
    """Return the RenderCV working directory for a variant."""
    return ROOT_DIR / "cv" / "generated" / "rendered" / variant
