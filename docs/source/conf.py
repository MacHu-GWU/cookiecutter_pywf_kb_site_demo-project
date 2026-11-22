# -*- coding: utf-8 -*-

"""
Sphinx configuration of the knowledge base site.

Layout: one document = one folder holding a ``README.md``, ``README.rst`` or
``README.ipynb`` file (``README`` so that GitHub renders it too). The home
page is ``docs/source/README.md``. See
:mod:`cookiecutter_pywf_kb_site_demo.sphinx_ext`.
"""

import os
from datetime import datetime
from importlib.metadata import metadata

# -- Project ------------------------------------------------------------------
package_name = "cookiecutter_pywf_kb_site_demo"
_meta = metadata(package_name)

# Extract author from "Author-email: Name <email@example.com>" format
_author_email_raw = _meta.get("Author-email", "")
if _author_email_raw and "<" in _author_email_raw:
    package_author = _author_email_raw.split("<")[0].strip()
else:
    package_author = _meta.get("Author", "Unknown")

# The site title: sidebar, browser tab, and _extra/404.html (keep them the same).
project = "KB Site Demo"
author = package_author
copyright = f"{datetime.now().year}, {author}"

# Sets <html lang="...">. Pagefind picks its word segmentation from it: a
# Chinese site uses "zh_CN", together with html_search_language = "zh" below
# and the jieba package in the doc extra of pyproject.toml.
language = "en"

root_doc = "README"

extensions = [
    # MyST-NB = myst-parser + notebooks: .md pages and the Markdown cells of
    # .ipynb pages are both parsed as MyST, so no pandoc is needed.
    "myst_nb",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_jinja",
    "sphinxcontrib.mermaid",
    "sphinx.ext.mathjax",
    "cookiecutter_pywf_kb_site_demo.sphinx_ext",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}

templates_path = ["_templates"]

exclude_patterns = [
    "**/.ipynb_checkpoints",
    # Writing material of the blog-* skills (blog-base ref/02-spec/01-repository-layout.md):
    # the plan and other people's sources stay in git but never reach the site.
    "**/plan.md",
    "**/resources",
]

pygments_style = "monokai"
pygments_dark_style = "monokai"

# -- MyST Markdown ------------------------------------------------------------
myst_enable_extensions = [
    "colon_fence",  # :::{card} ... ::: for sphinx-design
    "deflist",
    "fieldlist",
    "tasklist",
    "attrs_inline",
    "attrs_block",
    "html_image",
    "dollarmath",
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
html_theme_options = {
    "sidebar_hide_name": False,
}
html_static_path = ["_static"]
html_css_files = [
    "css/custom-style.css",
    "css/kb.css",
]
html_js_files = [
    "js/sorttable.js",
    "js/kb-search.js",
    "js/kb-copy.js",
]
html_logo = "./_static/cookiecutter_pywf_kb_site_demo-logo.png"  # sidebar logo
# <link rel="icon">: a PNG under its real name, so it is served as image/png.
html_favicon = "./_static/cookiecutter_pywf_kb_site_demo-favicon.png"
# Copied to the site root as is: _headers (Cloudflare Pages), robots.txt,
# favicon.ico (browsers also ask for /favicon.ico) and 404.html (without it
# Cloudflare Pages answers every unknown path with the home page and status 200).
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

# -- reST ---------------------------------------------------------------------
# color roles such as :red:`text` (see _static/.custom-style.rst)
with open(
    os.path.join(os.path.dirname(__file__), "_static", ".custom-style.rst"),
    "rb",
) as f:
    rst_prolog = "\n" + f.read().decode("utf-8") + "\n"

# -- sphinx-jinja -------------------------------------------------------------
# ``{jinja} doc_data`` renders its body with these variables, then parses the
# result in the page's own syntax (MyST in .md, reST in .rst).
from cookiecutter_pywf_kb_site_demo.docs import doc_data

jinja_contexts = {
    "doc_data": {
        "doc_data": doc_data,
    },
}

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
