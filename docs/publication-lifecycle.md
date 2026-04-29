# Publication Lifecycle

Bionic Writing Lab separates source from surface. Markdown files and publication manifests are the source; the public website, search index, feed, and downloads are generated surfaces.

Publication `status` controls which source material is allowed into those generated surfaces.

## Statuses

- `draft`: new writing that is not ready for public readers.
- `imported`: material brought in from another folder, export, or archive before it has been reviewed.
- `review`: writing that is being shaped, checked, or prepared for release.
- `published`: public writing. This is the only status included in normal public builds.
- `archived`: older writing kept for reference but removed from prominent public surfaces.
- `superseded`: writing kept for provenance after a newer version or argument replaces it.
- `private`: source material that should not be generated unless an explicit local preview build asks for it.

## Public Builds

Normal build commands are safe for public deployment:

```bash
make site
make downloads
make build
```

These include only `published` publications in generated pages, listing pages, `publications.json`, `feed.json`, `search-index.json`, and downloads. This is the path used by GitHub Pages.

## All-Status Preview Builds

Use draft preview mode when you want to inspect the whole lab locally:

```bash
INCLUDE_DRAFTS=1 make site
make site-drafts
make build-drafts
```

Preview mode includes every valid status, including `draft`, `imported`, `review`, `archived`, `superseded`, and `private`. Non-published pages show a status badge. Archived and superseded pages also show a lifecycle notice near the top.

Do not use preview output for public deployment.

## Recommended Flow

Use `draft` for new writing created inside this repo.

Use `imported` for writing copied in from another project, folder, Google export, chat transcript, or older archive before you have reviewed its metadata and public readiness.

A typical lifecycle is:

```text
draft/imported -> review -> published -> archived/superseded/private
```

Move a piece to `published` only when it is ready to appear in public listings, feeds, search, indexes, downloads, and GitHub Pages output.
