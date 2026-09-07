"""Locate the digital archive without hard-coding a host-specific path.

Resolution order for the archive root:
  1. $BWL_ARCHIVE_ROOT
  2. ~/.claude_launchpad/digital-archive   (Zenith / WSL2 layout, via symlink)
  3. ~/digital-archive                     (expected ops-dev layout)

Nothing in this package writes to the archive. Every DuckDB connection is
opened read_only=True, which also prevents DuckDB from silently upgrading the
8.1GB storage file's format on open.
"""
from __future__ import annotations

import os
from pathlib import Path

_CANDIDATES = (
    Path.home() / ".claude_launchpad" / "digital-archive",
    Path.home() / "digital-archive",
)


def archive_root() -> Path:
    env = os.environ.get("BWL_ARCHIVE_ROOT")
    if env:
        p = Path(env).expanduser()
        if not p.is_dir():
            raise SystemExit(f"BWL_ARCHIVE_ROOT is not a directory: {p}")
        return p
    for p in _CANDIDATES:
        if p.is_dir():
            return p
    raise SystemExit(
        "Digital archive not found. Set BWL_ARCHIVE_ROOT to its path.\n"
        "Tried: " + ", ".join(str(p) for p in _CANDIDATES)
    )


def duckdb_path() -> Path:
    p = archive_root() / "schema" / "digital_archive.duckdb"
    if not p.exists():
        raise SystemExit(f"Archive DuckDB not found at {p}")
    return p


def corpus_dir() -> Path:
    """The provenance-tiered corpus built by villain-author-context-v1."""
    p = archive_root() / "derived" / "villain-author-context-v1" / "corpus"
    if not p.is_dir():
        raise SystemExit(f"Tiered corpus not found at {p}")
    return p


def connect_readonly():
    import duckdb

    con = duckdb.connect(str(duckdb_path()), read_only=True)
    con.execute("PRAGMA threads=3")  # host discipline: Zenith is also a desktop
    return con


def workdir() -> Path:
    """Derived intermediates. Documented location, not /tmp, not committed."""
    root = Path(os.environ.get("BWL_ARCHIVE_WORK", "")) if os.environ.get(
        "BWL_ARCHIVE_WORK"
    ) else Path(__file__).resolve().parents[2] / ".research-work"
    root.mkdir(parents=True, exist_ok=True)
    return root
