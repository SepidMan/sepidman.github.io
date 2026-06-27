"""Validation for resume content and pipeline configuration."""

from __future__ import annotations

from jsonschema import Draft7Validator, FormatChecker, RefResolver

from .assets import resume_slug
from .errors import ResumePipelineError
from .io_utils import assert_condition, ensure_readable, read_json, read_yaml
from .paths import (
    BASE_RENDER_CV_PATH,
    JSONRESUME_SCHEMA_PATH,
    MAIN_PATH,
    ROOT_DIR,
    SCHEMA_PATH,
    VARIANTS_PATH,
    profile_path,
    theme_path,
)
from .transform import build_jsonresume_data
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
    message = f'Variant "{name}" output must live under build/website/assets/.'
    assert_condition(
        condition=output.startswith("build/website/assets/"),
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
        (MAIN_PATH, "Canonical resume source"),
        (SCHEMA_PATH, "Canonical schema"),
        (JSONRESUME_SCHEMA_PATH, "JSON Resume schema"),
        (VARIANTS_PATH, "RenderCV variants config"),
        (BASE_RENDER_CV_PATH, "RenderCV base config"),
    ]:
        ensure_readable(path, label)

    resume = read_yaml(MAIN_PATH)
    schema = read_json(SCHEMA_PATH)
    jsonresume_schema = read_json(JSONRESUME_SCHEMA_PATH)
    variants_data = read_yaml(VARIANTS_PATH)
    canonical_resume_slug = resume_slug(resume)

    resolver = RefResolver(
        base_uri=SCHEMA_PATH.resolve().as_uri(),
        referrer=schema,
        store={JSONRESUME_SCHEMA_PATH.resolve().as_uri(): jsonresume_schema},
    )
    validator = Draft7Validator(
        schema,
        format_checker=FormatChecker(),
        resolver=resolver,
    )
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
        message = "data/main.yaml failed schema validation:\n" + "\n".join(messages)
        raise ResumePipelineError(message)

    jsonresume = build_jsonresume_data(resume)
    jsonresume_validator = Draft7Validator(
        jsonresume_schema,
        format_checker=FormatChecker(),
    )
    jsonresume_errors = sorted(
        jsonresume_validator.iter_errors(jsonresume),
        key=lambda error: list(error.path),
    )
    if jsonresume_errors:
        messages = []
        for error in jsonresume_errors:
            pointer = (
                "/" + "/".join(str(part) for part in error.path)
                if error.path
                else "/"
            )
            messages.append(f"{pointer} {error.message}")
        message = (
            "Generated JSON Resume output failed schema validation:\n"
            + "\n".join(messages)
        )
        raise ResumePipelineError(message)

    assert_condition(
        condition=isinstance(variants_data, dict),
        message="data/rendercv/variants.yaml must be an object keyed by variant name.",
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
