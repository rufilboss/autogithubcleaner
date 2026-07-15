"""Delete forked repositories the authenticated user has not contributed to.

The script is safe by default and only prints the repos it would delete unless
`--delete` is passed or `DELETE_REPOS=true` is set in the environment.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

import requests

API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 30


def build_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    expected_status: int | None = None,
    **kwargs,
):
    response = session.request(method, url, timeout=DEFAULT_TIMEOUT, **kwargs)
    if expected_status is not None and response.status_code != expected_status:
        raise requests.HTTPError(
            f"{method} {url} failed with status {response.status_code}: {response.text}",
            response=response,
        )
    response.raise_for_status()
    return response.json() if response.content else None


def get_authenticated_user(session: requests.Session, headers: dict[str, str]) -> dict:
    return request_json(session, "GET", f"{API_BASE}/user", headers=headers)


def iter_owned_repositories(session: requests.Session, headers: dict[str, str]) -> Iterable[dict]:
    page = 1
    while True:
        repos = request_json(
            session,
            "GET",
            f"{API_BASE}/user/repos",
            headers=headers,
            params={"type": "owner", "per_page": 100, "page": page},
        )
        if not repos:
            break
        for repo in repos:
            yield repo
        if len(repos) < 100:
            break
        page += 1


def has_authored_commits(
    session: requests.Session,
    headers: dict[str, str],
    full_name: str,
    login: str,
) -> bool:
    commits = request_json(
        session,
        "GET",
        f"{API_BASE}/repos/{full_name}/commits",
        headers=headers,
        params={"author": login, "per_page": 1},
    )
    return bool(commits)


def delete_repository(session: requests.Session, headers: dict[str, str], full_name: str) -> None:
    request_json(
        session,
        "DELETE",
        f"{API_BASE}/repos/{full_name}",
        headers=headers,
        expected_status=204,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete forked repositories that the authenticated user never contributed to."
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete repositories instead of doing a dry run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("Missing GH_PAT or GITHUB_TOKEN environment variable.", file=sys.stderr)
        return 1

    should_delete = args.delete or os.getenv("DELETE_REPOS", "false").lower() == "true"

    session = requests.Session()
    headers = build_headers(token)
    user = get_authenticated_user(session, headers)
    login = user["login"]

    deleted = 0
    reviewed = 0

    for repo in iter_owned_repositories(session, headers):
        if not repo.get("fork") or repo.get("private"):
            continue

        reviewed += 1
        full_name = repo["full_name"]

        if has_authored_commits(session, headers, full_name, login):
            print(f"Keeping {full_name}: authored commits found")
            continue

        if should_delete:
            delete_repository(session, headers, full_name)
            deleted += 1
            print(f"Deleted {full_name}")
        else:
            print(f"Would delete {full_name}")

    print(f"Reviewed {reviewed} forked repositories.")
    if should_delete:
        print(f"Deleted {deleted} repositories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())