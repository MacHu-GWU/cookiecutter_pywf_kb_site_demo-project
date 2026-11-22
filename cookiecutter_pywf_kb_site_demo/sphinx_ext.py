# -*- coding: utf-8 -*-

"""
Sphinx extension of the knowledge base. Enable it in ``conf.py``::

    extensions = [
        ...,
        "cookiecutter_pywf_kb_site_demo.sphinx_ext",
    ]

The core is the same as the ``sphinx-myst-kb-site`` skill's
``examples/docs-source/_ext/kb_ext.py``; this site adds the AI Reader link.

What it does:

1. **Validates the doc_id**: every document must have one, it must match
   :data:`~cookiecutter_pywf_kb_site_demo.doc_id.DOC_ID_PATTERN`, and it must be unique. A bad
   doc_id stops the build. Sphinx itself reads each document's metadata into
   ``env.metadata[docname]``: MyST from the front matter, docutils from the
   top field list of a ``.rst`` file, MyST-NB from the notebook metadata.
2. **Registers each doc_id as a label** at the top of its document, so any
   page can write ``{ref}`<doc_id>``` (MyST) or ``:ref:`<doc_id>``` (reST);
   the link text is the document title, and the link follows the document
   wherever its folder moves.
3. **The AI Reader link**: a chatbot deep link right below the H1 of every
   page (see :mod:`cookiecutter_pywf_kb_site_demo.ai_reader`).
4. **The ``kb-toctree`` directive** lists the child folders of the current
   document that hold a ``README.<ext>`` file, sorted by folder name. No
   toctree entry is kept by hand.
5. **Page context**: each HTML page gets ``kb_doc_id``, ``kb_permalink`` (the
   page), ``kb_text_url`` and ``kb_text_path`` (the agent text
   ``p/<doc_id>.md``, absolute and relative) for templates, and a
   ``<link rel="alternate">`` to the agent text in its head.
6. **Build outputs**: ``_redirects`` (Cloudflare Pages: ``/p/<doc_id>`` to the
   page), ``kb-titles.json`` (title index for the search box), and a root
   ``index.html`` copied from ``README.html``. The agent text files, ``llms.txt``
   and the strict metadata lint come from the skill's scripts (``build-doc.sh``).
"""

import typing as T
import json
import shutil
from pathlib import Path

from docutils import nodes
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree
from sphinx.environment import BuildEnvironment
from sphinx.errors import ExtensionError

from .ai_reader import render_ai_reader_html
from .doc_id import DOC_FILE_STEM
from .doc_id import find_doc_file
from .doc_id import is_valid_doc_id

KEY_DOC_ID = "doc_id"


# --- kb-toctree ---------------------------------------------------------------
class KbTocTree(TocTree):
    """
    A ``toctree`` whose entries are the child folders of the current document
    that hold a ``README.<ext>`` file, sorted by folder name (so a ``01-``
    prefix sets the order). Accepts every ``toctree`` option. Extra entries in
    the directive body come after the generated ones.
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
    Register the doc_id label and insert the AI Reader link. Connected with
    priority 900: after Sphinx collected the title and the metadata.
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
    _insert_ai_reader(
        doctree,
        doc_id=doc_id,
        site_url=app.config.kb_site_url,
        is_home=docname == app.config.root_doc,
    )


def _insert_ai_reader(doctree, doc_id: str, site_url: str, is_home: bool = False):
    """
    Put the AI Reader deep link (:mod:`cookiecutter_pywf_kb_site_demo.ai_reader`) right below the
    H1 of the page: after the title of the first top level section. Done on
    the doctree, not in a template: the H1 is part of the rendered body, so
    no template can put anything between it and the text. A raw HTML node,
    so non-HTML builders skip it. The home page gets the site-wide link.
    """
    section = next(
        (node for node in doctree.children if isinstance(node, nodes.section)), None
    )
    if section is None or not section.children:
        return
    if not isinstance(section.children[0], nodes.title):
        return
    block = nodes.raw(
        "",
        render_ai_reader_html(doc_id=doc_id, site_url=site_url, is_home=is_home),
        format="html",
    )
    section.insert(1, block)


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


def on_html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, T.Any],
    doctree,
):
    """
    Expose ``kb_doc_id``, ``kb_permalink``, ``kb_text_url`` and
    ``kb_text_path`` to templates, and link the agent text from the page head.
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
    ``(docname, title, metadata)`` of every document with a doc_id, parents
    before children, siblings by folder name.
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
    Write the Cloudflare Pages ``_redirects`` file: one 302 rule per document,
    ``/p/<doc_id>`` to its page (why 302: the skill's references/gotchas.md#redirect-rules).
    """
    lines = list()
    for docname, _, meta in _iter_docs(app.env):
        # Cloudflare Pages serves /a/b.html at /a/b, so link there directly.
        lines.append(f"/p/{meta[KEY_DOC_ID]}  /{docname}  302")
    outdir.joinpath("_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_titles_json(app: Sphinx, outdir: Path):
    """
    Write ``kb-titles.json``: ``[{title, url, description}]`` of every document.
    The search box matches the query as a plain substring of the titles, so a
    title hit never depends on how CJK text was segmented
    (see ``_static/js/kb-search.js``).
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
    """
    Sphinx entry point of the knowledge base extension.
    """
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
