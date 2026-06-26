# Sepideh Mansouri Portfolio

This repository contains a data-driven personal portfolio website built with Eleventy for a UI/UX designer. The public site, HTML resume, and downloadable PDF resume are generated from shared structured content.

## Stack

- Eleventy
- Nunjucks
- JSON Resume data
- RenderCV for paper-native PDF export
- Playwright for the legacy HTML-print PDF export

## Project structure

- `src/` — site templates, pages, styles, and project content
- `src/projects/` — data-driven case-study entries
- `src/_data/` — global site data and normalized resume data
- `cv/resume.json` — canonical resume source
- `cv/profiles/` — variant-specific content overrides for PDF builds
- `cv/rendercv/` — RenderCV base config, theme presets, and variant definitions
- `build/` — generated site output for deployment
- `tools/build_resume_pdf.mjs` — RenderCV PDF build orchestration
- `tools/generate_resume_pdf.mjs` — legacy Playwright PDF export
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

Build the site and the default resume PDF:

```bash
npx task build
```

Build all configured resume PDF variants:

```bash
npx task build:resume:all
```

## Content workflow

- Update resume content in `cv/resume.json`
- Add PDF-specific content overrides in `cv/profiles/`
- Tune PDF design defaults in `cv/rendercv/base.yaml`
- Add or adjust variant definitions in `cv/rendercv/variants.json`
- Update site-wide biography/contact content in `src/_data/site.json`
- Add or edit case studies in `src/projects/`

The web resume page and the downloadable PDFs are both generated from the same canonical resume source file, but they now have separate presentation pipelines:

- Web resume: `cv/resume.json` -> `src/_data/resume.js` -> Eleventy/Nunjucks
- PDF resume: `cv/resume.json` -> profile override -> RenderCV YAML -> RenderCV PDF

The legacy Playwright print pipeline is still available via `npx task legacy:resume-print`, but it is now a fallback rather than the preferred PDF path.
