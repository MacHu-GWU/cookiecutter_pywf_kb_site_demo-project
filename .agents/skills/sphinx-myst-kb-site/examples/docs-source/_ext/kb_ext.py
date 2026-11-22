# -*- coding: utf-8 -*-

"""
Sphinx extension of the knowledge base: stable doc_id links, auto toctree,
Cloudflare Pages redirects, agent text links. One self-contained file;
conf.py loads it with ``sys.path.insert(0, <docs/source>/_ext)`` and
``extensions = ["kb_ext"]``.

Layout it assumes: one document = one folder with a ``README.md``,
``README.rst`` or ``README.ipynb`` file. Sphinx itself reads each document's
metadata into ``env.metadata[docname]``: MyST from the front matter, docutils
from the field list at the top of a ``.rst`` file, MyST-NB from the notebook
level metadata. ``doc_id`` (12 random ``[A-Za-z]``) is required and never
changes. The strict metadata format is enforced before the build by the
skill's scripts/lint_docs.py; this extension only checks doc_id.

What the extension does:

1. Validates doc_id: present, well formed, unique. A bad one stops the build.
2. Registers each doc_id as a label at the top of its document, so
   ``{ref}`<doc_id>``` (MyST) or ``:ref:`<doc_id>``` (reST) links to it with
   the document title as text, wherever the folder moves.
3. ``kb-toctree`` directive: a toctree of the child folders that hold a
   ``README.<ext>`` file, sorted by folder name.
4. Template context: ``kb_doc_id``, ``kb_permalink`` (the page),
   ``kb_text_url`` and ``kb_text_path`` (the agent text ``p/<doc_id>.md``),
   and a ``<link rel="alternate">`` to the agent text in every page's head.
5. Build outputs: ``_redirects`` (``/p/<doc_id>`` to the page),
   ``kb-titles.json`` (title index for the search box), and ``index.html``
   copied from ``README.html``. The agent text files and llms.txt come from
   the skill's scripts (build-doc.sh).
"""

import typing as T
import json
import re
import shutil
from pathlib import Path

from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree
from sphinx.environment import BuildEnvironment
from sphinx.errors import ExtensionError

KEY_DOC_ID = "doc_id"
DOC_ID_PATTERN = re.compile(r"^[A-Za-z]{12}$")
DOC_FILE_STEM = "README"
DOC_FILE_SUFFIXES = (".md", ".rst", ".ipynb")


# --- doc_id and document files ------------------------------------------------
def is_valid_doc_id(doc_id: T.Any) -> bool:
    return isinstance(doc_id, str) and bool(DOC_ID_PATTERN.match(doc_id))


def find_doc_file(dir_folder: Path) -> Path | None:
    for suffix in DOC_FILE_SUFFIXES:
        path = dir_folder / f"{DOC_FILE_STEM}{suffix}"
        if path.exists():
            return path
    return None


# --- kb-toctree ---------------------------------------------------------------
class KbTocTree(TocTree):
    """
    A toctree of the child folders that hold a ``README.<ext>`` file, sorted by
    folder name (so a ``01-`` prefix sets the order). Accepts every toctree
    option; extra entries in the body come after the generated ones.
    """

    def run(self):
        path_doc = Path(self.env.doc2path(self.env.docname))
        entries = list()
        for dir_child in sorted(path_doc.parent.iterdir()):
            if not dir_child.is_dir() or dir_child.name[0] in "._":
                continue
            if find_doc_file(dir_child) is not None:
                entries.append(f"{dir_child.name}/{DOC_FILE_STEM}")
        entries.extend(line for line in self.content if line.strip())
        self.content = StringList(entries)
        return super().run()


# --- Sphinx events ------------------------------------------------------------
def _title(env: BuildEnvironment, docname: str) -> str:
    """The document's H1 title, or its docname when it has none."""
    return env.titles[docname].astext() if docname in env.titles else docname


def on_doctree_read(app: Sphinx, doctree):
    """
    Register the doc_id label. Connected with priority 900: after Sphinx
    collected the title and the metadata.
    """
    env = app.env
    docname = env.docname
    doc_id = env.metadata[docname].get(KEY_DOC_ID)
    if not is_valid_doc_id(doc_id):
        return  # reported in on_check_consistency
    title = _title(env, docname)
    # The :ref: role lowercases its target before the lookup, while
    # sphinx-design's ``:link-type: ref`` does not: register both spellings.
    std = env.get_domain("std")
    for label in {doc_id, doc_id.lower()}:
        std.anonlabels[label] = (docname, "")
        std.labels[label] = (docname, "", title)


def on_check_consistency(app: Sphinx, env: BuildEnvironment):
    """
    Every document has a valid, unique doc_id; otherwise stop the build.
    """
    errors = list()
    owners: dict[str, str] = dict()
    for docname in sorted(env.found_docs):
        doc_id = env.metadata.get(docname, {}).get(KEY_DOC_ID)
        if doc_id is None:
            errors.append(f"{docname}: missing {KEY_DOC_ID}")
        elif not is_valid_doc_id(doc_id):
            errors.append(f"{docname}: invalid {KEY_DOC_ID} {doc_id!r}")
        elif doc_id.lower() in owners:  # labels are case-insensitive
            errors.append(
                f"{docname}: duplicate {KEY_DOC_ID} {doc_id!r}, "
                f"also used by {owners[doc_id.lower()]}"
            )
        else:
            owners[doc_id.lower()] = docname
    if errors:
        raise ExtensionError("[kb] bad doc_id:\n  " + "\n  ".join(errors))


def on_html_page_context(app: Sphinx, pagename, templatename, context, doctree):
    """
    kb_doc_id, kb_permalink, kb_text_url and kb_text_path for the templates,
    and a link to the agent text in the page head.
    """
    env = app.env
    doc_id = env.metadata.get(pagename, {}).get(KEY_DOC_ID)
    if doc_id is None:
        return
    site = app.config.kb_site_url.rstrip("/")
    context["kb_doc_id"] = doc_id
    context["kb_permalink"] = f"{site}/p/{doc_id}"
    context["kb_text_path"] = f"p/{doc_id}.md"
    context["kb_text_url"] = f"{site}/p/{doc_id}.md"
    # <link rel="alternate"> to the agent text, so an agent that fetched the
    # HTML page finds it. A notebook's agent text is its Markdown copy.
    suffix = Path(env.doc2path(pagename)).suffix
    mimetype = {
        ".md": "text/markdown",
        ".ipynb": "text/markdown",
        ".rst": "text/x-rst",
    }.get(suffix, "text/plain")
    href = "../" * pagename.count("/") + context["kb_text_path"]
    context["metatags"] = (
        context.get("metatags", "")
        + f'\n<link rel="alternate" type="{mimetype}" href="{href}">'
    )


# --- build outputs ------------------------------------------------------------
def _iter_docs(env: BuildEnvironment) -> list[tuple[str, str, dict[str, T.Any]]]:
    """
    (docname, title, metadata) of every document, parents before children.
    """
    rows = list()
    for docname in sorted(env.found_docs, key=lambda d: d.split("/")[:-1]):
        meta = env.metadata.get(docname, {})
        if KEY_DOC_ID not in meta:
            continue
        rows.append((docname, _title(env, docname), meta))
    return rows


def write_redirects(app: Sphinx, outdir: Path):
    """
    Cloudflare Pages ``_redirects``: one 302 rule per document, ``/p/<doc_id>``
    to its page (why 302: references/gotchas.md#redirect-rules).
    """
    lines = list()
    for docname, _, meta in _iter_docs(app.env):
        # Cloudflare Pages serves /a/b.html at /a/b, so link there directly.
        lines.append(f"/p/{meta[KEY_DOC_ID]}  /{docname}  302")
    outdir.joinpath("_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_titles_json(app: Sphinx, outdir: Path):
    """
    ``kb-titles.json``: [{title, url, description}]. The search box matches the
    query as a plain substring of these titles, so a title hit never depends
    on how CJK text was segmented (see _static/js/kb-search.js).
    """
    rows = [
        {
            "title": title,
            "url": f"/{docname}.html",  # same form as Pagefind's result URLs
            "description": meta.get("description", ""),
        }
        for docname, title, meta in _iter_docs(app.env)
    ]
    outdir.joinpath("kb-titles.json").write_text(
        json.dumps(rows, ensure_ascii=False), encoding="utf-8"
    )


def on_build_finished(app: Sphinx, exc: Exception | None):
    if exc is not None or app.builder.format != "html":
        return
    outdir = Path(app.outdir)
    write_redirects(app, outdir)
    write_titles_json(app, outdir)
    # The home page is README.html; make it the site root as well.
    path_root = outdir / f"{app.config.root_doc}.html"
    path_index = outdir / "index.html"
    if path_root != path_index and path_root.exists():
        shutil.copyfile(path_root, path_index)


def setup(app: Sphinx) -> dict[str, T.Any]:
    app.add_config_value("kb_site_url", "", "html")
    app.add_directive("kb-toctree", KbTocTree)
    # after the TitleCollector and MetadataCollector (priority 500)
    app.connect("doctree-read", on_doctree_read, priority=900)
    app.connect("env-check-consistency", on_check_consistency)
    app.connect("html-page-context", on_html_page_context)
    app.connect("build-finished", on_build_finished)
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
