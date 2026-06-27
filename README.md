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
- `src/_data/` — Eleventy data loaders derived from the canonical YAML source
- `data/main.yaml` — canonical profile, resume, and website source data
- `data/profiles/` — variant-specific content overrides for PDF builds
- `data/rendercv/` — RenderCV base config, theme presets, and variant definitions
- `.dev/resume/` — Python package for resume validation, conversion, and PDF builds
- `build/website/` — generated website output for deployment
- `build/cv/` — generated RenderCV inputs and working files
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

- Update shared resume and website content in `data/main.yaml`
- Add PDF-specific content overrides in `data/profiles/`
- Tune PDF design defaults in `data/rendercv/base.yaml`
- Add or adjust RenderCV export variants in `data/main.yaml` under `exports.rendercv.variants`
- Add or edit case studies in `src/projects/`

The web resume page and the downloadable PDFs are both generated from the same canonical resume source file, but they now have separate presentation pipelines:

- Web resume and site data: `data/main.yaml` -> `src/_data/*.js` -> Eleventy/Nunjucks
- PDF resume: `data/main.yaml` -> profile override -> RenderCV YAML -> RenderCV PDF
- JSON Resume export: `data/main.yaml` -> published JSON asset in `build/website/assets/`

RenderCV intermediate files now live under `build/cv/`, and the final public PDFs plus the JSON Resume asset are published into `build/website/assets/`.
