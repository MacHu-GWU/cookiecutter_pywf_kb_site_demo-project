# cookiecutter_pywf_kb_site_demo

Entry point for Antigravity. Claude Code reads `CLAUDE.md`, which holds the full rules; this file repeats the ones that matter for writing and illustrating knowledge base documents.

A knowledge base site: Sphinx + furo + MyST Markdown + MyST-NB, Pagefind search, `llms.txt` for agents, deployed to Cloudflare Pages. The documents are under `docs/source/`.

## Rules

- **The documentation spec is the `sphinx-myst-kb-site` skill.** Load it before writing, moving or linking a document.
- **One document = one folder** with a `README.md`, `README.rst` or `README.ipynb`. Its metadata has a `doc_id` (12 random `[A-Za-z]` letters, `mise run new-doc-id`, never changed) and a one-line, two-sentence `description` (double-quoted in `.md` front matter). Link to another document only by doc_id: `` {ref}`<doc_id>` ``.
- **Notebooks use MyST-NB**: roles and directives go in Markdown cells; raw cells are dropped. Never commit a `README.md` next to a `README.ipynb`.
- **Never write the "🌐 AI Reader" link into a source file**: the build adds it under every H1.
- `plan.md` and `resources/` of a document never reach the site.
- Check a document with `mise run lint-doc`; build the site with `mise run build-doc`, look at it with `mise run view-doc`.
- Never read `$HOME/home_secret.toml`, and never print the values of `GITHUB_TOKEN`, `CODECOV_TOKEN`, `PYPI_TOKEN`, `CLOUDFLARE_API_TOKEN` or `CLOUDFLARE_ACCOUNT_ID`.
- `mise run deploy-doc`, `mise run publish`, `mise run release`, `mise run update-github-metadata` and the `setup-*` tasks change external services: run each one only after the user's yes, one step per yes.

## Skills

`.agents/skills/` is a generated copy of `.claude/skills/` (`mise run sync-agents-skills`), except `antigravity-image-gen`, which exists only here. **Never edit a skill in `.agents/skills/`**: edit it in `.claude/skills/` and run the sync. Each group is used on its own; the user decides when.

| Job | Skill |
| :--- | :--- |
| Build, extend or debug the site; add, move or link a document | `sphinx-myst-kb-site` |
| Answer a question from the live knowledge base | `sphinx-myst-kb-query` |
| Collect sources for a knowledge base document | `blog-intake` |
| Plan a knowledge base document | `blog-plan` |
| Write or rewrite a knowledge base document | `blog-write` |
| Migrate a Confluence page into the knowledge base | `blog-write-migrate-from-confluence` |
| Add images to a knowledge base document | `blog-add-images` |
| Writing spec, or not sure which `blog-*` skill | `blog-base` |
| Write or polish in the author's style | `sanhe-blog-language-style` |
| Illustration style and prompt templates | `editorial-ink-art` |
| Generate or edit an image (quota-safe) | `antigravity-image-gen` |
| Compress images | `pypi-imgsqueeze` |
