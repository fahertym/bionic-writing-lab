from __future__ import annotations

from publication_lib import (
    DIST_SITE_DIR,
    KIND_TO_SECTION,
    build_publication_contexts,
    clear_directory,
    copy_site_assets,
    export_publication_downloads,
    join_url,
    kind_label,
    load_publications,
    load_site_config,
    load_site_environment,
    relative_file,
    relative_route,
    route_to_output_path,
    sort_publications,
    validate_publications,
    write_json,
    write_text,
)


def build_navigation(site_config: dict, current_route: str) -> list[dict[str, str]]:
    navigation = [{"label": "Home", "href": relative_route(current_route, "/")}]
    for link in site_config["nav_links"]:
        href = link.get("href") or relative_route(current_route, link["route"])
        navigation.append({"label": link["label"], "href": href})
    return navigation


def linkify_publications(publications: list[dict], current_route: str) -> list[dict]:
    linked: list[dict] = []
    for publication in publications:
        item = dict(publication)
        item["href"] = relative_route(current_route, publication["_route"])
        linked.append(item)
    return linked


def render_downloads(site_config: dict, publication: dict, current_route: str) -> list[dict]:
    downloads, warnings = export_publication_downloads(publication, DIST_SITE_DIR)
    publication["download_warnings"] = warnings
    rendered: list[dict] = []
    for link in downloads:
        route = "/" + link["href"].lstrip("/")
        rendered.append(
            {
                **link,
                "href": relative_file(current_route, link["href"]),
                "route": route,
                "absolute_url": join_url(site_config["base_url"], route),
            }
        )
    return rendered


def publication_index_entry(site_config: dict, publication: dict) -> dict:
    return {
        "id": publication["id"],
        "title": publication["title"],
        "subtitle": publication.get("subtitle"),
        "author": publication["author"],
        "kind": publication["kind"],
        "slug": publication["slug"],
        "description": publication["description"],
        "status": publication["status"],
        "tags": publication.get("tags", []),
        "route": publication["_route"],
        "url": join_url(site_config["base_url"], publication["_route"]),
        "output_formats": publication.get("output_formats", []),
        "downloadable": publication.get("downloadable", False),
        "series": publication.get("series"),
        "collection": publication.get("collection"),
        "members": publication.get("members", []),
        "series_memberships": [item["id"] for item in publication["series_memberships"]],
        "collection_memberships": [item["id"] for item in publication["collection_memberships"]],
        "member_count": len(publication["member_publications"]),
        "word_count": publication["word_count"],
        "section_count": publication["section_count"],
        "excerpt": publication["excerpt"],
        "date": publication.get("date"),
        "updated": publication.get("updated"),
        "downloads": [
            {"label": item["label"], "url": item["absolute_url"], "route": item["route"]}
            for item in publication["downloads"]
        ],
    }


def build_feed(site_config: dict, publications: list[dict]) -> dict:
    items: list[dict] = []
    for publication in publications:
        if not publication.get("date") and not publication.get("updated"):
            continue
        items.append(
            {
                "id": join_url(site_config["base_url"], publication["_route"]),
                "url": join_url(site_config["base_url"], publication["_route"]),
                "title": publication["title"],
                "summary": publication["description"],
                "content_text": publication["excerpt"],
                "date_published": publication.get("date"),
                "date_modified": publication.get("updated") or publication.get("date"),
                "tags": publication.get("tags", []),
            }
        )
    return {
        "version": "https://jsonfeed.org/version/1.1",
        "title": site_config["site_title"],
        "home_page_url": join_url(site_config["base_url"], "/"),
        "feed_url": join_url(site_config["base_url"], "/feed.json"),
        "description": site_config["description"],
        "language": site_config["language"],
        "authors": [{"name": site_config["author"]}],
        "items": items,
    }


def render_site() -> int:
    site_config = load_site_config()
    publications = load_publications()
    errors = validate_publications(publications, site_config)
    if errors:
        print("Site build failed because validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    clear_directory(DIST_SITE_DIR)
    copy_site_assets(DIST_SITE_DIR)
    env = load_site_environment()

    publication_contexts = sort_publications(build_publication_contexts(publications))

    for publication in publication_contexts:
        publication["downloads"] = render_downloads(site_config, publication, publication["_route"])

    grouped_publications = {
        kind: [item for item in publication_contexts if item["kind"] == kind]
        for kind in KIND_TO_SECTION
    }
    kind_labels = {kind: kind_label(kind) for kind in KIND_TO_SECTION}
    kind_routes = {
        kind: relative_route("/", f"/{section}/")
        for kind, section in KIND_TO_SECTION.items()
    }

    index_template = env.get_template("index.html")
    listing_template = env.get_template("listing.html")
    publication_template = env.get_template("publication.html")

    write_text(
        route_to_output_path(DIST_SITE_DIR, "/"),
        index_template.render(
            site=site_config,
            current_route="/",
            nav_items=build_navigation(site_config, "/"),
            recent_publications=linkify_publications(publication_contexts[:6], "/"),
            grouped_publications={
                kind: linkify_publications(items, "/")
                for kind, items in grouped_publications.items()
            },
            kind_labels=kind_labels,
            kind_routes=kind_routes,
            asset_href=relative_file("/", "assets/style.css"),
        ),
    )

    for kind, section in KIND_TO_SECTION.items():
        route = f"/{section}/"
        items = grouped_publications[kind]
        write_text(
            route_to_output_path(DIST_SITE_DIR, route),
            listing_template.render(
                site=site_config,
                current_route=route,
                nav_items=build_navigation(site_config, route),
                listing_title=kind_labels[kind],
                listing_description=f"{kind_labels[kind]} published through the Bionic Writing Lab system.",
                publications=linkify_publications(items, route),
                asset_href=relative_file(route, "assets/style.css"),
            ),
        )

    for publication in publication_contexts:
        render_publication = dict(publication)
        render_publication["member_publications"] = linkify_publications(
            publication["member_publications"], publication["_route"]
        )
        render_publication["series_memberships"] = linkify_publications(
            publication["series_memberships"], publication["_route"]
        )
        render_publication["collection_memberships"] = linkify_publications(
            publication["collection_memberships"], publication["_route"]
        )
        write_text(
            route_to_output_path(DIST_SITE_DIR, publication["_route"]),
            publication_template.render(
                site=site_config,
                current_route=publication["_route"],
                nav_items=build_navigation(site_config, publication["_route"]),
                publication=render_publication,
                asset_href=relative_file(publication["_route"], "assets/style.css"),
            ),
        )

    write_json(
        DIST_SITE_DIR / "publications.json",
        {
            "site": {
                "title": site_config["site_title"],
                "base_url": site_config["base_url"],
                "generated_from": "publication manifests",
            },
            "publications": [publication_index_entry(site_config, item) for item in publication_contexts],
        },
    )
    write_json(DIST_SITE_DIR / "feed.json", build_feed(site_config, publication_contexts))

    print(f"Built static site for {len(publication_contexts)} publication(s) into {DIST_SITE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(render_site())
