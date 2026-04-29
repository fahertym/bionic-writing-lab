# Public Site

Bionic Writing Lab is the public identity layer for Matt Faherty's writing.

The homepage introduces the lab as a place for systems essays, political machinery, speculative fiction, working notes, pamphlets, poems, series, collections, concepts, reading paths, and long-form work. The About page provides the author frame and links to related InterCooperative Network infrastructure work.

The site stays static:

- `site/site.json` owns site title, tagline, description, author, base URL, and navigation.
- `site/templates/index.html` owns homepage structure.
- `site/templates/about.html` owns the About page.
- publication pages still come from Markdown content and JSON manifests.

Public builds still include only `published` publications. Draft, imported, review, private, archived, and superseded material appears only in draft preview builds.
