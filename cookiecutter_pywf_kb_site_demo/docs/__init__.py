# -*- coding: utf-8 -*-

"""
Data passed to the ``{jinja} doc_data`` directive in the docs
(see ``jinja_contexts`` in ``docs/source/conf.py``).
"""

#: A tiny "dataframe": one tuple per row, ``(id, name)``. Rendered as a table
#: by the ``{jinja} doc_data`` demo in the knowledge base docs.
users = [
    (1, "alice"),
    (2, "bob"),
]

doc_data = {
    "users": users,
}
