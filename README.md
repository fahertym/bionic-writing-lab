# Bionic Writing Lab

Bionic Writing Lab is a Markdown-first static publishing system for long-form and short-form writing. The repository is designed to hold publication manifests, source Markdown, static site templates, and simple build scripts that turn writing into a website and downloadable artifacts.

Markdown is the source of truth. The website, downloadable files, and release artifacts are generated outputs.

## What This Repository Is For

This repo is the publishing layer, not another single-manuscript project. It is meant to support:

- books
- series
- essays
- poems
- posts
- pamphlets
- collections
- web-native writing

The goal is to make each publication kind a first-class citizen without forcing every project into a book and chapter model.

## How Publications Work

Each publication lives in a JSON manifest inside `publications/`. A manifest defines the publication identity, kind, route, source content, descriptive metadata, and requested output formats.

The build scripts use manifests to:

- validate publication metadata
- resolve Markdown sources
- build HTML pages into `dist/site/`
- create listing pages by publication kind
- export Markdown and optional pandoc-based downloads into `dist/site/downloads/`

The publication schema lives at `schema/publication.schema.json`.

## Repository Layout

- `content/` holds Markdown source files and folders
- `publications/` holds manifest JSON files
- `schema/` holds the JSON schema
- `site/` holds Jinja templates and CSS assets
- `scripts/` holds the Python build and validation tools
- `dist/` is generated output and is intentionally ignored in git

## Add A New Essay

1. Create a Markdown file in `content/essays/`, for example `content/essays/my-new-essay.md`.
2. Add a manifest in `publications/`, for example `publications/my-new-essay.json`.
3. Set `kind` to `essay`, give it a unique `id` and `slug`, and point `source` at the Markdown file.
4. Run `make validate` and `make site`.

Minimal example:

```json
{
  "id": "my-new-essay",
  "title": "My New Essay",
  "author": "Matt Faherty",
  "kind": "essay",
  "slug": "my-new-essay",
  "description": "A short description for the site and feeds.",
  "status": "draft",
  "tags": ["essay"],
  "source": "content/essays/my-new-essay.md",
  "web_route": "/essays/my-new-essay/",
  "output_formats": ["site", "markdown"],
  "downloadable": true
}
```

## Add A New Book

1. Create a folder such as `content/books/my-book/`.
2. Put your Markdown files inside it in reading order, for example `01-opening.md`, `02-middle.md`, `03-ending.md`.
3. Add a manifest in `publications/`.
4. Set `kind` to `book`.
5. Use `source` for the directory and `sources` for explicit ordering when needed.

Example:

```json
{
  "id": "my-book",
  "title": "My Book",
  "author": "Matt Faherty",
  "kind": "book",
  "slug": "my-book",
  "description": "A longer work built from multiple Markdown files.",
  "status": "draft",
  "tags": ["book"],
  "source": "content/books/my-book",
  "sources": ["01-opening.md", "02-middle.md", "03-ending.md"],
  "web_route": "/books/my-book/",
  "output_formats": ["site", "markdown", "pdf", "epub", "docx"],
  "downloadable": true
}
```

## Add A Collection Or Series

Collections and series can have their own landing-page Markdown plus their own manifests.

- A `collection` groups related pieces under one publication route.
- A `series` provides a web-facing home for a sequence of related works.

For the first pass, these are manifest-driven pages with Markdown content and metadata. They do not yet auto-assemble other publication pages into navigable member pages, but the schema is ready for that direction.

## Build Locally

Create a local virtual environment and install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run the full local build:

```bash
make build
```

Useful individual commands:

```bash
make validate
make site
make downloads
make clean
```

## Serve Locally

```bash
make serve
```

This serves `dist/site/` with Python's built-in HTTP server. Open `http://localhost:8000/`.

## GitHub Pages Deployment

The repository includes `.github/workflows/publish-site.yml`, which:

- runs on pushes to `main`
- installs Python dependencies
- validates manifests
- builds the site and downloads
- uploads `dist/site/` as a Pages artifact
- deploys the artifact to GitHub Pages using the current Pages Actions flow

The quality workflow in `.github/workflows/quality.yml` validates the repo and confirms the static site build succeeds.

## How Downloads Work

Every downloadable publication gets a Markdown download in `dist/site/downloads/`.

If `pandoc` is available and the manifest requests `pdf`, `epub`, or `docx`, those formats are generated too. If `pandoc` is missing, the downloads step prints a clear warning and continues instead of failing the whole build.

## Custom Domains Later

This repo is compatible with GitHub Pages and can grow into a public Bionic Writing Lab site. A custom domain can be added later by:

1. adding a `CNAME` file to the built site or workflow
2. pointing DNS at GitHub Pages
3. updating the canonical site URL in manifests or site config when the final domain is known

That keeps the current scaffold simple while leaving room for a future `bionicwritinglab.com` setup.
