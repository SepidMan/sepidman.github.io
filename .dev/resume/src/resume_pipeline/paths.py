"""Workspace-relative paths used by the resume pipeline."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path.cwd()
DATA_DIR = ROOT_DIR / "data"
BUILD_DIR = ROOT_DIR / "build"
CV_BUILD_DIR = BUILD_DIR / "cv"
WEBSITE_BUILD_DIR = BUILD_DIR / "website"
WEBSITE_ASSETS_DIR = WEBSITE_BUILD_DIR / "assets"
MAIN_PATH = DATA_DIR / "main.yaml"
SCHEMA_PATH = DATA_DIR / "schema.json"
JSONRESUME_SCHEMA_PATH = DATA_DIR / "jsonresume.schema.json"
BASE_RENDER_CV_PATH = DATA_DIR / "rendercv" / "base.yaml"
PIXI_BINARY = Path.home() / ".pixi" / "bin" / "pixi"


def profile_path(name: str) -> Path:
    """Return the path to a profile override file."""
    return DATA_DIR / "profiles" / f"{name}.yaml"


def theme_path(name: str) -> Path:
    """Return the path to a RenderCV theme overlay file."""
    return DATA_DIR / "rendercv" / "themes" / f"{name}.yaml"


def generated_yaml_path(variant: str, output: str | None = None) -> Path:
    """Return the generated YAML path for a variant."""
    return ROOT_DIR / (output or f"build/cv/rendercv-{variant}.yaml")


def render_output_dir(variant: str) -> Path:
    """Return the RenderCV working directory for a variant."""
    return CV_BUILD_DIR / "rendered" / variant
