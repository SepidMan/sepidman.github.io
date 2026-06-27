from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from jsonschema import Draft7Validator, FormatChecker
from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path.cwd()
CV_DIR = ROOT_DIR / "cv"
BUILD_DIR = ROOT_DIR / "build"
RESUME_PATH = CV_DIR / "resume.json"
RESUME_SCHEMA_PATH = CV_DIR / "resume_schema.json"
VARIANTS_PATH = CV_DIR / "rendercv" / "variants.json"
BASE_RENDER_CV_PATH = CV_DIR / "rendercv" / "base.yaml"
NODE_CONVERTER_PATH = ROOT_DIR / "node_modules" / "@jsonresume" / "jsonresume-to-rendercv" / "index.js"
PIXI_BINARY = Path.home() / ".pixi" / "bin" / "pixi"


class ResumePipelineError(RuntimeError):
    """Raised when the resume pipeline cannot complete."""


def assert_condition(condition: bool, message: str) -> None:
    if not condition:
        raise ResumePipelineError(message)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf8") as handle:
        return json.load(handle)


def read_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf8") as handle:
        return yaml.safe_load(handle)


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)


def deep_merge(target: Any, source: Any) -> Any:
    if not isinstance(source, dict):
        return source

    result = dict(target) if isinstance(target, dict) else {}
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def ensure_readable(path: Path, label: str) -> None:
    if not path.is_file():
        raise ResumePipelineError(f"{label} is missing or unreadable: {path}")


def validate_variant_shape(name: str, config: Any) -> None:
    assert_condition(isinstance(config, dict), f'Variant "{name}" must be an object.')
    assert_condition(isinstance(config.get("profile"), str) and config["profile"], f'Variant "{name}" must define a profile.')
    assert_condition(isinstance(config.get("theme"), str) and config["theme"], f'Variant "{name}" must define a theme.')
    assert_condition(isinstance(config.get("output"), str) and config["output"], f'Variant "{name}" must define an output path.')
    assert_condition(config["output"].startswith("build/assets/"), f'Variant "{name}" output must live under build/assets/.')


def validate_resume_pipeline() -> dict[str, Any]:
    for path, label in [
        (RESUME_PATH, "Resume source"),
        (RESUME_SCHEMA_PATH, "Resume schema"),
        (VARIANTS_PATH, "RenderCV variants config"),
        (BASE_RENDER_CV_PATH, "RenderCV base config"),
        (NODE_CONVERTER_PATH, "JSON Resume converter"),
    ]:
        ensure_readable(path, label)

    resume = read_json(RESUME_PATH)
    schema = read_json(RESUME_SCHEMA_PATH)
    variants = read_json(VARIANTS_PATH)

    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(resume), key=lambda error: list(error.path))
    if errors:
        messages = []
        for error in errors:
            pointer = "/" + "/".join(str(part) for part in error.path) if error.path else "/"
            messages.append(f"{pointer} {error.message}")
        raise ResumePipelineError("cv/resume.json failed schema validation:\n" + "\n".join(messages))

    assert_condition(isinstance(variants, dict), "cv/rendercv/variants.json must be an object keyed by variant name.")

    default_theme = CV_DIR / "rendercv" / "themes" / "default.yaml"
    ensure_readable(default_theme, "Default theme config")

    for name, config in variants.items():
        validate_variant_shape(name, config)
        ensure_readable(CV_DIR / "profiles" / f"{config['profile']}.json", f'Profile for variant "{name}"')
        ensure_readable(CV_DIR / "rendercv" / "themes" / f"{config['theme']}.yaml", f'Theme for variant "{name}"')

    return {"resume": resume, "variants": variants}


def clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def pick_username(profile: dict[str, Any]) -> str:
    username = profile.get("username")
    if isinstance(username, str) and username:
        return username

    url = profile.get("url")
    if isinstance(url, str) and url:
        try:
            from urllib.parse import urlparse

            return urlparse(url).path.lstrip("/")
        except Exception:
            return url

    return ""


def format_location(location: dict[str, Any] | None) -> str:
    if not isinstance(location, dict):
        return ""

    country = location.get("countryCode") or ""
    region = location.get("region") or ""
    city = location.get("city") or ""
    if region == city:
        region = ""

    parts = [part for part in [city, region, country] if part]
    return ", ".join(parts)


def to_date_fields(start_date: Any, end_date: Any) -> dict[str, Any] | None:
    fields: dict[str, Any] = {}
    if start_date:
        fields["start_date"] = start_date
    if end_date:
        fields["end_date"] = end_date
    elif start_date:
        fields["end_date"] = "present"
    return fields or None


def with_summary_highlights(summary: Any, highlights: Any) -> list[str]:
    if isinstance(highlights, list):
        normalized = [item for item in highlights if item]
        if normalized:
            return normalized
    return [summary] if isinstance(summary, str) and summary else []


def apply_profile_overrides(resume: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    next_resume = clone(resume)

    summary = profile.get("summary")
    if isinstance(summary, str) and summary:
        next_resume.setdefault("basics", {})["summary"] = summary

    sections = profile.get("sections", {})
    if isinstance(sections, dict):
        for section_name, config in sections.items():
            if not isinstance(config, dict):
                continue
            if config.get("enabled") is False:
                next_resume[section_name] = []
                continue
            limit = config.get("limit")
            if isinstance(limit, int) and isinstance(next_resume.get(section_name), list):
                next_resume[section_name] = next_resume[section_name][:limit]

    return next_resume


def build_sections(resume: dict[str, Any]) -> dict[str, Any]:
    sections: dict[str, Any] = {}
    basics = resume.get("basics", {})

    if basics.get("summary"):
        sections["summary"] = [basics["summary"]]

    work_items = resume.get("work")
    if isinstance(work_items, list) and work_items:
        entries = []
        for item in work_items:
            entry = {
                "company": item.get("name"),
                "position": item.get("position"),
                "highlights": with_summary_highlights(item.get("summary"), item.get("highlights")),
            }
            if item.get("location"):
                entry["location"] = item["location"]
            if item.get("summary"):
                entry["summary"] = item["summary"]
            dates = to_date_fields(item.get("startDate"), item.get("endDate"))
            if dates:
                entry.update(dates)
            entries.append(entry)
        sections["experience"] = entries

    education_items = resume.get("education")
    if isinstance(education_items, list) and education_items:
        entries = []
        for item in education_items:
            entry = {
                "institution": item.get("institution"),
                "area": item.get("area") or "",
                "degree": item.get("studyType") or "",
            }
            if item.get("location"):
                entry["location"] = item["location"]
            if item.get("summary"):
                entry["summary"] = item["summary"]
            dates = to_date_fields(item.get("startDate"), item.get("endDate"))
            if dates:
                entry.update(dates)
            entries.append(entry)
        sections["education"] = entries

    skills = resume.get("skills")
    if isinstance(skills, list) and skills:
        sections["skills"] = [
            {
                "label": item.get("name"),
                "details": ", ".join(item.get("keywords", [])) if isinstance(item.get("keywords"), list) else "",
            }
            for item in skills
        ]

    projects = resume.get("projects")
    if isinstance(projects, list) and projects:
        entries = []
        for item in projects:
            entry = {
                "name": item.get("name"),
                "highlights": with_summary_highlights(item.get("description"), item.get("highlights")),
            }
            if item.get("description"):
                entry["summary"] = item["description"]
            dates = to_date_fields(item.get("startDate"), item.get("endDate"))
            if dates:
                entry.update(dates)
            entries.append(entry)
        sections["projects"] = entries

    certifications = resume.get("certifications")
    if isinstance(certifications, list) and certifications:
        sections["certifications"] = [
            {
                "label": item.get("name"),
                "details": " | ".join(part for part in [item.get("issuer"), item.get("date")] if part),
            }
            for item in certifications
        ]

    languages = resume.get("languages")
    if isinstance(languages, list) and languages:
        sections["languages"] = [
            {"label": item.get("language"), "details": item.get("fluency") or ""}
            for item in languages
        ]

    awards = resume.get("awards")
    if isinstance(awards, list) and awards:
        sections["awards"] = [
            {"bullet": " | ".join(part for part in [item.get("title"), item.get("awarder")] if part)}
            for item in awards
        ]

    return sections


def run_jsonresume_converter(profiled_resume: dict[str, Any]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="resume-pipeline-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        input_path = temp_dir / "resume.json"
        output_path = temp_dir / "resume.yaml"
        input_path.write_text(json.dumps(profiled_resume), encoding="utf8")
        subprocess.run(
            ["node", str(NODE_CONVERTER_PATH), str(input_path)],
            cwd=temp_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        return yaml.safe_load(output_path.read_text(encoding="utf8"))


def build_rendercv_data(
    resume: dict[str, Any],
    converted_seed: dict[str, Any],
    theme_config: dict[str, Any],
    output_path: Path,
    render_output_dir: Path,
    rendered_pdf_path: Path,
) -> dict[str, Any]:
    basics = resume.get("basics", {})
    output_folder = Path(render_output_dir.relative_to(output_path.parent))
    pdf_path = Path(rendered_pdf_path.relative_to(output_path.parent))
    typst_path = pdf_path.with_suffix(".typ")

    cv = dict(converted_seed.get("cv", {}))
    cv.update(
        {
            "name": basics.get("name"),
            "headline": basics.get("label") or "",
            "location": format_location(basics.get("location")),
            "email": basics.get("email") or "",
            "phone": basics.get("phone") or "",
            "website": basics.get("url") or "",
            "social_networks": [
                {"network": profile.get("network"), "username": pick_username(profile)}
                for profile in basics.get("profiles", [])
            ],
            "sections": build_sections(resume),
        }
    )

    return deep_merge(
        theme_config,
        {
            "cv": cv,
            "settings": {
                "current_date": "today",
                "render_command": {
                    "output_folder": str(output_folder),
                    "pdf_path": str(pdf_path),
                    "typst_path": str(typst_path),
                    "dont_generate_markdown": True,
                    "dont_generate_html": True,
                    "dont_generate_png": True,
                },
            },
        },
    )


def load_variant(variant: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    validated = validate_resume_pipeline()
    resume = validated["resume"]
    variants = validated["variants"]
    variant_config = variants.get(variant)
    assert_condition(isinstance(variant_config, dict), f'Unknown resume variant "{variant}".')

    profile = read_json(CV_DIR / "profiles" / f"{variant_config['profile']}.json")
    base_config = read_yaml(BASE_RENDER_CV_PATH)
    theme_config = read_yaml(CV_DIR / "rendercv" / "themes" / f"{variant_config['theme']}.yaml")
    return resume, variant_config, deep_merge(base_config, theme_config), profile


def generate_rendercv_yaml(variant: str = "default", output: str | None = None) -> dict[str, Any]:
    resume, variant_config, theme_config, profile = load_variant(variant)
    profiled_resume = apply_profile_overrides(resume, profile)
    converted_seed = run_jsonresume_converter(profiled_resume)

    output_path = ROOT_DIR / (output or f"cv/generated/rendercv-{variant}.yaml")
    render_output_dir = ROOT_DIR / "cv" / "generated" / "rendered" / variant
    rendered_pdf_path = render_output_dir / f"{variant}.pdf"
    public_pdf_output_path = ROOT_DIR / variant_config["output"]

    rendercv_data = build_rendercv_data(
        profiled_resume,
        converted_seed,
        theme_config,
        output_path,
        render_output_dir,
        rendered_pdf_path,
    )
    write_yaml(output_path, rendercv_data)

    return {
        "output_path": output_path,
        "profile": variant_config["profile"],
        "theme": variant_config["theme"],
        "render_output_dir": render_output_dir,
        "rendered_pdf_path": rendered_pdf_path,
        "public_pdf_output_path": public_pdf_output_path,
    }


def ensure_pixi() -> None:
    if not PIXI_BINARY.is_file():
        raise ResumePipelineError(f"Pixi is not installed at {PIXI_BINARY}. Install it first or reopen the devcontainer.")


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT_DIR, check=True)


def build_variant(variant: str) -> Path:
    ensure_pixi()
    generated = generate_rendercv_yaml(variant=variant)
    output_path = generated["output_path"]
    rendered_pdf_path = generated["rendered_pdf_path"]
    public_pdf_output_path = generated["public_pdf_output_path"]

    (BUILD_DIR / "assets").mkdir(parents=True, exist_ok=True)
    run([str(PIXI_BINARY), "run", "rendercv", "render", str(output_path)])
    assert_condition(rendered_pdf_path.is_file(), f"RenderCV did not produce {rendered_pdf_path}")
    shutil.copyfile(rendered_pdf_path, public_pdf_output_path)
    assert_condition(public_pdf_output_path.is_file(), f"Public PDF was not copied to {public_pdf_output_path}")
    return public_pdf_output_path


def build_resume_pdf(variant: str = "default", build_all: bool = False) -> list[Path]:
    validated = validate_resume_pipeline()
    variants = validated["variants"]
    names = list(variants.keys()) if build_all else [variant]
    return [build_variant(name) for name in names]
