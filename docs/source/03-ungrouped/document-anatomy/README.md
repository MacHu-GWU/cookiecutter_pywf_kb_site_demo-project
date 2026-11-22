---
doc_id: NaHsHTYtOvMO
description: "Shows the files of one knowledge base document and which of them reach the site. A sample document written the way the blog-* skills write one."
tags: [knowledge-base]
created_at: "2026-11-22"
updated_at: "2026-11-22"
---

# Anatomy of a Document

A document is a folder. Its `README.md` is the page; everything else in the folder is either part of the page or writing material that never reaches the site.

## The files of this folder

```text
03-ungrouped/document-anatomy/
├── README.md     # this page: front matter + body
└── plan.md       # the writing plan: kept in git, excluded from the build
```

A `resources/` folder next to `plan.md` holds the sources a document was written from (articles, transcripts, an exported Confluence page). Like `plan.md`, it is excluded in `conf.py` (`exclude_patterns`), and git ignores it.

## The front matter

| Key | Meaning |
| :--- | :--- |
| `doc_id` | 12 random letters, the document's identity; `mise run new-doc-id` prints one |
| `description` | Two sentences, double-quoted: what the document says, then what kind of document it is. `llms.txt` lists it |
| `tags` | Optional keywords |
| `created_at` / `updated_at` | Dates, `YYYY-MM-DD` |

## Linking to it

Every link is built from the doc_id, so moving or renaming the folder breaks nothing: {ref}`NaHsHTYtOvMO` links to this page, and `/p/NaHsHTYtOvMO` redirects to it on the live site. Agents read its plain text at `/p/NaHsHTYtOvMO.md`.
