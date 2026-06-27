# CV Pipeline

This directory contains the resume source data and the configuration that turns it into one or more paper-native PDFs.

The resume system now has two separate presentation layers:

- Web resume: `cv/resume.yaml` -> Eleventy data normalization -> `/resume/`
- PDF resume: `cv/resume.yaml` -> profile override -> RenderCV YAML -> PDF in `build/assets/`

The important idea is that `resume.yaml` is the canonical source, while the files under `profiles/` and `rendercv/` control how that source is shaped and styled for specific PDF outputs.

## Layout

```text
cv/
  README.md
  resume.yaml
  resume_schema.json
  resume_ux.md
  generated/
  profiles/
  rendercv/
```

## Files And Directories

`resume.yaml`

- The canonical resume source.
- This is the primary file to edit when the actual content changes.
- Both the website resume and the PDF pipeline ultimately derive from this file.

`resume_schema.json`

- The JSON Resume schema used by the validation step.
- The pipeline checks `resume.yaml` against this before generating PDFs.
- Usually you should not edit this unless the schema version or local validation approach changes.

`resume_ux.md`

- Supporting notes and non-pipeline content related to the resume.
- This is not part of the automated PDF build.

`generated/`

- Intermediate RenderCV YAML files produced by the conversion step.
- These are build artifacts, not source files.
- They help with debugging the final RenderCV input if a PDF looks wrong or RenderCV validation fails.
- RenderCV also writes its working `.typ` and intermediate PDF files under `generated/rendered/<variant>/`.
- Only the final public PDFs are copied to `build/assets/`.
- They are ignored by git and can be regenerated at any time.

`profiles/`

- Small content overrides used to create different PDF variants from the same canonical resume.
- A profile does not replace `resume.yaml`; it adjusts it.
- Current supported overrides are intentionally narrow:
  - replace the summary
  - disable a section
  - limit how many items from a section are included

Examples:

- [profiles/cv.yaml](/workspaces/sepidman.github.io/cv/profiles/cv.yaml:1)
  Leaves the canonical content untouched for the full CV output.
- [profiles/resume.yaml](/workspaces/sepidman.github.io/cv/profiles/resume.yaml:1)
  Replaces the summary, hides awards, limits projects to 1, and limits certificates to 2.

`rendercv/`

- RenderCV-specific configuration for PDF generation.
- This directory answers:
  - which PDF variants exist
  - which profile each variant uses
  - which theme preset each variant uses
  - the shared page/layout defaults for all PDFs

## RenderCV Config

`rendercv/variants.yaml`

- The registry of available PDF outputs.
- Each variant maps a name like `cv` or `resume` to:
  - a profile in `profiles/`
  - a theme preset in `rendercv/themes/`
  - an output path in `build/assets/`

See [rendercv/variants.yaml](/workspaces/sepidman.github.io/cv/rendercv/variants.yaml:1).

`rendercv/base.yaml`

- Shared RenderCV defaults for page size, margins, typography, header spacing, and section spacing.
- This is the right place for global paper-layout tuning that should affect all PDF variants.

See [rendercv/base.yaml](/workspaces/sepidman.github.io/cv/rendercv/base.yaml:1).

`rendercv/themes/`

- Small theme overlays layered on top of `base.yaml`.
- These control visual differences between variants, such as theme choice, colors, and font decisions.
- Use these when you want one PDF version to look more minimal or more branded without changing the underlying content logic.

Current examples:

- [rendercv/themes/default.yaml](/workspaces/sepidman.github.io/cv/rendercv/themes/default.yaml:1)
- [rendercv/themes/minimal.yaml](/workspaces/sepidman.github.io/cv/rendercv/themes/minimal.yaml:1)

## How The Pieces Work Together

The PDF flow is:

1. Validate [resume.yaml](/workspaces/sepidman.github.io/cv/resume.yaml:1) against [resume_schema.json](/workspaces/sepidman.github.io/cv/resume_schema.json:1).
2. Read [rendercv/variants.yaml](/workspaces/sepidman.github.io/cv/rendercv/variants.yaml:1) to determine which variant to build.
3. Load that variant’s profile from `profiles/`.
4. Apply the profile override to the canonical resume content.
5. Convert the result to RenderCV-shaped YAML.
6. Merge in `rendercv/base.yaml` plus the selected theme overlay from `rendercv/themes/`.
7. Write the merged YAML to `generated/`.
8. Ask RenderCV to produce the final PDF in `build/assets/`.
9. Publish the canonical JSON Resume file in `build/assets/`.

The main implementation point is the Python package under [.dev/resume](/workspaces/sepidman.github.io/.dev/resume/pyproject.toml:1).

- [resume_pipeline.cli](/workspaces/sepidman.github.io/.dev/resume/src/resume_pipeline/cli.py:1)
  Provides the argparse-based CLI used by the task runner.
- [resume_pipeline.pipeline](/workspaces/sepidman.github.io/.dev/resume/src/resume_pipeline/pipeline.py:1)
  Validates source data, applies profile overrides, generates RenderCV YAML, and runs the PDF build.

## Working On Different Parts

### Update resume content

Edit [resume.yaml](/workspaces/sepidman.github.io/cv/resume.yaml:1).

Use this when:

- job history changes
- education changes
- skills or certificates change
- contact details change
- project entries change

Then run:

```bash
npx task validate:resume
npx task build:resume
```

### Make a more targeted PDF version

Edit or add a file in `profiles/`.

Use this when:

- a shorter application version is needed
- one version should hide a section
- a variant should show fewer projects or certificates
- a variant needs a different summary

Then connect it in [rendercv/variants.yaml](/workspaces/sepidman.github.io/cv/rendercv/variants.yaml:1).

### Change how all PDFs look on paper

Edit [rendercv/base.yaml](/workspaces/sepidman.github.io/cv/rendercv/base.yaml:1).

Use this when:

- margins need adjustment
- typography feels too dense or too loose
- section spacing needs refinement
- header layout should change everywhere

### Change the look of one PDF family

Edit or add a theme file in `rendercv/themes/`.

Use this when:

- one variant should be more minimal
- one variant should feel more branded
- colors or theme choice should differ between outputs

Then point the variant at that theme in [rendercv/variants.yaml](/workspaces/sepidman.github.io/cv/rendercv/variants.yaml:1).

### Debug conversion or RenderCV issues

Inspect the YAML in `generated/`.

Use this when:

- the PDF contains unexpected sections
- a profile override does not seem to apply
- RenderCV reports a validation error
- you want to see the exact input RenderCV received

## Common Commands

Validate the pipeline:

```bash
npx task validate:resume
```

Build all public resume assets:

```bash
npx task build:resume
```

Build a specific variant:

```bash
npx task build:resume:variant VARIANT=resume
```

Build all configured PDF variants:

```bash
npx task build:resume:all
```

Build the site plus all public resume assets:

```bash
npx task build
```

## Adding A New PDF Variant

1. Add a profile in `profiles/` if the new variant needs content changes.
2. Add a theme file in `rendercv/themes/` if it needs distinct styling.
3. Register the variant in [rendercv/variants.yaml](/workspaces/sepidman.github.io/cv/rendercv/variants.yaml:1).
4. Run:

```bash
npx task validate:resume
npx task build:resume:variant VARIANT=<name>
```

## Notes

- The website resume and the PDF resume are intentionally decoupled now.
- Editing the website template or CSS does not automatically improve the PDF anymore.
