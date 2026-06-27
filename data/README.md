# Data Pipeline

This directory is the canonical content source for the website, JSON Resume export, and RenderCV PDF pipeline.

## Layout

```text
data/
  README.md
  main.yaml
  schema.json
  schema/
  jsonresume.schema.json
  resume_ux.md
  profile-model.md
  profiles/
  rendercv/
```

## What Lives Where

`main.yaml`

- The single source of truth for resume content and website editorial copy.
- Includes standard JSON Resume fields plus internal `website.*` extensions.
- Edit this when job history, bio, contact details, social links, homepage copy, or resume content changes.

`schema.json`

- Thin top-level validation schema for `main.yaml`.
- Composes smaller schema modules under `schema/`.

`schema/`

- Split internal schema modules for canonical content, website content, shared definitions, and export configuration.
- Keeps model changes localized instead of editing one monolithic schema file.

`jsonresume.schema.json`

- Local copy of the official JSON Resume schema.
- Used to validate the generated JSON Resume export.

`profiles/`

- Small PDF-only content overrides.
- `cv.yaml` leaves the canonical content untouched.
- `resume.yaml` trims the content for the shorter application-oriented variant.

`rendercv/`

- RenderCV-specific configuration.
- `base.yaml` holds shared paper-layout defaults.
- `themes/` contains visual overlays for different PDF families.
- Canonical variant metadata now lives in `main.yaml` under `exports.rendercv.variants`.

## Build Outputs

- Intermediate RenderCV YAML and Typst/PDF working files are written to `build/cv/`.
- Public downloadable assets are written to `build/website/assets/`.

## Flow

1. Validate `main.yaml` against `schema.json`.
2. Project JSON Resume fields from `main.yaml` and validate that export against `jsonresume.schema.json`.
3. Load a profile from `profiles/` for each requested PDF variant.
4. Read RenderCV variant/settings metadata from `main.yaml` and merge `rendercv/base.yaml` with the selected theme overlay.
5. Write the generated RenderCV YAML to `build/cv/`.
6. Render the paper-native PDFs through RenderCV.
7. Publish the PDFs and the generated JSON Resume asset into `build/website/assets/`.

## Common Commands

```bash
npx task validate:resume
npx task build:resume
npx task build:resume:variant VARIANT=resume
npx task build
```
