# ⚠️ Under construction ⚠️

This document will grow over time, for now, it's a place to dump re-used commands and notes on development.

# Git Secret Scanning

We use [`betterleaks`](https://github.com/betterleaks/betterleaks) to help avoid pushing secrets publicly.

NOTE: Docker required for the following command

```bash
docker run \
    -e GIT_CONFIG_COUNT=1 \
    -e GIT_CONFIG_KEY_0="safe.directory" \
    -e GIT_CONFIG_VALUE_0="/src" \
    --rm \
    -v $(pwd):/src \
    ghcr.io/betterleaks/betterleaks:latest \
    git /src
```

# Using Snyk Code analysis

This can be done locally after [installing snyk cli](https://docs.snyk.io/developer-tools/snyk-cli/snyk-cli/install-the-snyk-cli)

`snyk code test`

# pre-commit

Do linters and scans on commit.

(once per cloned repo)

- `cd app`
- `poetry sync --all-groups`
- `poetry run pre-commit install`
