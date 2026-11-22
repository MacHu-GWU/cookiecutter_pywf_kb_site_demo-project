# -*- coding: utf-8 -*-

from cookiecutter_pywf_kb_site_demo.ai_reader import AI_READER_BASE_URL
from cookiecutter_pywf_kb_site_demo.ai_reader import build_ai_reader_prompt
from cookiecutter_pywf_kb_site_demo.ai_reader import build_ai_site_prompt
from cookiecutter_pywf_kb_site_demo.ai_reader import build_ai_reader_url
from cookiecutter_pywf_kb_site_demo.ai_reader import render_ai_reader_html

from urllib.parse import unquote


def test_build_ai_reader_prompt():
    prompt = build_ai_reader_prompt(
        doc_id="UxFDfuiOJDuv", site_url="https://kb.example.com/"
    )
    assert "https://kb.example.com/p/UxFDfuiOJDuv.md," in prompt
    # one URL only: the plain text, never the HTML page
    assert prompt.count("https://") == 1
    assert "//p/" not in prompt


def test_build_ai_reader_url():
    url = build_ai_reader_url(doc_id="UxFDfuiOJDuv", site_url="https://kb.example.com")
    assert url.startswith(AI_READER_BASE_URL)
    encoded = url[len(AI_READER_BASE_URL) :]
    # encodeURIComponent: spaces, "/" and ":" are encoded, "." is not
    assert " " not in encoded
    assert "%20" in encoded
    assert "%2F" in encoded
    assert "%3A" in encoded
    assert "UxFDfuiOJDuv.md" in encoded
    assert unquote(encoded) == build_ai_reader_prompt(
        doc_id="UxFDfuiOJDuv", site_url="https://kb.example.com"
    )


def test_build_ai_site_prompt():
    prompt = build_ai_site_prompt(site_url="https://kb.example.com/")
    assert "https://kb.example.com/llms.txt" in prompt
    assert "//llms" not in prompt
    # short enough to read at a glance
    assert len(prompt) <= 300
    url = build_ai_reader_url(
        doc_id="UxFDfuiOJDuv", site_url="https://kb.example.com", is_home=True
    )
    assert unquote(url[len(AI_READER_BASE_URL) :]) == build_ai_site_prompt(
        site_url="https://kb.example.com"
    )


def test_render_ai_reader_html():
    block = render_ai_reader_html(
        doc_id="UxFDfuiOJDuv", site_url="https://kb.example.com"
    )
    assert block.startswith('<blockquote class="kb-ai-reader" data-pagefind-ignore>')
    assert "🌐 AI Reader" in block
    # "'" is left unencoded by encodeURIComponent; the href must still be safe
    assert "'" not in block.split('href="', 1)[1].split('"', 1)[0]
    assert "Read this document" in block
    home = render_ai_reader_html(
        doc_id="UxFDfuiOJDuv", site_url="https://kb.example.com", is_home=True
    )
    assert "Ask AI about this whole knowledge base" in home
    assert "llms.txt" in home


if __name__ == "__main__":
    from cookiecutter_pywf_kb_site_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_pywf_kb_site_demo.ai_reader",
        preview=False,
    )
