# Public Site

Bionic Writing Lab is the public home for Matt Faherty's writing.

The homepage should center the work itself: a featured piece, a short authorial frame, and quiet routes into published writing. It should feel like a reading room, not a product page or a tour of the publishing system.

The About page explains the site in human terms: Matt Faherty, the work, what bionic means, and adjacent infrastructure work. ICN can remain linked and named, but it is secondary to the writing-home identity.

The site stays static:

- `site/site.json` owns site title, tagline, description, author, base URL, and navigation.
- `site/templates/index.html` owns homepage structure.
- `site/templates/about.html` owns the About page.
- publication pages still come from Markdown content and JSON manifests.

Public builds still include only `published` publications. Draft, imported, review, private, archived, and superseded material appears only in draft preview builds.

The public surface should not overexplain implementation details. Search may be static and client-side; downloads may be generated; manifests may preserve concepts, paths, and relationships. Those facts should stay true underneath the surface, while public copy stays reader-facing and restrained.
