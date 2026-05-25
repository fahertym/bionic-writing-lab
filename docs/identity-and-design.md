# Identity And Design

Bionic Writing Lab is Matt Faherty's writing home: a public surface for essays, fragments, pamphlets, fiction, and longer works about the machinery underneath things.

The writing is the center. The site is the room around it.

The machinery matters because it lets the work keep structure, memory, and continuity, but the public surface should not read like a manual for that machinery. Readers should meet the work first: the argument, the voice, the pressure, the piece in front of them.

## Platform Rejection

Bionic Writing Lab should not adopt any external publishing model wholesale. It should borrow selectively, but obey its own structure. Do not make the lab fit the platform. Make the platform fit the lab.

It is not trying to become a Substack clone, a WordPress blog, a Medium publication, a GitBook/doc site, a portfolio, a startup landing page, an AI influencer brand, a generic archive, or a social feed pretending to be a library.

This is not aesthetic snobbery. It is structural discipline.

- Substack is too feed-shaped.
- Medium is too article-shaped.
- WordPress is too CMS-shaped.
- GitBook is too documentation-shaped.
- A portfolio is too resume-shaped.
- A blog is too chronological.
- A wiki is too flat.
- A newsletter is too disposable.
- A social feed is where thought goes to die.

This repo is argument-shaped, provenance-shaped, concept-shaped, and artifact-shaped. The public site, though, should feel writerly and reader-facing before it feels structural.

## Source And Surface

Source is durable; surfaces are generated.

Markdown content and JSON manifests are the source. Website pages, downloads, feeds, indexes, search, concept pages, reading paths, and relationship views are generated surfaces. Generated output may be rebuilt, redesigned, exported, bundled, or replaced. Source should remain inspectable, portable, and plain enough to survive the failure of any one tool.

The lab should preserve this discipline even as the public design becomes more expressive. Do not commit generated site output unless there is an explicit release reason.

## Form Matters

Form matters.

A poem is not a post. A pamphlet is not a chapter by force. A concept is not a tag.

Publication kinds stay first-class because writing does not all want the same container. Books, series, essays, poems, posts, pamphlets, and collections may share one engine without being flattened into one generic post model.

Fragments are first-class because they are often the seed form of the work: argument scraps, reply drafts, debate skeletons, AI-assisted notes, outlines, excerpts, observations, and rough machinery that may later become posts, essays, pamphlets, chapters, or books.

## Lifecycle

Not everything in the lab is public.

Status exists because the lab has benches, drafts, imported material, experiments, reviewed pieces, published artifacts, archived work, superseded arguments, and private notes. Public builds should remain conservative. Preview builds can include everything for local inspection.

The recommended movement is:

```text
imported/draft -> review -> published -> archived/superseded/private
```

`imported` means material came from outside the repo and has not yet been reviewed in this system. `draft` means active authorship inside the lab.

## Concepts, Paths, Relationships

Tags are loose metadata. Concepts are defined recurring ideas with descriptions, related concepts, and publication links.

Categories sort piles. Reading paths guide readers through ordered routes.

Chronology records when something appeared. Relationships record how arguments evolve: expansion, response, supersession, related work, excerpts, and adaptations.

These layers are the reason the lab is not just a blog. On the public site, they should behave like quiet reader aids, not the main character.

## ICN Relationship

Bionic Writing Lab and the InterCooperative Network are related but not identical.

Bionic Writing Lab is cognitive, publishing, and explanatory infrastructure. ICN is institutional, governance, and economic coordination infrastructure.

The lab can explain the systems, concepts, arguments, and political machinery that make ICN necessary. ICN can become a major reading path, concept cluster, essay sequence, pamphlet set, or book subject over time. But ICN should not take over the identity of the lab.

Do not turn every page into an ICN ad. Do not hard-code ICN as the center of the repo. Keep it as related long-term infrastructure work with room to grow.

## Visual Foundation

The design direction is dark reading room.

The visual language should feel dark-mode first, serious, archival, writerly, and calm. It should suggest a room built around durable work: enough structure to hold long arguments, enough restraint that the prose remains the center.

Avoid generic AI robot imagery, SaaS gradients, influencer-brand gloss, Matrix cosplay, fake futuristic clutter, terminal cosplay, and neon decoration for its own sake.

Suggested palette:

- void black: `#030604`
- deep black: `#070D0A`
- dark panel: `#0D1712`
- soft panel: `#12211A`
- emerald: `#00E676`
- neo green: `#39FF14`
- jade: `#18D88F`
- mint text: `#B9FBC0`
- main text: `#EAF7EF`
- muted text: `#8BA99A`
- line: `#1F3A2D`
- amber: `#F5C542` for annotations, warnings, and provenance markers
- violet: `#8B5CF6` for AI, recursive, or speculative accents
- cyan: `#45E6FF` for active links
- red: `#FF4D6D` only for warning and danger states

Use color as structure, not spectacle. The site should remain readable on phones, fast to load, and calm enough for long reading. Metadata, downloads, tags, concepts, paths, and relationships should help readers continue; they should not compete with the body of a piece.
