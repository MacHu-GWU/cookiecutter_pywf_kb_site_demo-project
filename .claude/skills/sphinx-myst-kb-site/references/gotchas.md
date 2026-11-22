# Gotchas

Every pitfall below was hit while building a real site with this skill. Each entry: **symptom**, **cause**, **fix** (or just the rule, when that says it all). Sections go from the bottom of the stack up: documents, rendering, notebooks, the agent text, search, hosting, local tooling, CI.

Other files cite an entry by its anchor, `gotchas.md#<heading-slug>` (for example `gotchas.md#redirect-rules`), never by number, so entries can move. Keep each heading a short noun phrase whose slug is its anchor; renaming a heading means updating `grep -rn "gotchas.md#<old-slug>"`.

---

## Documents and metadata

### Front matter quoting

- **Cause:** YAML reads a bare value with `: ` as a mapping, ` #` starts a comment, a leading `[`, `{`, `*` or `&` is syntax, and a date-like value becomes a date. A description is free text, so it hits these sooner or later.
- **Fix:** the strict format of `scripts/kb_docs.py`: one `key: value` per line; a value is `"double-quoted text"`, `[bare, words]` or one bare word (letters, digits, `_`, `-`, `.`; not a date and not yes/no/true/false/null); `description` is always double-quoted and contains no `"` (so nothing ever needs escaping) and no line break. `lint_docs.py` enforces it. Inside this subset every YAML parser agrees with the standard-library parser, so the lint and Sphinx always read the same values.

### Sphinx reads the metadata itself

- MyST puts the front matter into `env.metadata[docname]`, docutils the field list at the top of a `.rst` file, MyST-NB the notebook level metadata. The extension reads `env.metadata`; it needs no parser of its own.
- MyST stores a non-string value as its JSON text: `tags: [a, b]` is the string `'["a", "b"]'` in `env.metadata`. Read lists from `kb_docs.py` (`Doc.meta`) when you need them as lists.
- The extension's `doctree-read` handler runs with priority 900, after Sphinx's metadata and title collectors (500).

### doc_id labels are lowercased

- **Symptom:** `WARNING: undefined label: 'uxfdfuiojduv'` for `` {ref}`UxFDfuiOJDuv` ``.
- **Cause:** the `:ref:` role lowercases its target before the lookup. A label registered as `UxFDfuiOJDuv` is never found.
- **Fix:** register the lowercased doc_id. sphinx-design's `:link-type: ref` (cards, buttons) does **not** lowercase, so register **both** spellings, and check uniqueness case-insensitively (`on_doctree_read` and `on_check_consistency` in `examples/docs-source/_ext/kb_ext.py`).

### Toctree from folders

- `kb-toctree` lists only docnames (`01-child/README`); Sphinx takes each entry's title from the document itself. Sorting by folder name lets a `01-` prefix set the order.
- A page with `kb-toctree` is not rebuilt when a child folder is added in an incremental build. Build from scratch (`rm -rf docs/build`), as `build-doc.sh` does.

---

## MyST and Sphinx rendering

### CJK heading anchors

- **Symptom:** `'myst' cross-reference target not found: '.../readme.md#<CJK heading>'`; the heading's HTML id is `id1`.
- **Cause:** `myst_heading_anchors` computes a slug, but docutils gives a non-ASCII heading the HTML id `id1`, `id2`, ..., so the slug resolves to nothing.
- **Fix:** link to a CJK heading through a label: `(<doc_id>-<slug>)=` on the line above the heading, then `` {ref}`<doc_id>-<slug>` ``. `[text](#heading)` works for ASCII headings only.

### Links to non-document files

- **Symptom:** `[llms.txt](llms.txt)` warns `cross-reference target not found: 'llms.txt'`.
- **Cause:** MyST treats a relative link without a URL scheme as a link to a document.
- **Fix:** use raw HTML, `<a href="llms.txt">llms.txt</a>`, or an absolute URL. A link to a file that exists in the source tree (such as `example.py`) is fine: it becomes a download.

### Dollar math

- `$$ ... $$` renders as text until `dollarmath` is in `myst_enable_extensions`.

### Source copy suffix

- **Cause:** Sphinx copies sources to `_sources/` as `README.md.txt` by default (`html_sourcelink_suffix = ".txt"`).
- **Fix:** `html_copy_source = True` and `html_sourcelink_suffix = ""`: `_sources/<docname>.md` (or `.rst`, `.ipynb`) is then the exact source.

### Site root page

- **Cause:** `root_doc = "README"` produces `README.html`, and the site root has no `index.html`.
- **Fix:** copy `README.html` to `index.html` after the build (same folder, so every relative path stays valid). `on_build_finished` in `kb_ext.py` does it.

### Page toc depth

- The "On this page" navigation shows H4 and deeper. `kb.css` hides them: `.toc-tree > ul > li > ul > li > ul > li > ul { display: none; }` keeps H2 and H3 (H1 is the page title).

---

## Notebooks

### nbsphinx needs pandoc

- **Symptom:** `nbsphinx.NotebookError: PandocMissing ... Pandoc wasn't found.`
- **Cause:** nbsphinx converts every notebook Markdown cell to reST with pandoc, so pandoc is needed locally **and** in CI.
- **Fix:** use **MyST-NB** (`myst_nb`) instead of nbsphinx and myst-parser: Markdown cells are parsed as MyST, no pandoc anywhere. Set `".md": "myst-nb"` and `".ipynb": "myst-nb"` in `source_suffix`, and `nb_execution_mode = "off"` to use the committed outputs. MyST-NB still installs ipython and ipykernel, although nothing runs.

### Raw cells disappear

- **Symptom:** content of a raw cell (`raw_mimetype: text/restructuredtext`) is missing from the HTML, with no warning.
- **Cause:** MyST-NB does not render raw cells.
- **Fix:** write roles and directives (`{ref}`, `:::{note}`, a ```` ```mermaid ```` fence) in ordinary Markdown cells. Recent JupyterLab renders mermaid fences in Markdown cells too.

---

## Templates and data

### Jinja output syntax

- sphinx-jinja parses its rendered text in the page's own syntax: MyST in a `.md` page, reST in a `.rst` page. To emit reST from a `.md` page, wrap it in ```` ```{eval-rst} ```` inside the `{jinja}` body (outer fence one backtick longer). MyST's own `{list-table}` avoids reST entirely.
- Data comes from `jinja_contexts` in `conf.py`; the directive argument names the context.

### literalinclude part of a file

- Prefer `:pyobject: Name` or comment markers with `:start-after:` / `:end-before:` (markers excluded) over `:lines:`, which shifts with every edit. `:dedent:` for a region inside a method. Paths are relative to the document; a leading `/` is relative to the Sphinx source folder. A marker that is not found fails the `-W` build.

---

## Agent text

### Agent text permalink

- **Symptom:** an AI chatbot given `https://<site>/p/<doc_id>` reads the HTML page (navigation, sidebar, scripts) instead of the text; or a fetch tool stops at a 302, or refuses to follow it to another URL than the one the user gave.
- **Cause:** `/p/<doc_id>` is a redirect to an HTML page. Agent fetch tools differ: some do not follow redirects, some only to URLs the user named, and every redirect is a second request.
- **Fix:** every document's agent text is a real file at `https://<site>/p/<doc_id>.md`, answered with 200: `write_permalink_sources.py` copies `_sources/<path>/README.<ext>` there (a notebook's Markdown copy, see [Notebook agent copy](#notebook-agent-copy)). It is the one URL agents get everywhere: `llms.txt`, the page's raw button, `<link rel="alternate">` in every page head, and any prompt that hands a document to a chatbot. Give a chatbot only this URL: a second one (the HTML page) is a choice it can get wrong. It is short, stable across folder moves and needs no redirect rule. The file is named `.md` even for a reST document; `_headers` serves `/p/*` as `text/plain`.
- `_sources/<path>/README.<ext>` is still published (Sphinx's copy); a notebook's original `README.ipynb` is there for anyone who needs the full outputs.

### Notebook agent copy

- **Symptom:** an agent gets a `README.ipynb`: kilobytes of JSON, base64 images and cell metadata around a few paragraphs.
- **Fix:** `nb_to_md.py` (after sphinx-build) writes a compact Markdown copy, `_sources/<path>/README.md`, next to the `README.ipynb` Sphinx copied there, and `write_permalink_sources.py` serves that copy at `p/<doc_id>.md`. `write_permalink_sources.py` fails when the copy is missing, so a build that skipped `nb_to_md.py` stops.
- Never write the copy into the source tree (nor run `jupyter nbconvert --to markdown` there): a `README.md` next to `README.ipynb` is a second document in one folder. `nb_to_md.py` refuses an output folder inside the source folder.

### Index for agents

- `scripts/build_llms_txt.py` scans `docs/source` itself (standard library only) and refuses to write when `lint_docs.py` would fail. One generator: the Sphinx extension does not write llms.txt.
- Line format: `- [<H1 title>](<site>/p/<doc_id>.md): <description>`, indented two spaces per folder level; the header is the home page's title and description.

---

## Search (Pagefind)

### Pagefind needs http

- **Cause:** Pagefind loads its index and WebAssembly with `fetch`, which fails on `file://`.
- **Fix:** serve the build over http locally with `scripts/serve_docs.py` (`mise run view-doc`). Keep Sphinx's own search page as the fallback: the search form still submits to `search.html`.

### Pagefind index scope

- `--glob "**/README.html"`: skips the `index.html` copy (duplicate results), `genindex.html`, `search.html`.
- `--root-selector "#furo-main-content"`: furo's article only, no sidebar or navigation.
- `--exclude-selectors ".headerlink"`: otherwise every result title ends with `¶`.
- The doc_id bar sits outside `#furo-main-content`, so `--root-selector` already skips it; its `data-pagefind-ignore` only guards against a theme change.
- The log line "Did not find a data-pagefind-body element" is informational when `--root-selector` is set.

### CJK title ranking

- **Symptom:** a query that is a substring of a title (such as part of a Chinese title) ranks that page second or third, and its title is not highlighted.
- **Cause:** Pagefind weighs headings (H1 7, H2 6, H3 5, body 1) but BM25-style length normalization favors short pages that repeat the words, and CJK segmentation may split the query differently from the title. Pagefind also matches words by prefix only: `include` does not find `literalinclude`.
- **Fix:** the build writes `kb-titles.json` (`[{title, url, description}]`); `kb-search.js` puts plain substring title hits first (whole query > all words > shorter title), then Pagefind's results, and highlights the title match itself.

### Section results

- Results link to the page, not the section: Sphinx puts the anchor `id` on `<section>`, not on the `<h2>`, and Pagefind builds sub-results only from headings that carry an `id`. Accept it, or add ids to headings in a custom HTML translator.

### Stale fragments

- "404 fetching /pagefind/fragment/..." after a rebuild: a page opened before the rebuild still uses the old index, whose fragment hashes no longer exist. Reload the page.

### Search language

- Pagefind picks its segmentation from `<html lang>`, which Sphinx sets from `language`. A Chinese site needs `language = "zh_CN"`; Sphinx's own search page then needs `html_search_language = "zh"` and the `jieba` package.
- `kb-search.js` picks its one piece of UI text ("No results") from `<html lang>` too, so the file is the same on every site.
- The `/` key already focuses the search box (Sphinx's `doctools.js`, `ENABLE_SEARCH_SHORTCUTS`).

---

## Hosting (Cloudflare Pages)

### Unknown path returns home

- **Cause:** without a `404.html` at the root, Cloudflare Pages serves the site as a single page app.
- **Effect:** `/favicon.ico` returns HTML (no favicon in Safari and others), and an agent fetching a wrong URL gets a 200 and the home page.
- **Fix:** `_extra/404.html`. Pages then answers unknown paths with it and status 404.

### Favicon

- Also ship a real `favicon.ico` at the root (`_extra/favicon.ico`). Some browsers request `/favicon.ico` regardless of `<link rel="icon">`.
- A PNG named `.ico` is served as `image/vnd.microsoft.icon`; name it `.png` for `html_favicon`. Make a real multi-size ICO with Pillow: `Image.open(png).save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])`.
- Browsers cache favicons hard: check in a private window.

### Redirect rules

- `/p/<doc_id>` must be an HTTP 302: not 301 (browsers cache it forever, so a moved document keeps redirecting to its old path), not a 200 rewrite (Sphinx pages use relative paths, which break under `/p/`), not a `<meta refresh>` page (many agent fetch tools do not follow it).
- Point the target at the extensionless path (`/a/b/README`): Pages redirects `/a/b/README.html` there anyway.
- Limit: 2,000 static rules, so 2,000 documents at one rule each (`/p/<doc_id>.md` is a file, not a rule). Beyond that, consider Bulk Redirects.
- Free plan: 20,000 files per deployment. Images count; keep many images elsewhere (R2).

### Noindex instead of robots

- `_headers`: `/*` with `X-Robots-Tag: noindex, nofollow`. Do **not** `Disallow: /` in `robots.txt`: crawlers must fetch a page to see its noindex, and some agent fetch tools obey robots.txt.
- Cloudflare Access (Zero Trust) is off by default: agent fetch tools and the chatbots behind the AI Reader link cannot sign in or send service-token headers. If a site must be private, follow the reserved design in `access-control.md`.

### Text content type

- In `_headers`, `/_sources/*`, `/p/*` and `/llms.txt` get `Content-Type: text/plain; charset=utf-8`, so browsers show them and non-ASCII text survives.

### Wrangler account cache

- **Symptom:** "Authentication error [code: 10000]" with a valid token.
- **Cause:** wrangler caches the account it last used in `.wrangler/cache/wrangler-account.json` in the project folder. After switching to a token of another account, it keeps calling the old account.
- **Fix:** pin `CLOUDFLARE_ACCOUNT_ID`, delete `.wrangler/`, and add `.wrangler/` to `.gitignore`.
- Diagnose without wrangler: `GET https://api.cloudflare.com/client/v4/user/tokens/verify` (token valid?), `GET /memberships` (the token's accounts), `GET /accounts/<id>/pages/projects` (Pages permission on that account).

### API token location

- A **User API token** is under the avatar > My Profile > API Tokens (`https://dash.cloudflare.com/profile/api-tokens`); `wrangler whoami` says "logged in with an User API Token". An **Account API token** is under Manage account > Account API tokens; wrangler cannot infer the account from it, so `CLOUDFLARE_ACCOUNT_ID` is required.
- Permission: Account > Cloudflare Pages > Edit, on the one account.

### Project detection

- `deploy-doc.sh` greps `wrangler pages project list` (a table) for ` <project> `. If a wrangler release changes that output, the script tries to create the existing project and stops with "already exists": loud, never a wrong deploy. Fix the grep then.

---

## Local tooling (mise)

### Local mojibake

- **Symptom:** CJK text in `llms.txt` or `_sources/...` reads like `çš„` in the browser; `file llms.txt` says UTF-8.
- **Cause:** `python -m http.server` sends `Content-type: text/plain` without a charset (and `.md` as `text/markdown`), so the browser falls back to Windows-1252. `_headers` only applies on Cloudflare Pages.
- **Fix:** serve locally with `scripts/serve_docs.py`: the same rules as `_headers` (every text type with `charset=utf-8`, `_sources/`, `p/` and `llms.txt` as `text/plain`). Check with `curl -sI <url> | grep -i content-type`.

### Port in use

- **Symptom:** `view-doc` fails with "Address already in use": another server already listens on the port (an earlier `view-doc`, an editor's preview server).
- **Fix:** an uncommon port in one env var, and an idempotent task: kill whatever listens on it, then start the server (`examples/tooling/mise.toml`).

### lsof aborts the task

- **Cause:** mise runs task scripts with `set -e`; `lsof` exits 1 when the port is free, which aborts the assignment `pids=$(lsof ...)`.
- **Fix:** `pids=$(lsof -tiTCP:$PORT -sTCP:LISTEN || true)`.

### Executable task scripts

- **Cause:** mise registers every **executable** file in `.mise/tasks/` as a file task named after it.
- **Fix:** keep shared shell scripts non-executable and call them with `sh .mise/tasks/build-doc.sh`.

### Secret template names

- The pattern `X = "{{ env.X | default(value=exec(command='<read secret> || true')) }}"` lets an exported `X` (a CI secret) win over the local secret store.
- **Gotcha:** `CLOUDFLARE_ACCOUNT_ID = "{{ env.CLOUDFLARE_API_TOKEN | default(...) }}"` (copy-paste) silently assigns the **token** to the account id; wrangler then puts it in a URL, in its error output and in its log file. Rotate a token that leaked this way.

### Desktop app Python

- On macOS, Apple's `/usr/bin/python3` launched by a desktop app (an editor's preview config such as `.claude/launch.json`) may be denied `~/Documents` ("Operation not permitted"). Start such configs with `.venv/bin/python`. Inside `mise run`, `python3` is mise's own Python, which is fine.

---

## CI (GitHub Actions)

### No mise in CI

- `mise-action` plus mise-managed tools costs a download and setup on every run, and every `mise run` evaluates all `[env]` templates, including secret-store commands that can only fail in CI. Call the shared scripts directly, with `actions/setup-*` for the tools. The price is that the Python and Node versions are written twice (mise.toml and the workflow), each line saying "Must match".

### Lock Node CLIs

- `package.json` pins pagefind and wrangler exactly; `package-lock.json` locks everything below them and records the Linux binaries (`@pagefind/linux-x64`, `@cloudflare/workerd-linux-64`) even when generated on macOS.
- CI caches `node_modules` keyed on Node version + `hashFiles('package-lock.json')`, and runs `npm ci` only on a miss (the same pattern as `.venv` keyed on `uv.lock`). `npm ci` deletes `node_modules` first, so never run it on a cache hit.
- `cloudflare/wrangler-action` is not faster: it installs wrangler with npm on every run.

### Separate deploy workflow

- Keep deployment out of a test matrix that cannot pass for the repository (for example a Codecov upload, which refuses private repositories).
- The `.venv` cache key of the deploy job needs its own prefix: a venv cached by a test job may lack the docs extra.
- Set the GitHub secrets **before** the first push to main, or the first run fails at the secret check.
