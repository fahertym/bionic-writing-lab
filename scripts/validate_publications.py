from __future__ import annotations

import sys

from publication_lib import (
    load_concepts,
    load_publications,
    load_reading_paths,
    load_site_config,
    print_errors,
    validate_publications,
)


def main() -> int:
    publications = load_publications()
    reading_paths = load_reading_paths()
    concepts = load_concepts()
    site_config = load_site_config()
    errors = validate_publications(publications, site_config, reading_paths, concepts)

    if errors:
        print("Publication validation failed:", file=sys.stderr)
        print_errors(errors)
        return 1

    kinds = sorted({publication["kind"] for publication in publications})
    print(
        f"Validated site config, {len(publications)} publication manifest(s), "
        f"{len(reading_paths)} reading path manifest(s), and {len(concepts)} concept manifest(s) "
        f"across {len(kinds)} kind(s): {', '.join(kinds)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
