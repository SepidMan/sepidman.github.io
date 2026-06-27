"""Validation for resume content and pipeline configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jsonschema import Draft7Validator
from pyserials import validate as serial_validate

from .assets import resume_slug
from .errors import ResumePipelineError
from .io_utils import assert_condition, ensure_readable, read_json, read_yaml
from .jsonresume import build_jsonresume_data
from .paths import (
    BASE_RENDER_CV_PATH,
    JSONRESUME_SCHEMA_PATH,
    MAIN_PATH,
    ROOT_DIR,
    SCHEMA_PATH,
    profile_path,
    theme_path,
)
from .types import PipelineConfig, RenderCVConfig, VariantConfig

if TYPE_CHECKING:
    from .types import JsonDict


def _pointer_for_error(error: object) -> str:
    """Convert a validation error path into a JSON pointer."""
    path = getattr(error, "path", ())
    path_parts = list(path) if path else []
    return "/" + "/".join(str(part) for part in path_parts) if path_parts else "/"


def _validate_schema(
    *,
    data: JsonDict,
    schema: JsonDict,
    failure_message: str,
) -> None:
    """Validate data against a JSON Schema using pyserials."""
    errors = serial_validate.jsonschema(
        data,
        schema,
        validator=Draft7Validator,
        iter_errors=True,
        raise_invalid_data=False,
    )
    if not errors:
        return

    messages = [
        f"{_pointer_for_error(error)} {error.message}"
        for error in sorted(errors, key=lambda error: list(error.path))
    ]
    raise ResumePipelineError(f"{failure_message}\n" + "\n".join(messages))


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


def _validate_canonical_resume(
    *,
    resume: JsonDict,
    schema: JsonDict,
    jsonresume_schema: JsonDict,
) -> None:
    _validate_schema(
        data=resume,
        schema=schema,
        failure_message="data/main.yaml failed schema validation:",
    )
    _validate_schema(
        data=build_jsonresume_data(resume),
        schema=jsonresume_schema,
        failure_message="Generated JSON Resume output failed schema validation:",
    )


def _extract_rendercv_config(
    resume: object,
    *,
    canonical_resume_slug: str,
) -> tuple[dict[str, VariantConfig], RenderCVConfig]:
    assert_condition(
        condition=isinstance(resume, dict),
        message="Canonical resume data must be an object.",
    )
    exports = resume.get("exports")
    message = "data/main.yaml must define exports.rendercv for PDF generation."
    assert_condition(condition=isinstance(exports, dict), message=message)
    rendercv = exports.get("rendercv")
    assert_condition(condition=isinstance(rendercv, dict), message=message)

    settings = rendercv.get("settings")
    message = "data/main.yaml exports.rendercv.settings must be an object."
    assert_condition(condition=isinstance(settings, dict), message=message)
    locale = rendercv.get("locale")
    message = "data/main.yaml exports.rendercv.locale must be an object when provided."
    assert_condition(
        condition=locale is None or isinstance(locale, dict),
        message=message,
    )
    variants_data = rendercv.get("variants")
    assert_condition(
        condition=isinstance(variants_data, dict),
        message="data/main.yaml exports.rendercv.variants must be an object keyed by variant name.",
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

    current_date = settings.get("currentDate")
    message = "exports.rendercv.settings.currentDate must be a string."
    assert_condition(
        condition=isinstance(current_date, str),
        message=message,
    )
    bold_keywords = settings.get("boldKeywords")
    message = "exports.rendercv.settings.boldKeywords must be an array when provided."
    assert_condition(
        condition=bold_keywords is None or isinstance(bold_keywords, list),
        message=message,
    )
    pdf_title = settings.get("pdfTitle")
    message = "exports.rendercv.settings.pdfTitle must be a string when provided."
    assert_condition(
        condition=pdf_title is None or isinstance(pdf_title, str),
        message=message,
    )
    locale_language = locale.get("language") if isinstance(locale, dict) else None
    message = "exports.rendercv.locale.language must be a string when provided."
    assert_condition(
        condition=locale_language is None or isinstance(locale_language, str),
        message=message,
    )

    return variants, RenderCVConfig(
        current_date=current_date,
        bold_keywords=(
            [item for item in bold_keywords if isinstance(item, str)]
            if isinstance(bold_keywords, list)
            else []
        ),
        pdf_title=pdf_title,
        locale_language=locale_language,
    )


def validate_resume_pipeline() -> PipelineConfig:
    """Validate canonical resume content and variant configuration."""
    for path, label in [
        (MAIN_PATH, "Canonical resume source"),
        (SCHEMA_PATH, "Canonical schema"),
        (JSONRESUME_SCHEMA_PATH, "JSON Resume schema"),
        (BASE_RENDER_CV_PATH, "RenderCV base config"),
    ]:
        ensure_readable(path, label)

    resume = read_yaml(MAIN_PATH)
    schema = read_json(SCHEMA_PATH)
    jsonresume_schema = read_json(JSONRESUME_SCHEMA_PATH)
    canonical_resume_slug = resume_slug(resume)
    _validate_canonical_resume(
        resume=resume,
        schema=schema,
        jsonresume_schema=jsonresume_schema,
    )
    variants, rendercv = _extract_rendercv_config(
        resume,
        canonical_resume_slug=canonical_resume_slug,
    )

    return PipelineConfig(resume=resume, variants=variants, rendercv=rendercv)
