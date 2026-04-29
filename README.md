# Bionic Writing Lab

Bionic Writing Lab is a Markdown-first static publishing system for long-form and short-form writing. The repository is designed to hold publication manifests, source Markdown, static site templates, and simple build scripts that turn writing into a website and downloadable artifacts.

Markdown is the source of truth. The website, downloadable files, and release artifacts are generated outputs.

## What This Repository Is For

This repo is the publishing layer, not another single-manuscript project. It is meant to support:

- books
- series
- essays
- fragments
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
- validate site-level config in `site/site.json`
- resolve Markdown sources
- build HTML pages into `dist/site/`
- create listing pages by publication kind
- build a static `/search/` page backed by `dist/site/search-index.json`
- connect series and collections to their member publications
- preserve section-level structure for multi-file publications
- add standalone section pages and previous/next reading links for multi-file publications
- export Markdown and optional pandoc-based downloads into `dist/site/downloads/`
- generate machine-readable indexes in `dist/site/publications.json` and `dist/site/feed.json`
- add canonical and Open Graph metadata from site and publication config

The publication schema lives at `schema/publication.schema.json`.

## Repository Layout

- `content/` holds Markdown source files and folders
- `publications/` holds manifest JSON files
- `schema/` holds the JSON schema
- `site/` holds Jinja templates and CSS assets
- `site/site.json` holds site metadata and navigation config
- `scripts/` holds the Python build and validation tools
- `dist/` is generated output and is intentionally ignored in git
- `docs/` holds planning notes for domains and future imports

## Create A New Publication

Use the authoring scaffold when starting a new piece. It creates the Markdown source and matching manifest together, fills in sensible defaults from the site config, refuses to overwrite existing files, and validates the repo after creation.

```bash
make new kind=essay title="Capitalism Behaves Like Cancer"
make new kind=pamphlet title="The Freedom They Mean" tags="politics,freedom"
make new kind=book title="Empire Exposed"
```

Supported kinds are `book`, `series`, `essay`, `fragment`, `poem`, `post`, `pamphlet`, and `collection`.

Single-file kinds create one Markdown file:

```text
content/essays/capitalism-behaves-like-cancer.md
publications/capitalism-behaves-like-cancer.json
```

Folder-based kinds create a content folder with a starter file:

```text
content/books/empire-exposed/00-introduction.md
publications/empire-exposed.json
```

Optional arguments can override defaults:

```bash
make new kind=essay title="Property Is Command" \
  subtitle="Notes on ownership and coercion" \
  description="A draft essay about property, command, and survival pressure." \
  status=review \
  tags="property,coercion"
```

## Publication Status And Visibility

Every manifest must use one of these statuses: `draft`, `imported`, `review`, `published`, `archived`, `superseded`, or `private`.

Normal public builds are intentionally conservative:

```bash
make site
make downloads
make build
```

These include only `published` publications in generated publication pages, listing pages, `publications.json`, `feed.json`, `search-index.json`, and downloads. GitHub Pages uses this safe public build path.

Use draft preview mode when you want to inspect everything locally:

```bash
INCLUDE_DRAFTS=1 make site
make site-drafts
make build-drafts
```

Preview mode includes all statuses, including `private`, and marks non-published pages with status badges. See [docs/publication-lifecycle.md](/home/matt/docs/bionic-writing-lab/docs/publication-lifecycle.md) for the recommended `draft/imported -> review -> published -> archived/superseded/private` workflow.

## Public Site Identity

The public site is framed as Matt Faherty's publishing lab for systems essays, political machinery, speculative fiction, notes, pamphlets, and long-form work. Site-level identity lives in `site/site.json`, with homepage and About page templates under `site/templates/`.

The lab should not adopt any external publishing model wholesale. It is not a Substack clone, WordPress blog, Medium publication, GitBook/doc site, portfolio, startup page, or generic feed. See [docs/identity-and-design.md](/home/matt/docs/bionic-writing-lab/docs/identity-and-design.md) for the durable identity and design doctrine, and [docs/public-site.md](/home/matt/docs/bionic-writing-lab/docs/public-site.md) for the small public-site surface area.

## Reading Paths

Reading paths are curated routes through existing publications. They live in `paths/*.json`, generate `/paths/` and `/paths/<slug>/`, and add backlinks on publication pages when a publication appears in a visible path.

They are distinct from other organization layers: `kind` is publication form, `tag` is a loose topic, `series` and `collection` are publication structures, and a reading path is an ordered route through works. See [docs/reading-paths.md](/home/matt/docs/bionic-writing-lab/docs/reading-paths.md).

## Concept Index

Concepts are defined recurring ideas that can appear across publications. They live in `concepts/*.json`, generate `/concepts/` and `/concepts/<slug>/`, and add backlinks on publication pages when a visible concept references that publication.

They are not tags. `kind` is form, `tag` is loose topic metadata, `series` and `collection` are publication structures, `reading path` is a curated route, and `concept` is a defined idea with a short definition, description, related concepts, and linked publications. See [docs/concepts.md](/home/matt/docs/bionic-writing-lab/docs/concepts.md).

## Fragments

Fragments are first-class seed forms: argument shards, reply drafts, debate skeletons, concept stubs, AI-assisted notes, rough observations, and compressed ideas that may later mature into posts, essays, pamphlets, chapters, or books.

They obey the normal lifecycle and are not automatically public. Fragments can appear in reading paths, concepts, search, publication relationships, and generated indexes when visible in the current build. See [docs/fragments.md](/home/matt/docs/bionic-writing-lab/docs/fragments.md).

## Publication Relationships

Publication relationships describe provenance between pieces: expansion, response, supersession, related work, excerpts, and adaptations. They are optional manifest metadata under `relationships`, and backlinks are generated automatically on referenced publication pages.

Relationships are distinct from other organization layers: `kind` is form, `tag` is loose topic metadata, `series` and `collection` are publication structures, `reading path` is a curated route, `concept` is a defined recurring idea, and `relationship` is a provenance or evolution link between publications. See [docs/relationships.md](/home/matt/docs/bionic-writing-lab/docs/relationships.md).

## Import Existing Markdown

Use the import pipeline as a safe loading dock for existing Markdown files and folders. Imports copy Markdown into `content/`, create a manifest in `publications/`, mark the publication as `imported` by default, and write a report under `reports/imports/`.

Preview first:

```bash
make import source=/path/to/essay.md kind=essay dry_run=1
```

Import a single essay:

```bash
make import source=/path/to/essay.md kind=essay title="Capitalism Behaves Like Cancer"
```

Import a folder-based book:

```bash
make import source=/path/to/empire-exposed kind=book title="Empire Exposed"
```

`imported` means the piece came from existing source and has not been reviewed for publication inside this repo yet. `draft` means new writing actively authored here. Normal public builds exclude imported material; draft preview builds include it. See [docs/importing.md](/home/matt/docs/bionic-writing-lab/docs/importing.md) for details.

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
- Both can declare ordered `members` using publication ids.

Member publications can also point back to a parent with `series` or `collection`, but the simplest pattern is to keep membership order in the parent manifest.

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
make smoke
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

Pandoc exports use small kind-aware defaults in `site/pandoc/defaults/` for books, collections, essays, pamphlets, poems, and series. See [docs/downloads.md](/home/matt/docs/bionic-writing-lab/docs/downloads.md).

## Machine-Readable Indexes

The site build also writes:

- `dist/site/publications.json` for later search/index work
- `dist/site/feed.json` as a JSON feed of recent publications
- `dist/site/search-index.json` for the static client-side search page at `/search/`

The `/search/` page uses plain browser-side JavaScript to load and filter `search-index.json`. If JavaScript is unavailable, the page still points readers directly at the raw index file.

Search facets are generated from the same visible publication metadata. Readers can filter by kind, tag, year, concept, and reading path while text search still covers titles, descriptions, tags, excerpts, routes, dates, concept titles, path titles, and relationship IDs. Different filter groups combine with `AND`; multiple choices inside one group match any selected choice. See [docs/search.md](/home/matt/docs/bionic-writing-lab/docs/search.md).

## Multi-File Reading Navigation

Multi-file publications keep their full publication page as the canonical reading surface.

- The main publication page renders the full work with an on-page table of contents.
- Each section now gets previous/next reading links inside the full page.
- Multi-file publications can also emit simple standalone section pages with predictable routes based on source filenames, such as `/books/example-book/01-opening/`.

This keeps long-form and grouped reading navigable without turning the site into a reader app.

## Canonical Metadata

The site builder uses `site/site.json` `base_url` to generate canonical URLs and basic Open Graph metadata.

- Index, listing, and search pages use site-level metadata.
- Publication pages use publication metadata.
- Standalone section pages point their canonical URL back to the full publication page so the full publication remains the canonical version.

## Smoke Checks

Use `make smoke` after a build to confirm that core outputs exist, including the homepage, JSON indexes, search page, example publication routes, multi-file section routes, and downloads directory.

## Custom Domains Later

This repo is compatible with GitHub Pages and can grow into a public Bionic Writing Lab site. A custom domain can be added later by:

1. adding a `CNAME` file to the built site or workflow
2. pointing DNS at GitHub Pages
3. updating the canonical site URL in manifests or site config when the final domain is known

That keeps the current scaffold simple while leaving room for a future `bionicwritinglab.com` setup.

See [docs/custom-domain.md](/home/matt/docs/bionic-writing-lab/docs/custom-domain.md) for the planned approach and [docs/importing-villain.md](/home/matt/docs/bionic-writing-lab/docs/importing-villain.md) for the future Villain import plan.
