from __future__ import annotations

from publication_lib import (
    DIST_SITE_DIR,
    KIND_TO_SECTION,
    PUBLICATION_INVERSE_RELATIONSHIP_LABELS,
    PUBLICATION_RELATIONSHIP_KEYS,
    PUBLICATION_RELATIONSHIP_LABELS,
    build_visibility_metadata,
    build_publication_contexts,
    clear_directory,
    copy_site_assets,
    export_publication_downloads,
    filter_concepts_for_build,
    filter_publications_for_build,
    filter_reading_paths_for_build,
    join_url,
    kind_label,
    load_concepts,
    load_publications,
    load_reading_paths,
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


def prune_relationships(publications: list[dict]) -> None:
    included_ids = {publication["id"] for publication in publications}
    for publication in publications:
        publication["member_publications"] = [
            item for item in publication["member_publications"] if item["id"] in included_ids
        ]
        publication["series_memberships"] = [
            item for item in publication["series_memberships"] if item["id"] in included_ids
        ]
        publication["collection_memberships"] = [
            item for item in publication["collection_memberships"] if item["id"] in included_ids
        ]


def build_navigation(site_config: dict, current_route: str) -> list[dict[str, str]]:
    navigation = [{"label": "Home", "href": relative_route(current_route, "/")}]
    for link in site_config["nav_links"]:
        href = link.get("href") or relative_route(current_route, link["route"])
        navigation.append({"label": link["label"], "href": href})
    return navigation


def build_page_meta(
    site_config: dict,
    *,
    route: str,
    title: str,
    description: str,
    og_type: str,
    canonical_route: str | None = None,
) -> dict[str, str]:
    resolved_canonical_route = canonical_route or route
    canonical_url = join_url(site_config["base_url"], resolved_canonical_route)
    return {
        "title": title,
        "description": description,
        "canonical_url": canonical_url,
        "og_title": title,
        "og_description": description,
        "og_type": og_type,
        "og_url": canonical_url,
    }


def linkify_publications(publications: list[dict], current_route: str) -> list[dict]:
    linked: list[dict] = []
    for publication in publications:
        item = dict(publication)
        item["href"] = relative_route(current_route, publication["_route"])
        linked.append(item)
    return linked


def linkify_reading_paths(reading_paths: list[dict], current_route: str) -> list[dict]:
    linked: list[dict] = []
    for reading_path in reading_paths:
        item = dict(reading_path)
        item["href"] = relative_route(current_route, reading_path["_route"])
        linked.append(item)
    return linked


def linkify_concepts(concepts: list[dict], current_route: str) -> list[dict]:
    linked: list[dict] = []
    for concept in concepts:
        item = dict(concept)
        item["href"] = relative_route(current_route, concept["_route"])
        linked.append(item)
    return linked


def build_reading_path_contexts(reading_paths: list[dict], publications: list[dict]) -> list[dict]:
    by_id = {publication["id"]: publication for publication in publications}
    contexts: list[dict] = []
    for reading_path in reading_paths:
        item_publications = [
            by_id[item_id]
            for item_id in reading_path.get("items", [])
            if item_id in by_id
        ]
        context = {
            **reading_path,
            "status_label": reading_path.get("status", "").replace("-", " ").title(),
            "is_public": reading_path.get("status") == "published",
            "item_publications": item_publications,
        }
        contexts.append(context)

    contexts.sort(key=lambda item: item.get("title", ""))
    return contexts


def build_concept_contexts(concepts: list[dict], publications: list[dict]) -> list[dict]:
    by_publication_id = {publication["id"]: publication for publication in publications}
    by_concept_id = {concept["id"]: concept for concept in concepts}
    contexts: list[dict] = []

    for concept in concepts:
        concept_publications = [
            by_publication_id[publication_id]
            for publication_id in concept.get("publications", [])
            if publication_id in by_publication_id
        ]
        context = {
            **concept,
            "status_label": concept.get("status", "").replace("-", " ").title(),
            "is_public": concept.get("status") == "published",
            "concept_publications": concept_publications,
            "related_concept_items": [],
        }
        contexts.append(context)

    by_context_id = {context["id"]: context for context in contexts}
    for context in contexts:
        context["related_concept_items"] = [
            by_context_id[concept_id]
            for concept_id in context.get("related_concepts", [])
            if concept_id in by_context_id and concept_id in by_concept_id
        ]

    contexts.sort(key=lambda item: item.get("title", ""))
    return contexts


def attach_reading_path_backlinks(publications: list[dict], reading_paths: list[dict]) -> None:
    by_id = {publication["id"]: publication for publication in publications}
    for publication in publications:
        publication["reading_paths"] = []
    for reading_path in reading_paths:
        for publication in reading_path["item_publications"]:
            publication_id = publication["id"]
            if publication_id in by_id:
                by_id[publication_id]["reading_paths"].append(reading_path)


def attach_concept_backlinks(publications: list[dict], concepts: list[dict]) -> None:
    by_id = {publication["id"]: publication for publication in publications}
    for publication in publications:
        publication["concepts"] = []
    for concept in concepts:
        for publication in concept["concept_publications"]:
            publication_id = publication["id"]
            if publication_id in by_id:
                by_id[publication_id]["concepts"].append(concept)


def build_publication_relationship_groups(publications: list[dict]) -> None:
    by_id = {publication["id"]: publication for publication in publications}

    for publication in publications:
        publication["relationship_groups"] = []
        publication["inverse_relationship_groups"] = []

    for publication in publications:
        relationships = publication.get("relationships", {})
        if not isinstance(relationships, dict):
            relationships = {}

        for relationship_key in PUBLICATION_RELATIONSHIP_KEYS:
            related_items = [
                by_id[publication_id]
                for publication_id in relationships.get(relationship_key, [])
                if publication_id in by_id
            ]
            if related_items:
                publication["relationship_groups"].append(
                    {
                        "key": relationship_key,
                        "label": PUBLICATION_RELATIONSHIP_LABELS[relationship_key],
                        "publications": related_items,
                    }
                )

            for related_item in related_items:
                related_item["inverse_relationship_groups"].append(
                    {
                        "key": relationship_key,
                        "label": PUBLICATION_INVERSE_RELATIONSHIP_LABELS[relationship_key],
                        "publications": [publication],
                    }
                )

    for publication in publications:
        merged_inverse_groups: list[dict] = []
        for relationship_key in PUBLICATION_RELATIONSHIP_KEYS:
            items: list[dict] = []
            seen_ids: set[str] = set()
            for group in publication["inverse_relationship_groups"]:
                if group["key"] != relationship_key:
                    continue
                for item in group["publications"]:
                    if item["id"] not in seen_ids:
                        items.append(item)
                        seen_ids.add(item["id"])
            if items:
                merged_inverse_groups.append(
                    {
                        "key": relationship_key,
                        "label": PUBLICATION_INVERSE_RELATIONSHIP_LABELS[relationship_key],
                        "publications": items,
                    }
                )
        publication["inverse_relationship_groups"] = merged_inverse_groups


def render_downloads(site_config: dict, publication: dict, current_route: str) -> list[dict]:
    downloads, warnings = export_publication_downloads(publication, DIST_SITE_DIR, site_config)
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
    relationship_groups = [
        {
            "key": group["key"],
            "label": group["label"],
            "items": [item["id"] for item in group["publications"]],
        }
        for group in publication["relationship_groups"]
    ]
    inverse_relationship_groups = [
        {
            "key": group["key"],
            "label": group["label"],
            "items": [item["id"] for item in group["publications"]],
        }
        for group in publication["inverse_relationship_groups"]
    ]
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
        "series": publication["series_memberships"][0]["id"] if publication["series_memberships"] else None,
        "collection": publication["collection_memberships"][0]["id"] if publication["collection_memberships"] else None,
        "members": [item["id"] for item in publication["member_publications"]],
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
        "relationships": relationship_groups,
        "relationship_backlinks": inverse_relationship_groups,
    }


def publication_year(publication: dict) -> str | None:
    for field in ("date", "updated"):
        value = publication.get(field)
        if isinstance(value, str) and len(value) >= 4:
            year = value[:4]
            if year.isdigit():
                return year
    return None


def index_link_item(item: dict) -> dict:
    return {
        "id": item["id"],
        "title": item["title"],
    }


def unique_ordered(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            ordered.append(value)
            seen.add(value)
    return ordered


def search_index_entry(site_config: dict, publication: dict) -> dict:
    section_titles = [section["title"] for section in publication["sections"]]
    concept_items = [index_link_item(item) for item in publication.get("concepts", [])]
    reading_path_items = [index_link_item(item) for item in publication.get("reading_paths", [])]
    concept_ids = [item["id"] for item in concept_items]
    path_ids = [item["id"] for item in reading_path_items]
    concept_titles = [item["title"] for item in concept_items]
    path_titles = [item["title"] for item in reading_path_items]
    series_items = [index_link_item(item) for item in publication["series_memberships"]]
    collection_items = [index_link_item(item) for item in publication["collection_memberships"]]
    series_ids = [item["id"] for item in series_items]
    collection_ids = [item["id"] for item in collection_items]
    relationship_titles = [
        item["title"]
        for group in publication["relationship_groups"] + publication["inverse_relationship_groups"]
        for item in group["publications"]
    ]
    relationship_ids = unique_ordered([
        item["id"]
        for group in publication["relationship_groups"] + publication["inverse_relationship_groups"]
        for item in group["publications"]
    ])
    year = publication_year(publication)
    search_terms = [
        publication["title"],
        publication.get("subtitle") or "",
        publication["description"],
        publication["kind"],
        kind_label(publication["kind"]),
        " ".join(publication.get("tags", [])),
        publication["status"],
        publication["author"],
        publication["_route"],
        publication.get("date") or "",
        publication.get("updated") or "",
        year or "",
        publication["excerpt"],
        " ".join(section_titles),
        " ".join(concept_ids),
        " ".join(concept_titles),
        " ".join(path_ids),
        " ".join(path_titles),
        " ".join(series_ids),
        " ".join(item["title"] for item in series_items),
        " ".join(collection_ids),
        " ".join(item["title"] for item in collection_items),
        " ".join(relationship_titles),
        " ".join(relationship_ids),
    ]
    return {
        "type": "publication",
        "id": publication["id"],
        "title": publication["title"],
        "subtitle": publication.get("subtitle"),
        "description": publication["description"],
        "excerpt": publication["excerpt"],
        "author": publication["author"],
        "kind": publication["kind"],
        "kind_label": kind_label(publication["kind"]),
        "status": publication["status"],
        "tags": publication.get("tags", []),
        "route": publication["_route"],
        "url": join_url(site_config["base_url"], publication["_route"]),
        "date": publication.get("date"),
        "updated": publication.get("updated"),
        "year": year,
        "section_count": publication["section_count"],
        "section_titles": section_titles,
        "concepts": concept_items,
        "concept_ids": concept_ids,
        "reading_paths": reading_path_items,
        "path_ids": path_ids,
        "series": series_items[0]["id"] if series_items else None,
        "series_ids": series_ids,
        "series_titles": [item["title"] for item in series_items],
        "collection": collection_items[0]["id"] if collection_items else None,
        "collection_ids": collection_ids,
        "collection_titles": [item["title"] for item in collection_items],
        "relationship_ids": relationship_ids,
        "search_text": " ".join(part for part in search_terms if part).lower(),
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
        "publications": items,
    }


def render_publication_sections(publication: dict, current_route: str) -> list[dict]:
    rendered_sections: list[dict] = []
    for section in publication["sections"]:
        rendered_section = dict(section)
        rendered_section["standalone_href"] = relative_route(current_route, section["route"])

        previous_section = section.get("previous_section")
        if previous_section:
            rendered_section["previous_section"] = {
                **previous_section,
                "href": f"#{previous_section['anchor']}",
                "standalone_href": relative_route(current_route, previous_section["route"]),
            }

        next_section = section.get("next_section")
        if next_section:
            rendered_section["next_section"] = {
                **next_section,
                "href": f"#{next_section['anchor']}",
                "standalone_href": relative_route(current_route, next_section["route"]),
            }

        rendered_sections.append(rendered_section)
    return rendered_sections


def render_publication_toc(publication: dict, current_route: str) -> list[dict]:
    return [
        {
            "anchor": section["anchor"],
            "title": section["title"],
            "href": f"#{section['anchor']}",
            "standalone_href": relative_route(current_route, section["route"]),
        }
        for section in publication["sections"]
    ]


def build_section_page_context(publication: dict, section: dict, current_route: str) -> dict:
    rendered_section = dict(section)
    rendered_section["back_to_publication_href"] = relative_route(current_route, publication["_route"])

    previous_section = section.get("previous_section")
    if previous_section:
        rendered_section["previous_section"] = {
            **previous_section,
            "href": relative_route(current_route, previous_section["route"]),
        }

    next_section = section.get("next_section")
    if next_section:
        rendered_section["next_section"] = {
            **next_section,
            "href": relative_route(current_route, next_section["route"]),
        }

    return rendered_section


def build_section_page_title(publication: dict, section: dict, site_title: str) -> str:
    if section["title"] == publication["title"]:
        return f"{publication['title']} · {site_title}"
    return f"{section['title']} · {publication['title']} · {site_title}"


def render_site() -> int:
    site_config = load_site_config()
    publications = load_publications()
    reading_paths = load_reading_paths()
    concepts = load_concepts()
    errors = validate_publications(publications, site_config, reading_paths, concepts)
    if errors:
        print("Site build failed because validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    clear_directory(DIST_SITE_DIR)
    copy_site_assets(DIST_SITE_DIR)
    env = load_site_environment()

    all_publication_contexts = sort_publications(build_publication_contexts(publications))
    publication_contexts = filter_publications_for_build(all_publication_contexts)
    prune_relationships(publication_contexts)
    build_publication_relationship_groups(publication_contexts)
    visibility = build_visibility_metadata(all_publication_contexts, publication_contexts)
    reading_path_contexts = build_reading_path_contexts(
        filter_reading_paths_for_build(reading_paths),
        publication_contexts,
    )
    concept_contexts = build_concept_contexts(
        filter_concepts_for_build(concepts),
        publication_contexts,
    )
    attach_reading_path_backlinks(publication_contexts, reading_path_contexts)
    attach_concept_backlinks(publication_contexts, concept_contexts)

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
    about_template = env.get_template("about.html")
    paths_template = env.get_template("paths.html")
    path_template = env.get_template("path.html")
    concepts_template = env.get_template("concepts.html")
    concept_template = env.get_template("concept.html")
    listing_template = env.get_template("listing.html")
    publication_template = env.get_template("publication.html")
    search_template = env.get_template("search.html")
    section_template = env.get_template("section.html")

    write_text(
        route_to_output_path(DIST_SITE_DIR, "/"),
        index_template.render(
            site=site_config,
            meta=build_page_meta(
                site_config,
                route="/",
                title=site_config["site_title"],
                description=site_config["description"],
                og_type="website",
            ),
            current_route="/",
            nav_items=build_navigation(site_config, "/"),
            visibility=visibility,
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

    about_route = "/about/"
    write_text(
        route_to_output_path(DIST_SITE_DIR, about_route),
        about_template.render(
            site=site_config,
            meta=build_page_meta(
                site_config,
                route=about_route,
                title=f"About · {site_config['site_title']}",
                description=site_config.get("about_description", site_config["description"]),
                og_type="website",
            ),
            current_route=about_route,
            nav_items=build_navigation(site_config, about_route),
            visibility=visibility,
            asset_href=relative_file(about_route, "assets/style.css"),
        ),
    )

    paths_route = "/paths/"
    write_text(
        route_to_output_path(DIST_SITE_DIR, paths_route),
        paths_template.render(
            site=site_config,
            meta=build_page_meta(
                site_config,
                route=paths_route,
                title=f"Reading Paths · {site_config['site_title']}",
                description="Curated routes through publications in Bionic Writing Lab.",
                og_type="website",
            ),
            current_route=paths_route,
            nav_items=build_navigation(site_config, paths_route),
            visibility=visibility,
            reading_paths=linkify_reading_paths(reading_path_contexts, paths_route),
            asset_href=relative_file(paths_route, "assets/style.css"),
        ),
    )

    for reading_path in reading_path_contexts:
        current_route = reading_path["_route"]
        render_path = dict(reading_path)
        render_path["item_publications"] = linkify_publications(
            reading_path["item_publications"],
            current_route,
        )
        write_text(
            route_to_output_path(DIST_SITE_DIR, current_route),
            path_template.render(
                site=site_config,
                meta=build_page_meta(
                    site_config,
                    route=current_route,
                    title=f"{reading_path['title']} · {site_config['site_title']}",
                    description=reading_path["description"],
                    og_type="website",
                ),
                current_route=current_route,
                nav_items=build_navigation(site_config, current_route),
                visibility=visibility,
                reading_path=render_path,
                asset_href=relative_file(current_route, "assets/style.css"),
            ),
        )

    concepts_route = "/concepts/"
    write_text(
        route_to_output_path(DIST_SITE_DIR, concepts_route),
        concepts_template.render(
            site=site_config,
            meta=build_page_meta(
                site_config,
                route=concepts_route,
                title=f"Concepts · {site_config['site_title']}",
                description="Defined recurring ideas in Bionic Writing Lab.",
                og_type="website",
            ),
            current_route=concepts_route,
            nav_items=build_navigation(site_config, concepts_route),
            visibility=visibility,
            concepts=linkify_concepts(concept_contexts, concepts_route),
            asset_href=relative_file(concepts_route, "assets/style.css"),
        ),
    )

    for concept in concept_contexts:
        current_route = concept["_route"]
        render_concept = dict(concept)
        render_concept["concept_publications"] = linkify_publications(
            concept["concept_publications"],
            current_route,
        )
        render_concept["related_concept_items"] = linkify_concepts(
            concept["related_concept_items"],
            current_route,
        )
        write_text(
            route_to_output_path(DIST_SITE_DIR, current_route),
            concept_template.render(
                site=site_config,
                meta=build_page_meta(
                    site_config,
                    route=current_route,
                    title=f"{concept['title']} · {site_config['site_title']}",
                    description=concept["short_definition"],
                    og_type="website",
                ),
                current_route=current_route,
                nav_items=build_navigation(site_config, current_route),
                visibility=visibility,
                concept=render_concept,
                asset_href=relative_file(current_route, "assets/style.css"),
            ),
        )

    for kind, section in KIND_TO_SECTION.items():
        route = f"/{section}/"
        items = grouped_publications[kind]
        write_text(
            route_to_output_path(DIST_SITE_DIR, route),
            listing_template.render(
                site=site_config,
                meta=build_page_meta(
                    site_config,
                    route=route,
                    title=f"{kind_labels[kind]} · {site_config['site_title']}",
                    description=site_config["description"],
                    og_type="website",
                ),
                current_route=route,
                nav_items=build_navigation(site_config, route),
                visibility=visibility,
                listing_title=kind_labels[kind],
                listing_description=f"{kind_labels[kind]} published through the Bionic Writing Lab system.",
                publications=linkify_publications(items, route),
                asset_href=relative_file(route, "assets/style.css"),
            ),
        )

    search_route = "/search/"
    write_text(
        route_to_output_path(DIST_SITE_DIR, search_route),
        search_template.render(
            site=site_config,
            meta=build_page_meta(
                site_config,
                route=search_route,
                title=f"Search · {site_config['site_title']}",
                description=site_config["description"],
                og_type="website",
            ),
            current_route=search_route,
            nav_items=build_navigation(site_config, search_route),
            visibility=visibility,
            asset_href=relative_file(search_route, "assets/style.css"),
            search_index_href=relative_file(search_route, "search-index.json"),
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
        render_publication["reading_paths"] = linkify_reading_paths(
            publication["reading_paths"], publication["_route"]
        )
        render_publication["concepts"] = linkify_concepts(
            publication["concepts"], publication["_route"]
        )
        render_publication["relationship_groups"] = [
            {
                **group,
                "publications": linkify_publications(group["publications"], publication["_route"]),
            }
            for group in publication["relationship_groups"]
        ]
        render_publication["inverse_relationship_groups"] = [
            {
                **group,
                "publications": linkify_publications(group["publications"], publication["_route"]),
            }
            for group in publication["inverse_relationship_groups"]
        ]
        render_publication["sections"] = render_publication_sections(publication, publication["_route"])
        render_publication["toc"] = render_publication_toc(publication, publication["_route"])
        write_text(
            route_to_output_path(DIST_SITE_DIR, publication["_route"]),
            publication_template.render(
                site=site_config,
                meta=build_page_meta(
                    site_config,
                    route=publication["_route"],
                    title=f"{publication['title']} · {site_config['site_title']}",
                    description=publication["description"],
                    og_type="article",
                ),
                current_route=publication["_route"],
                nav_items=build_navigation(site_config, publication["_route"]),
                visibility=visibility,
                publication=render_publication,
                asset_href=relative_file(publication["_route"], "assets/style.css"),
            ),
        )

        if publication["multi_file"]:
            for section in publication["sections"]:
                section_route = section["route"]
                write_text(
                    route_to_output_path(DIST_SITE_DIR, section_route),
                    section_template.render(
                        site=site_config,
                        meta=build_page_meta(
                            site_config,
                            route=section_route,
                            title=build_section_page_title(
                                publication,
                                section,
                                site_config["site_title"],
                            ),
                            description=publication["description"],
                            og_type="article",
                            canonical_route=publication["_route"],
                        ),
                        current_route=section_route,
                        nav_items=build_navigation(site_config, section_route),
                        visibility=visibility,
                        publication=render_publication,
                        section=build_section_page_context(publication, section, section_route),
                        asset_href=relative_file(section_route, "assets/style.css"),
                    ),
                )

    write_json(
        DIST_SITE_DIR / "publications.json",
        {
            "site": {
                "title": site_config["site_title"],
                "base_url": site_config["base_url"],
                "generated_from": "publication manifests",
                "visibility": visibility,
            },
            "publications": [publication_index_entry(site_config, item) for item in publication_contexts],
        },
    )
    write_json(DIST_SITE_DIR / "feed.json", build_feed(site_config, publication_contexts))
    write_json(
        DIST_SITE_DIR / "search-index.json",
        {
            "site": {
                "title": site_config["site_title"],
                "base_url": site_config["base_url"],
                "search_route": "/search/",
                "generated_from": "publication manifests",
                "visibility": visibility,
            },
            "publications": [search_index_entry(site_config, item) for item in publication_contexts],
        },
    )

    print(
        f"Built {visibility['mode']} static site for {len(publication_contexts)} of "
        f"{len(all_publication_contexts)} publication(s) into {DIST_SITE_DIR}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(render_site())
