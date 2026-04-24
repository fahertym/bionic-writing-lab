from __future__ import annotations

from publication_lib import (
    DIST_SITE_DIR,
    KIND_TO_SECTION,
    build_publication_context,
    clear_directory,
    copy_site_assets,
    export_publication_downloads,
    kind_label,
    load_publications,
    load_site_environment,
    relative_file,
    relative_route,
    route_to_output_path,
    sort_publications,
    validate_publications,
    write_text,
)


SITE_TITLE = "Bionic Writing Lab"
SITE_DESCRIPTION = "Markdown-first static publishing system for books, essays, poems, collections, and web-native writing."


def build_navigation(current_route: str) -> list[dict[str, str]]:
    navigation = [{"label": "Home", "href": relative_route(current_route, "/")}]
    for kind, section in KIND_TO_SECTION.items():
        navigation.append(
            {
                "label": kind_label(kind),
                "href": relative_route(current_route, f"/{section}/"),
            }
        )
    return navigation


def with_links(publications: list[dict], current_route: str) -> list[dict]:
    linked: list[dict] = []
    for publication in publications:
        item = dict(publication)
        item["href"] = relative_route(current_route, publication["_route"])
        linked.append(item)
    return linked


def render_site() -> int:
    publications = load_publications()
    errors = validate_publications(publications)
    if errors:
        print("Site build failed because validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    clear_directory(DIST_SITE_DIR)
    copy_site_assets(DIST_SITE_DIR)
    env = load_site_environment()

    publication_contexts = [build_publication_context(publication) for publication in publications]
    publication_contexts = sort_publications(publication_contexts)

    for publication in publication_contexts:
        downloads, warnings = export_publication_downloads(publication, DIST_SITE_DIR)
        publication["downloads"] = [
            {
                **link,
                "href": relative_file(publication["_route"], link["href"]),
            }
            for link in downloads
        ]
        publication["download_warnings"] = warnings

    index_template = env.get_template("index.html")
    listing_template = env.get_template("listing.html")
    publication_template = env.get_template("publication.html")

    write_text(
        route_to_output_path(DIST_SITE_DIR, "/"),
        index_template.render(
            site_title=SITE_TITLE,
            site_description=SITE_DESCRIPTION,
            current_route="/",
            nav_items=build_navigation("/"),
            publications=with_links(publication_contexts, "/"),
            grouped_publications={
                kind: with_links([item for item in publication_contexts if item["kind"] == kind], "/")
                for kind in KIND_TO_SECTION
            },
            kind_labels={kind: kind_label(kind) for kind in KIND_TO_SECTION},
            asset_href=relative_file("/", "assets/style.css"),
        ),
    )

    for kind, section in KIND_TO_SECTION.items():
        route = f"/{section}/"
        items = [item for item in publication_contexts if item["kind"] == kind]
        write_text(
            route_to_output_path(DIST_SITE_DIR, route),
            listing_template.render(
                site_title=SITE_TITLE,
                site_description=SITE_DESCRIPTION,
                current_route=route,
                nav_items=build_navigation(route),
                listing_title=kind_label(kind),
                listing_description=f"All {section} currently defined by publication manifests.",
                publications=with_links(items, route),
                asset_href=relative_file(route, "assets/style.css"),
            ),
        )

    for publication in publication_contexts:
        write_text(
            route_to_output_path(DIST_SITE_DIR, publication["_route"]),
            publication_template.render(
                site_title=SITE_TITLE,
                site_description=SITE_DESCRIPTION,
                current_route=publication["_route"],
                nav_items=build_navigation(publication["_route"]),
                publication=publication,
                asset_href=relative_file(publication["_route"], "assets/style.css"),
            ),
        )

    print(f"Built static site for {len(publication_contexts)} publication(s) into {DIST_SITE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(render_site())

