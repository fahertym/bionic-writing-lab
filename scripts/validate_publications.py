from __future__ import annotations

import sys

from publication_lib import load_publications, print_errors, validate_publications


def main() -> int:
    publications = load_publications()
    errors = validate_publications(publications)

    if errors:
        print("Publication validation failed:", file=sys.stderr)
        print_errors(errors)
        return 1

    kinds = sorted({publication["kind"] for publication in publications})
    print(
        f"Validated {len(publications)} publication manifest(s) across {len(kinds)} kind(s): {', '.join(kinds)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

