---
doc_id: FmYjZdIfCMmW
description: "Includes part of a Python file in a page by comment markers or by function name with literalinclude. A code inclusion demo."
tags: [sphinx, literalinclude, python]
---

# literalinclude: Including Part of a File

In MyST, `literalinclude` is a ```` ```{literalinclude} <path> ```` fence with the same options as in reST. A path is relative to the current document; a path starting with `/` is relative to the Sphinx source folder.

Every example below includes [example.py](example.py) from this folder.

## Region markers in comments (recommended)

Mark a region of the Python file with a pair of comments:

```python
# --- begin: make-id
def make_id(n: int = 12) -> str: ...


# --- end: make-id
```

Then `:start-after:` and `:end-before:` include only what is between them; the marker lines themselves stay out:

````markdown
```{literalinclude} example.py
:language: python
:start-after: "# --- begin: make-id"
:end-before: "# --- end: make-id"
```
````

Result:

```{literalinclude} example.py
:language: python
:start-after: "# --- begin: make-id"
:end-before: "# --- end: make-id"
```

### A region inside a method, dedented

For a region inside a method, `:dedent:` removes the common indentation; add a caption and line numbers:

````markdown
```{literalinclude} example.py
:language: python
:start-after: "# --- begin: put-body"
:end-before: "# --- end: put-body"
:dedent:
:caption: Body of Store.put
:linenos:
```
````

```{literalinclude} example.py
:language: python
:start-after: "# --- begin: put-body"
:end-before: "# --- end: put-body"
:dedent:
:caption: Body of Store.put
:linenos:
```

## By function or class name (no markers needed)

`:pyobject:` finds a function, class or method by name, so the include survives any edit of the file:

````markdown
```{literalinclude} example.py
:pyobject: Store.put
:emphasize-lines: 4
```
````

```{literalinclude} example.py
:pyobject: Store.put
:emphasize-lines: 4
```

## A file elsewhere in the repository

The path can point outside the document's folder, for example straight at the knowledge base extension:

````markdown
```{literalinclude} ../../_ext/kb_ext.py
:pyobject: is_valid_doc_id
```
````

```{literalinclude} ../../_ext/kb_ext.py
:pyobject: is_valid_doc_id
```

## Option cheat sheet

| Option | Effect |
| :--- | :--- |
| `:start-after:` / `:end-before:` | From after a line / up to before a line (marker lines excluded) |
| `:start-at:` / `:end-at:` | From a line / up to a line (marker lines included) |
| `:pyobject:` | A Python function / class / method by name |
| `:lines:` | By line numbers, such as `1,3,5-10`. Shifts with every edit: avoid |
| `:dedent:` | Remove the common indentation |
| `:emphasize-lines:` | Highlight lines (numbers relative to the included snippet) |
| `:caption:` / `:linenos:` | Caption / line numbers |

```{note}
PyCharm and GitHub Markdown previews show `{literalinclude}` as a code block with the directive text; only the Sphinx build shows the included code.
```
