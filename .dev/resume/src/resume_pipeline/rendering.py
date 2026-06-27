"""RenderCV execution and public PDF publication."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .conversion import generate_rendercv_yaml
from .errors import ResumePipelineError
from .paths import BUILD_DIR, PIXI_BINARY
from .validation import validate_resume_pipeline


def _ensure_pixi() -> None:
    if not PIXI_BINARY.is_file():
        msg = f"Pixi is not installed at {PIXI_BINARY}. Install it first or reopen the devcontainer."
        raise ResumePipelineError(msg)


def _run_rendercv(command: list[str]) -> None:
    subprocess.run(command, check=True, cwd=BUILD_DIR.parent)  # noqa: S603


def _build_variant(name: str) -> Path:
    generated = generate_rendercv_yaml(variant=name)
    BUILD_DIR.joinpath("assets").mkdir(parents=True, exist_ok=True)
    _run_rendercv(
        [
            str(PIXI_BINARY),
            "run",
            "--environment",
            "rendercv",
            "rendercv",
            "render",
            str(generated.paths.output_path),
        ],
    )
    if not generated.paths.rendered_pdf_path.is_file():
        msg = f"RenderCV did not produce {generated.paths.rendered_pdf_path}"
        raise ResumePipelineError(msg)
    shutil.copyfile(generated.paths.rendered_pdf_path, generated.paths.public_pdf_output_path)
    if not generated.paths.public_pdf_output_path.is_file():
        msg = f"Public PDF was not copied to {generated.paths.public_pdf_output_path}"
        raise ResumePipelineError(msg)
    return generated.paths.public_pdf_output_path


def build_resume_pdf(variant: str = "default", *, build_all: bool = False) -> list[Path]:
    """Build one or more PDF variants through RenderCV."""
    _ensure_pixi()
    variants = validate_resume_pipeline().variants
    names = list(variants) if build_all else [variant]
    return [_build_variant(name) for name in names]
