# Publication Relationships

Publication relationships describe provenance and evolution between pieces.

They are different from the other organization layers:

- `kind` is publication form.
- `tag` is loose topic metadata.
- `series` and `collection` are publication/grouping structures.
- `reading path` is a curated route through works.
- `concept` is a defined recurring idea.
- `relationship` is a provenance or evolution link between publications.

## Manifest Shape

Relationships are optional. Add a `relationships` object to a publication manifest when one piece explicitly depends on, develops, answers, revises, or derives from another.

```json
{
  "relationships": {
    "expands": ["example-essay"],
    "responds_to": [],
    "supersedes": [],
    "related": ["example-pamphlet"],
    "excerpt_of": [],
    "adapted_from": []
  }
}
```

Empty relationship keys may be omitted. All relationship targets are internal publication IDs.

Supported keys:

- `expands`
- `responds_to`
- `supersedes`
- `related`
- `excerpt_of`
- `adapted_from`

## Backlinks

Backlinks are generated automatically. If publication B declares:

```json
{
  "relationships": {
    "expands": ["publication-a"]
  }
}
```

then publication A shows publication B under `Expanded By`.

## Visibility

Relationship visibility follows publication visibility.

Normal public builds show relationships only when both publications are visible in the public build:

```bash
make build
```

Draft preview builds can show relationships among all preview-visible publications:

```bash
make build-drafts
INCLUDE_DRAFTS=1 make site
```

This prevents public pages and JSON indexes from leaking draft, imported, review, private, archived, or superseded publication titles.
