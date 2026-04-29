from __future__ import annotations

import json
from pathlib import Path

from publication_lib import (
    DIST_SITE_DIR,
    build_download_filename,
    build_publication_contexts,
    filter_concepts_for_build,
    filter_publications_for_build,
    filter_reading_paths_for_build,
    load_concepts,
    load_publications,
    load_reading_paths,
    route_to_output_path,
)


REQUIRED_FILES = (
    "index.html",
    "about/index.html",
    "concepts/index.html",
    "concepts/source-and-surface/index.html",
    "paths/index.html",
    "publications.json",
    "feed.json",
    "search-index.json",
    "search/index.html",
    "books/example-book/index.html",
    "essays/example-essay/index.html",
    "fragments/example-fragment/index.html",
    "poems/example-poem/index.html",
    "posts/example-post/index.html",
    "pamphlets/example-pamphlet/index.html",
    "collections/example-collection/index.html",
    "series/example-series/index.html",
)

SEARCH_INDEX_REQUIRED_FIELDS = (
    "id",
    "title",
    "kind",
    "status",
    "tags",
    "year",
    "concept_ids",
    "path_ids",
    "relationship_ids",
    "search_text",
)


def require_path(path: Path, label: str, failures: list[str]) -> None:
    if not path.exists():
        failures.append(f"missing {label}: {path}")


def main() -> int:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        require_path(DIST_SITE_DIR / relative_path, relative_path, failures)

    publications = filter_publications_for_build(build_publication_contexts(load_publications()))
    reading_paths = filter_reading_paths_for_build(load_reading_paths())
    concepts = filter_concepts_for_build(load_concepts())
    search_index_path = DIST_SITE_DIR / "search-index.json"
    if search_index_path.exists():
        search_index = json.loads(search_index_path.read_text(encoding="utf-8"))
        for item in search_index.get("publications", []):
            missing_fields = [
                field for field in SEARCH_INDEX_REQUIRED_FIELDS if field not in item
            ]
            if missing_fields:
                failures.append(
                    f"search-index publication {item.get('id', '<unknown>')} missing "
                    f"{', '.join(missing_fields)}"
                )

    for publication in publications:
        if not publication["multi_file"]:
            continue
        for section in publication["sections"]:
            require_path(
                route_to_output_path(DIST_SITE_DIR, section["route"]),
                f"section route {section['route']}",
                failures,
            )

    if any(publication.get("downloadable") for publication in publications):
        require_path(DIST_SITE_DIR / "downloads", "downloads directory", failures)

    for publication in publications:
        if not publication.get("downloadable"):
            continue
        require_path(
            DIST_SITE_DIR / "downloads" / publication["_section"] / build_download_filename(publication, "md"),
            f"Markdown download for {publication['id']}",
            failures,
        )

    for reading_path in reading_paths:
        require_path(
            route_to_output_path(DIST_SITE_DIR, reading_path["_route"]),
            f"reading path route {reading_path['_route']}",
            failures,
        )

    for concept in concepts:
        require_path(
            route_to_output_path(DIST_SITE_DIR, concept["_route"]),
            f"concept route {concept['_route']}",
            failures,
        )

    if failures:
        print("Smoke check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Smoke check passed for site outputs, search index, and section routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
