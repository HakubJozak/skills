# GitOps for Tailscale ACLs

Manage your tailnet policy file via Git. PRs validate and test; merges to main apply changes automatically.

Available for all plans. Supports GitHub Actions, GitLab CI, and Bitbucket Pipelines.

Docs: https://tailscale.com/docs/gitops

## Common Setup Steps (All Platforms)

1. **Create `policy.hujson`** in your repo root - copy current policy from Tailscale Admin > Access Controls
2. **Configure secrets** - API key or OAuth credentials + tailnet name
3. **Add CI workflow** - platform-specific config below
4. **Lock the admin console** - Tailscale Admin > Policy file management > "Prevent edits in the admin console" (optionally add repo URL as external reference)

## Authentication Options

**API Key** (simpler, expires):
- `TS_API_KEY` - Generate at Tailscale Admin > Settings > Keys
- `TS_TAILNET` - Your tailnet name (from General settings)

**OAuth Client** (recommended for CI, no expiry):
- `TS_OAUTH_ID` - OAuth client ID
- `TS_OAUTH_SECRET` - OAuth client secret
- `TS_TAILNET` - Your tailnet name

## GitHub Actions

File: `.github/workflows/tailscale.yml`

Uses the official `tailscale/gitops-acl-action@v1` action.

### With API Key

```yaml
name: Sync Tailscale ACLs

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  acls:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy ACL
        if: github.event_name == 'push'
        uses: tailscale/gitops-acl-action@v1
        with:
          api-key: ${{ secrets.TS_API_KEY }}
          tailnet: ${{ secrets.TS_TAILNET }}
          action: apply

      - name: Test ACL
        if: github.event_name == 'pull_request'
        uses: tailscale/gitops-acl-action@v1
        with:
          api-key: ${{ secrets.TS_API_KEY }}
          tailnet: ${{ secrets.TS_TAILNET }}
          action: test
```

### With OAuth Client

```yaml
name: Sync Tailscale ACLs

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  acls:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy ACL
        if: github.event_name == 'push'
        uses: tailscale/gitops-acl-action@v1
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tailnet: ${{ secrets.TS_TAILNET }}
          action: apply

      - name: Test ACL
        if: github.event_name == 'pull_request'
        uses: tailscale/gitops-acl-action@v1
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tailnet: ${{ secrets.TS_TAILNET }}
          action: test
```

Secrets: Add in GitHub repo > Settings > Secrets and variables > Actions.

## GitLab CI

File: `.gitlab-ci.yml`

Uses the official `tailscale-dev/gitops-acl-ci` template.

```yaml
include:
  - project: 'tailscale-dev/gitops-acl-ci'
    ref: main
    file: 'acls.gitlab-ci.yaml'
    inputs:
      api-key: $TS_API_KEY
      tailnet: $TS_TAILNET

stages:
  - test
  - apply

test:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event" &&
           $CI_MERGE_REQUEST_TARGET_BRANCH_NAME == $CI_DEFAULT_BRANCH'

apply:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" &&
           $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

Variables: Add `TS_API_KEY` and `TS_TAILNET` in GitLab > Settings > CI/CD > Variables (enable "Expand variable reference").

## Repo Structure

```
your-repo/
├── policy.hujson           # The tailnet policy file
├── .github/
│   └── workflows/
│       └── tailscale.yml   # GitHub Actions (if using GitHub)
└── .gitlab-ci.yml          # GitLab CI (if using GitLab)
```

## Workflow Behavior

| Event | Action |
|-------|--------|
| Pull request / Merge request | Validates syntax, runs `tests` section. Does NOT apply. Blocks merge if tests fail. |
| Push / merge to main | Validates, runs tests, then applies the policy to your tailnet. |

## Tips

- Always have a `"tests"` section in your policy - GitOps runs them on every change
- Use branch protection rules to require PR reviews before ACL changes reach main
- The `policy.hujson` file supports huJSON (comments and trailing commas)
- After enabling GitOps, lock the admin console editor to prevent drift
- OAuth clients are preferred over API keys for CI - they don't expire
