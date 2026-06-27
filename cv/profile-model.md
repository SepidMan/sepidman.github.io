# Canonical Profile Model

This document defines the proposed internal source-of-truth data model that would
eventually replace the current split between:

- `cv/resume.yaml`
- `src/_data/site.js`
- `cv/rendercv/variants.yaml`

The intent is to keep the model close to JSON Resume while adding:

- website-only content
- RenderCV export metadata
- a few richer content fields that RenderCV supports and JSON Resume does not

## Design Goals

- Use JSON Resume as the structural base for resume data.
- Keep authored facts in one place.
- Avoid duplicating facts across resume and website data.
- Keep generated/exported data derived rather than hand-maintained.
- Validate at three layers:
  - canonical profile schema
  - generated JSON Resume output
  - generated RenderCV output

## What Stays Canonical

The following should be authored in the canonical model:

- personal identity and contact data
- work, education, volunteer, projects, skills, certificates, references
- website-specific copy and navigation
- RenderCV export metadata that is not purely theme implementation

## What Should Be Derived

The following should be generated rather than authored twice:

- website author block
- website social link arrays
- website email link rows
- exported asset URLs
- normalized Eleventy resume data
- JSON Resume export
- RenderCV input YAML

## Proposed Top-Level Shape

```yaml
$schema: ./cv/profile.schema.json

meta:
basics:
work:
volunteer:
education:
awards:
certificates:
publications:
skills:
languages:
interests:
references:
projects:

website:
  baseUrl:
  description:
  navigation:
  home:
  about:
  contact:

exports:
  rendercv:
    locale:
    settings:
    variants:
```

## JSON Resume Extensions To Keep

These additions fit naturally inside the existing JSON Resume-shaped objects:

### `basics`

- `shortName`
  For UI surfaces like the site header or greeting copy.
- `connections[]`
  For arbitrary header/contact links that are not well represented by `profiles[]`.
- `photo`
  Optional RenderCV photo override if it should differ from `basics.image`.

### `publications[]`

- `authors[]`
- `doi`
- `journal`

These come from RenderCV's publication model and are useful content fields even
outside RenderCV.

## Website Fields To Add

The current `site.js` contains two kinds of data:

- duplicated factual data that should be derived from the canonical profile
- genuine website/editorial content that should be stored explicitly

### These should be authored under `website`

- `website.baseUrl`
- `website.description`
- `website.navigation[]`
- `website.home`
  - `eyebrow`
  - `headline`
  - `intro`
  - `highlights[]`
  - `ctaPrimary`
  - `ctaSecondary`
  - `stats[]`
- `website.about`
  - `summary[]`
  - `principles[]`
- `website.contact`
  - `intro`
  - `availability`

### Icon fields

Website navigation and connection icons should support both:

- custom site icon tokens
- Font Awesome icons

Recommended canonical shape:

```yaml
icon:
  kind: custom
  name: work
```

or:

```yaml
icon:
  kind: fontawesome
  name: linkedin
  style: brands
```

For migration convenience, the draft schema also allows a plain string icon value.
That should be interpreted as a legacy custom icon token.

### These should be derived instead of authored twice

- site title from `basics.name`
- tagline from `basics.label`
- author location from `basics.location`
- author email from `basics.email`
- brand image from `basics.image`
- social/header social from `basics.profiles` plus email
- download asset URLs from generated export outputs

## RenderCV Fields To Add

Some RenderCV concepts are pure presentation and can remain separate for now,
such as `rendercv/base.yaml` and theme overlays. Other fields are useful as
canonical export metadata and belong in the internal model.

### Add under `exports.rendercv`

- `locale.language`
- `settings.currentDate`
- `settings.boldKeywords[]`
- `settings.pdfTitle`
- `variants`
  - `label`
  - `profile`
  - `theme`
  - `output`
  - `summary`

This would absorb the current role of `cv/rendercv/variants.yaml`.

## Sample Canonical File Layout

This is an illustrative shape, not a fully migrated file:

```yaml
$schema: ./cv/profile.schema.json

meta:
  canonical: https://sepidehmansouri.com/assets/sepideh-mansouri-jsonresume.json
  version: 1.0.0
  lastModified: 2026-06-27

basics:
  name: Sepideh Mansouri
  shortName: Sepideh
  label: UX/UI Designer
  image: https://sepidehmansouri.com/assets/images/headshot.jpg
  email: sepideh.mansouri85@gmail.com
  url: https://sepidehmansouri.com
  summary: ...
  location:
    city: Berlin
    countryCode: DE
    region: Berlin
  profiles:
    - network: LinkedIn
      username: sepid-mans
      url: https://www.linkedin.com/in/sepid-mans/
  connections: []

work: []
education: []
projects: []
skills: []
certificates: []

website:
  baseUrl: https://sepidman.github.io
  description: Portfolio website for Sepideh Mansouri, a UI/UX designer focused on calm interfaces, thoughtful systems, and human-centered digital experiences.
  navigation:
    - label: Work
      url: /work/
      icon:
        kind: custom
        name: work
    - label: Resume
      url: /resume/
      icon:
        kind: custom
        name: resume
  home:
    eyebrow: UI/UX designer based in Berlin
    headline: I design digital products that feel clear, calm, and genuinely human.
    intro: ...
    highlights:
      - Mobile-first product thinking
      - Clear flows and information architecture
    ctaPrimary:
      label: View selected work
      url: /work/
    ctaSecondary:
      label: Download CV
      asset: cvPdf
    stats:
      - label: Focus
        value: UX strategy
        detail: User flows, clarity, and design systems
  about:
    summary:
      - ...
    principles:
      - Start from real user intent
  contact:
    intro: If you would like to talk about a role, collaboration, or portfolio feedback, I would love to hear from you.
    availability: Currently open to junior UI/UX roles, internships, and collaborative product design opportunities.

exports:
  rendercv:
    locale:
      language: english
    settings:
      currentDate: today
      pdfTitle: NAME - CV
    variants:
      cv:
        label: CV
        profile: cv
        theme: default
        output: build/assets/{resume_slug}-cv.pdf
      resume:
        label: Resume
        profile: resume
        theme: minimal
        output: build/assets/{resume_slug}-resume.pdf
```

## Migration Notes

The expected migration order is:

1. Finalize this schema.
2. Create a new canonical profile YAML file that follows it.
3. Generate JSON Resume output from the canonical file.
4. Generate Eleventy site data from the canonical file.
5. Move variant metadata into `exports.rendercv.variants`.
6. Remove duplicated factual content from `site.js`.
7. Retire `resume.yaml` once the new canonical file is in place.

## Current Status

This schema is a design draft only.

It is not yet wired into:

- VS Code schema mapping
- the Python validation pipeline
- the Eleventy data loaders
- the PDF export tasks
