from __future__ import annotations

import json
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
SCHEMA_PATH = ROOT / "schema" / "publication.schema.json"
SITE_DIR = ROOT / "site"
SITE_TEMPLATES_DIR = SITE_DIR / "templates"
SITE_ASSETS_DIR = SITE_DIR / "assets"
DIST_DIR = ROOT / "dist"
DIST_SITE_DIR = DIST_DIR / "site"
DIST_BUILD_DIR = DIST_DIR / "build"

SUPPORTED_KINDS = (
    "book",
    "series",
    "essay",
    "poem",
    "post",
    "pamphlet",
    "collection",
)
SUPPORTED_OUTPUT_FORMATS = ("site", "markdown", "pdf", "epub", "docx")
PANDOC_OUTPUT_FORMATS = ("pdf", "epub", "docx")
KIND_TO_SECTION = {
    "book": "books",
    "series": "series",
    "essay": "essays",
    "poem": "poems",
    "post": "posts",
    "pamphlet": "pamphlets",
    "collection": "collections",
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_manifest_paths() -> List[Path]:
    return sorted(PUBLICATIONS_DIR.glob("*.json"))


def load_schema() -> Dict[str, Any]:
    return load_json(SCHEMA_PATH)


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


def normalize_route(route: str | None, kind: str, slug: str) -> str:
    if route:
        normalized = "/" + route.strip("/") + "/"
    else:
        section = KIND_TO_SECTION.get(kind, "writing")
        normalized = f"/{section}/{slug}/"
    return normalized


def resolve_manifest_path(publication: Dict[str, Any], reference: str) -> Path:
    candidate = (ROOT / reference).resolve()
    if candidate.exists():
        return candidate
    manifest_relative = (publication["_manifest_path"].parent / reference).resolve()
    return manifest_relative


def expand_markdown_paths(path: Path) -> List[Path]:
    if path.is_file():
        return [path]
    return sorted(child for child in path.rglob("*.md") if child.is_file())


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


def dedupe_paths(paths: Iterable[Path]) -> List[Path]:
    seen: set[Path] = set()
    ordered: List[Path] = []
    for path in paths:
        if path not in seen:
            ordered.append(path)
            seen.add(path)
    return ordered


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")


def validate_publications(publications: List[Dict[str, Any]]) -> List[str]:
    schema = load_schema()
    required = schema.get("required", [])
    id_to_manifest: Dict[str, str] = {}
    route_to_id: Dict[str, str] = {}
    slug_to_id: Dict[str, str] = {}
    errors: List[str] = []

    for publication in publications:
        manifest_label = publication["_manifest_path"].name
        publication_id = str(publication.get("id", manifest_label))

        for field in required:
            if field not in publication:
                errors.append(f"{manifest_label}: missing required field '{field}'")

        kind = publication.get("kind")
        if kind not in SUPPORTED_KINDS:
            errors.append(
                f"{manifest_label}: invalid kind '{kind}' (expected one of: {', '.join(SUPPORTED_KINDS)})"
            )

        slug = publication.get("slug")
        if slug and slugify(slug) != slug:
            errors.append(f"{manifest_label}: slug '{slug}' should use lowercase letters, numbers, and dashes only")

        if publication.get("id"):
            other_manifest = id_to_manifest.get(publication["id"])
            if other_manifest:
                errors.append(f"{manifest_label}: duplicate publication id '{publication['id']}' also used by {other_manifest}")
            id_to_manifest[publication["id"]] = manifest_label

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

        if not publication.get("source") and not publication.get("sources"):
            errors.append(f"{manifest_label}: at least one of 'source' or 'sources' is required")

        source_value = publication.get("source")
        if source_value:
            source_path = resolve_manifest_path(publication, source_value)
            if not source_path.exists():
                errors.append(f"{manifest_label}: source path does not exist: {source_value}")

        if publication.get("sources"):
            for entry in publication["sources"]:
                entry_path = Path(entry)
                if source_value:
                    source_root = resolve_manifest_path(publication, source_value)
                else:
                    source_root = None
                if source_root and source_root.exists() and source_root.is_dir() and not entry_path.is_absolute():
                    candidate = (source_root / entry_path).resolve()
                else:
                    candidate = resolve_manifest_path(publication, entry)
                if not candidate.exists():
                    errors.append(f"{manifest_label}: referenced source path does not exist: {entry}")

        try:
            resolved_sources = resolve_source_paths(publication)
        except Exception as exc:  # pragma: no cover - defensive branch
            errors.append(f"{manifest_label}: could not resolve sources ({exc})")
            resolved_sources = []

        if not resolved_sources:
            errors.append(f"{manifest_label}: no Markdown source files were resolved")
        elif not all(path.suffix.lower() == ".md" for path in resolved_sources):
            errors.append(f"{manifest_label}: all resolved sources must be Markdown files")

        if publication.get("web_route") and publication["_route"] != publication["web_route"]:
            errors.append(f"{manifest_label}: web_route should begin and end with '/'")

    return errors


def markdown_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["extra", "fenced_code", "tables", "toc", "sane_lists"],
        output_format="html5",
    )


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_>~-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def render_excerpt(text: str, limit: int = 180) -> str:
    plain = strip_markdown(text)
    if len(plain) <= limit:
        return plain
    return plain[: limit - 1].rstrip() + "…"


def assemble_markdown(publication: Dict[str, Any]) -> str:
    parts: List[str] = []
    for path in resolve_source_paths(publication):
        content = path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)
    return "\n\n".join(parts).strip() + "\n"


def publication_word_count(publication: Dict[str, Any]) -> int:
    return len(strip_markdown(assemble_markdown(publication)).split())


def build_download_filename(publication: Dict[str, Any], extension: str) -> str:
    return f"{publication['slug']}.{extension}"


def load_site_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(SITE_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


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


def relative_route(current_route: str, target_route: str) -> str:
    current_dir = route_directory(current_route)
    target_dir = route_directory(target_route)
    relative = posixpath.relpath(target_dir, start=current_dir)
    return "./" if relative == "." else relative.rstrip("/") + "/"


def relative_file(current_route: str, target_file: str) -> str:
    current_dir = route_directory(current_route)
    relative = posixpath.relpath(target_file.lstrip("/"), start=current_dir)
    return relative


def build_publication_context(publication: Dict[str, Any]) -> Dict[str, Any]:
    markdown_body = assemble_markdown(publication)
    return {
        **publication,
        "body_markdown": markdown_body,
        "body_html": markdown_to_html(markdown_body),
        "excerpt": render_excerpt(markdown_body),
        "word_count": publication_word_count(publication),
        "downloads": [],
    }


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


def kind_label(kind: str) -> str:
    return KIND_TO_SECTION[kind].replace("-", " ").title()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def find_publication(publication_id: str, publications: List[Dict[str, Any]]) -> Dict[str, Any]:
    for publication in publications:
        if publication.get("id") == publication_id:
            return publication
    raise KeyError(f"Unknown publication id: {publication_id}")


def pandoc_available() -> bool:
    return shutil.which("pandoc") is not None


def copy_source_markdown(publication: Dict[str, Any], destination_root: Path) -> List[Path]:
    copied: List[Path] = []
    bundle_root = destination_root / "source" / publication["slug"]
    source_root = resolve_manifest_path(publication, publication["source"]) if publication.get("source") else None

    for source_path in resolve_source_paths(publication):
        if source_root and source_root.exists() and source_root.is_dir():
            relative_name = source_path.relative_to(source_root)
        else:
            relative_name = Path(source_path.name)
        destination = bundle_root / relative_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        copied.append(destination)
    return copied


def export_publication_downloads(publication: Dict[str, Any], site_root: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    if not publication.get("downloadable", False):
        return [], []

    warnings: List[str] = []
    links: List[Dict[str, str]] = []
    downloads_dir = site_root / "downloads" / publication["_section"]
    downloads_dir.mkdir(parents=True, exist_ok=True)

    markdown_output = downloads_dir / build_download_filename(publication, "md")
    markdown_output.write_text(assemble_markdown(publication), encoding="utf-8")
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
        return links, warnings

    if not pandoc_available():
        warnings.append(
            f"{publication['id']}: pandoc is not available, skipped {', '.join(requested)} export"
        )
        return links, warnings

    for fmt in requested:
        output_path = downloads_dir / build_download_filename(publication, fmt)
        command = [
            "pandoc",
            str(markdown_output),
            "--from",
            "markdown",
            "--standalone",
            "--metadata",
            f"title={publication['title']}",
            "--metadata",
            f"author={publication['author']}",
            "--output",
            str(output_path),
        ]
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

    return links, warnings


def print_errors(errors: List[str]) -> None:
    for error in errors:
        print(f"- {error}", file=sys.stderr)

