# -*- coding: utf-8 -*-

"""
Example source file for the literalinclude demo. The ``# --- begin: <name>``
and ``# --- end: <name>`` comments mark regions that a doc page can include.
"""

import secrets
import string


# --- begin: make-id
def make_id(n: int = 12) -> str:
    alphabet = string.ascii_letters
    return "".join(secrets.choice(alphabet) for _ in range(n))


# --- end: make-id


class Store:
    """A tiny in-memory key value store."""

    def __init__(self):
        self.data = {}

    def put(self, value: str) -> str:
        # --- begin: put-body
        key = make_id()
        self.data[key] = value
        return key
        # --- end: put-body

    def get(self, key: str) -> str | None:
        return self.data.get(key)


if __name__ == "__main__":
    store = Store()
    print(store.get(store.put("hello")))
