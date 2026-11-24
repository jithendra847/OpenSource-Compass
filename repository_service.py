
import os

import requests


GITHUB_API_BASE = "https://api.github.com"

REQUEST_TIMEOUT = 15

MAX_FILE_SIZE = 100_000  # 100 KB per source file


def get_github_headers():
    """Build headers for GitHub API requests."""

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def fetch_repository_metadata(owner, repo):
    """Fetch repository metadata, including its default branch."""

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

    response = requests.get(
        url,
        headers=get_github_headers(),
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return response.json()


def fetch_repository_tree(owner, repo, branch):
    """Fetch the repository's recursive file tree."""

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{branch}"

    response = requests.get(
        url,
        params={"recursive": "1"},
        headers=get_github_headers(),
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "tree": data.get("tree", []),
        "truncated": data.get("truncated", False),
    }


def fetch_source_file(owner, repo, path):
    """Fetch a text source file from a repository."""

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"

    response = requests.get(
        url,
        headers=get_github_headers(),
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("type") != "file":
        return None

    if data.get("size", 0) > MAX_FILE_SIZE:
        return None

    import base64

    content = data.get("content", "")
    encoding = data.get("encoding")

    if encoding != "base64":
        return None

    try:
        decoded = base64.b64decode(content).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None

    return decoded
