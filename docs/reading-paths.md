# Reading Paths

Reading paths are curated routes through existing publications. They are ordered by hand and stored as JSON manifests in `paths/`.

They are separate from other organizing tools:

- `kind` is the form of a publication, such as essay, book, poem, pamphlet, post, series, or collection.
- `tag` is a loose topic label.
- `series` and `collection` are publication/grouping structures.
- `reading path` is a suggested route through works, regardless of kind.

## Manifest Shape

```json
{
  "id": "start-here",
  "title": "Start Here",
  "slug": "start-here",
  "description": "A short route through selected publications.",
  "status": "published",
  "tags": ["orientation"],
  "items": ["example-essay", "example-pamphlet", "example-book"]
}
```

`items` is an ordered list of publication IDs.

## Visibility

Reading paths use the same lifecycle statuses as publications.

Normal public builds include only `published` reading paths:

```bash
make build
```

Draft preview builds include all reading paths:

```bash
make build-drafts
INCLUDE_DRAFTS=1 make site
```

Publication pages show backlinks to visible reading paths that include them.

## Search

Search currently remains focused on publications. Reading path pages are generated as static pages and linked from publication backlinks, but they are not search result records yet.
