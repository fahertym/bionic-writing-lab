# Library Reconstruction — the corpus that is actually here

**Session:** BWL Library Reconstruction (Path B), 2026-09-07
**Repo:** `fahertym/bionic-writing-lab`, branch `research/library-reconstruction`
**Status:** cartography. No book prose drafted, no manuscripts edited.

Classification labels used throughout: `ESTABLISHED_ARCHIVAL_FINDING`,
`SUPPORTED_INTERPRETATION`, `CURRENT_SYNTHESIS`, `FUTURE_RESEARCH_HYPOTHESIS`,
`MATT_DECISION`, `UNKNOWN`.

---

## 1. What is actually here

`ESTABLISHED_ARCHIVAL_FINDING` — verified in the archive DuckDB and in live
Google Drive, not from memory summaries.

| Work | Size | Created | Last touched | State |
|---|---:|---|---|---|
| **Book 1 — American Imperialism Unhinged** (internal title *Empire Exposed*) | ~76,800 w | 2024-06-27 | 2025-03-16 | complete draft, 10 chapters + intro, conclusion, epilogue |
| **Book 2 — American Capitalism Unchecked** | ~47,500 w | 2024-06-27 | 2025-03-18 | complete draft, 10 chapters + intro, conclusion, epilogue |
| **Book 3 — American Democracy Undone** | ~38,500 w (Drive doc only 28 KB) | 2024-07-02 | 2024-09-08 (doc) / 2025-03-17 (export) | **thinnest and least finished** |
| **Gospel of Liberation** | ~84 KB doc; five Oct-2024 sessions totalling ~93,500 w | 2024-09-25 | **2025-12-30** | the most recently active non-Villain work |
| **The Villain in the Verse** | 78,534 w | 2025 | 2026-09 | editorial, not releaseable |
| **The Radical Carpenter** | ~10,400 w draft + conversations into late 2024 | 2023-09-19 | 2023-11-13 | abandoned at nine chapters |
| **The Terminal Economy** | ~18 KB doc + PDF | 2025-03-08 | 2025-03-08 | short work, unclear scope |
| **The Great Unraveling: Reimagining Society in an Age of Collapse** | ~13 KB | 2024-09-27 | 2024-09-27 | **outline of a constructive book** |

Plus a cluster of short cosmic-horror pieces (*The Universe Screams in
Silence*, *The Horror of Awakening*, *The Architect of Echoes*, *The Universe
Awakens in Horror*, *Recursion: A Self-Deconstructing Text*, *Introduction:
The Silent Scream of Existence*), all Feb–Mar 2025, and a small number of
standalone essays including **The Narrative That Writes Us** (2025-02-21).

Total identified book-scale manuscript, excluding Villain: **roughly 163,000
words of American trilogy plus ~93,500 words of Gospel of Liberation material.**

## 2. What is not here

`ESTABLISHED_ARCHIVAL_FINDING` — searched the archive (titles, document
bodies, posts), both local repositories, live OneDrive, and live Google Drive.

**Five of the titles named at session start do not exist in any source:**

- *The Property Trick*
- *The Machine Is Not Broken*
- *Declaration of Human Sovereignty*
- *Humanity v. Yahweh*
- *The Fire We Owe Each Other*
- *They Called It Reality*

Zero hits on titles, zero in document bodies, zero in posts, zero in Drive,
zero in either repository. "Human sovereignty" occurs only as a phrase inside
two short BWL essays, not as a work.

`UNKNOWN` — these may be intended works never started, working titles Matt
remembers proposing, titles suggested in a conversation the archive did not
capture, or works stored somewhere not reached. **They should not be treated
as existing manuscripts.** This is a question for Matt, and it is the only
corpus question the evidence cannot settle.

## 3. The shape of the corpus

`SUPPORTED_INTERPRETATION`

The corpus is **not** several unrelated books. It is also not a single
programme executed to plan. What the record shows is **one method applied
repeatedly to different revered objects, in bursts, over roughly three years**,
with abandoned work left where it fell rather than retracted.

Four observations carry that reading.

**a. The introductions all perform the same move.** Book 1: *"The Indecent
Exposure of American Exceptionalism."* Book 2: *"The Emperor's New Clothes —
Unmasking American Capitalism."* Book 3: *"The Illusion of Freedom — Unmasking
American Democracy."* Villain's Preface: *an audit of the character described
by the text.* Every one strips a label before describing a mechanism. That is
step 2 of the audit method, four times, in four books.

**b. Matt already treated the trilogy as one organism.** Book 1 closes with
**"Epilogue: The Hydra's Second Head."** Book 2 closes with **"Epilogue: The
Hydra's Third Head."** He was not writing three books about three topics. He
was writing three heads of one animal, and he said so inside the manuscripts.

**c. The frame was already too small, and he said so before writing it.**
2024-06-22, five days before creating Books 1 and 2: *"I don't just bitch
about the US, it's all of Western civilization that is ill with the
comorbidities of imperialism and capitalism."* See
[`american-trilogy-reassessment.md`](american-trilogy-reassessment.md) §4.

**d. The constructive half exists but is thin and scattered.** *The Great
Unraveling: Reimagining Society in an Age of Collapse* (2024-09-27) is a
13 KB outline. *Gospel of Liberation* is the largest constructive-adjacent
body. ICN is where the actual mechanism design lives, and it lives in code and
specs rather than in prose. See
[`constructive-corpus.md`](constructive-corpus.md).

## 4. The provenance situation

`ESTABLISHED_ARCHIVAL_FINDING`, inherited from the Villain pass and confirmed
again here.

Nearly all of this corpus sits inside the model-assistance era (mid-2023
onward). *The Narrative That Writes Us* still contains the model's sign-off
at the end of the document — *"I've crafted a metafictional essay... Let me
know if you want any refinements or expansions!"* — left in place in Matt's
own writing folder.

That single artifact is the whole provenance problem in miniature. The **idea**
is his: he asked for it, kept it, filed it. The **prose** is not evidence of
how he writes. Both facts are true at once, and the research standard has to
carry both. See [`bwl-research-standard.md`](bwl-research-standard.md).

**Consequence for the rebuild.** Matt's decision to rebuild the trilogy from
scratch is not merely an editorial preference. The existing drafts cannot
support a provenance claim of the kind Villain now has. Rebuilding is the only
route to a defensible edition.

## 5. Where the work should live

`MATT_DECISION` pending, but the repository question is settled by inspection.

`fahertym/bionic-writing-lab` is the correct home. It is already a
Markdown-first multi-format publishing system with `content/{books,essays,
pamphlets,poems,posts,collections,series,fragments}`, a `publications/`
manifest layer, and — importantly — an existing **`concepts/` ontology** of
eleven concept nodes. Its own operating notes say *"Do not center the
architecture on any one existing project."*

The concept ontology already contains `legitimacy`, `coercion`,
`property-as-command`, `institutional-laundering`, `artificial-scarcity`,
`capitalism-as-cancer`, `religion-as-infrastructure`,
`democratic-infrastructure`, `survival-pressure`, `ai-as-amplifier`, and
`source-and-surface`. **Six of those are load-bearing nodes in the concept map
this session built independently from the archive.** The repo already knew
part of the answer.

Nothing in this session was written into `villain-in-the-verse`.
