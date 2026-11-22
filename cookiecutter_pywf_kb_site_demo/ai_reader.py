# -*- coding: utf-8 -*-

"""
The "AI Reader" chatbot deep link shown right below the title of every page.

The link opens a fallback page of ``esc_mini_tools_chatbot_deeplink`` that
carries a prompt in its URL fragment: the reader copies it with one click and
continues in Claude, ChatGPT, Gemini or another chatbot, which then reads the
document and rewrites it in English.

The home page is the exception: nobody asks about the home page itself, so its
link carries a site-wide prompt instead (``build_ai_site_prompt``): answer
questions from the whole knowledge base, starting at ``<site>/llms.txt``, the
way the ``sphinx-myst-kb-query`` skill does, in a few hundred characters.

The prompt names one URL, ``<site>/p/<doc_id>.md``: the document's plain-text
source (a real file, not a redirect). It leaves out the web page
``<site>/p/<doc_id>``, an HTML redirect target a chatbot might fetch instead.
So the link depends on the doc_id alone
and survives every move of the document folder. :mod:`cookiecutter_pywf_kb_site_demo.sphinx_ext`
inserts it at build time; source files never contain it.

The encoding is the one of ``esc_mini_tools_chatbot_deeplink.build_deeplink``
(JavaScript ``encodeURIComponent``), reimplemented here so the docs build needs
no extra dependency.
"""

import html
from urllib.parse import quote

#: The fallback page prefix, everything up to and including ``#q=``.
AI_READER_BASE_URL = (
    "https://mini-tools.easyscalecloud.com/tools/chatbot-deeplink-fallback#q="
)

#: Characters ``encodeURIComponent`` leaves alone besides letters, digits, ``-_.``.
_SAFE = "!~*'()"


def build_ai_reader_prompt(doc_id: str, site_url: str) -> str:
    """
    The prompt the AI Reader link hands to the chatbot for one document.
    """
    site = site_url.rstrip("/")
    # Only the plain text: a second URL (the HTML page /p/<doc_id>) only gives
    # the chatbot a choice to get wrong. "plain-text source", not "Markdown":
    # a few documents are reStructuredText.
    return (
        f"Please read {site}/p/{doc_id}.md, the full plain-text source of a "
        "knowledge base document, and rewrite it faithfully in English "
        "using Markdown in an Artifact or Canvas for me to read, "
        "then I will ask questions based on it."
    )


def build_ai_site_prompt(site_url: str) -> str:
    """
    The prompt of the home page link: answer questions from the whole site,
    found through ``llms.txt`` (a short English version of the ``sphinx-myst-kb-query``
    skill).
    """
    site = site_url.rstrip("/")
    return (
        f"Read {site}/llms.txt, the index of a knowledge base, "
        "and answer my questions from it: fetch the .md links of the relevant "
        "documents, follow their links as needed, and cite the pages you used. "
        "Answer in my language. "
        "I will ask next."
    )


def _deeplink(prompt: str) -> str:
    """
    The deep link URL of a prompt, byte for byte the URL that
    ``esc_mini_tools_chatbot_deeplink.build_deeplink`` returns for it.
    """
    return AI_READER_BASE_URL + quote(prompt, safe=_SAFE, encoding="utf-8")


def build_ai_reader_url(doc_id: str, site_url: str, is_home: bool = False) -> str:
    """
    The full deep link URL of one document; for the home page
    (``is_home=True``) the site-wide one.
    """
    if is_home:
        return _deeplink(build_ai_site_prompt(site_url=site_url))
    return _deeplink(build_ai_reader_prompt(doc_id=doc_id, site_url=site_url))


def render_ai_reader_html(doc_id: str, site_url: str, is_home: bool = False) -> str:
    """
    The HTML block inserted below the H1 of a page. ``data-pagefind-ignore``
    keeps the same line on every page out of the search index. On the home
    page (``is_home=True``) the link asks about the whole site.
    """
    url = build_ai_reader_url(doc_id=doc_id, site_url=site_url, is_home=is_home)
    href = html.escape(url)
    label = (
        "Ask AI about this whole knowledge base:"
        if is_home
        else "Read this document in English or ask questions:"
    )
    return (
        '<blockquote class="kb-ai-reader" data-pagefind-ignore><p>'
        "<code>🌐 AI Reader</code> "
        f"<strong>{label}</strong> "
        f'<a href="{href}" target="_blank" rel="noopener">'
        "<strong>Open in Claude, ChatGPT, or Gemini ↗</strong></a>"
        "</p></blockquote>"
    )
