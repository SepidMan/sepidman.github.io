# Sepidman Personal Website

This repository is an Eleventy-powered personal website ready for GitHub Pages deployment.

## Quick start

1. Install dependencies:

```bash
npm install
```

2. Start the local development server:

```bash
npm run dev
```

3. Build the site for deployment:

```bash
npm run build
```

## GitHub Pages

This site builds into the `docs/` folder, so you can deploy it by using GitHub Pages with the `main` branch and the `docs/` folder as the publishing source.

A GitHub Actions workflow is included at `.github/workflows/deploy.yml` to build and deploy the site automatically on every push to `main`.

## Project structure

- `src/` — source files and templates
- `docs/` — generated site output
- `.eleventy.js` — Eleventy configuration
- `package.json` — build and development scripts
