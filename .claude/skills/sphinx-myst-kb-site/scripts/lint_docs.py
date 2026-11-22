#!/usr/bin/env python3
"""Lint the metadata and titles of every document of a knowledge base."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_docs import default_source_dir  # noqa: E402
from kb_docs import scan_docs  # noqa: E402


def _main(source_dir: Path | None = None, quiet: bool = False) -> int:
    """
    Discover every README.md / README.rst / README.ipynb below ``source_dir``
    (default: <git repo root>/docs/source) and report every problem: a missing
    or malformed doc_id, a duplicate doc_id, a missing, multi-line, unquoted
    (.md) or one-sentence description, a description with a double quote, a
    missing H1 title, two README files in one folder, front matter outside the
    strict ``key: value`` subset, a missing home page.

    Returns 0 when there is no problem, 1 otherwise.
    """
    try:
        source_dir = source_dir or default_source_dir()
    except FileNotFoundError as e:
        print(f"ERROR: {e}; pass --source_dir", file=sys.stderr)
        return 1
    if not source_dir.is_dir():
        print(f"ERROR: source folder not found: {source_dir}", file=sys.stderr)
        return 1
    docs, problems = scan_docs(source_dir)
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if problems:
        print(
            f"{len(problems)} problem(s) in {len(docs)} document(s) under {source_dir}",
            file=sys.stderr,
        )
        return 1
    if not quiet:
        print(f"OK: {len(docs)} document(s) under {source_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lint_docs",
        description="Lint the metadata and titles of every document of a knowledge base.",
    )
    parser.add_argument(
        "--source_dir",
        type=Path,
        default=None,
        help="the Sphinx source folder (default: <git repo root>/docs/source)",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="print nothing when there is no problem"
    )
    args = parser.parse_args(argv)
    return _main(source_dir=args.source_dir, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
