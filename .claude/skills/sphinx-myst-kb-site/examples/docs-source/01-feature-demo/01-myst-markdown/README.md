---
doc_id: bhNtpbPvxMCO
description: "Covers cross-file links, section labels, admonitions, code blocks, tables and math in MyST Markdown. A hands-on MyST syntax demo."
tags: [sphinx, myst, markdown]
created_at: "2026-11-06"
---

# MyST Markdown Basics

This document shows what MyST Markdown can do in Sphinx. The "On this page" navigation on the right lists the H2 and H3 headings of this page; H4 and deeper stay out of it.

(bhNtpbPvxMCO-cross-ref)=
## Cross-File Links

### Link to a whole document

Link by doc_id; the link text is the target document's title:

- {ref}`RMLeYqeJefsZ` (a document three folders deep)
- {ref}`custom link text <OAFSttVJviBK>` (a reStructuredText document)
- {ref}`diUoGPNCOIwO` (a Jupyter Notebook)

### Link to a section

Put a label `(<doc_id>-<slug>)=` on the line above the heading; the doc_id prefix keeps it unique across the site. For example {ref}`bhNtpbPvxMCO-admonition` points to a section below, and {ref}`RMLeYqeJefsZ-section` to a section of another document.

### Link inside the page

`myst_heading_anchors = 3` gives H1 to H3 GitHub style anchors, so a plain Markdown link like [jump to Admonition](#admonition) works in the page, and on GitHub too.

```{note}
This only works for ASCII headings. A CJK heading gets no usable HTML anchor: use the `(<doc_id>-<slug>)=` label and {ref} instead.
```

(bhNtpbPvxMCO-admonition)=
## Admonition

```{note}
A note, written as a backtick fence. GitHub shows it as a code block.
```

:::{tip}
A tip, written as a colon fence; the **Markdown** inside renders as usual.
:::

:::{warning}
A warning.
:::

## Code Blocks

```python
import secrets
import string

print("".join(secrets.choice(string.ascii_letters) for _ in range(12)))
```

```bash
python3 .claude/skills/sphinx-myst-kb-site/scripts/new_doc_id.py
```

## Tables and Lists

| Format | File name | Where the metadata lives |
| :--- | :--- | :--- |
| MyST Markdown | `README.md` | YAML front matter |
| reStructuredText | `README.rst` | the field list at the top of the file |
| Jupyter Notebook | `README.ipynb` | the notebook `metadata` |

- [x] A task list (tasklist extension)
- [ ] An open task

Term
: A definition list (deflist extension).

## Inline HTML

<details>
<summary>Click to expand</summary>

Inline HTML is passed through as is; Markdown inside still renders.

</details>

## Heading Levels

### An H3 heading shows in the right side navigation

#### An H4 heading does not

Body text.

## Math

$$
E = mc^2
$$
