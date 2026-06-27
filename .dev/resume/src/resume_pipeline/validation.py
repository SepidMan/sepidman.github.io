"""Validation for resume content and pipeline configuration."""

from __future__ import annotations

from jsonschema import Draft7Validator, FormatChecker, RefResolver

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
    resume: object,
    schema: object,
    jsonresume_schema: object,
) -> None:
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
