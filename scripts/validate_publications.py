from __future__ import annotations

import sys

from publication_lib import load_publications, load_site_config, print_errors, validate_publications


def main() -> int:
    publications = load_publications()
    site_config = load_site_config()
    errors = validate_publications(publications, site_config)

    if errors:
        print("Publication validation failed:", file=sys.stderr)
        print_errors(errors)
        return 1

    kinds = sorted({publication["kind"] for publication in publications})
    print(
        f"Validated site config and {len(publications)} publication manifest(s) across {len(kinds)} kind(s): {', '.join(kinds)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
