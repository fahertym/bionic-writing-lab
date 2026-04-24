from __future__ import annotations

from pathlib import Path

from publication_lib import DIST_SITE_DIR, build_publication_contexts, load_publications, route_to_output_path


REQUIRED_FILES = (
    "index.html",
    "publications.json",
    "feed.json",
    "search-index.json",
    "search/index.html",
    "books/example-book/index.html",
    "essays/example-essay/index.html",
    "poems/example-poem/index.html",
    "posts/example-post/index.html",
    "pamphlets/example-pamphlet/index.html",
    "collections/example-collection/index.html",
    "series/example-series/index.html",
)


def require_path(path: Path, label: str, failures: list[str]) -> None:
    if not path.exists():
        failures.append(f"missing {label}: {path}")


def main() -> int:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        require_path(DIST_SITE_DIR / relative_path, relative_path, failures)

    publications = build_publication_contexts(load_publications())
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

    if failures:
        print("Smoke check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Smoke check passed for site outputs, search index, and section routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
