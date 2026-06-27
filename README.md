# Sepideh Mansouri Portfolio

This repository contains a data-driven personal portfolio website built with Eleventy for a UI/UX designer. The public site, HTML resume, downloadable PDFs, and exported JSON Resume are generated from shared structured content.

## Stack

- Eleventy
- Nunjucks
- JSON Resume data
- Python resume pipeline package in `.dev/resume`
- RenderCV for paper-native PDF export

## Project structure

- `src/` — site templates, pages, styles, and project content
- `src/projects/` — data-driven case-study entries
- `src/_data/` — global site data and normalized resume data
- `cv/resume.yaml` — canonical resume source
- `cv/profiles/` — variant-specific content overrides for PDF builds
- `cv/rendercv/` — RenderCV base config, theme presets, and variant definitions
- `.dev/resume/` — Python package for resume validation, conversion, and PDF builds
- `build/` — generated site output for deployment
- `Taskfile.yml` — top-level task runner commands
- `pixi.toml` — Python environment management for RenderCV

## Local development

Install dependencies:

```bash
npm install
~/.pixi/bin/pixi install
```

Start the local dev server:

```bash
npx task dev
```

Build the site and all public resume assets:

```bash
npx task build
```

Build all configured resume PDF variants:

```bash
npx task build:resume:all
```

## Content workflow

- Update resume content in `cv/resume.yaml`
- Add PDF-specific content overrides in `cv/profiles/`
- Tune PDF design defaults in `cv/rendercv/base.yaml`
- Add or adjust variant definitions in `cv/rendercv/variants.yaml`
- Update site-wide biography/contact content in `src/_data/site.js`
- Add or edit case studies in `src/projects/`

The web resume page and the downloadable PDFs are both generated from the same canonical resume source file, but they now have separate presentation pipelines:

- Web resume: `cv/resume.yaml` -> `src/_data/resume.js` -> Eleventy/Nunjucks
- PDF resume: `cv/resume.yaml` -> profile override -> RenderCV YAML -> RenderCV PDF
- JSON Resume export: `cv/resume.yaml` -> published JSON asset in `build/assets/`

RenderCV intermediate files stay under `cv/generated/`, and the final public PDFs plus the JSON Resume asset are copied into `build/assets/`.
