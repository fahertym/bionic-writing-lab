from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from publication_lib import assemble_markdown, find_publication, load_publications, validate_publications


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble a publication into a single Markdown document.")
    parser.add_argument("publication_id", help="Publication id from publications/*.json")
    parser.add_argument("--output", type=Path, help="Optional output file for assembled Markdown")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print publication metadata and source list as JSON instead of assembled Markdown",
    )
    args = parser.parse_args()

    publications = load_publications()
    errors = validate_publications(publications)
    if errors:
        print("Cannot build publication because validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    publication = find_publication(args.publication_id, publications)
    if args.json:
        payload = {
            "id": publication["id"],
            "title": publication["title"],
            "kind": publication["kind"],
            "route": publication["_route"],
        }
        print(json.dumps(payload, indent=2))
        return 0

    assembled = assemble_markdown(publication)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(assembled, encoding="utf-8")
        print(f"Wrote {args.output}")
        return 0

    print(assembled, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

