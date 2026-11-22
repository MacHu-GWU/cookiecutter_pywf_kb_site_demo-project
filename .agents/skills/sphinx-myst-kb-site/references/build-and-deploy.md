# Build and Deploy

How the pieces fit, from the bottom up: Python and Node dependencies, the two shared shell scripts, the two runners that call them (mise locally, GitHub Actions in CI), the one-time setup, and how a site keeps its copies of the examples in sync. File names below are the conventional ones; the ready-made files are in `examples/tooling/`.

```
author README.md / .rst / .ipynb
   │
   ├─ local:  mise run build-doc  ─┐                     mise run view-doc (http://localhost:<port>)
   │          mise run deploy-doc ─┤
   └─ CI:     push to main ────────┤
                                   ▼
          build-doc.sh:  lint_docs.py
                         sphinx-build docs/source docs/build/html
                         nb_to_md.py (notebook -> _sources/<path>/README.md)
                         write_permalink_sources.py (-> p/<doc_id>.md)
                         build_llms_txt.py
                         pagefind --site docs/build/html ...
          deploy-doc.sh: wrangler pages project create (if missing)
                         wrangler pages deploy docs/build/html
                                   ▼
          Cloudflare Pages: HTML + _sources/ + p/ + pagefind/ + _redirects + _headers + llms.txt
```

---

## 1. Python dependencies

The project's `pyproject.toml` has a `doc` optional dependency group (an "extra") with: `sphinx`, `myst-nb` (brings `myst-parser`, ipython and ipykernel), `furo`, `sphinx-design`, `sphinx-copybutton`, `sphinx-jinja`, `sphinxcontrib-mermaid`, and `jieba` for a Chinese site. Lock with uv (`uv.lock`); install with `uv sync --extra doc` (or all extras locally).

No pandoc ([gotchas](gotchas.md#nbsphinx-needs-pandoc)) and no YAML library: Sphinx reads the metadata itself ([gotchas](gotchas.md#sphinx-reads-the-metadata-itself)), and the skill's `scripts/` are standard library only, so they run with any `python3` (3.10+) and need no install.

---

## 2. Node CLIs

`package.json` at the repository root (`examples/tooling/package.json`) pins the two CLIs exactly as devDependencies: `pagefind` and `wrangler`. Run `npm install` once to create `package-lock.json` and commit it; add `node_modules/` to `.gitignore`. The scripts call `node_modules/.bin/pagefind` and `node_modules/.bin/wrangler`, never `npx <pkg>@<version>`, so local and CI run the same locked versions ([gotchas](gotchas.md#lock-node-clis)). Node itself is pinned to one exact version on both runners (sections 4 and 5).

---

## 3. The two shared scripts

The only place the build and deploy commands live. Both run from the repository root, live in `.mise/tasks/`, are **not** executable ([gotchas](gotchas.md#executable-task-scripts)) and are called with `sh`.

- `build-doc.sh` (`examples/tooling/build-doc.sh`), in this order:
  1. `lint_docs.py --source_dir docs/source`: stop before Sphinx on any metadata problem.
  2. `rm -rf docs/build`, then `sphinx-build -W --keep-going -b html docs/source docs/build/html`: any warning (a broken `{ref}`, for one) fails the build. Build from scratch every time ([gotchas](gotchas.md#toctree-from-folders)).
  3. `nb_to_md.py`: the Markdown copy of every notebook ([gotchas](gotchas.md#notebook-agent-copy)).
  4. `write_permalink_sources.py`: `p/<doc_id>.md`, every document's agent text ([gotchas](gotchas.md#agent-text-permalink)).
  5. `build_llms_txt.py --site_url "https://$KB_SUBDOMAIN.$KB_DOMAIN"`.
  6. Pagefind with `--glob "**/README.html" --root-selector "#furo-main-content" --exclude-selectors ".headerlink"` ([gotchas](gotchas.md#pagefind-index-scope)).

  It needs `KB_DOMAIN` and `KB_SUBDOMAIN` and builds the site URL from them, as `conf.py` does; `KB_SCRIPTS` (the skill's `scripts/` folder) defaults to `.agents/skills/sphinx-myst-kb-site/scripts`.
- `deploy-doc.sh` (`examples/tooling/deploy-doc.sh`): checks `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` and `KB_SUBDOMAIN` (which is also the Pages project name), lists Pages projects (stops on an auth error instead of mistaking it for a missing project), creates the project with `--production-branch main` if missing ([gotchas](gotchas.md#project-detection)), then `wrangler pages deploy docs/build/html --project-name "$KB_SUBDOMAIN" --branch main --commit-dirty=true`. `--commit-dirty=true` silences wrangler's warning about uncommitted changes, which a local deploy of a work in progress always has.

---

## 4. Local runner: mise

`examples/tooling/mise.toml` holds the docs part of a site's `mise.toml`: merge it into the project's file. In short:

- `[env]` is the single source of truth for the site's two values: `KB_DOMAIN` and `KB_SUBDOMAIN`. Nothing derived from them is stored: the scripts build the site URL `https://<KB_SUBDOMAIN>.<KB_DOMAIN>` (`conf.py`, `build-doc.sh`; no default, so a build without them stops instead of linking a wrong site) and use `KB_SUBDOMAIN` as the Pages project name (`deploy-doc.sh`). Also `KB_DOCS_PORT`, `KB_SCRIPTS`, and the Cloudflare account ID and Pages upload token, read from the local secret store with a template that lets an exported value win ([gotchas](gotchas.md#secret-template-names)).
- `[tools]`: `python`, `uv`, and `node` at the **exact** version of the workflow.
- Tasks: `build-doc` and `deploy-doc` call the shared scripts; `view-doc` (re)starts `scripts/serve_docs.py` on `KB_DOCS_PORT` ([gotchas](gotchas.md#port-in-use), [gotchas](gotchas.md#local-mojibake)); `lint-doc`, `new-doc-id`, `nb-to-md` and `check-kb-sync` call the skill's scripts with `python3`; `setup-cloudflare-secrets` runs `examples/tooling/setup-cloudflare-secrets.py`, which writes the two Cloudflare secrets and the two site values (as GitHub Actions variables) to the repository.

`serve_docs.py` serves over http (Pagefind fails on `file://`, [gotchas](gotchas.md#pagefind-needs-http)), adds `charset=utf-8` and listens on 127.0.0.1 only. Give an editor's preview server (such as `.claude/launch.json`) the same port, so `view-doc` replaces it instead of running a second one, and start it with `.venv/bin/python` ([gotchas](gotchas.md#desktop-app-python)).

`deploy-doc`, `setup-cloudflare-secrets` (and any task that writes to Cloudflare or GitHub) change external services: run them on purpose, not as a side effect.

---

## 5. CI runner: GitHub Actions

`examples/tooling/deploy-doc.yml`, its own workflow file ([gotchas](gotchas.md#separate-deploy-workflow)), without mise ([gotchas](gotchas.md#no-mise-in-ci)):

1. Trigger: push to `main`, plus `workflow_dispatch`; the job runs only on `main` (deploys always go to production); `concurrency` cancels a deploy superseded by a newer push.
2. Workflow `env`: the two Cloudflare secrets (`secrets.*`) and `KB_DOMAIN`, `KB_SUBDOMAIN` (`vars.*`, GitHub Actions variables, so the workflow holds no site value and never drifts from `mise.toml`).
3. Fail fast if a secret or variable is empty.
4. `actions/setup-python`, `astral-sh/setup-uv` (its own cache off), `actions/setup-node` with the exact Node version.
5. `actions/cache` for `.venv` (key: full Python version + `uv.lock` hash, with a `venv-doc-` prefix) and for `node_modules` (key: setup-node's resolved Node version + `package-lock.json` hash).
6. `uv sync --locked --extra doc` always (well under a second on a hit; fails on a stale `uv.lock`); `npm ci` only on a `node_modules` cache miss.
7. `sh .mise/tasks/build-doc.sh`, then `sh .mise/tasks/deploy-doc.sh`.

---

## 6. One-time setup

Once per Cloudflare account, by hand (a token cannot create itself):

1. **Upload token** (`CLOUDFLARE_API_TOKEN`), a user API token (avatar > My Profile > API Tokens > Create Token > Custom token, [gotchas](gotchas.md#api-token-location)) with Account > Cloudflare Pages > Edit and nothing else: it becomes a GitHub Actions secret. Store it and the account ID (from the dashboard URL `dash.cloudflare.com/<account_id>/...`) in the local secret store.
2. **The domain** (`KB_DOMAIN`) is a zone on Cloudflare in the same account. Skip it with `KB_DOMAIN = "pages.dev"`.

Once per site (the commands change external services: run them on purpose):

3. **GitHub repository** exists and the code is pushed (the next step writes to it).
4. **GitHub secrets and variables**: `mise run setup-cloudflare-secrets` (PyGithub, needs a `GITHUB_TOKEN` allowed to write the repository's secrets and variables). Idempotent; run it again after changing `KB_DOMAIN` or `KB_SUBDOMAIN`. Do this before the first push to main that should deploy.
5. **First deploy creates the Pages project**: push to main (or `mise run deploy-doc`). `deploy-doc.sh` creates the project `KB_SUBDOMAIN` with production branch `main` when it is missing, then uploads. Check the `*.pages.dev` address wrangler prints: when `<KB_SUBDOMAIN>.pages.dev` is taken by someone else, Cloudflare adds a suffix, and with `KB_DOMAIN = "pages.dev"` the site URL is then wrong (pick another `KB_SUBDOMAIN`).
6. **Custom domain, in the dashboard** (skip for `pages.dev`): Workers & Pages > the project > Custom domains > Set up a custom domain > `<KB_SUBDOMAIN>.<KB_DOMAIN>` > Activate. With the zone on Cloudflare in the same account, Cloudflare creates the CNAME itself; the domain is active (with a certificate) a few minutes later. Attach the domain in the project first: a hand-made CNAME without the attachment answers 522. A domain whose DNS is elsewhere: add the CNAME `<KB_SUBDOMAIN> -> <project>.pages.dev` at that DNS provider.
7. **Check live**: `curl -I https://<site>/p/<doc_id>` gives a 302 to the page; `/p/<doc_id>.md` gives the agent text with status 200 (no redirect); responses carry `X-Robots-Tag: noindex, nofollow`; an unknown path gives 404; `/llms.txt` lists every document.

---

## 7. Keeping a site in sync with the examples

A site keeps its own copies of the example files (SKILL.md, "Two copies"). Two checks keep them honest:

- `scripts/check_example_sync.py` fails when a file that holds no site-specific value (the shared scripts, `kb-search.js`, `kb-copy.js`, `kb.css`, the two templates, `_headers`, `robots.txt`) differs from its example, or when a demo document is missing from the site or has another doc_id there. Run it with the project's lint (`mise run lint` in a site that copied this setup, `mise run check-kb-sync` in the example `mise.toml`).
- The examples build on their own: `KB_DOMAIN=example.com KB_SUBDOMAIN=kb .venv/bin/sphinx-build -W -b html .agents/skills/sphinx-myst-kb-site/examples/docs-source /tmp/kb-example` must pass after a change to `examples/docs-source/`.
- `tests/test_kb_docs.py` covers the scripts: `pytest .agents/skills/sphinx-myst-kb-site/tests`.
