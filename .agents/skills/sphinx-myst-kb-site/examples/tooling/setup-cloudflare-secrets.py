# -*- coding: utf-8 -*-

"""
Set what deploy-doc.yml needs on GitHub Actions of the repository in the
current directory (its ``origin`` remote): the Cloudflare secrets, and the
site's values as variables (CI runs without mise, so it cannot read mise.toml).

The values come from the environment (locally: mise.toml [env] reads them
from the secret store):

- CLOUDFLARE_API_TOKEN: Cloudflare user API token (Cloudflare Pages: Edit)
- CLOUDFLARE_ACCOUNT_ID: the Cloudflare account the token deploys to
- KB_DOMAIN, KB_SUBDOMAIN: the site is https://<KB_SUBDOMAIN>.<KB_DOMAIN>;
  plain values, so they become variables (readable in the logs), not secrets
- GITHUB_TOKEN: GitHub token allowed to write the repository's secrets

Idempotent: every run creates or updates the secrets and variables. Secret
values are never printed; variable values are.
Needs PyGithub in the project venv (for example in a "mise" extra). Run it only on purpose: it changes
the GitHub repository's settings.
"""

import os
import re
import subprocess
import sys

try:
    from github import Auth
    from github import Github
    from github import GithubException
    from github import UnknownObjectException
except ImportError:
    print("Error: PyGithub not installed")
    sys.exit(1)

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


def get_repo_fullname() -> str:
    """
    ``owner/repo`` from the ``origin`` remote (https or ssh URL).
    """
    url = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    # https://github.com/o/r(.git), https://user@github.com/o/r, git@github.com:o/r,
    # ssh://git@github.com/o/r
    match = re.match(
        r"(?:https://(?:[^@/]+@)?github\.com/|(?:ssh://)?git@github\.com[:/])"
        r"([^/]+)/(.+?)(?:\.git)?/?$",
        url,
    )
    if match is None:
        print(f"Error: not a GitHub remote: {url}")
        sys.exit(1)
    return f"{match.group(1)}/{match.group(2)}"


def main():
    github_token = os.environ.get(ENV_GITHUB_TOKEN)
    if not github_token:
        print(f"Error: {ENV_GITHUB_TOKEN} environment variable not set")
        sys.exit(1)

    values = dict()
    for name, env_name in {**SECRETS, **VARIABLES}.items():
        value = os.environ.get(env_name)
        if not value:
            print(f"Error: {env_name} environment variable not set")
            sys.exit(1)
        values[name] = value

    repo_fullname = get_repo_fullname()
    secrets_url = f"https://github.com/{repo_fullname}/settings/secrets/actions"
    print(
        f"Setting GitHub Actions secrets and variables on {repo_fullname} (preview at: {secrets_url})"
    )

    gh = Github(auth=Auth.Token(github_token))
    try:
        repo = gh.get_repo(repo_fullname)
    except GithubException as e:
        print(f"Error: Could not access repository {repo_fullname}: {e}")
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
            print(f"Error: Failed to create/update secret {secret_name}: {e}")
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
            print(f"Error: Failed to set variable {name}: {e}")
            sys.exit(1)
        print(f"✅ Set variable {name} = {value}")


if __name__ == "__main__":
    main()
