# autogithubcleaner

Delete forked repositories you no longer contribute to.

## What it does

This tool checks repositories owned by the authenticated GitHub account, looks for forked repos, and deletes the ones with no authored commits from you. By default it runs in dry-run mode and only prints what it would delete.

## Requirements

- Python 3.11 or newer
- A GitHub personal access token stored as `GH_PAT`
- `requests` installed from `requirements.txt`

For a classic PAT, use the `delete_repo` scope. For a fine-grained PAT, grant repository administration access for the repos you want to manage.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Set your token, for example `export GH_PAT=your_token_here`.
4. Run a dry run with `python main.py`.
5. Delete matching repositories with `python main.py --delete`.

You can also set `DELETE_REPOS=true` instead of passing `--delete`.

## GitHub Actions

The workflow is in [.github/workflows/clean-forks.yml](.github/workflows/clean-forks.yml).

1. Add a repository secret named `GH_PAT` in GitHub Settings.
2. Open the Actions tab and run **Clean Forked Repositories** manually.
3. Leave `delete_repositories` set to false for a dry run.
4. Set `delete_repositories` to true when you want the workflow to delete matching repos.
