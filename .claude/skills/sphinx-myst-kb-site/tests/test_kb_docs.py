# -*- coding: utf-8 -*-

"""
Tests of the skill's standard-library scripts. Run them with pytest from the
repository root: ``pytest .claude/skills/sphinx-myst-kb-site/tests``.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import kb_docs  # noqa: E402
import nb_to_md  # noqa: E402
import write_permalink_sources  # noqa: E402

DOC_ID = "UxFDfuiOJDuv"
DESC = "Covers X and Y. A demo."


def write_md(folder: Path, front: str, body: str = "# Title\n") -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "README.md"
    path.write_text(f"---\n{front}---\n\n{body}", encoding="utf-8")
    return path


def messages(problems) -> str:
    return "\n".join(str(p) for p in problems)


# --- front matter -------------------------------------------------------------
def test_parse_md_values():
    text = (
        "---\n"
        f"doc_id: {DOC_ID}\n"
        f'description: "{DESC}"\n'
        "tags: [a, b-c]\n"
        "# a comment\n"
        'created_at: "2026-11-06"\n'
        "---\n"
        "# Title\n"
    )
    meta, problems, body_start = kb_docs.parse_md(text, "README.md")
    assert problems == []
    assert meta == {
        "doc_id": DOC_ID,
        "description": DESC,
        "tags": ["a", "b-c"],
        "created_at": "2026-11-06",
    }
    assert text.splitlines()[body_start] == "# Title"


def test_parse_md_rejects_yaml_traps():
    for line in [
        "created_at: 2026-11-06",  # a date
        "draft: yes",  # a boolean
        "title: two words",  # not one word
        "tags: [a b]",  # a list item with a space
        "empty:",  # no value
        'description: "say \\"hi\\""',  # escapes
    ]:
        _, problems, _ = kb_docs.parse_md(f"---\n{line}\n---\n", "README.md")
        assert problems, line


def test_parse_md_description_must_be_quoted():
    _, problems, _ = kb_docs.parse_md("---\ndescription: word\n---\n", "README.md")
    assert "double-quoted" in messages(problems)


def test_parse_md_front_matter_shape():
    _, problems, _ = kb_docs.parse_md("# Title\n", "README.md")
    assert "no front matter" in messages(problems)
    _, problems, _ = kb_docs.parse_md("---\ndoc_id: x\n", "README.md")
    assert "not closed" in messages(problems)


def test_parse_rst():
    text = f":doc_id: {DOC_ID}\n:description: {DESC}\n\nTitle\n=====\n"
    meta, problems = kb_docs.parse_rst(text, "README.rst")
    assert problems == []
    assert meta == {"doc_id": DOC_ID, "description": DESC}
    _, problems = kb_docs.parse_rst(":description: one\n  two\n", "README.rst")
    assert "one line" in messages(problems)


# --- titles -------------------------------------------------------------------
def test_md_h1():
    assert kb_docs._md_h1(["# Learn C#"]) == "Learn C#"
    assert kb_docs._md_h1(["# Title #"]) == "Title"
    assert kb_docs._md_h1(["## Sub", "# Title"]) is None  # H1 must come first
    # a heading inside a code fence is not a heading
    assert kb_docs._md_h1(["```", "# not", "```", "# Title"]) == "Title"
    # a fence line with an info string ("```python") never closes a fence
    lines = ["```", "```python", "# not", "```", "# Title"]
    assert kb_docs._md_h1(lines) == "Title"


def test_rst_title():
    assert kb_docs._rst_title([":doc_id: x", "", "Title", "====="]) == "Title"
    assert kb_docs._rst_title(["=====", "Title", "====="]) == "Title"
    assert kb_docs._rst_title(["Title", "=="]) is None  # underline too short


# --- lint of the whole folder -------------------------------------------------
def test_scan_docs_ok(tmp_path):
    write_md(tmp_path, f'doc_id: {DOC_ID}\ndescription: "{DESC}"\n')
    write_md(tmp_path / "01-a", f'doc_id: abcdefghijkl\ndescription: "{DESC}"\n')
    write_md(tmp_path / "_static", "broken\n")  # not a document folder
    docs, problems = kb_docs.scan_docs(tmp_path)
    assert problems == []
    assert [d.docname for d in docs] == ["README", "01-a/README"]


def test_scan_docs_problems(tmp_path):
    write_md(tmp_path / "a", f'doc_id: {DOC_ID}\ndescription: "One sentence."\n')
    write_md(tmp_path / "b", f'doc_id: {DOC_ID.lower()}\ndescription: "{DESC}"\n')
    (tmp_path / "b" / "README.rst").write_text("Title\n=====\n", encoding="utf-8")
    write_md(tmp_path / "c", 'doc_id: short\ndescription: "A. B."\n', body="## x\n")
    _, problems = kb_docs.scan_docs(tmp_path)
    text = messages(problems)
    assert "no home page" in text
    assert "two sentences" in text
    assert "duplicate doc_id" in text  # compared case-insensitively
    assert "second document in one folder" in text
    assert "12 characters" in text
    assert "first heading must be the H1" in text


# --- notebooks ----------------------------------------------------------------
def notebook(cells) -> str:
    return json.dumps(
        {
            "metadata": {
                "doc_id": DOC_ID,
                "description": DESC,
                "tags": ["a"],
                "kernelspec": {"language": "python"},
            },
            "cells": cells,
        }
    )


def test_notebook_to_markdown():
    text = kb_docs.notebook_to_markdown(
        notebook(
            [
                {"cell_type": "markdown", "source": ["# Title\n", "Text"]},
                {
                    "cell_type": "code",
                    "source": "print(1)",
                    "outputs": [
                        {"output_type": "stream", "text": "1\n"},
                        {"output_type": "display_data", "data": {"image/png": "x"}},
                        {
                            "output_type": "execute_result",
                            "data": {"text/plain": "\n".join(map(str, range(50)))},
                        },
                    ],
                },
                {"cell_type": "raw", "source": "dropped"},
            ]
        )
    )
    head = text.split("\n---\n", 1)[0]
    assert f"doc_id: {DOC_ID}" in head
    assert f'description: "{DESC}"' in head
    assert "tags: [a]" in head
    assert 'source: "README.ipynb"' in head
    assert "kernelspec" not in head
    assert "```python\nprint(1)\n```" in text
    assert "*(image/png output not included)*" in text
    assert "(50 lines" in text  # long output cut
    assert "dropped" not in text
    # the copy passes the same strict front matter rules as a .md document
    _, problems, _ = kb_docs.parse_md(text, "README.md")
    assert problems == []


def test_fence_longer_than_content():
    assert kb_docs._fence("a ```` b").startswith("`````")


def test_nb_to_md_refuses_output_inside_source(tmp_path):
    assert nb_to_md._main(source_dir=tmp_path, output_dir=tmp_path / "x") == 1


# --- build outputs ------------------------------------------------------------
def test_render_llms_txt(tmp_path):
    write_md(tmp_path, f'doc_id: {DOC_ID}\ndescription: "{DESC}"\n', "# Home\n")
    write_md(tmp_path / "a", f'doc_id: abcdefghijkl\ndescription: "{DESC}"\n')
    docs, _ = kb_docs.scan_docs(tmp_path)
    text = kb_docs.render_llms_txt(docs, "https://kb.example.com/")
    assert text.startswith("# Home\n\n> Covers X and Y. A demo.\n")
    assert f"- [Title](https://kb.example.com/p/abcdefghijkl.md): {DESC}" in text


def test_write_permalink_sources(tmp_path):
    source = tmp_path / "source"
    html = tmp_path / "html"
    write_md(source, f'doc_id: {DOC_ID}\ndescription: "{DESC}"\n')
    # the Sphinx copy is missing: fail
    assert write_permalink_sources._main(source_dir=source, directory=html) == 1
    (html / "_sources").mkdir(parents=True)
    (html / "_sources" / "README.md").write_text("text", encoding="utf-8")
    assert write_permalink_sources._main(source_dir=source, directory=html) == 0
    assert (html / "p" / f"{DOC_ID}.md").read_text(encoding="utf-8") == "text"
