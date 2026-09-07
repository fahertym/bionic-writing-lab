# Session Report — BWL Library Reconstruction

**Date:** 2026-09-07 · **Repo:** `fahertym/bionic-writing-lab` ·
**Branch:** `research/library-reconstruction`
**Scope:** cartography. No book prose drafted. No manuscript edited. Nothing
written into `villain-in-the-verse`.

---

## Searches run

| Step | Method | Result |
|---|---|---|
| Canonical home | filesystem repo scan | **`/home/matt/docs/bionic-writing-lab`** — publishing system with existing `concepts/` ontology |
| Named-title sweep | archive DuckDB, titles + bodies + posts | trilogy present; **5 of 11 named titles absent** |
| Trilogy structure | full chapter extraction from 3 manuscripts | 30 chapters mapped; Book 3 missing ch 6 |
| Exceptionalism lineage | **8 text probes** of Book 1 body against 2024 posts | **resolved — it IS Book 1** |
| Live Drive | MCP `search_files`, 2 queries | real `createdTime` for all three books + folder listing |
| Absent titles | archive + both repos + live OneDrive + live Drive | zero hits, four independent sources |
| Western civilization | posts table, 22 rows | 2024-06-22 "comorbidities" post found |
| Internalized systems | Drive read | *The Narrative That Writes Us* read in full |
| Constructive side | ICN repo + design principles | invariants in code, CI-enforced |
| BWL ontology | `concepts/*.json` | 11 nodes; 6 overlap this session's spine |

## Findings that changed the picture

1. **The 2024 "American-exceptionalism project" is *American Imperialism
   Unhinged*.** Proved by text match, not resemblance: the 2024-09-11 post is
   the book's Introduction; 2024-08-22 is Chapter 1; 2024-09-12 is Chapter 7.
2. **The Villain pass had the direction backwards.** It treated the Facebook
   posts as the project. Drive shows Books 1 and 2 created 2024-06-27, seven
   weeks earlier. The posts are output, not origin.
3. **Matt already named the trilogy as one organism** — "The Hydra's Second
   Head" and "The Hydra's Third Head" as the epilogues of Books 1 and 2.
4. **He stated the correct analytical frame five days before adopting a
   narrower one.** 2024-06-22: *"it's all of Western civilization that is ill
   with the comorbidities of imperialism and capitalism."* 2024-06-27: Books 1
   and 2 created.
5. **The internalized-script idea is not new.** *The Narrative That Writes Us*
   (2025-02-21) argues it explicitly, eighteen months before the Villain
   closeout formulated it as fresh synthesis.
6. **Book 3 stalled 2024-09-08** and is two books wearing one title.

## Negative results

- ***The Property Trick*, *The Machine Is Not Broken*, *Declaration of Human
  Sovereignty*, *Humanity v. Yahweh*, *The Fire We Owe Each Other*, *They
  Called It Reality*: zero hits.** Searched archive titles, archive document
  bodies, posts, `bionic-writing-lab`, `villain-in-the-verse`, live OneDrive
  (2026 files), and live Google Drive by title. `UNKNOWN`.
- No developed material found on borders/citizenship, prisons, housing/finance,
  or surveillance as book-scale arguments.
- No document connects ICN's consent design to *Villain*'s Terms of Service
  chapter, despite the obvious structural parallel.

## Not read this session

- **Gospel of Liberation** — 84 KB doc plus ~93,500 w of Oct-2024 sessions,
  last modified 2025-12-30. Metadata only. **The largest unexamined body of
  work in the corpus and the highest-value remaining research task.**
- *The Great Unraveling*, *The Terminal Economy*, *The Engineered Collapse*,
  the cosmic-horror cluster — metadata only.
- Book 1 chapter 3 title could not be extracted from the HTML.

## Unresolved

1. Do the five absent titles exist anywhere, or were they intended works?
2. Is *Gospel of Liberation* alive, superseded by *Villain*, or a distinct book?
3. What is *The Terminal Economy*'s intended scope?
4. Does *Empire Exposed* or *American Imperialism Unhinged* win as the title?

## Repository state

Working in `fahertym/bionic-writing-lab` on `research/library-reconstruction`,
branched from `main` at `f0fcbc0`. Note: **`main` was already one commit ahead
of `origin/main` before this session** (`f0fcbc0`, pre-existing local work not
touched here).

`villain-in-the-verse` was not modified. Its manuscript remains 78,534 words.

Derived intermediates go to `.research-work/` (gitignored). Archive access is
read-only via `scripts/library_reconstruction/config.py`, resolving from
`$BWL_ARCHIVE_ROOT` first so the work is portable off Zenith.
