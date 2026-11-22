# Upload docs/build/html to Cloudflare Pages, creating the project first if it
# does not exist yet (idempotent).
#
# One source of truth for the deploy, used by `mise run deploy-doc` and by
# .github/workflows/deploy-doc.yml. Run from the repo root after the build:
# sh .mise/tasks/deploy-doc.sh
#
# Needs CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID and KB_CF_PAGES_PROJECT
# (mise.toml [env] locally, workflow env + secrets in CI).
#
# Not executable on purpose: mise would turn an executable file in .mise/tasks/
# into a file task of the same name.

set -eu

: "${CLOUDFLARE_API_TOKEN:?CLOUDFLARE_API_TOKEN is not set}"
: "${CLOUDFLARE_ACCOUNT_ID:?CLOUDFLARE_ACCOUNT_ID is not set}"
: "${KB_CF_PAGES_PROJECT:?KB_CF_PAGES_PROJECT is not set}"

# The version pinned in package-lock.json, the same locally and in CI.
wrangler() {
    node_modules/.bin/wrangler "$@"
}

# Stop on an auth error instead of mistaking it for "project missing".
if ! projects=$(wrangler pages project list 2>&1); then
    echo "$projects"
    exit 1
fi
if echo "$projects" | grep -q " ${KB_CF_PAGES_PROJECT} "; then
    echo "Cloudflare Pages project '${KB_CF_PAGES_PROJECT}' exists"
else
    wrangler pages project create "${KB_CF_PAGES_PROJECT}" --production-branch main
fi

wrangler pages deploy docs/build/html \
    --project-name "${KB_CF_PAGES_PROJECT}" \
    --branch main \
    --commit-dirty=true
