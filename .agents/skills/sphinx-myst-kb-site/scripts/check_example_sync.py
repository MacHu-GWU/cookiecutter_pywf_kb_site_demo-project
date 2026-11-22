#!/usr/bin/env python3
"""Check that a site's copies of the skill's example files have not drifted."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_docs import find_repo_root  # noqa: E402
from kb_docs import scan_docs  # noqa: E402

DIR_EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

#: examples/<path> -> <repo root>/<path>: files that hold no site-specific
#: value, so the site's copy must be byte for byte the example. Site-specific
#: files (conf.py, 404.html, the workflow, package.json, the extension when the
#: site splits it into a package) are compared by hand.
SAME_FILES = {
    "tooling/build-doc.sh": ".mise/tasks/build-doc.sh",
    "tooling/deploy-doc.sh": ".mise/tasks/deploy-doc.sh",
    "docs-source/_static/css/kb.css": "docs/source/_static/css/kb.css",
    "docs-source/_static/js/kb-copy.js": "docs/source/_static/js/kb-copy.js",
    "docs-source/_static/js/kb-search.js": "docs/source/_static/js/kb-search.js",
    "docs-source/_templates/components/view-this-page.html": "docs/source/_templates/components/view-this-page.html",
    "docs-source/_templates/sidebar/search.html": "docs/source/_templates/sidebar/search.html",
    "docs-source/_extra/_headers": "docs/source/_extra/_headers",
    "docs-source/_extra/robots.txt": "docs/source/_extra/robots.txt",
}


def _main(repo_root: Path | None = None) -> int:
    """
    Report every drift between the skill's ``examples/`` and the site:

    - a file of :data:`SAME_FILES` that is missing or differs;
    - a demo document of ``examples/docs-source/`` (every document but the
      home page) that is missing from ``<repo root>/docs/source/`` at the same
      path, or has another doc_id there. The site's copy may be translated, but
      it is the same document: same folder, same doc_id, same syntax.

    Returns 0 when nothing drifted, 1 otherwise.
    """
    try:
        repo_root = repo_root or find_repo_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}; pass --repo_root", file=sys.stderr)
        return 1
    problems = list()
    for example, copy in SAME_FILES.items():
        path_example = DIR_EXAMPLES / example
        path_copy = repo_root / copy
        if not path_copy.is_file():
            problems.append(f"{copy}: missing (copy of examples/{example})")
        elif path_copy.read_bytes() != path_example.read_bytes():
            problems.append(f"{copy}: differs from examples/{example}")
    example_docs, _ = scan_docs(DIR_EXAMPLES / "docs-source")
    site_docs, _ = scan_docs(repo_root / "docs" / "source")
    site_ids = {doc.docname: doc.doc_id for doc in site_docs}
    for doc in example_docs:
        if doc.depth == 0:
            continue  # the home page is the site's own
        if doc.docname not in site_ids:
            problems.append(f"docs/source/{doc.rel_path}: missing (demo document)")
        elif site_ids[doc.docname] != doc.doc_id:
            problems.append(
                f"docs/source/{doc.rel_path}: doc_id {site_ids[doc.docname]!r}, "
                f"the example has {doc.doc_id!r}"
            )
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if problems:
        print(
            "Change the example and the site's copy together.",
            file=sys.stderr,
        )
        return 1
    print(f"OK: the site's copies match {DIR_EXAMPLES}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_example_sync",
        description="Check that a site's copies of the skill's example files have not drifted.",
    )
    parser.add_argument(
        "--repo_root",
        type=Path,
        default=None,
        help="the site's repository (default: the git repo of the current directory)",
    )
    args = parser.parse_args(argv)
    return _main(repo_root=args.repo_root)


if __name__ == "__main__":
    sys.exit(main())
