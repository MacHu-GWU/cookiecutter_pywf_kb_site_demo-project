#!/usr/bin/env python3
"""Print new random doc_ids for knowledge base documents."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_docs import new_doc_id  # noqa: E402


def _main(count: int = 1) -> int:
    """
    Print ``count`` new doc_ids, one per line: 12 random characters of [A-Za-z].
    Uniqueness is case-insensitive (Sphinx lowercases :ref: targets), so the
    space is 26^12, about 9.5e16: a collision is practically impossible, and
    lint_docs.py still checks for one. Returns 0, or 1 when count is below 1.
    """
    if count < 1:
        print("ERROR: --count must be at least 1", file=sys.stderr)
        return 1
    for _ in range(count):
        print(new_doc_id())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="new_doc_id", description="Print new random doc_ids."
    )
    parser.add_argument(
        "--count", type=int, default=1, help="how many doc_ids to print (default: 1)"
    )
    args = parser.parse_args(argv)
    return _main(count=args.count)


if __name__ == "__main__":
    sys.exit(main())
