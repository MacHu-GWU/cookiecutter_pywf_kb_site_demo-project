# -*- coding: utf-8 -*-

"""
Set what .github/workflows/deploy-doc.yml needs on GitHub Actions of this
repository: the Cloudflare secrets, and the site's values as variables (CI
runs without mise, so it cannot read mise.toml [env]).

The values come from the environment, which mise.toml fills from the local
secret store (hst):

- CLOUDFLARE_API_TOKEN: Cloudflare user API token (Cloudflare Pages: Edit)
- CLOUDFLARE_ACCOUNT_ID: the Cloudflare account the token deploys to
- KB_DOMAIN, KB_SUBDOMAIN: the site is https://<KB_SUBDOMAIN>.<KB_DOMAIN>;
  plain values, so they become variables (readable in the logs), not secrets
- GITHUB_TOKEN: GitHub personal access token allowed to write repo secrets

Idempotent: every run creates or updates the secrets and variables. Secret
values are never printed; variable values are.
"""

import os
import sys

try:
    from github import Auth
    from github import Github
    from github import GithubException
    from github import UnknownObjectException
except ImportError:
    print("Error: PyGithub not installed. Run: mise run inst")
    sys.exit(1)

from utils import get_github_repo_info

ENV_GITHUB_TOKEN = "GITHUB_TOKEN"

#: GitHub secret name -> environment variable that holds its value.
SECRETS = {
    "CLOUDFLARE_API_TOKEN": "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID": "CLOUDFLARE_ACCOUNT_ID",
}

#: GitHub variable name -> environment variable that holds its value.
VARIABLES = {
    "KB_DOMAIN": "KB_DOMAIN",
    "KB_SUBDOMAIN": "KB_SUBDOMAIN",
}


def main():
    github_token = os.environ.get(ENV_GITHUB_TOKEN)
    if not github_token:
        print(f"Error: {ENV_GITHUB_TOKEN} environment variable not set")
        sys.exit(1)

    values = dict()
    for name, env_name in {**SECRETS, **VARIABLES}.items():
        value = os.environ.get(env_name)
        if not value:
            print(
                f"Error: {env_name} environment variable not set (see mise.toml [env])"
            )
            sys.exit(1)
        values[name] = value

    owner, repo_name = get_github_repo_info()
    repo_fullname = f"{owner}/{repo_name}"
    secrets_url = f"https://github.com/{repo_fullname}/settings/secrets/actions"
    print(
        f"Setting GitHub Actions secrets and variables on {repo_fullname} (preview at: {secrets_url})"
    )

    gh = Github(auth=Auth.Token(github_token))
    try:
        repo = gh.get_repo(repo_fullname)
    except GithubException as e:
        print(f"Error: Could not access repository {repo_fullname}")
        print(f"Details: {e}")
        sys.exit(1)

    for secret_name in SECRETS:
        value = values[secret_name]
        try:
            repo.create_secret(
                secret_name=secret_name,
                unencrypted_value=value,
                secret_type="actions",
            )
        except GithubException as e:
            print(f"Error: Failed to create/update secret {secret_name}")
            print(f"Details: {e}")
            sys.exit(1)
        print(f"✅ Set {secret_name}")

    for name in VARIABLES:
        value = values[name]
        try:
            try:
                repo.get_variable(name).edit(value)
            except UnknownObjectException:
                repo.create_variable(name, value)
        except GithubException as e:
            print(f"Error: Failed to set variable {name}")
            print(f"Details: {e}")
            sys.exit(1)
        print(f"✅ Set variable {name} = {value}")


if __name__ == "__main__":
    main()
