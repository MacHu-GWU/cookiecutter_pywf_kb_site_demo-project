#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Writing utilities of the blog-* skills for the knowledge base: create, find, search
and check knowledge base documents.

Standard library only. Document discovery, metadata parsing and the site's
metadata lint come from the sphinx-myst-kb-site skill (``kb_docs.py``), so this
script and ``mise run lint-doc`` can never disagree. This script adds the
writing rules of the blog-* family on top (see blog-base/ref/02-spec/).

Subcommands (run from anywhere inside the repository)::

    blog_utils.py new-post --parent <category> --slug <slug> --title "<title>" --description "<two sentences>"
    blog_utils.py new-category --parent <category or ""> --slug <slug> --title "<title>" --description "<two sentences>"
    blog_utils.py list-categories
    blog_utils.py get --doc_id <doc_id> | --path <document folder>
    blog_utils.py list-recent --k 10
    blog_utils.py search --query "<words>" --k 20
    blog_utils.py check [--doc_id <doc_id> | --path <document folder>]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date as Date
from pathlib import Path

DIR_HERE = Path(__file__).absolute().parent
DIR_ASSETS = DIR_HERE.parent / "assets"
DIR_KB_SCRIPTS = DIR_HERE.parents[1] / "sphinx-myst-kb-site" / "scripts"
sys.path.insert(0, str(DIR_KB_SCRIPTS))

from kb_docs import Doc  # noqa: E402
from kb_docs import DOC_FILE_STEM  # noqa: E402
from kb_docs import DOC_FILE_SUFFIXES  # noqa: E402
from kb_docs import find_repo_root  # noqa: E402
from kb_docs import new_doc_id  # noqa: E402
from kb_docs import parse_doc  # noqa: E402
from kb_docs import scan_docs  # noqa: E402

DIR_REPO = find_repo_root(DIR_HERE)
DIR_SOURCE = DIR_REPO / "docs" / "source"

#: Front matter keys of a blog-* document, in order (blog-base ref/02-spec/02-metadata.md).
META_KEYS = ("doc_id", "description", "tags", "created_at", "updated_at")
#: Keys of a resources/*.md file (blog-base ref/02-spec/05-resources.md).
RESOURCE_KEYS = (
    "title",
    "source_url",
    "source_type",
    "author",
    "published_at",
    "intake_at",
    "note",
)
#: The chatbot deep link is injected at build time by cookiecutter_pywf_kb_site_demo.sphinx_ext;
#: a copy in a source file is an error.
DEEPLINK_MARKER = "mini-tools.easyscalecloud.com/tools/chatbot-deeplink"

RE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
RE_INLINE_CODE = re.compile(r"`[^`]*`")
RE_HEADING = re.compile(r"^(#{1,6})\s")
RE_IMAGE = re.compile(r"!\[[^\]]*\]\((\./)?(img/[^)\s]+|cover\.[a-z]+)\)")
RE_FM_LINE = re.compile(r'^([A-Za-z_][\w-]*):\s*"(.*)"\s*$')
FULLWIDTH = "，。：；？！（）“”‘’、《》【】…"
AI_SUMMARY_MARKS = ("✅", "❌", "⚠️")
IMAGE_SUFFIXES = (".jpeg", ".jpg", ".png", ".webp", ".svg", ".gif")
#: MyST directives whose body is code or data, not prose.
CODE_DIRECTIVES = (
    "{code",
    "{literalinclude",
    "{mermaid",
    "{jinja",
    "{eval-rst",
    "{kb-toctree",
    "{math",
    "{raw",
)


# --- helpers ------------------------------------------------------------------
def today() -> str:
    return Date.today().isoformat()


def rel(path: Path) -> str:
    """A path relative to the repository root, for printing."""
    return path.relative_to(DIR_REPO).as_posix()


def all_docs() -> list[Doc]:
    docs, _ = scan_docs(DIR_SOURCE)
    return docs


def doc_folder(doc: Doc) -> Path:
    return doc.path.parent


def find_doc(doc_id: str | None = None, path: Path | None = None) -> Doc | None:
    """The document with this doc_id (case-insensitive), or in this folder."""
    if path is not None:
        candidates = (
            [path]
            if path.is_absolute()
            else [Path.cwd() / path, DIR_REPO / path, DIR_SOURCE / path]
        )
        folder = next((c.resolve() for c in candidates if c.exists()), None)
        if folder is None:
            return None
        if folder.is_file():
            folder = folder.parent
        for suffix in DOC_FILE_SUFFIXES:
            file = folder / f"{DOC_FILE_STEM}{suffix}"
            if file.exists():
                doc, _ = parse_doc(file, DIR_SOURCE)
                return doc
        return None
    for doc in all_docs():
        if doc.doc_id and doc_id and doc.doc_id.lower() == doc_id.lower():
            return doc
    return None


def is_category(doc: Doc) -> bool:
    """A document whose source lists its children with kb-toctree."""
    return "{kb-toctree}" in doc.path.read_text(encoding="utf-8")


def print_doc(doc: Doc) -> None:
    print(
        f"doc_id = {doc.doc_id}, path = {rel(doc_folder(doc))}, "
        f"title = {doc.title}, description = {doc.description}"
    )


def render(name: str, **values: str) -> str:
    text = (DIR_ASSETS / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def unique_doc_id() -> str:
    taken = {d.doc_id.lower() for d in all_docs() if d.doc_id}
    while True:
        doc_id = new_doc_id()
        if doc_id.lower() not in taken:
            return doc_id


def split_front_matter(text: str) -> tuple[list[str], list[str]]:
    """(front matter lines without the --- fences, body lines)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:i], lines[i + 1 :]
    return lines[1:], []


def prose_lines(body: list[str]) -> list[tuple[int, str]]:
    """(index, line) of body lines outside code fences, with inline code removed."""
    out = list()
    # open fences, innermost last: (marker, holds_prose). A MyST directive such
    # as ```{note} holds prose; a code fence or a code-like directive does not.
    stack: list[tuple[str, bool]] = list()
    for i, line in enumerate(body):
        match = RE_FENCE.match(line)
        if match:
            marker = match.group(1)
            info = line.strip()[len(marker) :].strip()
            if stack and not info and marker.startswith(stack[-1][0]):
                stack.pop()
            elif not stack or stack[-1][1]:
                prose = info.startswith("{") and not info.startswith(CODE_DIRECTIVES)
                stack.append((marker, prose))
            continue
        if all(holds_prose for _, holds_prose in stack):
            out.append((i, RE_INLINE_CODE.sub("", line)))
    return out


# --- create -------------------------------------------------------------------
def _create(
    parent: str,
    slug: str,
    title: str,
    description: str,
    date: str,
    category: bool,
) -> int:
    if not RE_SLUG.match(slug):
        print(
            f"ERROR: slug must be lowercase English words joined by '-', got {slug!r}",
            file=sys.stderr,
        )
        return 1
    dir_parent = (DIR_SOURCE / parent).resolve() if parent else DIR_SOURCE
    if not any(
        (dir_parent / f"{DOC_FILE_STEM}{s}").exists() for s in DOC_FILE_SUFFIXES
    ):
        print(
            f"ERROR: {rel(dir_parent)} is not a category (no README); "
            "list them with 'list-categories' or create one with 'new-category'",
            file=sys.stderr,
        )
        return 1
    dir_doc = dir_parent / slug
    if dir_doc.exists():
        print(f"ERROR: {rel(dir_doc)} already exists", file=sys.stderr)
        return 1
    values = dict(
        doc_id=unique_doc_id(),
        description=description,
        title=title,
        date=date,
    )
    dir_doc.mkdir(parents=True)
    path_readme = dir_doc / "README.md"
    template = "category-readme-template.md" if category else "readme-template.md"
    path_readme.write_text(render(template, **values), encoding="utf-8")
    created = [path_readme]
    if not category:
        path_plan = dir_doc / "plan.md"
        path_plan.write_text(render("plan-template.md", **values), encoding="utf-8")
        created.append(path_plan)
    doc, problems = parse_doc(path_readme, DIR_SOURCE)
    if problems:
        shutil.rmtree(dir_doc)
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        print("Nothing was created.", file=sys.stderr)
        return 1
    for path in created:
        print(f"Created {rel(path)}")
    print_doc(doc)
    return 0


# --- check --------------------------------------------------------------------
def check_resources(dir_doc: Path) -> list[str]:
    warns = list()
    dir_res = dir_doc / "resources"
    if not dir_res.is_dir():
        return warns
    for path in sorted(dir_res.iterdir()):
        if path.stem == DOC_FILE_STEM:
            warns.append(f"ERROR {rel(path)}: a resource must not be named README.*")
            continue
        if path.is_file() and path.stat().st_size > 10 * 1024 * 1024:
            warns.append(f"WARN {rel(path)}: larger than 10 MB, keep only the .md")
        if path.suffix != ".md":
            continue
        fm, _ = split_front_matter(path.read_text(encoding="utf-8"))
        values = dict(m.groups() for m in map(RE_FM_LINE.match, fm) if m)
        missing = [k for k in RESOURCE_KEYS if k not in values]
        if missing:
            warns.append(
                f"WARN {rel(path)}: front matter is missing {', '.join(missing)}"
            )
        elif not values["intake_at"]:
            warns.append(f"WARN {rel(path)}: intake_at is empty")
    return warns


def check_doc(doc: Doc) -> list[str]:
    """Every finding of one document, each starting with ERROR or WARN."""
    found = list()
    dir_doc = doc_folder(doc)
    _, problems = parse_doc(doc.path, DIR_SOURCE)
    found.extend(f"ERROR {p}" for p in problems)
    text = doc.path.read_text(encoding="utf-8")
    name = rel(doc.path)
    if DEEPLINK_MARKER in text:
        found.append(
            f"ERROR {name}: the AI Reader deep link is added at build time; "
            "remove it from the source"
        )
    found.extend(check_resources(dir_doc))
    if doc.path.suffix != ".md":
        return found

    fm, body = split_front_matter(text)
    keys = [line.split(":", 1)[0].strip() for line in fm if ":" in line]
    for key in ("created_at", "updated_at"):
        value = doc.meta.get(key)
        if value is None:
            found.append(f"WARN {name}: no {key}")
        elif not (isinstance(value, str) and RE_DATE.match(value)):
            found.append(f'ERROR {name}: {key} must be "YYYY-MM-DD", got {value!r}')
    extra = [k for k in keys if k not in META_KEYS]
    if extra:
        found.append(f"WARN {name}: front matter keys outside the spec: {extra}")
    ordered = [k for k in META_KEYS if k in keys]
    if [k for k in keys if k in META_KEYS] != ordered:
        found.append(f"WARN {name}: front matter order should be {list(META_KEYS)}")
    description = doc.description or ""
    if any(c in FULLWIDTH for c in description):
        found.append(f"WARN {name}: full-width punctuation in description")
    if not is_category(doc) and not (dir_doc / "plan.md").exists():
        found.append(f"WARN {rel(dir_doc)}: no plan.md")

    fullwidth_lines = list()
    for i, line in prose_lines(body):
        if any(c in FULLWIDTH for c in line):
            fullwidth_lines.append(i + len(fm) + 3)
        match = RE_HEADING.match(line)
        if match and len(match.group(1)) >= 5:
            found.append(
                f"WARN {name}:{i + len(fm) + 3}: H{len(match.group(1))} heading, "
                "split the section"
            )
        if any(mark in line for mark in AI_SUMMARY_MARKS):
            found.append(
                f"WARN {name}:{i + len(fm) + 3}: checkmark/warning emoji, "
                "write prose or use an admonition"
            )
    if fullwidth_lines:
        shown = ", ".join(map(str, fullwidth_lines[:10]))
        more = " ..." if len(fullwidth_lines) > 10 else ""
        found.append(
            f"WARN {name}: full-width punctuation on lines {shown}{more}; run c2ep"
        )

    referenced = set()
    for match in RE_IMAGE.finditer(text):
        target = match.group(2)
        referenced.add(target)
        if not (dir_doc / target).exists():
            found.append(f"ERROR {name}: image not found: {target}")
    dir_img = dir_doc / "img"
    if dir_img.is_dir():
        for path in sorted(dir_img.iterdir()):
            if (
                path.suffix.lower() in IMAGE_SUFFIXES
                and f"img/{path.name}" not in referenced
            ):
                found.append(f"WARN {rel(path)}: image is not referenced by the body")
    return found


# --- commands -----------------------------------------------------------------
def cmd_list_categories() -> int:
    for doc in all_docs():
        if is_category(doc):
            print(
                f"parent = {doc_folder(doc).relative_to(DIR_SOURCE).as_posix() or '.'}, "
                f"doc_id = {doc.doc_id}, title = {doc.title}"
            )
    return 0


def cmd_get(doc_id: str | None, path: Path | None) -> int:
    doc = find_doc(doc_id=doc_id, path=path)
    if doc is None:
        print(f"ERROR: no document for {doc_id or path}", file=sys.stderr)
        return 1
    dir_doc = doc_folder(doc)
    print_doc(doc)
    print(f"file = {rel(doc.path)}")
    for key in ("tags", "created_at", "updated_at"):
        print(f"{key} = {doc.meta.get(key, '')}")
    print(f"plan = {'plan.md' if (dir_doc / 'plan.md').exists() else '(none)'}")
    dir_res = dir_doc / "resources"
    resources = sorted(p.name for p in dir_res.glob("*.md")) if dir_res.is_dir() else []
    print(f"resources = {', '.join(resources) or '(none)'}")
    children = [d for d in all_docs() if d.path.parent.parent == dir_doc]
    if children:
        print(f"children = {', '.join(doc_folder(c).name for c in children)}")
    return 0


def cmd_list_recent(k: int) -> int:
    docs = [d for d in all_docs() if d.depth > 0]
    docs.sort(
        key=lambda d: str(d.meta.get("created_at") or ""),
        reverse=True,
    )
    for doc in docs[:k]:
        print(
            f"created_at = {doc.meta.get('created_at') or ''}, ",
            end="",
        )
        print_doc(doc)
    return 0


def cmd_search(query: str, k: int) -> int:
    words = [w.lower() for w in query.split() if w.strip()]
    if not words:
        print("ERROR: empty query", file=sys.stderr)
        return 1
    scored = list()
    for doc in all_docs():
        haystack = f"{doc.title or ''} {doc.description or ''} {' '.join(doc.meta.get('tags') or [])}".lower()
        hits = 0
        for word in words:
            if word.isascii():
                hits += bool(re.search(rf"\b{re.escape(word)}\b", haystack))
            else:
                hits += word in haystack
        if hits:
            scored.append((hits, doc))
    scored.sort(key=lambda x: -x[0])
    for _, doc in scored[:k]:
        print_doc(doc)
    if not scored:
        print("(no match)")
    return 0


def cmd_check(doc_id: str | None, path: Path | None) -> int:
    if doc_id or path:
        doc = find_doc(doc_id=doc_id, path=path)
        if doc is None:
            print(f"ERROR: no document for {doc_id or path}", file=sys.stderr)
            return 1
        docs = [doc]
    else:
        docs = all_docs()
    errors = 0
    for doc in docs:
        for finding in check_doc(doc):
            errors += finding.startswith("ERROR")
            print(
                finding, file=sys.stderr if finding.startswith("ERROR") else sys.stdout
            )
    print(f"{'FAIL' if errors else 'OK'}: {len(docs)} document(s), {errors} error(s)")
    return 1 if errors else 0


def _main(
    command: str,
    parent: str = "",
    slug: str = "",
    title: str = "",
    description: str = "",
    date: str = "",
    doc_id: str | None = None,
    path: Path | None = None,
    query: str = "",
    k: int = 10,
) -> int:
    """
    Run one subcommand of the blog-* writing utilities.

    - new-post: create ``docs/source/<parent>/<slug>/`` with README.md (fresh
      doc_id, dates, the given title and provisional description) and plan.md.
    - new-category: create a category folder with a kb-toctree README.md.
    - list-categories: every document that lists children with kb-toctree.
    - get: print one document's metadata, plan and resources.
    - list-recent: the newest documents by created_at.
    - search: match words against title, description and tags.
    - check: the site lint plus the blog-* rules (ERROR / WARN lines).

    Returns 0 on success, 1 on failure (for check: when there is an ERROR).
    """
    if command in ("new-post", "new-category"):
        return _create(
            parent=parent.strip("/"),
            slug=slug,
            title=title,
            description=description,
            date=date or today(),
            category=command == "new-category",
        )
    if command == "list-categories":
        return cmd_list_categories()
    if command == "get":
        return cmd_get(doc_id=doc_id, path=path)
    if command == "list-recent":
        return cmd_list_recent(k=k)
    if command == "search":
        return cmd_search(query=query, k=k)
    if command == "check":
        return cmd_check(doc_id=doc_id, path=path)
    print(f"ERROR: unknown command {command!r}", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="blog_utils",
        description="Create, find, search and check knowledge base documents (blog-* skills).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("new-post", "create a document folder with README.md and plan.md"),
        ("new-category", "create a category folder with a kb-toctree README.md"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument(
            "--parent",
            required=name == "new-post",
            default="",
            help="the category folder, relative to docs/source ('' for the home page)",
        )
        p.add_argument(
            "--slug", required=True, help="English folder name, lowercase, '-' joined"
        )
        p.add_argument("--title", required=True, help="the H1 title")
        p.add_argument(
            "--description",
            required=True,
            help="one line, two sentences, no double quote (provisional is fine)",
        )
        p.add_argument(
            "--date", default="", help="created_at, YYYY-MM-DD (default: today)"
        )

    sub.add_parser("list-categories", help="list category documents")

    for name, help_text in (
        ("get", "show one document"),
        ("check", "check one document (default: all)"),
    ):
        p = sub.add_parser(name, help=help_text)
        group = p.add_mutually_exclusive_group(required=name == "get")
        group.add_argument("--doc_id", default=None, help="the document's doc_id")
        group.add_argument(
            "--path", type=Path, default=None, help="the document folder or file"
        )

    p = sub.add_parser("list-recent", help="newest documents by created_at")
    p.add_argument("--k", type=int, default=10, help="how many (default: 10)")

    p = sub.add_parser("search", help="search title, description and tags")
    p.add_argument("--query", required=True, help="words to look for")
    p.add_argument("--k", type=int, default=20, help="how many (default: 20)")

    args = parser.parse_args(argv)
    return _main(
        command=args.command,
        parent=getattr(args, "parent", ""),
        slug=getattr(args, "slug", ""),
        title=getattr(args, "title", ""),
        description=getattr(args, "description", ""),
        date=getattr(args, "date", ""),
        doc_id=getattr(args, "doc_id", None),
        path=getattr(args, "path", None),
        query=getattr(args, "query", ""),
        k=getattr(args, "k", 10),
    )


if __name__ == "__main__":
    sys.exit(main())
