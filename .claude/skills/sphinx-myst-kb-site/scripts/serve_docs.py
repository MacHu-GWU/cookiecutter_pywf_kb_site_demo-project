#!/usr/bin/env python3
"""Serve the built site locally with the same Content-Type rules as production."""

from __future__ import annotations

import argparse
import functools
import http.server
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_docs import find_repo_root  # noqa: E402

#: Served as text/plain, like the _headers rules on Cloudflare Pages.
PLAIN_TEXT_PREFIXES = ("/_sources/", "/p/")
PLAIN_TEXT_FILES = ("/llms.txt",)

#: Non text/* types that are text too and need a charset.
TEXT_LIKE_TYPES = ("application/json", "application/javascript", "image/svg+xml")

UTF8 = "; charset=utf-8"


class Utf8Handler(http.server.SimpleHTTPRequestHandler):
    """
    SimpleHTTPRequestHandler sends text types without a charset (``text/plain``),
    so a browser decodes UTF-8 as Windows-1252 and CJK text turns into mojibake.
    This handler adds ``charset=utf-8`` to every text type and serves raw
    sources and llms.txt as ``text/plain; charset=utf-8``, matching _headers.
    """

    def guess_type(self, path: str) -> str:
        url_path = self.path.split("?", 1)[0]
        if url_path.startswith(PLAIN_TEXT_PREFIXES) or url_path in PLAIN_TEXT_FILES:
            return "text/plain" + UTF8
        mimetype = super().guess_type(path)
        if mimetype.startswith("text/") or mimetype in TEXT_LIKE_TYPES:
            return mimetype + UTF8
        return mimetype


def _main(port: int, directory: Path | None = None) -> int:
    """
    Serve ``directory`` (the Sphinx HTML output; default: <git repo root>/docs/build/html)
    on http://localhost:<port>/ until Ctrl+C, reachable from this machine only.
    Pagefind needs http (not file://), and every text response says
    charset=utf-8, as on the hosted site.

    Returns 0 after Ctrl+C, 1 when the folder is missing or the port is taken.
    """
    if directory is None:
        try:
            directory = find_repo_root() / "docs" / "build" / "html"
        except FileNotFoundError as e:
            print(f"ERROR: {e}; pass --directory", file=sys.stderr)
            return 1
    if not directory.is_dir():
        print(f"ERROR: {directory} not found; build the docs first", file=sys.stderr)
        return 1
    handler = functools.partial(Utf8Handler, directory=str(directory))
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError as e:
        print(f"ERROR: cannot listen on port {port}: {e}", file=sys.stderr)
        return 1
    print(f"Serving {directory} at http://localhost:{port}/ (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="serve_docs",
        description="Serve the built site locally with the same Content-Type rules as production.",
    )
    parser.add_argument("--port", type=int, required=True, help="port to listen on")
    parser.add_argument(
        "--directory",
        type=Path,
        default=None,
        help="the built site (default: <git repo root>/docs/build/html)",
    )
    args = parser.parse_args(argv)
    return _main(port=args.port, directory=args.directory)


if __name__ == "__main__":
    sys.exit(main())
