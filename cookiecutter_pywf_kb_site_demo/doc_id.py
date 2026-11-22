# -*- coding: utf-8 -*-

"""
Stable document IDs and document files of the knowledge base.

Every knowledge base document is one folder with a ``README.md``,
``README.rst``, or ``README.ipynb`` file. Its ``doc_id`` metadata key is a
random 12 character ``[A-Za-z]`` string: the document's identity, which
never changes, even when the folder is renamed or moved, so every link to the
document is built from it.

Sphinx reads the metadata itself (``env.metadata``); the strict format rules
and the doc_id generator live in the ``sphinx-myst-kb-site`` skill's scripts
(``mise run lint-doc``, ``mise run new-doc-id``).
"""

import typing as T
import re
from pathlib import Path

#: Regular expression a valid doc_id matches.
DOC_ID_PATTERN = re.compile(r"^[A-Za-z]{12}$")

#: The base name of the file that holds a document, without extension.
DOC_FILE_STEM = "README"

#: Source file extensions a document may use, in lookup order.
DOC_FILE_SUFFIXES = (".md", ".rst", ".ipynb")


def is_valid_doc_id(doc_id: T.Any) -> bool:
    """
    Return True if ``doc_id`` is a string matching :data:`DOC_ID_PATTERN`.
    """
    return isinstance(doc_id, str) and bool(DOC_ID_PATTERN.match(doc_id))


def find_doc_file(dir_folder: Path) -> Path | None:
    """
    Return the ``README.<ext>`` document file in a folder, or None.
    """
    for suffix in DOC_FILE_SUFFIXES:
        path = dir_folder / f"{DOC_FILE_STEM}{suffix}"
        if path.exists():
            return path
    return None
