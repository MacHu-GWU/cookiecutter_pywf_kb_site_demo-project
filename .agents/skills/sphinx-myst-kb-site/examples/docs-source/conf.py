# -*- coding: utf-8 -*-

"""
Sphinx configuration of a knowledge base site.

Layout: one document = one folder holding a README.md, README.rst or
README.ipynb file (README, so GitHub renders the folder too). The home page is
README.md next to this file. The kb_ext extension (_ext/kb_ext.py) adds the
doc_id links, the kb-toctree directive, the redirects and the agent text links;
the skill's scripts/build_llms_txt.py writes llms.txt.

Python packages (the docs extra of the project):
    sphinx, myst-nb, sphinx-design, sphinx-copybutton, sphinx-jinja,
    sphinxcontrib-mermaid, furo; jieba for a Chinese site.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_ext"))

# -- Project ------------------------------------------------------------------
project = "My KB"
author = "Your Name"
copyright = f"{datetime.now().year}, {author}"

# Sets <html lang="...">. Pagefind picks its word segmentation from it, so a
# Chinese site uses "zh_CN" (together with html_search_language below).
language = "en"

root_doc = "README"  # docs/source/README.md is the home page

extensions = [
    # MyST-NB = myst-parser + notebooks: .md pages and the Markdown cells of
    # .ipynb pages are both parsed as MyST, so no pandoc is needed.
    "myst_nb",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_jinja",
    "sphinxcontrib.mermaid",
    "sphinx.ext.mathjax",
    "kb_ext",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}

templates_path = ["_templates"]

exclude_patterns = [
    "**/.ipynb_checkpoints",
]

# -- MyST Markdown ------------------------------------------------------------
myst_enable_extensions = [
    "colon_fence",  # :::{card} ... ::: for sphinx-design
    "deflist",
    "fieldlist",
    "tasklist",
    "attrs_inline",
    "attrs_block",
    "html_image",
    "dollarmath",  # $$ ... $$ math blocks
]
# A plain ```mermaid fence renders in PyCharm / GitHub preview AND in Sphinx.
myst_fence_as_directive = ["mermaid"]
# H1 to H3 get GitHub style anchors, so [text](#some-heading) works in a page
# (ASCII headings only: a CJK heading gets no usable HTML anchor).
myst_heading_anchors = 3

# -- MyST-NB (notebooks) ------------------------------------------------------
# Notebooks are committed with their outputs; the build never runs them.
# Raw cells are NOT rendered: write roles and directives in Markdown cells.
nb_execution_mode = "off"

# -- HTML ---------------------------------------------------------------------
html_theme = "furo"
html_title = project
html_static_path = ["_static"]
html_css_files = [
    "css/kb.css",
]
html_js_files = [
    "js/kb-search.js",
    "js/kb-copy.js",
]
# html_logo = "_static/logo.png"
# A PNG favicon under its real name, so the server sends image/png. Also put
# a real favicon.ico in _extra/: browsers ask for /favicon.ico too.
# html_favicon = "_static/favicon.png"

# Copied to the site root as is: _headers (Cloudflare Pages), robots.txt and
# 404.html (without it Cloudflare Pages answers every unknown path with the
# home page and status 200). Add a real favicon.ico here too (references/gotchas.md#favicon).
html_extra_path = ["_extra"]

# Raw source of every page at _sources/<docname>.md (not .md.txt), for agents.
html_copy_source = True
html_show_sourcelink = True
html_sourcelink_suffix = ""

# Sphinx's own search page (the fallback when Pagefind cannot load). For a
# Chinese site: html_search_language = "zh" and install jieba.
html_search_language = "en"

# -- mermaid ------------------------------------------------------------------
mermaid_d3_zoom = False

# -- sphinx-jinja -------------------------------------------------------------
# ``{jinja} doc_data`` renders its body with these variables, then parses the
# result in the page's own syntax (MyST in .md, reST in .rst).
users = [
    (1, "alice"),
    (2, "bob"),
]

jinja_contexts = {
    "doc_data": {
        "doc_data": {
            "users": users,
        },
    },
}
# -- end sphinx-jinja ---------------------------------------------------------

# -- knowledge base extension -------------------------------------------------
# The site lives at https://<KB_SUBDOMAIN>.<KB_DOMAIN> (mise.toml [env]
# locally, GitHub Actions variables in CI); build-doc.sh builds the same URL
# for build_llms_txt.py. No default here: a build without them stops instead
# of writing permalinks to a wrong site.
kb_domain = os.environ.get("KB_DOMAIN", "")
kb_subdomain = os.environ.get("KB_SUBDOMAIN", "")
if not (kb_domain and kb_subdomain):
    raise RuntimeError(
        "KB_DOMAIN / KB_SUBDOMAIN are not set (mise.toml [env]): "
        "run `mise run build-doc`"
    )
kb_site_url = f"https://{kb_subdomain}.{kb_domain}"
