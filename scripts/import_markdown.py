from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date, datetime
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


REPORTS_DIR = ROOT / "reports" / "imports"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely import existing Markdown into Bionic Writing Lab.")
    parser.add_argument("--source", required=True, type=Path, help="Markdown file or folder to import")
    parser.add_argument("--kind", required=True, choices=SUPPORTED_KINDS, help="Publication kind")
    parser.add_argument("--title", help="Optional publication title")
    parser.add_argument("--subtitle", help="Optional subtitle")
    parser.add_argument("--description", help="Optional manifest description")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--status", default="imported", help="Publication status; defaults to imported")
    parser.add_argument("--slug", help="Optional slug override; defaults to a slugified title")
    parser.add_argument("--author", help="Optional author override; defaults to site/site.json author")
    parser.add_argument("--formats", help="Comma-separated output formats; defaults by publication kind")
    parser.add_argument("--dry-run", action="store_true", help="Print the import plan without writing files")
    return parser.parse_args()


def title_from_path(path: Path) -> str:
    stem = path.stem if path.is_file() else path.name
    cleaned = stem.replace("-", " ").replace("_", " ").strip()
    return cleaned.title() if cleaned else "Imported Publication"


def manifest_path(slug: str) -> Path:
    return ROOT / "publications" / f"{slug}.json"


def collect_markdown_files(source: Path) -> tuple[list[Path], list[Path]]:
    if source.is_file():
        if source.suffix.lower() == ".md":
            return [source], []
        return [], [source]

    markdown_files: list[Path] = []
    skipped: list[Path] = []
    for path in sorted(child for child in source.rglob("*") if child.is_file()):
        if path.suffix.lower() == ".md":
            markdown_files.append(path)
        else:
            skipped.append(path)
    return markdown_files, skipped


def build_targets(kind: str, slug: str, source: Path, markdown_files: list[Path]) -> tuple[Path, str, list[str] | None, list[tuple[Path, Path]]]:
    section = KIND_TO_SECTION[kind]

    if kind in SINGLE_FILE_KINDS:
        if len(markdown_files) != 1:
            raise ValueError(f"{kind} imports require exactly one Markdown file; found {len(markdown_files)}")
        target_file = ROOT / "content" / section / f"{slug}.md"
        return target_file, target_file.relative_to(ROOT).as_posix(), None, [(markdown_files[0], target_file)]

    if kind not in FOLDER_KINDS:
        raise ValueError(f"Unsupported publication kind: {kind}")

    target_dir = ROOT / "content" / section / slug
    copies: list[tuple[Path, Path]] = []
    sources: list[str] = []
    for markdown_file in markdown_files:
        relative_name = markdown_file.name if source.is_file() else markdown_file.relative_to(source).as_posix()
        target_file = target_dir / relative_name
        copies.append((markdown_file, target_file))
        sources.append(Path(relative_name).as_posix())
    return target_dir, target_dir.relative_to(ROOT).as_posix(), sources, copies


def build_manifest(
    args: argparse.Namespace,
    *,
    title: str,
    slug: str,
    source: str,
    sources: list[str] | None,
) -> dict[str, Any]:
    site_config = load_site_config()
    today = date.today().isoformat()
    formats = parse_csv(args.formats) if args.formats else DEFAULT_OUTPUT_FORMATS[args.kind]

    manifest: dict[str, Any] = {
        "id": slug,
        "title": title,
        "author": args.author or site_config.get("author", ""),
        "kind": args.kind,
        "slug": slug,
        "description": args.description or f"Imported {args.kind} publication awaiting review.",
        "status": args.status,
        "tags": parse_csv(args.tags),
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


def preflight(args: argparse.Namespace) -> tuple[dict[str, Any], Path, Path, list[tuple[Path, Path]], list[Path], list[str]]:
    source = args.source.expanduser().resolve()
    errors: list[str] = []
    if not source.exists():
        errors.append(f"source path does not exist: {source}")
        return {}, Path(), Path(), [], [], errors

    if args.status not in SUPPORTED_STATUSES:
        expected_statuses = ", ".join(SUPPORTED_STATUSES)
        errors.append(f"unsupported status '{args.status}' (expected one of: {expected_statuses})")

    title = args.title or title_from_path(source)
    slug = args.slug or slugify(title)
    if not slug:
        errors.append("could not generate a slug from the title; provide --slug")
    elif slugify(slug) != slug:
        errors.append(f"slug must use lowercase letters, numbers, and dashes only: {slug}")

    formats = parse_csv(args.formats) if args.formats else DEFAULT_OUTPUT_FORMATS[args.kind]
    errors.extend(validate_output_formats(formats))

    markdown_files, skipped_files = collect_markdown_files(source)
    if not markdown_files:
        errors.append(f"no Markdown files found in source: {source}")

    if errors:
        return {}, Path(), Path(), [], skipped_files, errors

    try:
        content_target, manifest_source, sources, copies = build_targets(args.kind, slug, source, markdown_files)
    except ValueError as exc:
        return {}, Path(), Path(), [], skipped_files, [str(exc)]

    new_manifest_path = manifest_path(slug)
    if new_manifest_path.exists():
        errors.append(f"refusing to overwrite existing manifest: {new_manifest_path}")
    if args.kind in FOLDER_KINDS and content_target.exists():
        errors.append(f"refusing to overwrite existing content folder: {content_target}")
    for _, target_file in copies:
        if target_file.exists():
            errors.append(f"refusing to overwrite existing content file: {target_file}")

    manifest = build_manifest(args, title=title, slug=slug, source=manifest_source, sources=sources)
    return manifest, new_manifest_path, content_target, copies, skipped_files, errors


def report_payload(
    args: argparse.Namespace,
    manifest: dict[str, Any],
    manifest_path_value: Path,
    content_target: Path,
    copies: list[tuple[Path, Path]],
    skipped_files: list[Path],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_path": str(args.source.expanduser().resolve()),
        "target_content_path": str(content_target),
        "manifest_path": str(manifest_path_value),
        "publication_id": manifest["id"],
        "kind": manifest["kind"],
        "status": manifest["status"],
        "files_copied": [
            {"source": str(source), "target": str(target)}
            for source, target in copies
        ],
        "files_skipped": [str(path) for path in skipped_files],
        "warnings": warnings,
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_report(payload: dict[str, Any], slug: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = REPORTS_DIR / f"{timestamp}-{slug}.json"
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return report_path


def print_plan(
    *,
    dry_run: bool,
    manifest: dict[str, Any],
    manifest_path_value: Path,
    copies: list[tuple[Path, Path]],
    skipped_files: list[Path],
) -> None:
    prefix = "DRY RUN: would import" if dry_run else "Importing"
    print(f"{prefix} {manifest['kind']} publication '{manifest['title']}'")
    print(f"- Publication id: {manifest['id']}")
    print(f"- Status: {manifest['status']}")
    print(f"- Manifest: {manifest_path_value.relative_to(ROOT)}")
    for source, target in copies:
        print(f"- Copy: {source} -> {target.relative_to(ROOT)}")
    for skipped in skipped_files:
        print(f"- Skip non-Markdown: {skipped}")


def main() -> int:
    args = parse_args()
    manifest, new_manifest_path, content_target, copies, skipped_files, errors = preflight(args)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    warnings = [f"skipped non-Markdown file: {path}" for path in skipped_files]
    print_plan(
        dry_run=args.dry_run,
        manifest=manifest,
        manifest_path_value=new_manifest_path,
        copies=copies,
        skipped_files=skipped_files,
    )
    if args.dry_run:
        return 0

    for source, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    write_manifest(new_manifest_path, manifest)

    validation_errors = validate_publications(load_publications(), load_site_config())
    if validation_errors:
        print("Import wrote files, but validation failed:", file=sys.stderr)
        for error in validation_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    report = report_payload(args, manifest, new_manifest_path, content_target, copies, skipped_files, warnings)
    report_path = write_report(report, manifest["slug"])
    print(f"- Report: {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
