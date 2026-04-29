# Importing Markdown

The import pipeline is a loading dock for existing writing. It copies Markdown into this repo, creates a matching publication manifest, marks the publication as `imported` by default, and writes an import report.

It does not modify the original source path.

## Dry Run First

Preview an import before writing anything:

```bash
python scripts/import_markdown.py --source /path/to/essay.md --kind essay --dry-run
make import source=/path/to/essay.md kind=essay dry_run=1
```

Dry runs print the planned manifest, target paths, copied Markdown files, and skipped non-Markdown files. They do not copy files, create manifests, or write reports.

## Single-File Imports

Single-file publication kinds are `essay`, `poem`, `post`, and `pamphlet`.

```bash
make import source=/path/to/capitalism-behaves-like-cancer.md kind=essay
```

This creates:

```text
content/essays/capitalism-behaves-like-cancer.md
publications/capitalism-behaves-like-cancer.json
reports/imports/<timestamp>-capitalism-behaves-like-cancer.json
```

If the source is a folder for a single-file kind, it must contain exactly one Markdown file.

## Folder Imports

Folder-based publication kinds are `book`, `collection`, and `series`.

```bash
make import source=/path/to/empire-exposed kind=book title="Empire Exposed"
make import source=/path/to/debate-fragments kind=collection title="Debate Fragments"
```

This copies Markdown into:

```text
content/books/<slug>/
content/collections/<slug>/
content/series/<slug>/
```

Folder imports preserve Markdown file names and relative paths, and the generated manifest includes explicit `sources` ordering.

## Metadata

Optional arguments:

```bash
make import source=/path/to/file.md kind=essay \
  title="Property Is Command" \
  subtitle="Notes on ownership and coercion" \
  description="Imported notes awaiting review." \
  tags="property,coercion" \
  status=review \
  slug=property-is-command
```

The default status is `imported`.

Use `imported` for writing brought in from another source before it has been reviewed. Use `draft` for new writing actively authored inside this repo.

## Safety Rules

- Existing content files are never overwritten.
- Existing manifests are never overwritten.
- Slug collisions fail clearly.
- Non-Markdown files are skipped and reported.
- Imported publications are excluded from normal public builds because only `published` appears publicly.
- Imported publications appear in local preview builds with `INCLUDE_DRAFTS=1`, `make site-drafts`, or `make build-drafts`.

After a real import, the script runs the existing publication validation logic.
