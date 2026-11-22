#!/usr/bin/env python3
"""Write p/<doc_id>.md into the built site: each document's plain text at its permalink."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_docs import DEFAULT_SOURCE_DIR  # noqa: E402
from kb_docs import default_source_dir  # noqa: E402
from kb_docs import find_repo_root  # noqa: E402
from kb_docs import scan_docs  # noqa: E402

DEFAULT_HTML_DIR = Path("docs") / "build" / "html"


def _main(source_dir: Path | None = None, directory: Path | None = None) -> int:
    """
    For every document, copy ``<directory>/_sources/<agent_rel_path>`` (the raw
    source Sphinx copied, or a notebook's Markdown copy from nb_to_md.py) to
    ``<directory>/p/<doc_id>.md``. A real file, not a redirect, so every agent
    fetch tool gets the text in one request with status 200, whether or not it
    follows redirects. Run after sphinx-build and nb_to_md.py.
    Returns 0 on success, 1 on failure.
    """
    try:
        root = find_repo_root() if directory is None else None
        source_dir = source_dir or default_source_dir()
    except FileNotFoundError as e:
        print(f"ERROR: {e}; pass --source_dir and --directory", file=sys.stderr)
        return 1
    directory = directory or root / DEFAULT_HTML_DIR
    docs, problems = scan_docs(source_dir)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    dir_p = directory / "p"
    if dir_p.exists():
        shutil.rmtree(dir_p)  # no stale doc_id from a deleted document
    dir_p.mkdir(parents=True)
    missing = list()
    for doc in docs:
        src = directory / "_sources" / doc.agent_rel_path
        if not src.is_file():
            missing.append(src)
            continue
        shutil.copyfile(src, dir_p / f"{doc.doc_id}.md")
    if missing:
        for src in missing:
            print(
                f"ERROR: {src} not found (run sphinx-build, then nb_to_md.py)",
                file=sys.stderr,
            )
        return 1
    print(f"Wrote {len(docs)} permalink source(s) to {dir_p}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="write_permalink_sources",
        description="Write <directory>/p/<doc_id>.md, the plain text of every document at its permalink.",
    )
    parser.add_argument(
        "--source_dir",
        type=Path,
        default=None,
        help=f"the Sphinx source folder (default: <git repo root>/{DEFAULT_SOURCE_DIR.as_posix()})",
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=None,
        help=f"the built site (default: <git repo root>/{DEFAULT_HTML_DIR.as_posix()})",
    )
    args = parser.parse_args(argv)
    return _main(source_dir=args.source_dir, directory=args.directory)


if __name__ == "__main__":
    sys.exit(main())
