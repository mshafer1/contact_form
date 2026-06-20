# ⚠️ Under construction ⚠️

This document will grow over time, for now, it's a place to dump re-used commands and notes on development.

# Git Secret Scanning

We use [`betterleaks`](https://github.com/betterleaks/betterleaks) to help avoid pushing secrets publicly.

NOTE: Docker required for the following command



# pre-commit

Do linters and scans on commit.

(once per cloned repo)

- `cd app`
- `poetry sync --all-groups`
- `poetry run pre-commit install`
