Seed Repo Release and Version History
==============================================================================
The changelog of this **seed repo** itself. The seed is a runnable project that `cookiecutter-pywf_kb_site <https://github.com/MacHu-GWU/cookiecutter-pywf_kb_site>`_ (the template repo) turns into a cookiecutter template, so every change here is a change to what newly generated projects get.

- The seed and the template repo share one version number. The source is ``version`` in this repo's ``pyproject.toml``; the template repo copies it and refuses to publish when the two differ.
- ``release-history.rst`` is template content: the starting changelog of every generated project. It never records the seed's own changes, and is never edited for a seed release.
- This file is excluded from the template. Each template release links to its section here.


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


1.0.0 (2026-11-22)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First release. The seed starts from the pywf open-source Python library template and replaces its Read the Docs documentation with a knowledge base site, ported from a working knowledge base. This section describes everything a project generated from this seed gets.

**Features and Improvements**

- **Python library base:** the pywf open-source layout (``api.py`` as the only public API, ``paths.py``, mirrored ``tests/`` with ``all.py`` and ``run_cov_test``), Python 3.11+, uv with a committed ``uv.lock``, ruff format and lint, GitHub Actions tests with Codecov, PyPI publish and GitHub release tasks
- **Knowledge base site:** Sphinx with furo, MyST Markdown and MyST-NB notebooks (no pandoc), sphinx-design, sphinx-jinja, sphinxcontrib-mermaid; one folder per document with a ``README.md``, ``README.rst`` or ``README.ipynb``
- **Stable links:** every document has a random 12-letter ``doc_id`` in its metadata and is linked only by it; the ``kb-toctree`` directive lists child documents from the folder tree, and ``/p/<doc_id>`` redirects to the page wherever it moves
- **Readable by AI agents:** ``p/<doc_id>.md`` (each document's plain text), a Markdown copy of every notebook, ``llms.txt`` with one line per document, and an "AI Reader" link under every H1 that hands the page to a chatbot (the home page's link covers the whole site)
- **Search and hosting:** Pagefind type-as-you-search, ``_headers`` with ``noindex``, ``_redirects``, ``404.html``; deployed to Cloudflare Pages by ``.github/workflows/deploy-doc.yml`` on every push to ``main``, the first deploy creating the Pages project
- **Two site values:** ``KB_DOMAIN`` and ``KB_SUBDOMAIN`` in ``mise.toml`` (the site is ``https://<KB_SUBDOMAIN>.<KB_DOMAIN>``, or ``pages.dev`` for no custom domain); the scripts derive the URL and the Pages project name, and CI reads both as GitHub Actions variables
- **mise tasks for the site:** ``inst-node`` (Pagefind and wrangler pinned in ``package-lock.json``), ``build-doc``, ``view-doc``, ``deploy-doc``, ``lint-doc``, ``new-doc-id``, ``nb-to-md``, ``setup-cloudflare-secrets`` (the Cloudflare secrets and the two site variables on GitHub Actions), ``sync-agents-skills``
- **Feature demo documents:** one document per site feature (MyST, notebooks, mermaid, sphinx-design, jinja tables, literalinclude, deep nesting), plus a document anatomy example
- **Skills, in three groups:** the ``pywf-oss-*`` family for the library side; ``blog-base`` and the ``blog-*`` invokers for writing documents (intake, plan, write, migrate from Confluence, add images); standalone skills ``sphinx-myst-kb-site`` (the site spec), ``sphinx-myst-kb-query`` (answer from the live site), ``sanhe-blog-language-style``, ``editorial-ink-art``, ``pypi-imgsqueeze``
- **Antigravity:** ``AGENTS.md`` and ``.agents/skills/``, a generated copy of the knowledge base skills (``mise run sync-agents-skills``) plus ``antigravity-image-gen``
- **Access control, designed but off:** the site is public with ``noindex``; the reserved design for a private site (Cloudflare Zero Trust, e-mail one-time PIN) is in the ``sphinx-myst-kb-site`` skill

**Miscellaneous**

- New ``release-history-seed-repo.rst`` (this file) and the seed-only ``pywf-oss-changelog-seed-repo`` skill that maintains it; both stay out of the template
