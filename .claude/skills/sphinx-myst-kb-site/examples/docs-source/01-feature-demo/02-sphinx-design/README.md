---
doc_id: tXPKdEHKANfY
description: "Shows sphinx-design cards, grids, tabs, dropdowns, badges and buttons written in MyST. A component demo."
tags: [sphinx, sphinx-design]
---

# sphinx-design Components

With `colon_fence` on, every sphinx-design component is written as `:::{...}`. When nesting, the outer fence has one more colon than the inner one.

## Grid and Card

::::{grid} 1 2 2 3
:gutter: 2

:::{grid-item-card} MyST Markdown
:link: bhNtpbPvxMCO
:link-type: ref

A card's `:link:` can be a doc_id too; clicking the card opens that document.
:::

:::{grid-item-card} mermaid and SVG
:link: wYJOstZIrweF
:link-type: ref

Diagrams.
:::

:::{grid-item-card} Jupyter Notebook
:link: diUoGPNCOIwO
:link-type: ref

Notebooks are first-class documents.
:::
::::

## Tab

::::{tab-set}

:::{tab-item} MyST
```markdown
{ref}`bhNtpbPvxMCO`
```
:::

:::{tab-item} reST
```rst
:ref:`bhNtpbPvxMCO`
```
:::

:::{tab-item} Notebook
Write it in an ordinary Markdown cell, exactly as in MyST (MyST-NB parses it):

```markdown
{ref}`bhNtpbPvxMCO`
```
:::

::::

## Dropdown

:::{dropdown} Click to expand
:icon: info

A dropdown can hold any content.
:::

## Badge and Button

{bdg-primary}`primary` {bdg-success}`success` {bdg-warning}`warning`

```{button-ref} OAFSttVJviBK
:color: primary
:outline:

Go to the reST document
```
