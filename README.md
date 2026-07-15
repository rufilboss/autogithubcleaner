# Autogithubcleaner

Delete all unuse forked repo

## GitHub Actions setup

This workflow needs a personal access token secret, not the default `GITHUB_TOKEN`. Create a secret named `GH_PAT` in the repository settings and use a token with permission to list and delete the repositories you want to clean up.

For a classic PAT, the `delete_repo` scope is required for deletion. If you use a fine-grained PAT, grant repository administration access for the repos you want the workflow to manage.

The workflow lives in [.github/workflows/clean-forks.yml](.github/workflows/clean-forks.yml). Run it manually from the Actions tab, leave `delete_repositories` off for a dry run, or set it to true to actually delete matching forked repositories.
