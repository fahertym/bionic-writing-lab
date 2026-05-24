# Launch Canon Content Generation Report

Generated repo-ready content files for the first Bionic Writing Lab launch sequence.

## Generated Works

1. `you-are-not-tired-because-you-are-weak` — essay, review
2. `everyone-at-that-table` — essay, review
3. `we-built-the-machine-we-can-build-the-door` — pamphlet, review

## Generated Paths

- `paths/start-here.json` is included as a draft reading path that orders the three launch works.

## Formatting Rules Applied

- Markdown source files contain reader-facing content only.
- Publication metadata lives in `publications/*.json`.
- Intake/provenance metadata lives in `intake/launch-canon/*.md`.
- No standalone HTML page shells, embedded CSS, scripts, progress bars, or front matter were placed in rendered content files.
- All publication statuses are `review` so the public build remains conservative until a deliberate launch pass.

## Recommended Validation After Copying Into Repo

```bash
make validate
make build
make smoke
make build-drafts
INCLUDE_DRAFTS=1 make smoke
git diff --check
```

## Follow-up Before Publishing

- Inspect generated HTML pages in draft build.
- Decide whether to add custom PDF artifact support for the designed `You Are Not Tired` PDF.
- Add source notes for `Everyone at That Table` before making it public.
- Add/update concept manifests in a separate metadata PR.
- Flip publication statuses and `paths/start-here.json` to `published` only after review.
