"""
Discover, parse and lint the documents of a knowledge base source folder.

Standard library only, so it runs anywhere (an agent, a git hook, CI) without
the docs dependencies. Imported by the CLIs next to it:

- lint_docs.py: report every metadata problem, exit 1 if any.
- build_llms_txt.py: write llms.txt from the parsed documents.
- new_doc_id.py: print a fresh doc_id.
- nb_to_md.py: write the Markdown copy of every notebook document.
- write_permalink_sources.py: write p/<doc_id>.md, each document's agent text.
- serve_docs.py: only find_repo_root, for its default folder.

Other scripts of the site may import it too, so
rename a public name only together with them.

Document layout: one document = one folder with exactly one README.md,
README.rst or README.ipynb. Folders starting with "_" or "." are not documents
(Sphinx's _static, _templates, _ext, _extra, .ipynb_checkpoints).

Metadata format (strict, so a stdlib parser is enough and nobody has to escape):

- .md: YAML front matter, one ``key: value`` per line. A value is a
  double-quoted string, a ``[a, b]`` list of bare words, or a bare word/number.
  ``description`` must be double-quoted.
- .rst: the field list at the top of the file, ``:key: value``, one line each.
- .ipynb: the notebook level ``metadata`` object (JSON).

Agents read a notebook through its Markdown copy, not the JSON: the build
writes ``_sources/<path>/README.md`` next to ``_sources/<path>/README.ipynb``
(``notebook_to_markdown``). Every document's agent text is then copied to
``p/<doc_id>.md`` (write_permalink_sources.py), the URL llms.txt links.
The copy never lives in the source tree, where it would be a second document.

Required keys: ``doc_id`` (12 characters of [A-Za-z]) and ``description``
(one line, no double quote, at least two sentences: what the document covers,
then what kind of document it is).
"""

from __future__ import annotations

import dataclasses
import json
import re
import secrets
import string
from pathlib import Path

DOC_FILE_STEM = "README"
DOC_FILE_SUFFIXES = (".md", ".rst", ".ipynb")
DOC_ID_PATTERN = re.compile(r"^[A-Za-z]{12}$")
DEFAULT_SOURCE_DIR = Path("docs") / "source"

_RE_KEY = r"[A-Za-z_][\w-]*"
_RE_MD_LINE = re.compile(rf"^({_RE_KEY}):(?:\s+(.*))?$")
_RE_MD_QUOTED = re.compile(r'^"([^"\\]*)"$')
_RE_MD_LIST = re.compile(r"^\[(.*)\]$")
# A bare value is one word: letters, digits, "_", "-", ".".
_RE_MD_BARE = re.compile(r"^\w[\w.-]*$")
# Bare words a YAML parser turns into a boolean, null or date: must be quoted.
_RE_MD_YAML_TYPED = re.compile(
    r"^(?:yes|no|true|false|on|off|null|~|\d{4}-\d{2}-\d{2}.*)$", re.IGNORECASE
)
_RE_RST_FIELD = re.compile(rf"^:({_RE_KEY}):(?:\s+(.*))?$")
_RE_RST_ADORNMENT = re.compile(r"^([=\-~^\"'`#*+<>:._])\1+\s*$")
# "# Title" with an optional closing "#" sequence ("# Learn C#" keeps its "#").
_RE_MD_H1 = re.compile(r"^#\s+(.+?)(?:\s+#+)?\s*$")
_RE_MD_SUBHEADING = re.compile(r"^#{2,6}\s")
_RE_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
# Sentence ends: ASCII . ! ? followed by space or end, or a CJK full stop.
_RE_SENTENCE_END = re.compile(r"[.!?](?=\s|$)|[。！？]")


@dataclasses.dataclass
class Problem:
    """One lint finding. ``path`` is relative to the source folder."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclasses.dataclass
class Doc:
    """One parsed document."""

    path: Path  # absolute path of the README.<ext> file
    rel_path: str  # posix path relative to the source folder, with extension
    meta: dict[str, object]
    title: str | None

    @property
    def docname(self) -> str:
        """Sphinx docname: rel_path without the extension."""
        return self.rel_path.rsplit(".", 1)[0]

    @property
    def depth(self) -> int:
        """0 for the home page README, 1 for its children, and so on."""
        return self.rel_path.count("/")

    @property
    def doc_id(self) -> str | None:
        value = self.meta.get("doc_id")
        return value if isinstance(value, str) else None

    @property
    def description(self) -> str | None:
        value = self.meta.get("description")
        return value if isinstance(value, str) else None

    def page_url(self, site_url: str) -> str:
        """The web page (Cloudflare Pages serves a/b.html at a/b)."""
        return f"{site_url.rstrip('/')}/{self.docname}"

    @property
    def agent_rel_path(self) -> str:
        """
        The file agents read: the source itself, or for a notebook its Markdown
        copy (README.ipynb -> README.md, written by nb_to_md.py).
        """
        if self.rel_path.endswith(".ipynb"):
            return f"{self.docname}.md"
        return self.rel_path

    def raw_url(self, site_url: str) -> str:
        """
        The plain text for agents at its permalink, ``<site>/p/<doc_id>.md``: a
        real file (write_permalink_sources.py), a copy of ``_sources/<agent_rel_path>``.
        """
        return f"{site_url.rstrip('/')}/p/{self.doc_id}.md"


# --- repository and discovery -------------------------------------------------
def find_repo_root(start: Path | None = None) -> Path:
    """
    The closest folder at or above ``start`` (default: the current directory)
    that holds a ``.git`` entry. Raises FileNotFoundError if there is none.
    """
    here = (start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / ".git").exists():
            return folder
    raise FileNotFoundError(f"no .git found at or above {here}")


def default_source_dir(start: Path | None = None) -> Path:
    """``<repo root>/docs/source``, the repo found from ``start``."""
    return find_repo_root(start) / DEFAULT_SOURCE_DIR


def _is_skipped(rel_parts: tuple[str, ...]) -> bool:
    return any(part[0] in "._" for part in rel_parts[:-1])


def discover_doc_files(source_dir: Path) -> list[Path]:
    """
    Every README.md / README.rst / README.ipynb below ``source_dir``, parents
    before children, siblings by folder name.
    """
    found = list()
    for suffix in DOC_FILE_SUFFIXES:
        for path in source_dir.rglob(f"{DOC_FILE_STEM}{suffix}"):
            if not _is_skipped(path.relative_to(source_dir).parts):
                found.append(path)
    return sorted(
        found, key=lambda p: (p.relative_to(source_dir).parent.parts, p.suffix)
    )


# --- metadata parsers ---------------------------------------------------------
def _parse_md_value(raw: str) -> tuple[object, bool] | None:
    """(value, was_quoted), or None when the syntax is outside the strict subset."""
    match = _RE_MD_QUOTED.match(raw)
    if match:
        return match.group(1), True
    match = _RE_MD_LIST.match(raw)
    if match:
        items = [item.strip() for item in match.group(1).split(",") if item.strip()]
        if all(_is_bare_word(item) for item in items):
            return items, False
        return None
    if _is_bare_word(raw):
        return raw, False
    return None


def _is_bare_word(value: str) -> bool:
    """One word that every YAML parser reads as the same plain string."""
    return bool(_RE_MD_BARE.match(value)) and not _RE_MD_YAML_TYPED.match(value)


def parse_md(text: str, rel_path: str) -> tuple[dict[str, object], list[Problem], int]:
    """
    Front matter of a .md file: (metadata, problems, index of the first body line).
    """
    meta: dict[str, object] = dict()
    problems: list[Problem] = list()
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        problems.append(
            Problem(rel_path, "no front matter: the file must start with a '---' line")
        )
        return meta, problems, 0
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start = i + 1
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = _RE_MD_LINE.match(line)
        parsed = _parse_md_value((match.group(2) or "").strip()) if match else None
        if parsed is None:
            problems.append(
                Problem(
                    rel_path,
                    f'front matter line {i + 1}: use `key: "text"`, `key: [a, b]` '
                    f"or `key: word` (quote text, dates and yes/no), got {line!r}",
                )
            )
            continue
        key = match.group(1)
        value, quoted = parsed
        meta[key] = value
        if key == "description" and not quoted:
            problems.append(
                Problem(
                    rel_path, 'description must be double-quoted: description: "..."'
                )
            )
    else:
        problems.append(Problem(rel_path, "front matter is not closed by a '---' line"))
        return meta, problems, len(lines)
    return meta, problems, body_start


def parse_rst(text: str, rel_path: str) -> tuple[dict[str, object], list[Problem]]:
    """The field list at the very top of a .rst file."""
    meta: dict[str, object] = dict()
    problems: list[Problem] = list()
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            if meta:
                break
            continue
        match = _RE_RST_FIELD.match(line)
        if match is None:
            if meta and line[:1].isspace():
                problems.append(
                    Problem(rel_path, f"line {i}: a field value must fit on one line")
                )
                continue
            break
        meta[match.group(1)] = (match.group(2) or "").strip()
    return meta, problems


def parse_ipynb(
    text: str, rel_path: str
) -> tuple[dict[str, object], list[Problem], list[dict]]:
    """The notebook level metadata (without kernelspec / language_info), and the cells."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return {}, [Problem(rel_path, f"invalid notebook JSON: {e}")], []
    meta = {
        k: v
        for k, v in data.get("metadata", {}).items()
        if k not in ("kernelspec", "language_info")
    }
    return meta, [], data.get("cells", [])


# --- titles -------------------------------------------------------------------
def _md_h1(lines: list[str]) -> str | None:
    fence = None
    for line in lines:
        match = _RE_FENCE.match(line)
        if match:
            marker = match.group(1)
            stripped = line.strip()
            if fence is None:
                fence = marker
            # A closing fence is only fence characters, at least as many as
            # the opening one: "```python" inside a ``` fence does not close it.
            elif set(stripped) == {fence[0]} and len(stripped) >= len(fence):
                fence = None
            continue
        if fence is None:
            if _RE_MD_SUBHEADING.match(line):
                return None  # the first heading must be the H1
            match = _RE_MD_H1.match(line)
            if match:
                return match.group(1)
    return None


def _rst_title(lines: list[str]) -> str | None:
    for i in range(len(lines) - 1):
        title, under = lines[i].strip(), lines[i + 1]
        if (
            not title
            or _RE_RST_FIELD.match(lines[i])
            or _RE_RST_ADORNMENT.match(lines[i])
        ):
            continue
        if _RE_RST_ADORNMENT.match(under) and len(under.strip()) >= len(title):
            return title
    return None


def _ipynb_h1(cells: list[dict]) -> str | None:
    for cell in cells:
        if cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", "")
        text = "".join(source) if isinstance(source, list) else source
        title = _md_h1(text.splitlines())
        if title:
            return title
    return None


# --- one document -------------------------------------------------------------
def _lint_meta(doc: Doc) -> list[Problem]:
    problems = list()
    doc_id = doc.meta.get("doc_id")
    if doc_id is None:
        problems.append(
            Problem(doc.rel_path, "missing doc_id (generate one: new_doc_id.py)")
        )
    elif not isinstance(doc_id, str) or not DOC_ID_PATTERN.match(doc_id):
        problems.append(
            Problem(
                doc.rel_path,
                f"doc_id must be 12 characters of [A-Za-z], got {doc_id!r}",
            )
        )
    description = doc.meta.get("description")
    if description is None:
        problems.append(Problem(doc.rel_path, "missing description"))
    elif not isinstance(description, str) or not description.strip():
        problems.append(Problem(doc.rel_path, "description must be a non-empty string"))
    else:
        if "\n" in description or "\r" in description:
            problems.append(Problem(doc.rel_path, "description must be one line"))
        if '"' in description:
            problems.append(
                Problem(doc.rel_path, "description must not contain a double quote")
            )
        if len(_RE_SENTENCE_END.findall(description)) < 2:
            problems.append(
                Problem(
                    doc.rel_path,
                    "description needs two sentences: what the document covers, "
                    "then what kind of document it is",
                )
            )
    if not doc.title:
        problems.append(
            Problem(
                doc.rel_path,
                "the first heading must be the H1 title "
                "(# Title, or a reST title with an underline)",
            )
        )
    return problems


def parse_doc(path: Path, source_dir: Path) -> tuple[Doc, list[Problem]]:
    """Parse one README.<ext> file and lint it on its own."""
    rel_path = path.relative_to(source_dir).as_posix()
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        meta, problems, body_start = parse_md(text, rel_path)
        title = _md_h1(text.splitlines()[body_start:])
    elif path.suffix == ".rst":
        meta, problems = parse_rst(text, rel_path)
        title = _rst_title(text.splitlines())
    else:
        meta, problems, cells = parse_ipynb(text, rel_path)
        title = _ipynb_h1(cells)
    doc = Doc(path=path, rel_path=rel_path, meta=meta, title=title)
    return doc, problems + _lint_meta(doc)


# --- the whole source folder --------------------------------------------------
def scan_docs(source_dir: Path) -> tuple[list[Doc], list[Problem]]:
    """
    Discover, parse and lint every document below ``source_dir``.

    Returns the documents (parents before children) and every problem, including
    the cross-document ones: a folder with two README files, a duplicate doc_id
    (compared case-insensitively, as Sphinx labels are), a missing home page.
    """
    docs: list[Doc] = list()
    problems: list[Problem] = list()
    folders: dict[str, str] = dict()
    owners: dict[str, str] = dict()
    for path in discover_doc_files(source_dir):
        doc, doc_problems = parse_doc(path, source_dir)
        docs.append(doc)
        problems.extend(doc_problems)
        folder = path.parent.relative_to(source_dir).as_posix()
        if folder in folders:
            problems.append(
                Problem(
                    doc.rel_path,
                    f"second document in one folder, next to {folders[folder]}",
                )
            )
        else:
            folders[folder] = doc.rel_path
        if doc.doc_id and DOC_ID_PATTERN.match(doc.doc_id):
            key = doc.doc_id.lower()
            if key in owners:
                problems.append(
                    Problem(
                        doc.rel_path,
                        f"duplicate doc_id {doc.doc_id!r}, also used by {owners[key]}",
                    )
                )
            else:
                owners[key] = doc.rel_path
    if "." not in folders:
        problems.append(
            Problem(
                ".", "no home page: README.md (or .rst / .ipynb) in the source folder"
            )
        )
    return docs, problems


# --- notebook to Markdown -----------------------------------------------------
#: An output longer than this is cut, with a note saying how much was left out.
NB_OUTPUT_MAX_LINES = 30
NB_OUTPUT_MAX_CHARS = 3000
_RE_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_RE_BACKTICKS = re.compile(r"`{3,}")


def _cell_text(value: object) -> str:
    return "".join(value) if isinstance(value, list) else str(value or "")


def _fence(text: str, info: str = "") -> str:
    """``text`` in a backtick fence longer than any backtick run inside it."""
    longest = max((len(m) for m in _RE_BACKTICKS.findall(text)), default=2)
    marker = "`" * max(3, longest + 1)
    return f"{marker}{info}\n{text.rstrip()}\n{marker}"


def _cut(text: str) -> str:
    lines = text.rstrip().splitlines()
    cut_lines = lines[:NB_OUTPUT_MAX_LINES]
    cut = "\n".join(cut_lines)
    if len(cut) > NB_OUTPUT_MAX_CHARS:
        cut = cut[:NB_OUTPUT_MAX_CHARS]
    if cut != "\n".join(lines):
        cut += f"\n... ({len(lines)} lines, {len(text)} characters in all; cut)"
    return cut


def _render_output(output: dict) -> str | None:
    """One code cell output as Markdown, or None to drop it."""
    kind = output.get("output_type")
    if kind == "stream":
        return _fence(_cut(_cell_text(output.get("text"))), "text")
    if kind == "error":
        trace = "\n".join(output.get("traceback") or [])
        trace = (
            _RE_ANSI.sub("", trace) or f"{output.get('ename')}: {output.get('evalue')}"
        )
        return _fence(_cut(trace), "text")
    data = output.get("data") or {}
    if "text/markdown" in data:
        return _cut(_cell_text(data["text/markdown"]))
    # An image's text/plain is only its repr (<Figure size 640x480 ...>).
    images = [k for k in data if k.startswith("image/")]
    if images:
        return f"*({images[0]} output not included)*"
    if "text/plain" in data:
        return _fence(_cut(_cell_text(data["text/plain"])), "text")
    if data:
        return f"*({next(iter(data))} output not included)*"
    return None


def _front_matter_value(value: object) -> str | None:
    if isinstance(value, list) and all(
        isinstance(v, str) and _is_bare_word(v) for v in value
    ):
        return f"[{', '.join(value)}]"
    if isinstance(value, str) and "\n" not in value and '"' not in value:
        return value if _is_bare_word(value) else f'"{value}"'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return None


def notebook_to_markdown(text: str, source_name: str = "README.ipynb") -> str:
    """
    A notebook (its JSON text) as compact Markdown for agents:

    - front matter from the notebook metadata (doc_id, description, tags, ...,
      in the strict format of ``parse_md``), plus ``source`` naming the notebook;
    - Markdown cells as they are (they are MyST already);
    - code cells in a fence of the kernel's language, each output after it
      as a ``text`` fence (or Markdown), long outputs cut, images and HTML
      replaced by a one-line note;
    - raw cells dropped, as the HTML build drops them.
    """
    data = json.loads(text)
    meta = data.get("metadata", {})
    language = (
        (meta.get("kernelspec") or {}).get("language")
        or (meta.get("language_info") or {}).get("name")
        or ""
    )
    head = ["---"]
    for key, value in meta.items():
        if key in ("kernelspec", "language_info") or not re.match(rf"^{_RE_KEY}$", key):
            continue
        rendered = _front_matter_value(value)
        if rendered is not None:
            head.append(f"{key}: {rendered}")
    head.append(f'source: "{source_name}"')
    head.append("---")
    blocks = ["\n".join(head)]
    for cell in data.get("cells", []):
        kind = cell.get("cell_type")
        source = _cell_text(cell.get("source")).strip()
        if kind == "markdown":
            if source:
                blocks.append(source)
        elif kind == "code":
            if source:
                blocks.append(_fence(source, language))
            for output in cell.get("outputs", []):
                rendered = _render_output(output)
                if rendered:
                    blocks.append(rendered)
    return "\n\n".join(blocks) + "\n"


# --- outputs ------------------------------------------------------------------
def new_doc_id() -> str:
    """A new random doc_id: 12 characters from [A-Za-z]."""
    return "".join(secrets.choice(string.ascii_letters) for _ in range(12))


def render_llms_txt(docs: list[Doc], site_url: str) -> str:
    """
    llms.txt: the home page's title and description as the header, then one
    line per document, indented by folder depth:

        - [<H1 title>](<site_url>/p/<doc_id>.md): <description>
    """
    site = site_url.rstrip("/")
    home = next((d for d in docs if d.depth == 0), None)
    title = (home.title if home else None) or "Knowledge Base"
    summary = (home.description if home else None) or ""
    lines = [
        f"# {title}",
        "",
        f"> {summary}".rstrip(),
        "",
        "Each link below is a document's plain text at its permalink, "
        f"{site}/p/<doc_id>.md: the raw MyST Markdown or reStructuredText source, or for "
        "a Jupyter notebook a Markdown copy of it. "
        "A {ref}`<doc_id>` mark in a source links to another document: read it at "
        f"{site}/p/<doc_id>.md.",
        "",
    ]
    for doc in docs:
        if doc.depth == 0:
            continue
        line = f"{'  ' * (doc.depth - 1)}- [{doc.title or doc.docname}]({doc.raw_url(site)})"
        if doc.description:
            line += f": {doc.description}"
        lines.append(line)
    return "\n".join(lines) + "\n"
