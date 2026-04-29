# Fragments

Fragments are first-class publication kinds.

A fragment is a small durable seed of writing. It can be an argument shard, reply draft, debate skeleton, concept stub, opening line, closing line, paragraph, AI-assisted note, rough observation, excerpt waiting for structure, or compressed version of a larger idea.

A fragment is not a failed essay. It is raw ore.

## Pipeline

Fragments preserve the early form of work that may later mature:

```text
fragment -> post -> essay -> pamphlet -> chapter/book
```

That movement is not automatic. Relationship metadata records the evolution when it happens. For example, an essay can `expand` a fragment, a pamphlet can be `adapted_from` several fragments, or a fragment can `responds_to` another publication.

## Authoring

Create a new fragment with the normal scaffold:

```bash
make new kind=fragment title="Leave Who Alone"
```

This creates:

```text
content/fragments/leave-who-alone.md
publications/leave-who-alone.json
```

Fragments are single-file publications by default. New fragments default to `draft`, use `output_formats` of `site` and `markdown`, and default to `downloadable: false`.

## Importing

Import an existing Markdown note as a fragment:

```bash
make import source=/path/to/note.md kind=fragment
```

Imported fragments default to `status: imported`, obey dry-run and overwrite protection, and write import reports like other imported publications.

## Visibility

Fragments obey the normal lifecycle.

Normal public builds include only `published` fragments:

```bash
make build
```

Draft preview builds include all fragment statuses:

```bash
make build-drafts
INCLUDE_DRAFTS=1 make site
```

Draft, imported, review, private, archived, and superseded fragments do not leak into public search, listings, reading paths, concepts, relationship sections, feeds, or publication indexes unless the current build mode explicitly includes them.

## Organization

Fragments can appear anywhere a publication ID is valid:

- reading paths
- concepts
- publication relationships
- search
- generated publication indexes

They are general-purpose. They may eventually hold ICN-related governance notes, civic interface ideas, concept stubs, or explanatory arguments, but fragments are not ICN-specific. ICN is one future concept cluster and reading path, not the whole fragment system.
