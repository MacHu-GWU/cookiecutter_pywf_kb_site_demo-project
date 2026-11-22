# cookiecutter_pywf_kb_site_demo

<!-- BEGIN project block: facts about THIS library. Edit freely. -->

What this library does: see `README.rst`. In short: a knowledge base site (Sphinx + furo + MyST Markdown + MyST-NB, Pagefind search, `llms.txt` for agents) deployed to Cloudflare Pages, plus the Python package that holds its Sphinx extension.

Package: `cookiecutter_pywf_kb_site_demo/` (import name `cookiecutter_pywf_kb_site_demo`).

How to maintain this library: the `maintain-cookiecutter_pywf_kb_site_demo-*` skills, once they exist (create them with `pywf-oss-write-maintain-skill`).

<!-- END project block -->

<!-- BEGIN pywf-kb-site template block: shared by every repo built from the cookiecutter-pywf_kb_site template. Replace as a whole on template upgrade; do not edit per repo. -->

## Conventions

This repo follows the pywf open-source Python library template. **Before creating or restructuring modules, tests, or docs, load the `pywf-oss-base` skill** and read the reference for the job. `<package_name>` below is the import package directory. The rules below are the ones that are easy to break silently. The skill has the reasons and the details.

- Run everything through mise: `mise run inst` (install), `mise run inst-node` (Pagefind, wrangler), `mise run cov` (tests and coverage), `mise run build-doc` (docs). Use `.venv/bin/python`; never `pip install`.
- Python 3.11+ only: `X | None`, `list[str]`; never `T.Optional` / `T.List`. `import typing as T` is the only way typing is imported.
- Every `.py` file starts with `# -*- coding: utf-8 -*-` (on line 2, after a shebang if there is one).
- One imported name per statement: `from abc import e` and `from abc import f` on two lines, never `from abc import e, f`.
- Import order in source files: `typing as T`, then stdlib, then third party, then close-relative libraries, then this package's own modules, always as relative imports, farthest (`...`) before nearest (`.`).
- Public API = `<package_name>/api.py`, one re-exported name per line. Every public name has a docstring. The knowledge base modules (`doc_id.py`, `ai_reader.py`, `sphinx_ext.py`) are build internals that `docs/source/conf.py` loads by module path; they are not exported.
- Test path mirrors source path, with the directory path as a file-name prefix: `<package_name>/a/b/c.py` maps to `tests/a/b/test_a_b_c.py`. Every tested folder has an `all.py` with `is_folder=True`.
- In test files, the subject under test is imported first. The `run_cov_test(...)` block at the bottom puts one argument per line.
- Before finishing a code change: `mise run format`, then `mise run lint`.
- In dataclass / pydantic / SQLAlchemy models, keep one field definition per line, fenced by `# fmt: off` / `# fmt: on`.
- Knowledge is written for agents too: how to use the library goes in the `pypi-<package_name>` skill, how to maintain it in the `maintain-<package_name>-*` skills, never in a maintainer guide in the docs.
- Never read `$HOME/home_secret.toml`, and never print the values of `GITHUB_TOKEN`, `CODECOV_TOKEN`, `PYPI_TOKEN`, `CLOUDFLARE_API_TOKEN` or `CLOUDFLARE_ACCOUNT_ID`.
- `mise run publish`, `mise run release`, `mise run update-github-metadata`, `mise run deploy-doc` and the `setup-*` tasks (`setup-codecov`, `setup-cloudflare-secrets`) change external services: run each one only after the user's yes, one step per yes.
- The changelog is `release-history.rst`. Never edit its `x.y.z (Backlog)` section.

## The Knowledge Base Site

**The documentation spec is the `sphinx-myst-kb-site` skill, not the pywf-oss docs references.** Load it before writing, moving or linking a document, or touching `docs/source/conf.py`, `docs/source/_extra/`, `_static/`, `_templates/`, `.mise/tasks/build-doc.sh`, `.mise/tasks/deploy-doc.sh` or `.github/workflows/deploy-doc.yml`.

- **MyST-NB, not nbsphinx: this repo deviates from the pywf-oss skills here.** Notebooks use MyST-NB, so no pandoc is needed. In notebooks, Sphinx roles and directives go in ordinary Markdown cells, written in MyST; raw cells are dropped from the HTML without a warning. Ignore the pywf-oss skills' advice on nbsphinx raw reST cells, docfly and the generated `docs/source/api/` (this site has no API reference pages).
- **One document = one folder** with a `README.md`, `README.rst` or `README.ipynb`. Its metadata has a `doc_id` and a one-line, two-sentence `description` (double-quoted in `.md` front matter). `mise run lint-doc` checks every rule and runs first in `mise run build-doc`.
- **doc_id.** 12 random `[A-Za-z]` letters (`mise run new-doc-id`), unique, never changed, even when the folder moves. Link to another document only by doc_id: `` {ref}`<doc_id>` `` (MyST) or `` :ref:`<doc_id>` `` (reST), never by relative path. Child documents are listed by the `kb-toctree` directive, never by a hand-kept toctree.
- **Agents read the plain text.** The build writes `p/<doc_id>.md` (each document's source), `_sources/<path>/README.md` (a Markdown copy of each notebook, `mise run nb-to-md`) and `llms.txt` (one line per document). Never commit a `README.md` next to a `README.ipynb`.
- **AI Reader.** The "🌐 AI Reader" link under every H1 is added at build time by `cookiecutter_pywf_kb_site_demo/sphinx_ext.py` (prompt and URL in `ai_reader.py`); never write it into a source file. The home page's link carries the site-wide prompt, a short version of the `sphinx-myst-kb-query` skill: change one, change the other.
- **Site values** live in `mise.toml` `[env]`, two of them: `KB_DOMAIN` (a Cloudflare zone, or `pages.dev` for no custom domain) and `KB_SUBDOMAIN` (the package name as a slug). Nothing derived is stored: the scripts build the site URL `https://<KB_SUBDOMAIN>.<KB_DOMAIN>` (`docs/source/conf.py`, `build-doc.sh`) and use `KB_SUBDOMAIN` as the Cloudflare Pages project name (`deploy-doc.sh`). CI runs without mise and reads both as GitHub Actions variables, which `mise run setup-cloudflare-secrets` copies from `mise.toml`: run it again after changing one. `KB_DOCS_PORT` and `KB_SCRIPTS` are local.
- **Going live** (the `sphinx-myst-kb-site` skill, `references/build-and-deploy.md` section 6; the Pages upload token and account ID are in the secret store): push the repository; `mise run setup-codecov` and `mise run setup-cloudflare-secrets`; the next push to main deploys, and that first deploy creates the Pages project (`deploy-doc.sh`); then attach the custom domain once in the Cloudflare dashboard.
- **Writing material.** Each document's `plan.md` and `resources/` are excluded from the build in `docs/source/conf.py`; `resources/` is also git-ignored.
- **Access.** The site is public, hidden from search engines only (`X-Robots-Tag: noindex` in `_headers`), so that `llms.txt`, `p/<doc_id>.md` and the AI Reader link work for agents and public chatbots. A private site (Cloudflare Zero Trust, e-mail one-time PIN, allow-list, service token for the owner's agents) is designed but not set up: the `sphinx-myst-kb-site` skill, `references/access-control.md`. Turn it on only when the user asks.

## Skills

Skills come in three groups. Each group is used on its own; the user decides when.

- **The pywf-oss family** (`pywf-oss-*`): the Python library side. Kept as the template ships it, in `.claude/skills/` only.
- **The writing family** (`blog-base` and the `blog-*` invokers): writing knowledge base content. It relies on the site rules of `sphinx-myst-kb-site` (its `blog_utils.py` imports `kb_docs.py`).
- **Standalone skills** that mention no other skill: `sphinx-myst-kb-site` (the site), `sphinx-myst-kb-query` (answer questions from the live site), `sanhe-blog-language-style` (the author's writing style), and the image skills `editorial-ink-art`, `pypi-imgsqueeze`, `antigravity-image-gen`.

**Two copies: `.claude/skills/` is the source, `.agents/skills/` is the Antigravity copy.** Claude Code writes the content; Antigravity polishes the style and makes the images (`blog-add-images` only generates images in Antigravity). After editing a knowledge base skill in `.claude/skills/`, run `mise run sync-agents-skills`; never edit `.agents/skills/` by hand. Nothing checks for drift, so a forgotten sync goes unnoticed. `antigravity-image-gen` exists only in `.agents/skills/`, the pywf-oss family only in `.claude/skills/`. Antigravity's entry point is `AGENTS.md`.

| Job | Skill |
| :--- | :--- |
| Set up a new machine or rotate a token | `pywf-oss-setup-machine` |
| Take a new repo live (GitHub, Codecov) | `pywf-oss-setup-repo` |
| Add a module or subpackage | `pywf-oss-add-module` |
| Write or fix tests | `pywf-oss-write-test` |
| Update the changelog | `pywf-oss-changelog` |
| Release a version | `pywf-oss-release` |
| Generate a skill for this library's API | `pywf-oss-write-pypi-skill` |
| Write down how to maintain this repo | `pywf-oss-write-maintain-skill` |
| Fix a red CI run or Codecov upload | `pywf-oss-fix-ci` |
| Upgrade or replace dependencies | `pywf-oss-upgrade-deps` |
| Install an optional community skill, or catalog one | `pywf-oss-add-community-skill` |
| Check the repo against the template | `pywf-oss-audit` |
| Not sure which pywf-oss skill | `pywf-oss-base` |
| Build, extend or debug the site; add, move or link a document | `sphinx-myst-kb-site` |
| Answer a question from the live knowledge base | `sphinx-myst-kb-query` |
| Collect sources for a knowledge base document | `blog-intake` |
| Plan a knowledge base document | `blog-plan` |
| Write or rewrite a knowledge base document | `blog-write` |
| Migrate a Confluence page into the knowledge base | `blog-write-migrate-from-confluence` |
| Add images to a knowledge base document | `blog-add-images` |
| Writing spec, or not sure which `blog-*` skill | `blog-base` |
| Write or polish in the author's style | `sanhe-blog-language-style` |

<!-- END pywf-kb-site template block -->
