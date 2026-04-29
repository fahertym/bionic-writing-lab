# Content Intake Pilot

This pilot is the first controlled intake of real writing.

It is intentionally small. The goal is to prove the review rhythm, not to move the archive all at once.

## Batch Limits

- 5 to 10 fragments maximum
- 1 essay or post candidate maximum
- 1 pamphlet candidate maximum, only if the shape is obvious
- no books
- no full archive import
- no major project folders

Every imported piece starts as `imported` or `draft`. Nothing becomes public during intake unless it is separately reviewed.

## Intake Source Categories

Use a small set of hand-picked sources:

- recent posts or replies with strong argument seeds
- short notes that clearly map to existing draft concepts
- AI-assisted notes that preserve a useful structure or compression
- one short essay/post candidate with a coherent beginning, middle, and end
- one pamphlet candidate only if it already has pamphlet-scale shape

Avoid large folders, book drafts, chat dumps, and mixed archives in this pilot.

## Selection Criteria

Choose pieces that are:

- easy to classify by kind
- small enough to review manually
- connected to at least one existing concept
- safe to keep non-public while metadata is refined
- useful for testing relationships between fragments and longer pieces

Skip anything that requires major editorial cleanup before its metadata can be trusted.

## Naming Conventions

Use clear, durable slugs:

```text
content/fragments/<slug>.md
publications/<slug>.json
```

Prefer literal argument names over vague dates or source-platform names. Keep source-platform context in notes or descriptions only when it matters.

## Status Rules

- Use `imported` for material brought in from outside the repo.
- Use `draft` for material actively shaped inside the repo.
- Use `review` only after the text, metadata, concepts, and relationships have been checked.
- Use `published` only after a separate public-readiness pass.
- Use `private` for anything that should remain local-only even in normal archive planning.

Public builds must remain safe throughout the pilot.

## Concept Mapping Rules

Map each imported piece to at least one concept when the connection is obvious.

Likely first concepts:

- `survival-pressure`
- `coercion`
- `property-as-command`
- `religion-as-infrastructure`
- `democratic-infrastructure`
- `ai-as-amplifier`

Do not attach concepts just because a word appears. Attach them when the concept is part of the argument.

## Relationship Rules

Add relationships only when they are obvious.

Useful first patterns:

- an essay `expands` a fragment
- a pamphlet is `adapted_from` several fragments or posts
- a fragment `responds_to` a prior publication
- two pieces are `related` only when the link helps a reader understand the archive

Do not create dense relationship graphs during intake. Provenance should clarify, not decorate.

## Reading Path Rules

Keep reading paths draft during the pilot.

Add items only when the route has enough reviewed pieces to be useful. A draft path can hold planning intent, but public paths should not expose incomplete routes.

## Public And Private Safety

Before and after every import batch:

- run a public build
- confirm imported/draft/private items are absent from public search and JSON
- run a draft build
- confirm draft-mode pages show status badges
- check that concept, path, and relationship backlinks do not leak non-public titles in public mode

## Verification Commands

Run:

```bash
make validate
make build
make smoke
make build-drafts
INCLUDE_DRAFTS=1 make smoke
git diff --check
```

For public safety, also inspect:

```bash
dist/site/search-index.json
dist/site/publications.json
dist/site/feed.json
```

## Manual Review Checklist

For each imported piece:

- kind is correct
- title and slug are durable
- status is `imported` or `draft`
- source path is correct
- public route is predictable
- description is accurate
- tags are minimal
- concepts are intentional
- relationships are meaningful
- reading path membership is not premature
- public build does not expose non-public work

Stop after the first small batch and review the shape before importing more.
