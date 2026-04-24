from __future__ import annotations

from publication_lib import (
    DIST_SITE_DIR,
    export_publication_downloads,
    load_publications,
    load_site_config,
    sort_publications,
    validate_publications,
)


def main() -> int:
    publications = load_publications()
    site_config = load_site_config()
    errors = validate_publications(publications, site_config)
    if errors:
        print("Downloads not built because validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    generated_count = 0
    warnings: list[str] = []
    for publication in sort_publications(publications):
        links, link_warnings = export_publication_downloads(publication, DIST_SITE_DIR)
        generated_count += len(links)
        warnings.extend(link_warnings)
        if links:
            formats = ", ".join(link["label"] for link in links)
            print(f"{publication['id']}: exported {formats}")

    for warning in warnings:
        print(f"WARNING: {warning}")

    print(f"Finished exporting downloads for {len(publications)} publication(s); created {generated_count} artifact link(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
