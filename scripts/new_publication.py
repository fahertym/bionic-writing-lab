from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from publication_lib import (
    DEFAULT_OUTPUT_FORMATS,
    FOLDER_KINDS,
    KIND_TO_SECTION,
    ROOT,
    SINGLE_FILE_KINDS,
    SUPPORTED_KINDS,
    SUPPORTED_STATUSES,
    default_downloadable,
    load_publications,
    load_site_config,
    parse_csv,
    slugify,
    validate_output_formats,
    validate_publications,
)


STARTER_FILES = {
    "book": "00-introduction.md",
    "collection": "README.md",
    "series": "README.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Markdown source and manifest for a new publication.")
    parser.add_argument("--kind", required=True, choices=SUPPORTED_KINDS, help="Publication kind")
    parser.add_argument("--title", required=True, help="Publication title")
    parser.add_argument("--subtitle", help="Optional subtitle")
    parser.add_argument("--description", help="Optional manifest description")
    parser.add_argument("--slug", help="Optional slug override; defaults to a slugified title")
    parser.add_argument("--author", help="Optional author override; defaults to site/site.json author")
    parser.add_argument("--status", default="draft", help="Publication status; defaults to draft")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument(
        "--formats",
        help="Comma-separated output formats; defaults by publication kind",
    )
    return parser.parse_args()


def publication_paths(kind: str, slug: str) -> tuple[Path, str, list[str] | None]:
    section = KIND_TO_SECTION[kind]
    if kind in SINGLE_FILE_KINDS:
        source_path = ROOT / "content" / section / f"{slug}.md"
        return source_path, source_path.relative_to(ROOT).as_posix(), None

    if kind not in FOLDER_KINDS:
        raise ValueError(f"Unsupported publication kind: {kind}")
    starter_file = STARTER_FILES[kind]
    source_dir = ROOT / "content" / section / slug
    source_path = source_dir / starter_file
    return source_path, source_dir.relative_to(ROOT).as_posix(), [starter_file]


def manifest_path(slug: str) -> Path:
    return ROOT / "publications" / f"{slug}.json"


def ensure_available(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if path.exists():
            errors.append(f"refusing to overwrite existing path: {path}")
    return errors


def starter_markdown(title: str, kind: str) -> str:
    if kind == "book":
        return f"# Introduction\n\nBegin {title} here.\n"
    return f"# {title}\n\nBegin drafting here.\n"


def build_manifest(args: argparse.Namespace, source: str, sources: list[str] | None) -> dict[str, Any]:
    site_config = load_site_config()
    slug = args.slug or slugify(args.title)
    today = date.today().isoformat()
    tags = parse_csv(args.tags)
    formats = parse_csv(args.formats) if args.formats else DEFAULT_OUTPUT_FORMATS[args.kind]

    manifest: dict[str, Any] = {
        "id": slug,
        "title": args.title,
        "author": args.author or site_config.get("author", ""),
        "kind": args.kind,
        "slug": slug,
        "description": args.description or f"Draft {args.kind} publication.",
        "status": args.status,
        "tags": tags,
        "source": source,
        "web_route": f"/{KIND_TO_SECTION[args.kind]}/{slug}/",
        "output_formats": formats,
        "downloadable": default_downloadable(args.kind, formats),
        "order": 0,
        "date": today,
        "updated": today,
    }
    if args.subtitle:
        manifest["subtitle"] = args.subtitle
    if sources:
        manifest["sources"] = sources
    return manifest


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    slug = args.slug or slugify(args.title)
    if not slug:
        print("Could not generate a slug from the title. Provide --slug.", file=sys.stderr)
        return 1
    if slugify(slug) != slug:
        print(f"Slug must use lowercase letters, numbers, and dashes only: {slug}", file=sys.stderr)
        return 1
    if args.status not in SUPPORTED_STATUSES:
        expected_statuses = ", ".join(SUPPORTED_STATUSES)
        print(f"Unsupported status '{args.status}' (expected one of: {expected_statuses})", file=sys.stderr)
        return 1
    formats = parse_csv(args.formats) if args.formats else DEFAULT_OUTPUT_FORMATS[args.kind]
    format_errors = validate_output_formats(formats)
    if format_errors:
        for error in format_errors:
            print(error, file=sys.stderr)
        return 1

    content_path, source, sources = publication_paths(args.kind, slug)
    new_manifest_path = manifest_path(slug)
    errors = ensure_available([content_path, new_manifest_path])
    if content_path.parent.exists() and content_path.parent.is_file():
        errors.append(f"content parent is a file: {content_path.parent}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    manifest = build_manifest(args, source, sources)

    content_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_text(starter_markdown(args.title, args.kind), encoding="utf-8")
    write_manifest(new_manifest_path, manifest)

    publications = load_publications()
    validation_errors = validate_publications(publications, load_site_config())
    if validation_errors:
        print("Created files, but validation failed:", file=sys.stderr)
        for error in validation_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Created {args.kind} publication '{args.title}'")
    print(f"- Markdown: {content_path.relative_to(ROOT)}")
    print(f"- Manifest: {new_manifest_path.relative_to(ROOT)}")
    print(f"- Route: {manifest['web_route']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
