# -*- coding: utf-8 -*-

from cookiecutter_pywf_kb_site_demo.doc_id import is_valid_doc_id
from cookiecutter_pywf_kb_site_demo.doc_id import find_doc_file


def test_is_valid_doc_id():
    assert is_valid_doc_id("UxFDfuiOJDuv") is True
    assert is_valid_doc_id("UxFDfuiOJDu") is False  # 11 chars
    assert is_valid_doc_id("UxFDfuiOJDu1") is False  # digit
    assert is_valid_doc_id(None) is False


def test_find_doc_file(tmp_path):
    assert find_doc_file(tmp_path) is None
    tmp_path.joinpath("README.ipynb").write_text("{}")
    assert find_doc_file(tmp_path).name == "README.ipynb"
    tmp_path.joinpath("README.md").write_text("")
    assert find_doc_file(tmp_path).name == "README.md"


if __name__ == "__main__":
    from cookiecutter_pywf_kb_site_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_pywf_kb_site_demo.doc_id",
        preview=False,
    )
