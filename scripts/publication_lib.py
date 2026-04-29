from __future__ import annotations

import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape


ROOT = Path(__file__).resolve().parent.parent
PUBLICATIONS_DIR = ROOT / "publications"
PATHS_DIR = ROOT / "paths"
CONCEPTS_DIR = ROOT / "concepts"
SCHEMA_PATH = ROOT / "schema" / "publication.schema.json"
SITE_DIR = ROOT / "site"
SITE_CONFIG_PATH = SITE_DIR / "site.json"
SITE_TEMPLATES_DIR = SITE_DIR / "templates"
SITE_ASSETS_DIR = SITE_DIR / "assets"
SITE_PANDOC_DIR = SITE_DIR / "pandoc"
SITE_PANDOC_DEFAULTS_DIR = SITE_PANDOC_DIR / "defaults"
DIST_DIR = ROOT / "dist"
DIST_SITE_DIR = DIST_DIR / "site"

SUPPORTED_KINDS = (
    "book",
    "series",
    "essay",
    "fragment",
    "poem",
    "post",
    "pamphlet",
    "collection",
)
SUPPORTED_OUTPUT_FORMATS = ("site", "markdown", "pdf", "epub", "docx")
PANDOC_OUTPUT_FORMATS = ("pdf", "epub", "docx")
SINGLE_FILE_KINDS = ("essay", "fragment", "poem", "post", "pamphlet")
FOLDER_KINDS = ("book", "collection", "series")
DEFAULT_OUTPUT_FORMATS = {
    "book": ["site", "markdown", "pdf", "epub", "docx"],
    "collection": ["site", "markdown", "epub"],
    "essay": ["site", "markdown", "pdf"],
    "fragment": ["site", "markdown"],
    "pamphlet": ["site", "markdown", "pdf"],
    "poem": ["site", "markdown"],
    "post": ["site", "markdown"],
    "series": ["site", "markdown"],
}
SUPPORTED_STATUSES = (
    "draft",
    "imported",
    "review",
    "published",
    "archived",
    "superseded",
    "private",
)
PUBLIC_STATUSES = ("published",)
RELATIONSHIP_KINDS = ("series", "collection")
PUBLICATION_RELATIONSHIP_KEYS = (
    "expands",
    "responds_to",
    "supersedes",
    "related",
    "excerpt_of",
    "adapted_from",
)
PUBLICATION_RELATIONSHIP_LABELS = {
    "expands": "Expands",
    "responds_to": "Responds To",
    "supersedes": "Supersedes",
    "related": "Related",
    "excerpt_of": "Excerpt Of",
    "adapted_from": "Adapted From",
}
PUBLICATION_INVERSE_RELATIONSHIP_LABELS = {
    "expands": "Expanded By",
    "responds_to": "Responses",
    "supersedes": "Superseded By",
    "related": "Related",
    "excerpt_of": "Excerpts",
    "adapted_from": "Adaptations",
}
SITE_CONFIG_REQUIRED_FIELDS = (
    "site_title",
    "tagline",
    "author",
    "description",
    "base_url",
    "language",
    "copyright",
    "nav_links",
)
KIND_TO_SECTION = {
    "book": "books",
    "series": "series",
    "essay": "essays",
    "poem": "poems",
    "post": "posts",
    "pamphlet": "pamphlets",
    "collection": "collections",
    "fragment": "fragments",
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def list_manifest_paths() -> List[Path]:
    return sorted(PUBLICATIONS_DIR.glob("*.json"))


def list_reading_path_manifest_paths() -> List[Path]:
    return sorted(PATHS_DIR.glob("*.json"))


def list_concept_manifest_paths() -> List[Path]:
    return sorted(CONCEPTS_DIR.glob("*.json"))


def load_schema() -> Dict[str, Any]:
    return load_json(SCHEMA_PATH)


def load_site_config() -> Dict[str, Any]:
    if SITE_CONFIG_PATH.exists():
        site_config = load_json(SITE_CONFIG_PATH)
    else:
        site_config = {}
    site_config["_config_path"] = SITE_CONFIG_PATH
    site_config["_exists"] = SITE_CONFIG_PATH.exists()
    return site_config


def load_publications() -> List[Dict[str, Any]]:
    publications: List[Dict[str, Any]] = []
    for manifest_path in list_manifest_paths():
        publication = load_json(manifest_path)
        publication["_manifest_path"] = manifest_path
        publication["_section"] = KIND_TO_SECTION.get(publication.get("kind", ""), "writing")
        publication["_route"] = normalize_route(
            publication.get("web_route"),
            publication.get("kind", ""),
            publication.get("slug", ""),
        )
        publications.append(publication)
    return publications


def load_reading_paths() -> List[Dict[str, Any]]:
    reading_paths: List[Dict[str, Any]] = []
    for manifest_path in list_reading_path_manifest_paths():
        reading_path = load_json(manifest_path)
        reading_path["_manifest_path"] = manifest_path
        reading_path["_route"] = f"/paths/{reading_path.get('slug', reading_path.get('id', ''))}/"
        reading_paths.append(reading_path)
    return reading_paths


def load_concepts() -> List[Dict[str, Any]]:
    concepts: List[Dict[str, Any]] = []
    for manifest_path in list_concept_manifest_paths():
        concept = load_json(manifest_path)
        concept["_manifest_path"] = manifest_path
        concept["_route"] = f"/concepts/{concept.get('slug', concept.get('id', ''))}/"
        concepts.append(concept)
    return concepts


def normalize_route(route: str | None, kind: str, slug: str) -> str:
    if route:
        return "/" + route.strip("/") + "/"
    section = KIND_TO_SECTION.get(kind, "writing")
    return f"/{section}/{slug}/"


def join_url(base_url: str, route_or_path: str) -> str:
    normalized_base = base_url.rstrip("/")
    normalized_path = route_or_path.lstrip("/")
    if not normalized_path:
        return normalized_base + "/"
    return normalized_base + "/" + normalized_path


def resolve_manifest_path(publication: Dict[str, Any], reference: str) -> Path:
    candidate = (ROOT / reference).resolve()
    if candidate.exists():
        return candidate
    return (publication["_manifest_path"].parent / reference).resolve()


def expand_markdown_paths(path: Path) -> List[Path]:
    if path.is_file():
        return [path]
    return sorted(child for child in path.rglob("*.md") if child.is_file())


def dedupe_paths(paths: Iterable[Path]) -> List[Path]:
    seen: set[Path] = set()
    ordered: List[Path] = []
    for path in paths:
        if path not in seen:
            ordered.append(path)
            seen.add(path)
    return ordered


def resolve_source_paths(publication: Dict[str, Any]) -> List[Path]:
    resolved: List[Path] = []
    source_root: Path | None = None

    if publication.get("source"):
        source_root = resolve_manifest_path(publication, publication["source"])

    if publication.get("sources"):
        for entry in publication["sources"]:
            entry_path = Path(entry)
            if source_root and source_root.is_dir() and not entry_path.is_absolute():
                candidate = (source_root / entry_path).resolve()
            else:
                candidate = resolve_manifest_path(publication, entry)
            resolved.extend(expand_markdown_paths(candidate))
        return dedupe_paths(resolved)

    if source_root:
        return dedupe_paths(expand_markdown_paths(source_root))

    return []


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")


def parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_output_formats(formats: List[str]) -> List[str]:
    errors: List[str] = []
    if not formats:
        errors.append("formats must include at least one output format")
    for fmt in formats:
        if fmt not in SUPPORTED_OUTPUT_FORMATS:
            expected = ", ".join(SUPPORTED_OUTPUT_FORMATS)
            errors.append(f"unsupported output format '{fmt}' (expected one of: {expected})")
    return errors


def kind_label(kind: str) -> str:
    return KIND_TO_SECTION[kind].replace("-", " ").title()


def status_label(status: str) -> str:
    return status.replace("-", " ").title()


def include_drafts_enabled() -> bool:
    return os.environ.get("INCLUDE_DRAFTS", "").lower() in {"1", "true", "yes", "on"}


def publication_is_public(publication: Dict[str, Any]) -> bool:
    return publication.get("status") in PUBLIC_STATUSES


def publication_is_included(publication: Dict[str, Any]) -> bool:
    return include_drafts_enabled() or publication_is_public(publication)


def reading_path_is_public(reading_path: Dict[str, Any]) -> bool:
    return reading_path.get("status") in PUBLIC_STATUSES


def reading_path_is_included(reading_path: Dict[str, Any]) -> bool:
    return include_drafts_enabled() or reading_path_is_public(reading_path)


def concept_is_public(concept: Dict[str, Any]) -> bool:
    return concept.get("status") in PUBLIC_STATUSES


def concept_is_included(concept: Dict[str, Any]) -> bool:
    return include_drafts_enabled() or concept_is_public(concept)


def filter_publications_for_build(publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [publication for publication in publications if publication_is_included(publication)]


def filter_reading_paths_for_build(reading_paths: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [reading_path for reading_path in reading_paths if reading_path_is_included(reading_path)]


def filter_concepts_for_build(concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [concept for concept in concepts if concept_is_included(concept)]


def build_visibility_metadata(publications: List[Dict[str, Any]], included_publications: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "mode": "all-status preview" if include_drafts_enabled() else "public",
        "include_drafts": include_drafts_enabled(),
        "included_statuses": list(SUPPORTED_STATUSES) if include_drafts_enabled() else list(PUBLIC_STATUSES),
        "publication_count": len(publications),
        "included_publication_count": len(included_publications),
    }


def clear_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_site_assets(destination: Path) -> None:
    target = destination / "assets"
    shutil.copytree(SITE_ASSETS_DIR, target, dirs_exist_ok=True)


def route_directory(route: str) -> str:
    stripped = route.strip("/")
    return stripped or "."


def route_to_output_path(site_root: Path, route: str) -> Path:
    stripped = route.strip("/")
    if not stripped:
        return site_root / "index.html"
    return site_root / stripped / "index.html"


def extend_route(route: str, child_segment: str) -> str:
    parent = route.strip("/")
    child = child_segment.strip("/")
    if not parent:
        return f"/{child}/"
    if not child:
        return f"/{parent}/"
    return f"/{parent}/{child}/"


def relative_route(current_route: str, target_route: str) -> str:
    current_dir = route_directory(current_route)
    target_dir = route_directory(target_route)
    relative = posixpath.relpath(target_dir, start=current_dir)
    return "./" if relative == "." else relative.rstrip("/") + "/"


def relative_file(current_route: str, target_file: str) -> str:
    current_dir = route_directory(current_route)
    return posixpath.relpath(target_file.lstrip("/"), start=current_dir)


def load_site_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(SITE_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_>~]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def render_excerpt(text: str, limit: int = 180) -> str:
    plain = strip_markdown(text)
    if len(plain) <= limit:
        return plain
    return plain[: limit - 1].rstrip() + "..."


def markdown_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["extra", "fenced_code", "tables", "toc", "sane_lists"],
        output_format="html5",
    )


def humanize_filename(path: Path) -> str:
    stem = path.stem
    cleaned = re.sub(r"^[0-9]+[a-z]*-", "", stem)
    cleaned = cleaned.replace("-", " ").replace("_", " ").strip()
    return cleaned.title() if cleaned else path.name


def section_route_segment(path: Path) -> str:
    raw_parts = path.with_suffix("").parts
    cleaned_parts = [slugify(part) or "section" for part in raw_parts]
    return "/".join(cleaned_parts)


def extract_heading(content: str) -> str | None:
    match = re.search(r"^#\s+(.+?)\s*$", content, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def remove_first_h1(content: str) -> str:
    return re.sub(r"^\s*#\s+.+?\n+", "", content, count=1, flags=re.MULTILINE).strip()


def source_root(publication: Dict[str, Any]) -> Path | None:
    if not publication.get("source"):
        return None
    return resolve_manifest_path(publication, publication["source"])


def source_display_path(publication: Dict[str, Any], path: Path) -> Path:
    root = source_root(publication)
    if root and root.exists() and root.is_dir():
        return path.relative_to(root)
    return Path(path.name)


def resolve_sections(publication: Dict[str, Any]) -> List[Dict[str, Any]]:
    paths = resolve_source_paths(publication)
    multi_file = len(paths) > 1
    sections: List[Dict[str, Any]] = []

    for index, path in enumerate(paths, start=1):
        raw = path.read_text(encoding="utf-8").strip()
        display_path = source_display_path(publication, path)
        title = extract_heading(raw) or humanize_filename(display_path)
        anchor = slugify(display_path.with_suffix("").as_posix().replace("/", "-")) or f"section-{index}"
        route_segment = section_route_segment(display_path)
        section_markdown = remove_first_h1(raw) if multi_file and extract_heading(raw) else raw
        if not section_markdown.strip():
            section_markdown = raw
        sections.append(
            {
                "index": index,
                "path": display_path.as_posix(),
                "title": title,
                "anchor": anchor,
                "route_segment": route_segment,
                "route": extend_route(publication["_route"], route_segment),
                "markdown": section_markdown,
                "html": markdown_to_html(section_markdown),
                "excerpt": render_excerpt(raw),
                "word_count": len(strip_markdown(raw).split()),
            }
        )

    for index, section in enumerate(sections):
        previous_section = sections[index - 1] if index > 0 else None
        next_section = sections[index + 1] if index + 1 < len(sections) else None
        section["previous_section"] = (
            {
                "title": previous_section["title"],
                "anchor": previous_section["anchor"],
                "route": previous_section["route"],
                "route_segment": previous_section["route_segment"],
            }
            if previous_section
            else None
        )
        section["next_section"] = (
            {
                "title": next_section["title"],
                "anchor": next_section["anchor"],
                "route": next_section["route"],
                "route_segment": next_section["route_segment"],
            }
            if next_section
            else None
        )

    return sections


def assemble_markdown(publication: Dict[str, Any]) -> str:
    parts: List[str] = []
    for path in resolve_source_paths(publication):
        content = path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)
    return "\n\n".join(parts).strip() + "\n"


def assemble_pandoc_markdown(publication: Dict[str, Any]) -> str:
    paths = resolve_source_paths(publication)
    parts: List[str] = []
    for path in paths:
        content = path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)

    if publication.get("kind") not in {"book", "collection"} or len(parts) <= 1:
        return "\n\n".join(parts).strip() + "\n"

    page_break = "\n\n\\newpage\n\n<div style=\"page-break-after: always;\"></div>\n\n"
    return page_break.join(parts).strip() + "\n"


def publication_word_count(publication: Dict[str, Any]) -> int:
    return len(strip_markdown(assemble_markdown(publication)).split())


def build_download_filename(publication: Dict[str, Any], extension: str) -> str:
    return f"{publication['slug']}.{extension}"


def default_downloadable(kind: str, formats: List[str]) -> bool:
    if kind == "fragment":
        return False
    return "markdown" in formats


def validate_site_config(site_config: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    config_label = str(site_config.get("_config_path", SITE_CONFIG_PATH))

    if not site_config.get("_exists", False):
        errors.append(f"{config_label}: site config file is missing")
        return errors

    for field in SITE_CONFIG_REQUIRED_FIELDS:
        if field not in site_config:
            errors.append(f"{config_label}: missing required field '{field}'")

    if site_config.get("base_url") and not isinstance(site_config["base_url"], str):
        errors.append(f"{config_label}: base_url must be a string")

    nav_links = site_config.get("nav_links")
    if "nav_links" in site_config:
        if not isinstance(nav_links, list) or not nav_links:
            errors.append(f"{config_label}: nav_links must be a non-empty list")
        else:
            for index, link in enumerate(nav_links, start=1):
                if not isinstance(link, dict):
                    errors.append(f"{config_label}: nav_links[{index}] must be an object")
                    continue
                if not link.get("label"):
                    errors.append(f"{config_label}: nav_links[{index}] is missing 'label'")
                if not link.get("route") and not link.get("href"):
                    errors.append(f"{config_label}: nav_links[{index}] must define 'route' or 'href'")
                route = link.get("route")
                if route and normalize_route(route, "", "") != route:
                    errors.append(f"{config_label}: nav_links[{index}] route should begin and end with '/'")

    return errors


def validate_reading_paths(reading_paths: List[Dict[str, Any]], publications: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    publication_ids = {publication.get("id") for publication in publications}
    id_to_manifest: Dict[str, str] = {}
    slug_to_manifest: Dict[str, str] = {}

    required_fields = ("id", "title", "slug", "description", "status", "items")
    for reading_path in reading_paths:
        manifest_label = str(reading_path["_manifest_path"].relative_to(ROOT))

        for field in required_fields:
            if field not in reading_path:
                errors.append(f"{manifest_label}: missing required field '{field}'")

        path_id = reading_path.get("id")
        if path_id:
            if not isinstance(path_id, str) or slugify(path_id) != path_id:
                errors.append(f"{manifest_label}: id '{path_id}' should use lowercase letters, numbers, and dashes only")
            other_manifest = id_to_manifest.get(path_id)
            if other_manifest:
                errors.append(f"{manifest_label}: duplicate reading path id '{path_id}' also used by {other_manifest}")
            id_to_manifest[path_id] = manifest_label

        slug = reading_path.get("slug")
        if slug:
            if not isinstance(slug, str) or slugify(slug) != slug:
                errors.append(f"{manifest_label}: slug '{slug}' should use lowercase letters, numbers, and dashes only")
            other_manifest = slug_to_manifest.get(slug)
            if other_manifest:
                errors.append(f"{manifest_label}: duplicate reading path slug '{slug}' also used by {other_manifest}")
            slug_to_manifest[slug] = manifest_label

        status = reading_path.get("status")
        if "status" not in reading_path:
            errors.append(f"{manifest_label}: missing required field 'status'")
        elif status not in SUPPORTED_STATUSES:
            expected_statuses = ", ".join(SUPPORTED_STATUSES)
            errors.append(f"{manifest_label}: invalid status '{status}' (expected one of: {expected_statuses})")

        title = reading_path.get("title")
        if "title" in reading_path and (not isinstance(title, str) or not title.strip()):
            errors.append(f"{manifest_label}: title must be a non-empty string")

        description = reading_path.get("description")
        if "description" in reading_path and (not isinstance(description, str) or not description.strip()):
            errors.append(f"{manifest_label}: description must be a non-empty string")

        tags = reading_path.get("tags", [])
        if tags and (not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags)):
            errors.append(f"{manifest_label}: tags must be a list of strings")

        items = reading_path.get("items")
        if "items" in reading_path:
            if not isinstance(items, list) or not items:
                errors.append(f"{manifest_label}: items must be a non-empty list")
            else:
                seen_items: set[str] = set()
                for item_id in items:
                    if not isinstance(item_id, str):
                        errors.append(f"{manifest_label}: each item id must be a string")
                        continue
                    if item_id in seen_items:
                        errors.append(f"{manifest_label}: duplicate item id '{item_id}' in items")
                    seen_items.add(item_id)
                    if item_id not in publication_ids:
                        errors.append(f"{manifest_label}: item reference '{item_id}' does not match a known publication id")

    return errors


def validate_concepts(concepts: List[Dict[str, Any]], publications: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    publication_ids = {publication.get("id") for publication in publications}
    concept_ids = {concept.get("id") for concept in concepts}
    id_to_manifest: Dict[str, str] = {}
    slug_to_manifest: Dict[str, str] = {}

    required_fields = (
        "id",
        "title",
        "slug",
        "short_definition",
        "description",
        "status",
        "related_concepts",
        "publications",
    )
    for concept in concepts:
        manifest_label = str(concept["_manifest_path"].relative_to(ROOT))

        for field in required_fields:
            if field not in concept:
                errors.append(f"{manifest_label}: missing required field '{field}'")

        concept_id = concept.get("id")
        if concept_id:
            if not isinstance(concept_id, str) or slugify(concept_id) != concept_id:
                errors.append(f"{manifest_label}: id '{concept_id}' should use lowercase letters, numbers, and dashes only")
            other_manifest = id_to_manifest.get(concept_id)
            if other_manifest:
                errors.append(f"{manifest_label}: duplicate concept id '{concept_id}' also used by {other_manifest}")
            id_to_manifest[concept_id] = manifest_label

        slug = concept.get("slug")
        if slug:
            if not isinstance(slug, str) or slugify(slug) != slug:
                errors.append(f"{manifest_label}: slug '{slug}' should use lowercase letters, numbers, and dashes only")
            other_manifest = slug_to_manifest.get(slug)
            if other_manifest:
                errors.append(f"{manifest_label}: duplicate concept slug '{slug}' also used by {other_manifest}")
            slug_to_manifest[slug] = manifest_label

        status = concept.get("status")
        if "status" not in concept:
            errors.append(f"{manifest_label}: missing required field 'status'")
        elif status not in SUPPORTED_STATUSES:
            expected_statuses = ", ".join(SUPPORTED_STATUSES)
            errors.append(f"{manifest_label}: invalid status '{status}' (expected one of: {expected_statuses})")

        for field in ("title", "short_definition", "description"):
            value = concept.get(field)
            if field in concept and (not isinstance(value, str) or not value.strip()):
                errors.append(f"{manifest_label}: {field} must be a non-empty string")

        tags = concept.get("tags", [])
        if tags and (not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags)):
            errors.append(f"{manifest_label}: tags must be a list of strings")

        related_concepts = concept.get("related_concepts", [])
        if "related_concepts" in concept:
            if not isinstance(related_concepts, list):
                errors.append(f"{manifest_label}: related_concepts must be a list")
            else:
                seen_related: set[str] = set()
                for related_id in related_concepts:
                    if not isinstance(related_id, str):
                        errors.append(f"{manifest_label}: each related concept id must be a string")
                        continue
                    if related_id in seen_related:
                        errors.append(f"{manifest_label}: duplicate related concept id '{related_id}' in related_concepts")
                    seen_related.add(related_id)
                    if related_id == concept_id:
                        errors.append(f"{manifest_label}: concept cannot reference itself in related_concepts")
                    if related_id not in concept_ids:
                        errors.append(f"{manifest_label}: related_concepts reference '{related_id}' does not match a known concept id")

        concept_publications = concept.get("publications", [])
        if "publications" in concept:
            if not isinstance(concept_publications, list):
                errors.append(f"{manifest_label}: publications must be a list")
            else:
                seen_publications: set[str] = set()
                for publication_id in concept_publications:
                    if not isinstance(publication_id, str):
                        errors.append(f"{manifest_label}: each publication id must be a string")
                        continue
                    if publication_id in seen_publications:
                        errors.append(f"{manifest_label}: duplicate publication id '{publication_id}' in publications")
                    seen_publications.add(publication_id)
                    if publication_id not in publication_ids:
                        errors.append(f"{manifest_label}: publications reference '{publication_id}' does not match a known publication id")

    return errors


def validate_publications(
    publications: List[Dict[str, Any]],
    site_config: Dict[str, Any] | None = None,
    reading_paths: List[Dict[str, Any]] | None = None,
    concepts: List[Dict[str, Any]] | None = None,
) -> List[str]:
    schema = load_schema()
    required = schema.get("required", [])
    site_config = site_config or load_site_config()
    errors = validate_site_config(site_config)

    id_to_publication: Dict[str, Dict[str, Any]] = {}
    id_to_manifest: Dict[str, str] = {}
    route_to_id: Dict[str, str] = {}
    slug_to_id: Dict[str, str] = {}

    for publication in publications:
        manifest_label = str(publication["_manifest_path"].relative_to(ROOT))
        publication_id = str(publication.get("id", manifest_label))

        for field in required:
            if field not in publication and field != "status":
                errors.append(f"{manifest_label}: missing required field '{field}'")

        kind = publication.get("kind")
        if kind not in SUPPORTED_KINDS:
            errors.append(
                f"{manifest_label}: invalid kind '{kind}' (expected one of: {', '.join(SUPPORTED_KINDS)})"
            )

        slug = publication.get("slug")
        if slug and slugify(slug) != slug:
            errors.append(f"{manifest_label}: slug '{slug}' should use lowercase letters, numbers, and dashes only")

        publication_id_value = publication.get("id")
        if publication_id_value:
            other_manifest = id_to_manifest.get(publication_id_value)
            if other_manifest:
                errors.append(
                    f"{manifest_label}: duplicate publication id '{publication_id_value}' also used by {other_manifest}"
                )
            id_to_manifest[publication_id_value] = manifest_label
            id_to_publication[publication_id_value] = publication

        if slug:
            other_slug_owner = slug_to_id.get(slug)
            if other_slug_owner and other_slug_owner != publication_id:
                errors.append(f"{manifest_label}: duplicate slug '{slug}' already used by {other_slug_owner}")
            slug_to_id[slug] = publication_id

        route = publication["_route"]
        other_route_owner = route_to_id.get(route)
        if other_route_owner and other_route_owner != publication_id:
            errors.append(f"{manifest_label}: web route '{route}' already used by {other_route_owner}")
        route_to_id[route] = publication_id

        if publication.get("web_route") and publication["_route"] != publication["web_route"]:
            errors.append(f"{manifest_label}: web_route should begin and end with '/'")

        output_formats = publication.get("output_formats", [])
        if not isinstance(output_formats, list) or not output_formats:
            errors.append(f"{manifest_label}: output_formats must be a non-empty list")
        else:
            for fmt in output_formats:
                if fmt not in SUPPORTED_OUTPUT_FORMATS:
                    errors.append(
                        f"{manifest_label}: unsupported output format '{fmt}' (expected one of: {', '.join(SUPPORTED_OUTPUT_FORMATS)})"
                    )

        tags = publication.get("tags", [])
        if tags and (not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags)):
            errors.append(f"{manifest_label}: tags must be a list of strings")

        relationships = publication.get("relationships")
        if relationships is not None:
            if not isinstance(relationships, dict):
                errors.append(f"{manifest_label}: relationships must be an object")
            else:
                for relationship_key, relationship_value in relationships.items():
                    if relationship_key not in PUBLICATION_RELATIONSHIP_KEYS:
                        expected_keys = ", ".join(PUBLICATION_RELATIONSHIP_KEYS)
                        errors.append(
                            f"{manifest_label}: unsupported relationship key '{relationship_key}' "
                            f"(expected one of: {expected_keys})"
                        )
                        continue
                    if not isinstance(relationship_value, list):
                        errors.append(f"{manifest_label}: relationships.{relationship_key} must be a list")
                    elif not all(isinstance(item, str) for item in relationship_value):
                        errors.append(f"{manifest_label}: relationships.{relationship_key} must contain publication id strings")

        if not publication.get("source") and not publication.get("sources"):
            errors.append(f"{manifest_label}: at least one of 'source' or 'sources' is required")

        if publication.get("source"):
            source_path = resolve_manifest_path(publication, publication["source"])
            if not source_path.exists():
                errors.append(f"{manifest_label}: source path does not exist: {publication['source']}")

        if publication.get("sources") and not isinstance(publication["sources"], list):
            errors.append(f"{manifest_label}: sources must be a list when provided")
        elif publication.get("sources"):
            for entry in publication["sources"]:
                if not isinstance(entry, str):
                    errors.append(f"{manifest_label}: each entry in sources must be a string")
                    continue
                entry_path = Path(entry)
                current_source_root = source_root(publication)
                if current_source_root and current_source_root.exists() and current_source_root.is_dir() and not entry_path.is_absolute():
                    candidate = (current_source_root / entry_path).resolve()
                else:
                    candidate = resolve_manifest_path(publication, entry)
                if not candidate.exists():
                    errors.append(f"{manifest_label}: referenced source path does not exist: {entry}")

        try:
            resolved_sources = resolve_source_paths(publication)
        except Exception as exc:  # pragma: no cover
            errors.append(f"{manifest_label}: could not resolve sources ({exc})")
            resolved_sources = []

        if not resolved_sources:
            errors.append(f"{manifest_label}: no Markdown source files were resolved")
        elif not all(path.suffix.lower() == ".md" for path in resolved_sources):
            errors.append(f"{manifest_label}: all resolved sources must be Markdown files")

        members = publication.get("members")
        if members is not None:
            if publication.get("kind") not in {"series", "collection"}:
                errors.append(f"{manifest_label}: only series and collection manifests may define members")
            elif not isinstance(members, list):
                errors.append(f"{manifest_label}: members must be a list when provided")
            else:
                seen_members: set[str] = set()
                for member_id in members:
                    if not isinstance(member_id, str):
                        errors.append(f"{manifest_label}: each member id must be a string")
                        continue
                    if member_id == publication_id_value:
                        errors.append(f"{manifest_label}: a publication cannot include itself as a member")
                    if member_id in seen_members:
                        errors.append(f"{manifest_label}: duplicate member id '{member_id}' in members")
                    seen_members.add(member_id)

    for publication in publications:
        manifest_label = str(publication["_manifest_path"].relative_to(ROOT))
        publication_id = str(publication.get("id", manifest_label))

        members = publication.get("members", [])
        if isinstance(members, list):
            for member_id in members:
                member = id_to_publication.get(member_id)
                if not member:
                    errors.append(f"{manifest_label}: member reference '{member_id}' does not match a known publication id")

        for relation_kind in RELATIONSHIP_KINDS:
            parent_id = publication.get(relation_kind)
            if not parent_id:
                continue
            parent = id_to_publication.get(parent_id)
            if not parent:
                errors.append(f"{manifest_label}: {relation_kind} reference '{parent_id}' does not match a known publication id")
                continue
            if parent.get("kind") != relation_kind:
                errors.append(
                    f"{manifest_label}: {relation_kind} reference '{parent_id}' points to a {parent.get('kind')} manifest"
                )
            if parent_id == publication_id:
                errors.append(f"{manifest_label}: a publication cannot reference itself as its own {relation_kind}")

        relationships = publication.get("relationships")
        if isinstance(relationships, dict):
            for relationship_key, relationship_value in relationships.items():
                if relationship_key not in PUBLICATION_RELATIONSHIP_KEYS or not isinstance(relationship_value, list):
                    continue
                seen_related_publications: set[str] = set()
                for related_publication_id in relationship_value:
                    if not isinstance(related_publication_id, str):
                        continue
                    if related_publication_id == publication_id:
                        errors.append(
                            f"{manifest_label}: relationships.{relationship_key} cannot reference itself "
                            f"('{related_publication_id}')"
                        )
                    if related_publication_id in seen_related_publications:
                        errors.append(
                            f"{manifest_label}: duplicate relationships.{relationship_key} reference "
                            f"'{related_publication_id}'"
                        )
                    seen_related_publications.add(related_publication_id)
                    if related_publication_id not in id_to_publication:
                        errors.append(
                            f"{manifest_label}: relationships.{relationship_key} reference "
                            f"'{related_publication_id}' does not match a known publication id"
                        )

        status = publication.get("status")
        if "status" not in publication:
            errors.append(f"{manifest_label}: missing required field 'status'")
        elif status not in SUPPORTED_STATUSES:
            expected_statuses = ", ".join(SUPPORTED_STATUSES)
            errors.append(
                f"{manifest_label}: invalid status '{status}' (expected one of: {expected_statuses})"
            )

    if reading_paths is not None:
        errors.extend(validate_reading_paths(reading_paths, publications))
    if concepts is not None:
        errors.extend(validate_concepts(concepts, publications))

    return errors


def sort_publications(publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        publications,
        key=lambda item: (
            str(item.get("date", "")),
            str(item.get("updated", "")),
            -float(item.get("order", 0)),
            item.get("title", ""),
        ),
        reverse=True,
    )


def build_publication_context(publication: Dict[str, Any]) -> Dict[str, Any]:
    markdown_body = assemble_markdown(publication)
    sections = resolve_sections(publication)
    multi_file = len(sections) > 1
    single_file_body = remove_first_h1(markdown_body) if extract_heading(markdown_body) else markdown_body
    return {
        **publication,
        "body_markdown": markdown_body,
        "body_html": markdown_to_html(single_file_body),
        "excerpt": render_excerpt(markdown_body),
        "word_count": publication_word_count(publication),
        "status_label": status_label(publication.get("status", "")),
        "is_public": publication_is_public(publication),
        "sections": sections,
        "section_count": len(sections),
        "multi_file": multi_file,
        "toc": [{"anchor": section["anchor"], "title": section["title"]} for section in sections] if multi_file else [],
        "downloads": [],
        "member_publications": [],
        "series_memberships": [],
        "collection_memberships": [],
        "relationship_groups": [],
        "inverse_relationship_groups": [],
    }


def dedupe_publications(publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[str] = set()
    ordered: List[Dict[str, Any]] = []
    for publication in publications:
        publication_id = publication["id"]
        if publication_id not in seen:
            ordered.append(publication)
            seen.add(publication_id)
    return ordered


def build_publication_contexts(publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    contexts = [build_publication_context(publication) for publication in publications]
    by_id = {context["id"]: context for context in contexts}

    for context in contexts:
        parent_members = context.get("members", [])
        if context["kind"] in {"series", "collection"} and isinstance(parent_members, list):
            for member_id in parent_members:
                member = by_id.get(member_id)
                if not member:
                    continue
                context["member_publications"].append(member)
                if context["kind"] == "series":
                    member["series_memberships"].append(context)
                else:
                    member["collection_memberships"].append(context)

    for context in contexts:
        for relation_kind in RELATIONSHIP_KINDS:
            parent_id = context.get(relation_kind)
            if not parent_id:
                continue
            parent = by_id.get(parent_id)
            if not parent:
                continue
            parent["member_publications"].append(context)
            if relation_kind == "series":
                context["series_memberships"].append(parent)
            else:
                context["collection_memberships"].append(parent)

    for context in contexts:
        context["member_publications"] = dedupe_publications(context["member_publications"])
        context["series_memberships"] = dedupe_publications(context["series_memberships"])
        context["collection_memberships"] = dedupe_publications(context["collection_memberships"])

    return contexts


def find_publication(publication_id: str, publications: List[Dict[str, Any]]) -> Dict[str, Any]:
    for publication in publications:
        if publication.get("id") == publication_id:
            return publication
    raise KeyError(f"Unknown publication id: {publication_id}")


def pandoc_available() -> bool:
    return shutil.which("pandoc") is not None


def pandoc_defaults_path(kind: str) -> Path | None:
    candidate = SITE_PANDOC_DEFAULTS_DIR / f"{kind}.yaml"
    if candidate.exists():
        return candidate
    return None


def pandoc_metadata_args(publication: Dict[str, Any], site_config: Dict[str, Any] | None) -> List[str]:
    metadata: Dict[str, str] = {
        "title": publication["title"],
        "author": publication["author"],
        "description": publication.get("description", ""),
    }
    if publication.get("subtitle"):
        metadata["subtitle"] = publication["subtitle"]
    if publication.get("date"):
        metadata["date"] = publication["date"]
    elif publication.get("created"):
        metadata["date"] = publication["created"]
    if publication.get("updated"):
        metadata["updated"] = publication["updated"]
    if publication.get("tags"):
        metadata["keywords"] = ", ".join(publication["tags"])
    if site_config and site_config.get("language"):
        metadata["lang"] = site_config["language"]

    args: List[str] = []
    for key, value in metadata.items():
        if value:
            args.extend(["--metadata", f"{key}={value}"])
    return args


def copy_source_markdown(publication: Dict[str, Any], destination_root: Path) -> List[Path]:
    copied: List[Path] = []
    bundle_root = destination_root / "source" / publication["slug"]
    root = source_root(publication)

    for source_path in resolve_source_paths(publication):
        if root and root.exists() and root.is_dir():
            relative_name = source_path.relative_to(root)
        else:
            relative_name = Path(source_path.name)
        destination = bundle_root / relative_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        copied.append(destination)
    return copied


def export_publication_downloads(
    publication: Dict[str, Any],
    site_root: Path,
    site_config: Dict[str, Any] | None = None,
) -> Tuple[List[Dict[str, str]], List[str]]:
    if not publication.get("downloadable", False):
        return [], []

    warnings: List[str] = []
    links: List[Dict[str, str]] = []
    downloads_dir = site_root / "downloads" / publication["_section"]
    downloads_dir.mkdir(parents=True, exist_ok=True)

    markdown_output = downloads_dir / build_download_filename(publication, "md")
    markdown_output.write_text(assemble_markdown(publication), encoding="utf-8")
    pandoc_input = downloads_dir / f"{publication['slug']}.pandoc.md"
    pandoc_input.write_text(assemble_pandoc_markdown(publication), encoding="utf-8")
    copy_source_markdown(publication, site_root / "downloads")
    links.append(
        {
            "label": "Markdown",
            "filename": markdown_output.name,
            "href": f"downloads/{publication['_section']}/{markdown_output.name}",
        }
    )

    requested = [fmt for fmt in publication.get("output_formats", []) if fmt in PANDOC_OUTPUT_FORMATS]
    if not requested:
        if pandoc_input.exists():
            pandoc_input.unlink()
        return links, warnings

    if not pandoc_available():
        warnings.append(f"{publication['id']}: pandoc is not available, skipped {', '.join(requested)} export")
        if pandoc_input.exists():
            pandoc_input.unlink()
        return links, warnings

    for fmt in requested:
        output_path = downloads_dir / build_download_filename(publication, fmt)
        defaults_path = pandoc_defaults_path(publication["kind"])
        command = [
            "pandoc",
            str(pandoc_input),
        ]
        if defaults_path:
            command.extend(["--defaults", str(defaults_path)])
        else:
            command.extend(["--from", "markdown", "--standalone"])
        command.extend(
            [
            "--output",
            str(output_path),
            ]
        )
        command.extend(pandoc_metadata_args(publication, site_config))
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except OSError as exc:
            warnings.append(f"{publication['id']}: failed to invoke pandoc for {fmt} ({exc})")
            continue
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown pandoc error"
            warnings.append(f"{publication['id']}: pandoc could not create {fmt} ({detail})")
            continue
        links.append(
            {
                "label": fmt.upper(),
                "filename": output_path.name,
                "href": f"downloads/{publication['_section']}/{output_path.name}",
            }
        )

    if pandoc_input.exists():
        pandoc_input.unlink()

    return links, warnings


def print_errors(errors: List[str]) -> None:
    for error in errors:
        print(f"- {error}", file=sys.stderr)
