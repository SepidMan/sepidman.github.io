"""Conversion from canonical resume data to RenderCV YAML."""

from __future__ import annotations

from .errors import ResumePipelineError
from .io_utils import assert_condition, deep_merge, read_yaml, write_yaml
from .paths import (
    BASE_RENDER_CV_PATH,
    generated_yaml_path,
    profile_path,
    render_output_dir,
    theme_path,
)
from .profiles import apply_profile_overrides
from .transform import build_rendercv_data
from .types import GeneratedVariant, GeneratedVariantPaths, JsonDict, VariantConfig
from .validation import validate_resume_pipeline


def _load_variant(variant: str) -> tuple[JsonDict, VariantConfig, JsonDict, JsonDict]:
    validated = validate_resume_pipeline()
    variant_config = validated.variants.get(variant)
    if variant_config is None:
        msg = f'Unknown resume variant "{variant}".'
        raise ResumePipelineError(msg)

    profile = read_yaml(profile_path(variant_config.profile))
    base_config = read_yaml(BASE_RENDER_CV_PATH)
    theme_config = read_yaml(theme_path(variant_config.theme))
    merged_theme = deep_merge(base_config, theme_config)
    message = "Expected merged RenderCV theme config to stay object-shaped."
    assert_condition(condition=isinstance(merged_theme, dict), message=message)
    return validated.resume, variant_config, merged_theme, profile


def generate_rendercv_yaml(
    variant: str = "cv",
    output: str | None = None,
) -> GeneratedVariant:
    """Generate the RenderCV YAML input for a named resume variant."""
    resume, variant_config, theme_config, profile = _load_variant(variant)
    profiled_resume = apply_profile_overrides(resume, profile)

    output_path = generated_yaml_path(variant, output)
    render_dir = render_output_dir(variant)
    rendered_pdf_path = render_dir / f"{variant}.pdf"
    paths = GeneratedVariantPaths(
        output_path=output_path,
        render_output_dir=render_dir,
        rendered_pdf_path=rendered_pdf_path,
        public_pdf_output_path=variant_config.output,
    )

    rendercv_data = build_rendercv_data(
        profiled_resume,
        theme_config,
        paths,
    )
    write_yaml(paths.output_path, rendercv_data)

    return GeneratedVariant(variant=variant_config, profile=profile, paths=paths)
