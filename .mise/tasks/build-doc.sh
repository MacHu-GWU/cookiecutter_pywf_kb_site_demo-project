# Build the knowledge base: Sphinx HTML, then the Pagefind search index.
#
# One source of truth for the build, used by `mise run build-doc` and by
# .github/workflows/deploy-doc.yml. Run from the repo root, after .venv
# (uv.lock) and node_modules (package-lock.json) exist, with KB_DOMAIN and
# KB_SUBDOMAIN set (mise.toml [env] locally, GitHub Actions variables in CI):
# sh .mise/tasks/build-doc.sh
#
# Not executable on purpose: mise would turn an executable file in .mise/tasks/
# into a file task of the same name.

set -eu

: "${KB_DOMAIN:?KB_DOMAIN is not set}"
: "${KB_SUBDOMAIN:?KB_SUBDOMAIN is not set}"
# The site's public root URL; docs/source/conf.py builds the same one.
KB_SITE_URL="https://${KB_SUBDOMAIN}.${KB_DOMAIN}"
# The skill's stdlib-only scripts (mise.toml [env] sets KB_SCRIPTS; CI uses
# this default). Any python3 runs them: they need no package.
KB_SCRIPTS="${KB_SCRIPTS:-.claude/skills/sphinx-myst-kb-site/scripts}"

# Fail fast on a missing doc_id, a bad description, a missing H1, ...
python3 "${KB_SCRIPTS}/lint_docs.py" --source_dir docs/source

rm -rf docs/build
# -W: any warning (such as a {ref} to a mistyped doc_id) fails the build;
# --keep-going: report all of them first.
.venv/bin/sphinx-build -W --keep-going -b html docs/source docs/build/html

# A compact Markdown copy of every notebook, _sources/<path>/README.md next to
# the README.ipynb Sphinx copied there; p/<doc_id>.md of a notebook is this copy.
python3 "${KB_SCRIPTS}/nb_to_md.py" \
    --source_dir docs/source \
    --output_dir docs/build/html/_sources

# p/<doc_id>.md: each document's plain text at its permalink, a real file
# (status 200, no redirect for agent fetch tools to follow).
python3 "${KB_SCRIPTS}/write_permalink_sources.py" \
    --source_dir docs/source \
    --directory docs/build/html

# llms.txt: one line per document, linking its permalink plain text p/<doc_id>.md.
python3 "${KB_SCRIPTS}/build_llms_txt.py" \
    --site_url "${KB_SITE_URL}" \
    --source_dir docs/source \
    --output docs/build/html/llms.txt

# Index only the document pages (not the index.html copy, genindex, search),
# only the article body, and without the "¶" heading links.
node_modules/.bin/pagefind \
    --site docs/build/html \
    --glob "**/README.html" \
    --root-selector "#furo-main-content" \
    --exclude-selectors ".headerlink"
