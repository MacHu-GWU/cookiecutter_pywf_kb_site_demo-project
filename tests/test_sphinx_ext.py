# -*- coding: utf-8 -*-

import pytest

pytest.importorskip("sphinx")  # the docs extra; the CI test job installs only "test"

from cookiecutter_pywf_kb_site_demo.sphinx_ext import KEY_DOC_ID

import json
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

CONF = """
extensions = ["myst_parser", "cookiecutter_pywf_kb_site_demo.sphinx_ext"]
root_doc = "README"
kb_site_url = "https://kb.example.com"
"""

HOME = """---
doc_id: UxFDfuiOJDuv
description: "Home. The home page."
---

# Home

See {ref}`abcdefghijkl`.

```{kb-toctree}
```
"""

CHILD = """---
doc_id: AbcdefghijkL
description: "Child. A child."
---

# Child Page
"""


def build(tmp_path: Path, child: str = CHILD) -> Path:
    src = tmp_path / "src"
    (src / "01-child").mkdir(parents=True)
    (src / "conf.py").write_text(CONF, encoding="utf-8")
    (src / "README.md").write_text(HOME, encoding="utf-8")
    (src / "01-child" / "README.md").write_text(child, encoding="utf-8")
    out = tmp_path / "out"
    app = Sphinx(
        str(src),
        str(src),
        str(out),
        str(tmp_path / "doctrees"),
        "html",
        status=None,
        warningiserror=True,
    )
    app.build()
    return out


def test_build(tmp_path):
    assert KEY_DOC_ID in HOME
    out = build(tmp_path)
    home = out.joinpath("README.html").read_text(encoding="utf-8")
    # {ref} by a lowercased doc_id finds the mixed-case label; title as text
    assert "Child Page" in home
    assert 'href="01-child/README.html"' in home
    assert "kb-ai-reader" in home
    assert (
        '<link rel="alternate" type="text/markdown" href="p/UxFDfuiOJDuv.md">' in home
    )
    assert out.joinpath("index.html").read_text(encoding="utf-8") == home
    assert out.joinpath("_redirects").read_text(encoding="utf-8").splitlines() == [
        "/p/UxFDfuiOJDuv  /README  302",
        "/p/AbcdefghijkL  /01-child/README  302",
    ]
    titles = json.loads(out.joinpath("kb-titles.json").read_text(encoding="utf-8"))
    assert titles[1] == {
        "title": "Child Page",
        "url": "/01-child/README.html",
        "description": "Child. A child.",
    }


def test_duplicate_doc_id(tmp_path):
    with pytest.raises(ExtensionError, match="duplicate doc_id"):
        build(tmp_path, child=CHILD.replace("AbcdefghijkL", "uxfdfuiojduv"))


if __name__ == "__main__":
    from cookiecutter_pywf_kb_site_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_pywf_kb_site_demo.sphinx_ext",
        preview=False,
    )
