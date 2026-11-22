#!/usr/bin/env python3
"""Write the Markdown copy of every notebook document, for agents and llms.txt."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_docs import DEFAULT_SOURCE_DIR  # noqa: E402
from kb_docs import default_source_dir  # noqa: E402
from kb_docs import discover_doc_files  # noqa: E402
from kb_docs import find_repo_root  # noqa: E402
from kb_docs import notebook_to_markdown  # noqa: E402

DEFAULT_OUTPUT_DIR = Path("docs") / "build" / "html" / "_sources"


def _main(source_dir: Path | None = None, output_dir: Path | None = None) -> int:
    """
    For every ``<source_dir>/<path>/README.ipynb`` document, write
    ``<output_dir>/<path>/README.md`` (see ``kb_docs.notebook_to_markdown``).

    The defaults are ``<repo root>/docs/source`` and
    ``<repo root>/docs/build/html/_sources``: run it after sphinx-build, so the
    copy sits next to the ``README.ipynb`` Sphinx copied there. Never point
    ``output_dir`` at the source folder: a README.md next to README.ipynb is a
    second document in one folder. Returns 0 on success, 1 on failure.
    """
    try:
        root = find_repo_root() if source_dir is None or output_dir is None else None
    except FileNotFoundError as e:
        print(f"ERROR: {e}; pass --source_dir and --output_dir", file=sys.stderr)
        return 1
    source_dir = (source_dir or default_source_dir()).resolve()
    output_dir = (output_dir or root / DEFAULT_OUTPUT_DIR).resolve()
    if not source_dir.is_dir():
        print(f"ERROR: source folder not found: {source_dir}", file=sys.stderr)
        return 1
    if output_dir == source_dir or source_dir in output_dir.parents:
        print(
            f"ERROR: output folder {output_dir} is inside the source folder; "
            "the copies would become documents",
            file=sys.stderr,
        )
        return 1
    count = 0
    for path in discover_doc_files(source_dir):
        if path.suffix != ".ipynb":
            continue
        rel = path.relative_to(source_dir).with_suffix(".md")
        target = output_dir / rel
        try:
            text = notebook_to_markdown(path.read_text(encoding="utf-8"), path.name)
        except ValueError as e:  # json.JSONDecodeError is a ValueError
            print(f"ERROR: {path.relative_to(source_dir)}: {e}", file=sys.stderr)
            return 1
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        count += 1
    print(f"Wrote {count} notebook Markdown copy(ies) to {output_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nb_to_md",
        description=(
            "Write <output_dir>/<path>/README.md, a compact Markdown copy, "
            "for every <source_dir>/<path>/README.ipynb document."
        ),
    )
    parser.add_argument(
        "--source_dir",
        type=Path,
        default=None,
        help=f"the Sphinx source folder (default: <git repo root>/{DEFAULT_SOURCE_DIR.as_posix()})",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=None,
        help=f"where the copies go (default: <git repo root>/{DEFAULT_OUTPUT_DIR.as_posix()})",
    )
    args = parser.parse_args(argv)
    return _main(source_dir=args.source_dir, output_dir=args.output_dir)


if __name__ == "__main__":
    sys.exit(main())
