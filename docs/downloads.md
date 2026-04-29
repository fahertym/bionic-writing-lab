# Downloads And Print Exports

Downloads are generated surfaces. Markdown source files and publication manifests remain the source of truth.

## Always Generated

Every downloadable publication gets a Markdown download:

```text
dist/site/downloads/<kind-section>/<slug>.md
```

The build also copies original source Markdown files into:

```text
dist/site/downloads/source/<slug>/
```

Markdown does not require Pandoc and remains the fallback format for every downloadable publication.

## Optional Pandoc Formats

Publication manifests request download formats with `output_formats`:

```json
{
  "output_formats": ["site", "markdown", "pdf", "epub", "docx"],
  "downloadable": true
}
```

Supported optional Pandoc formats are:

- `pdf`
- `epub`
- `docx`

If `pandoc` is unavailable, the downloads step prints a warning and continues. Markdown downloads are still generated. If Pandoc is available but a PDF engine is missing or fails, that PDF is skipped with a warning while other formats can still be produced.

## Kind-Aware Defaults

Pandoc defaults live in `site/pandoc/defaults/`.

- `book.yaml`: standalone export, table of contents, book document class, chapter-level division.
- `collection.yaml`: standalone export, table of contents, book-like section structure.
- `essay.yaml`: standalone article-style export without table of contents.
- `fragment.yaml`: standalone article-style export for downloadable fragments.
- `pamphlet.yaml`: compact article-style export with tighter page margins.
- `poem.yaml`: preserves line breaks more aggressively for verse.
- `series.yaml`: standalone export with table of contents for grouped work.

The exporter passes publication metadata to Pandoc, including title, subtitle, author, description, date or created date, updated date, tags as keywords, and site language when configured.

## Page Breaks

The public Markdown download stays close to the assembled source Markdown.

For Pandoc-only input, multi-file books and collections get conservative section boundaries between source files. These page break hints help PDF/DOCX output without changing the HTML site rendering or the canonical Markdown source files.

## Templates

`site/pandoc/templates/` is reserved for future explicit Pandoc templates.

The current export layer intentionally relies on Pandoc defaults instead of custom LaTeX templates or required reference DOCX files. This keeps export behavior stable and optional across local machines and GitHub Pages.
