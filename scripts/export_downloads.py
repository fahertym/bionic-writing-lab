from __future__ import annotations

from publication_lib import (
    DIST_SITE_DIR,
    build_visibility_metadata,
    clear_directory,
    export_publication_downloads,
    filter_publications_for_build,
    load_concepts,
    load_publications,
    load_reading_paths,
    load_site_config,
    sort_publications,
    validate_publications,
)


def main() -> int:
    publications = load_publications()
    reading_paths = load_reading_paths()
    concepts = load_concepts()
    site_config = load_site_config()
    errors = validate_publications(publications, site_config, reading_paths, concepts)
    if errors:
        print("Downloads not built because validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    included_publications = sort_publications(filter_publications_for_build(publications))
    visibility = build_visibility_metadata(publications, included_publications)
    clear_directory(DIST_SITE_DIR / "downloads")

    generated_count = 0
    warnings: list[str] = []
    for publication in included_publications:
        links, link_warnings = export_publication_downloads(publication, DIST_SITE_DIR, site_config)
        generated_count += len(links)
        warnings.extend(link_warnings)
        if links:
            formats = ", ".join(link["label"] for link in links)
            print(f"{publication['id']}: exported {formats}")

    for warning in warnings:
        print(f"WARNING: {warning}")

    print(
        f"Finished exporting downloads for {len(included_publications)} of {len(publications)} "
        f"publication(s) in {visibility['mode']} mode; created {generated_count} artifact link(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
