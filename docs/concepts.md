# Concepts

Concepts are defined recurring ideas that can appear across publications.

They are not tags. A tag is loose metadata. A concept has a definition, a longer description, optional related concepts, and an ordered list of publications where the idea appears.

## Organization Layers

- `kind` is publication form, such as essay, book, poem, pamphlet, post, series, or collection.
- `tag` is a loose topic label.
- `series` and `collection` are publication/grouping structures.
- `reading path` is a curated route through works.
- `concept` is a defined recurring idea that can appear across works.

## Manifest Shape

Concept manifests live in `concepts/`.

```json
{
  "id": "source-and-surface",
  "title": "Source And Surface",
  "slug": "source-and-surface",
  "short_definition": "The distinction between canonical writing sources and generated publication outputs.",
  "description": "Source and surface names the repo's basic discipline.",
  "status": "published",
  "tags": ["example", "publishing"],
  "related_concepts": [],
  "publications": ["example-essay"]
}
```

`related_concepts` is an ordered list of concept IDs. `publications` is an ordered list of publication IDs.

`publications` may be empty while drafting a concept stub, but published concepts should normally point at at least one publication.

## Visibility

Concepts use the same lifecycle statuses as publications and reading paths.

Normal public builds include only `published` concepts:

```bash
make build
```

Draft preview builds include all concept statuses:

```bash
make build-drafts
INCLUDE_DRAFTS=1 make site
```

Publication pages show backlinks to visible concepts that reference them.

## Search

Search currently remains publication-focused. Concept pages are generated as static pages and linked from navigation and publication backlinks. Concept search can be added later when the search UI supports mixed result types cleanly.
