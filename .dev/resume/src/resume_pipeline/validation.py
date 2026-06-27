"""Validation for resume content and pipeline configuration."""

from __future__ import annotations

from jsonschema import Draft7Validator, FormatChecker

from .assets import resume_slug
from .errors import ResumePipelineError
from .io_utils import assert_condition, ensure_readable, read_json, read_yaml
from .paths import (
    BASE_RENDER_CV_PATH,
    RESUME_PATH,
    RESUME_SCHEMA_PATH,
    ROOT_DIR,
    VARIANTS_PATH,
    profile_path,
    theme_path,
)
from .types import PipelineConfig, VariantConfig


def _validate_variant_shape(
    name: str,
    config: object,
    *,
    canonical_resume_slug: str,
) -> VariantConfig:
    message = f'Variant "{name}" must be an object.'
    assert_condition(condition=isinstance(config, dict), message=message)
    profile = config.get("profile")
    theme = config.get("theme")
    output = config.get("output")
    label = config.get("label")
    summary = config.get("summary")

    message = f'Variant "{name}" must define a profile.'
    assert_condition(
        condition=isinstance(profile, str) and bool(profile),
        message=message,
    )
    message = f'Variant "{name}" must define a theme.'
    assert_condition(
        condition=isinstance(theme, str) and bool(theme),
        message=message,
    )
    message = f'Variant "{name}" must define an output path.'
    assert_condition(
        condition=isinstance(output, str) and bool(output),
        message=message,
    )
    message = f'Variant "{name}" output must live under build/assets/.'
    assert_condition(
        condition=output.startswith("build/assets/"),
        message=message,
    )
    message = f'Variant "{name}" label must be a string when provided.'
    assert_condition(
        condition=label is None or isinstance(label, str),
        message=message,
    )
    message = f'Variant "{name}" summary must be a string when provided.'
    assert_condition(
        condition=summary is None or isinstance(summary, str),
        message=message,
    )

    resolved_output = output.replace("{resume_slug}", canonical_resume_slug)

    return VariantConfig(
        name=name,
        profile=profile,
        theme=theme,
        output=ROOT_DIR / resolved_output,
        label=label,
        summary=summary,
    )


def validate_resume_pipeline() -> PipelineConfig:
    """Validate canonical resume content and variant configuration."""
    for path, label in [
        (RESUME_PATH, "Resume source"),
        (RESUME_SCHEMA_PATH, "Resume schema"),
        (VARIANTS_PATH, "RenderCV variants config"),
        (BASE_RENDER_CV_PATH, "RenderCV base config"),
    ]:
        ensure_readable(path, label)

    resume = read_yaml(RESUME_PATH)
    schema = read_json(RESUME_SCHEMA_PATH)
    variants_data = read_yaml(VARIANTS_PATH)
    canonical_resume_slug = resume_slug(resume)

    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(resume), key=lambda error: list(error.path))
    if errors:
        messages = []
        for error in errors:
            pointer = (
                "/" + "/".join(str(part) for part in error.path)
                if error.path
                else "/"
            )
            messages.append(f"{pointer} {error.message}")
        message = "cv/resume.yaml failed schema validation:\n" + "\n".join(messages)
        raise ResumePipelineError(message)

    assert_condition(
        condition=isinstance(variants_data, dict),
        message="cv/rendercv/variants.yaml must be an object keyed by variant name.",
    )

    ensure_readable(theme_path("default"), "Default theme config")

    variants: dict[str, VariantConfig] = {}
    for name, config in variants_data.items():
        assert_condition(
            condition=isinstance(name, str),
            message="Variant names must be strings.",
        )
        variant = _validate_variant_shape(
            name,
            config,
            canonical_resume_slug=canonical_resume_slug,
        )
        ensure_readable(profile_path(variant.profile), f'Profile for variant "{name}"')
        ensure_readable(theme_path(variant.theme), f'Theme for variant "{name}"')
        variants[name] = variant

    return PipelineConfig(resume=resume, variants=variants)
