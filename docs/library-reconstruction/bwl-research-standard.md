# BWL Research Standard (proposed)

**Session:** BWL Library Reconstruction, 2026-09-07
**Status:** `FUTURE_RESEARCH_HYPOTHESIS` — a proposal, not yet adopted.

Derived from what the *Villain* archival-authorship pass actually taught, not
from general good practice. Every rule below exists because something went
wrong without it.

---

## 1. Provenance classes

Inherited from the Villain pass and validated twice.

| Class | Meaning | May support |
|---|---|---|
| `DIRECT_MATT` | his own contemporaneous prose | position **and** style |
| `MATT_EDITED_OR_DIRECTED` | model-assisted, but he directed, selected, revised, published | **position only — never style** |
| `AI_RESPONSE` | assistant output | nothing |
| `DERIVED_ARCHIVE_ANALYSIS` | later summaries, this document included | orientation only |
| `EXTERNAL_SOURCE` | another person or entity | itself, cited |

**The rule that matters:** any style claim sourced to post-2023 material is
circular and must be marked. Matt asked models to draft in his voice; that
prose proves nothing about how he writes and everything about what he thinks.

## 2. The four-part provenance of a single passage

The hardest lesson from Villain, and the one general standards miss.

For any given paragraph, these can all differ:

1. **the idea** — whose was it
2. **the seed prose** — who wrote the first version
3. **the expanded prose** — who produced what shipped
4. **the editorial decision** — who chose to keep it

*Worked example.* The projection argument: idea **Matt**, seed prose **Matt**
(Facebook post, 2024-07-23), expanded prose **model** (two sessions,
2024-08-10), editorial decision **Matt** (published the 2,131-word version the
same day). Recording only "AI-assisted" would lose three of the four facts, and
the one it kept would be the least interesting.

*Counter-example.* *The Narrative That Writes Us* still carries the model's
sign-off inside the document. Idea **Matt**, seed prose **model**, expanded
prose **model**, editorial decision **Matt**. Same coarse label, completely
different artifact.

**Standard: record all four, per passage, or record none and say so.**

## 3. Evidence categories for autobiographical and historical claims

Never blur these four:

- **documented** — a contemporaneous artifact exists
- **contemporaneously corroborated** — a third party's record places it
- **remembered** — his later account, attributed as such, with the date of the
  recollection *and* the date recalled
- **later reconstructed** — this project's inference from the record

## 4. External research classification

For the rebuilt trilogy, where the evidentiary burden is far heavier than
Villain's single-text audit:

primary historical source · scholarly secondary source · government or
institutional record · quantitative dataset · journalism · advocacy source ·
firsthand testimony · disputed claim · **model synthesis**.

**Model synthesis is not a source.** It is a lead. The existing trilogy drafts
are full of confident historical assertion produced inside an assistance loop;
none of it is citable until independently verified. This is the main reason
rebuilding beats editing.

## 5. Process requirements

| Artifact | Purpose | Villain precedent |
|---|---|---|
| claim ledger | every load-bearing factual claim, with source and confidence | `research/claims/*.yml` |
| source manifest | every source actually inspected, with locator | `source-manifest.tsv` |
| chronology | real dates, with `date_basis` recorded | ingestion-timestamp trap |
| contradiction register | changes of mind preserved, not smoothed | `revision-register.md` |
| alternative explanations | tested and recorded, including failures | the failed marker tracer |
| steelman requirement | strongest version of the opposing case, before rebuttal | Apology Boxes |
| uncertainty labels | six classes, never blurred | this document set |
| negative results | what was searched and not found | Villain E11 |

## 6. Dates

**Never trust a `created_at` column.** Recover real dates from OOXML
`docProps/core.xml`, Drive `createdTime`, or platform timestamps. In the
Villain pass an entire arc was misdated because an ingestion pipeline
overwrote composition dates with import dates, and the error survived two
passes before a chronological search caught it.

## 7. Privacy

Availability is not permission. Private correspondence may serve as **evidence
for authorship** without becoming **publication material**. Prefer fresh
paraphrase; propose any direct quotation in a review artifact first; never
identify a correspondent; treat medical, financial, family and relationship
material as prohibited unless Matt raises it.

## 8. Search methodology

Two lessons, both learned by failing:

**Keyword search finds topics; chronology finds origins.** A keyword tracer
over 22,105 records returned 591 false positives where "genocide" meant Gaza
and the monster was Thomas Edison. Date-ordering found the real origin in one
pass.

**Bind the verdict to its object.** Scoring for moral vocabulary without
requiring the target in the same record measures nothing.
