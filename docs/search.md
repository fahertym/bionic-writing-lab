# Static Search

Search is fully static and client-side.

The site build writes `dist/site/search-index.json`, and `/search/` loads that JSON in the browser. There is no backend search service, database, crawler, or build-time JavaScript bundle.

## Indexed Fields

Search index entries are generated only for publications visible in the current build.

Each publication entry includes title, subtitle, description, author, kind, status, tags, route, URL, date, year, excerpt, section titles, visible concept IDs/titles, visible reading path IDs/titles, visible series and collection metadata, and visible relationship IDs.

Public builds include only public metadata. If a public publication references a draft/private concept, path, or relationship target, that hidden target is omitted from the public search index.

## Facets

The search page currently exposes these filters:

- kind
- tag
- year
- concept
- reading path

Text search still searches titles, descriptions, tags, concepts, reading paths, relationship IDs, body excerpts, dates, routes, and author metadata.

Filters combine with simple predictable rules:

- Different filter groups use `AND` behavior.
- Multiple choices inside one filter group use `OR` behavior.

For example, selecting `essay` under kind and `publishing` under tag shows publications that are essays and have the publishing tag. Selecting two tags shows publications that match either selected tag, while still respecting any selected kind, year, concept, or reading path filters.

## Draft Preview

Normal public builds keep search public:

```bash
make build
```

Draft preview builds include all publication statuses in `search-index.json`:

```bash
INCLUDE_DRAFTS=1 make site
make build-drafts
```

When draft preview search includes non-published publications, the search result cards show status badges.
