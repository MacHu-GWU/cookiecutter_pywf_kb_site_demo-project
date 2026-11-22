#!/usr/bin/env python3
"""Write llms.txt for a knowledge base: one line per document, linking its raw source."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_docs import default_source_dir  # noqa: E402
from kb_docs import render_llms_txt  # noqa: E402
from kb_docs import scan_docs  # noqa: E402


def _main(
    site_url: str, output: Path | None = None, source_dir: Path | None = None
) -> int:
    """
    Scan every document below ``source_dir`` (default: <git repo root>/docs/source)
    and write llms.txt to ``output`` (default: stdout). The header is the home
    page's title and description; then one line per document, indented by
    folder depth:

        - [<H1 title>](<site_url>/p/<doc_id>.md): <description>

    Refuses to write when the documents have lint problems (run lint_docs.py).
    Returns 0 on success, 1 on failure.
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
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    text = render_llms_txt(docs, site_url)
    if output is None:
        sys.stdout.write(text)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"Wrote {output} ({len(docs)} document(s))")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build_llms_txt",
        description="Write llms.txt for a knowledge base: one line per document, linking its raw source.",
    )
    parser.add_argument(
        "--site_url",
        required=True,
        help="site root URL, such as https://kb.example.com",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="where to write llms.txt (default: stdout)",
    )
    parser.add_argument(
        "--source_dir",
        type=Path,
        default=None,
        help="the Sphinx source folder (default: <git repo root>/docs/source)",
    )
    args = parser.parse_args(argv)
    return _main(site_url=args.site_url, output=args.output, source_dir=args.source_dir)


if __name__ == "__main__":
    sys.exit(main())
