"""Word-count and progress reporting for Bionic Writing Lab publications.

Shows the live word count for each publication, and -- when a manifest
declares an optional ``target_words`` field -- progress toward that goal.
This is the "you're at 47k of 80k" view that long-form drafting needs.

Standard library only.

Usage:
    python scripts/stats.py                              # every publication
    python scripts/stats.py --publication villain-in-the-verse
    python scripts/stats.py --kind book                  # only books
    python scripts/stats.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from publication_lib import (  # noqa: E402
    load_publications,
    publication_word_count,
    resolve_sections,
)

BAR_WIDTH = 24


def progress_bar(fraction: float) -> str:
    fraction = max(0.0, min(1.0, fraction))
    filled = round(fraction * BAR_WIDTH)
    return "[" + "#" * filled + "-" * (BAR_WIDTH - filled) + "]"


def collect(publication: dict) -> dict:
    words = publication_word_count(publication)
    try:
        sections = resolve_sections(publication)
    except Exception:
        sections = []
    target = publication.get("target_words")
    entry = {
        "id": publication.get("id"),
        "title": publication.get("title"),
        "kind": publication.get("kind"),
        "status": publication.get("status"),
        "word_count": words,
        "section_count": len(sections),
        "target_words": target if isinstance(target, int) else None,
    }
    if entry["target_words"]:
        entry["progress"] = round(words / entry["target_words"], 4)
        entry["words_remaining"] = max(0, entry["target_words"] - words)
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Word-count and progress for publications.")
    parser.add_argument("--publication", help="Only report this publication id")
    parser.add_argument("--kind", help="Only report publications of this kind")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    args = parser.parse_args()

    publications = load_publications()
    if args.publication:
        publications = [p for p in publications if p.get("id") == args.publication]
        if not publications:
            print(f"No publication with id '{args.publication}'", file=sys.stderr)
            return 1
    if args.kind:
        publications = [p for p in publications if p.get("kind") == args.kind]

    entries = sorted(
        (collect(p) for p in publications),
        key=lambda e: (e["kind"] or "", -e["word_count"]),
    )

    if args.json:
        print(json.dumps(entries, indent=2))
        return 0

    if not entries:
        print("No publications matched.")
        return 0

    total = sum(e["word_count"] for e in entries)
    width = max(len(e["title"] or e["id"] or "") for e in entries)
    for e in entries:
        name = (e["title"] or e["id"] or "").ljust(width)
        line = f"{name}  {e['word_count']:>7,} words"
        if e["section_count"]:
            line += f"  ({e['section_count']} sections)"
        if e.get("target_words"):
            pct = e["progress"] * 100
            line += f"  {progress_bar(e['progress'])} {pct:5.1f}% of {e['target_words']:,}"
            if e["words_remaining"]:
                line += f"  ({e['words_remaining']:,} to go)"
        print(line)

    print("-" * (width + 16))
    print(f"{'TOTAL'.ljust(width)}  {total:>7,} words across {len(entries)} publication(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
