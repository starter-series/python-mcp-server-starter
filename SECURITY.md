# Security Policy

## Reporting a Vulnerability

Use [GitHub's private vulnerability reporting](https://github.com/starter-series/python-mcp-server-starter/security/advisories/new)
(Security tab → Report a vulnerability). Do **not** open a public issue.

## Security Features

This template includes several security measures:

- **gitleaks** — Scans for accidentally committed secrets on every push (pinned by sha256)
- **pip-licenses** — Blocks copyleft licenses (GPL/AGPL)
- **CodeQL** — Static analysis for both `python` source and `actions` workflows
  on every push, PR, and weekly
- **Dependabot** — Automated dependency updates for pip + GitHub Actions, with
  GitHub-side security advisories also enabled (auto-PRs for known CVEs)
- **OIDC publishing** — No PyPI tokens stored as secrets (Trusted Publishers)
- **SLSA build provenance** — `actions/attest-build-provenance` signs wheel/sdist
  artifacts with sigstore; PyPI surfaces this as "Build attestations: verified"
- **Ruff** — Lint rules include `S` (bandit subset), `ASYNC`, `B` (bugbear),
  `RUF`, `SIM`, plus correctness/style/import-order/naming/pyupgrade
- **SHA-pinned third-party actions** — `softprops/action-gh-release`,
  `actions/stale`, `actions/github-script` are pinned to commit SHAs, not tags

## What clones inherit vs. what they don't

Everything above is **code-level** — it ships in the repo and a clone gets
it by virtue of having the same files. The items below are **runtime
GitHub settings** that GitHub does *not* copy when you create a new repo
from a template. **You must enable them on your fork.**

Run these `gh` calls (or use the web UI: Settings → Security/Branches) on
your new repo:

```bash
REPO=your-org/your-repo

# Most of these endpoints need repo admin AND token scopes that the default
# `gh auth login` flow does not request. Refresh first:
gh auth refresh -s admin:repo,security_events

# Secret scanning + push protection (public repos: free; private: needs GHAS)
gh api -X PATCH "repos/$REPO" \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'

# Dependabot security updates + vulnerability alerts
gh api -X PUT "repos/$REPO/vulnerability-alerts"
gh api -X PUT "repos/$REPO/automated-security-fixes"

# Branch protection — the `checks` list below MUST match the actual job names
# your ci.yml produces. The example matches this repo's matrix
# (`security`, `licenses`, plus `test (3.11/3.12/3.13)`). If you change the
# Python matrix (drop 3.11, add 3.14, rename `test`) UPDATE THIS LIST IN
# LOCKSTEP — otherwise required checks point at jobs that never report and
# every PR sits in "Expected — waiting for status" forever.
gh api -X PUT "repos/$REPO/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": {
    "strict": false,
    "checks": [
      {"context": "security"}, {"context": "licenses"},
      {"context": "test (3.11)"}, {"context": "test (3.12)"}, {"context": "test (3.13)"}
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON

# Auto-merge + auto-delete merged branches
gh api -X PATCH "repos/$REPO" -F allow_auto_merge=true -F delete_branch_on_merge=true

# Dependabot auto-merge needs a `manual-review` label (referenced by
# .github/workflows/dependabot-auto-merge.yml). The workflow creates it
# idempotently on first major-bump PR, but you can seed it now:
gh label create manual-review --color fbca04 \
  --description "Needs maintainer decision before merging" --force
```

## Best Practices

- Never commit `.env` files or API keys
- Keep dependencies up to date via Dependabot PRs
- Validate all tool inputs with type hints and explicit schemas
- Use environment variables for sensitive configuration
- **Shell command injection** — If your MCP tools execute shell commands, always escape or sanitize user input. Never pass raw tool arguments to `os.system()` or `subprocess.run(..., shell=True)`. Use `subprocess.run([...], shell=False)` with explicit argument lists instead.
- **Async safety** — Avoid blocking I/O in async tool handlers; use `asyncio.to_thread()` or async libraries (httpx, aiofiles) to prevent starving the event loop.
