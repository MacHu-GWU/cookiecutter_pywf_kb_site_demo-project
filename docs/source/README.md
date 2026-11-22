---
doc_id: UxFDfuiOJDuv
description: "Lists every topic of the knowledge base. The home page and top level table of contents."
---

# KB Site Demo

A demo knowledge base: every feature of the site, one small document each.

- One document = one folder with a `README.md` / `README.rst` / `README.ipynb` file.
- Every document's metadata has a 12 character `[A-Za-z]` `doc_id`: its identity, never changed.
- Link to another document only by doc_id, for example {ref}`bhNtpbPvxMCO`. The link follows the document when its folder moves.
- Entry point for AI agents: <a href="llms.txt">llms.txt</a>.

## Contents

```{kb-toctree}
:maxdepth: 2
```
