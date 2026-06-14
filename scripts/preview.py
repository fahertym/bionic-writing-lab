"""Local live-preview server for Bionic Writing Lab.

Rebuilds the static site whenever a source file changes and serves the
result over HTTP, so you can write and see the rendered page update on
refresh. Drafts are included by default so unfinished work is visible
locally without shipping it to the public build.

Standard library only -- no extra dependencies.

Usage:
    python scripts/preview.py                 # serve drafts at http://localhost:8000
    python scripts/preview.py --port 4000
    python scripts/preview.py --public        # mirror the public build (no drafts)
    python scripts/preview.py --no-browser
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Ensure sibling modules import cleanly regardless of working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from publication_lib import (  # noqa: E402
    CONCEPTS_DIR,
    DIST_SITE_DIR,
    PATHS_DIR,
    PUBLICATIONS_DIR,
    ROOT,
    SITE_DIR,
)

CONTENT_DIR = ROOT / "content"
WATCH_DIRS = [CONTENT_DIR, PUBLICATIONS_DIR, PATHS_DIR, CONCEPTS_DIR, SITE_DIR]
POLL_SECONDS = 1.0


def source_signature() -> tuple[int, float]:
    """A cheap fingerprint of all watched source files (count + newest mtime)."""
    count = 0
    newest = 0.0
    for directory in WATCH_DIRS:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file():
                count += 1
                mtime = path.stat().st_mtime
                if mtime > newest:
                    newest = mtime
    return count, newest


def run_build() -> bool:
    """Rebuild the site in-process. Returns True on success."""
    # Import lazily so a syntax error in build_site doesn't kill the watcher.
    import importlib

    import build_site

    importlib.reload(build_site)
    try:
        return build_site.render_site() == 0
    except Exception as exc:  # pragma: no cover - defensive: keep server alive
        print(f"[preview] build error: {exc}", file=sys.stderr)
        return False


def watch_loop(stop: threading.Event) -> None:
    last = None
    while not stop.is_set():
        current = source_signature()
        if current != last:
            if last is not None:
                print("[preview] change detected -- rebuilding...")
            ok = run_build()
            if ok:
                print("[preview] build OK")
            last = current
        stop.wait(POLL_SECONDS)


def serve(port: int) -> socketserver.TCPServer:
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(DIST_SITE_DIR),
    )
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def main() -> int:
    parser = argparse.ArgumentParser(description="Live preview server for Bionic Writing Lab.")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on (default 8000)")
    parser.add_argument(
        "--public",
        action="store_true",
        help="Build exactly what ships publicly (exclude drafts)",
    )
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser tab")
    args = parser.parse_args()

    # Drafts visible locally unless --public is requested.
    os.environ["INCLUDE_DRAFTS"] = "" if args.public else "1"

    print(f"[preview] root: {ROOT}")
    print(f"[preview] drafts: {'excluded (public mode)' if args.public else 'included'}")
    if not run_build():
        print("[preview] initial build failed -- fix the errors above, then save to retry.")
    DIST_SITE_DIR.mkdir(parents=True, exist_ok=True)

    httpd = serve(args.port)
    url = f"http://localhost:{args.port}/"
    print(f"[preview] serving {DIST_SITE_DIR} at {url}")
    print("[preview] watching for changes -- press Ctrl+C to stop")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    stop = threading.Event()
    watcher = threading.Thread(target=watch_loop, args=(stop,), daemon=True)
    watcher.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[preview] shutting down")
    finally:
        stop.set()
        httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
