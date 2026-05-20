# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue
2. Email the maintainer or use GitHub's private vulnerability reporting

## Reporting

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
- **Repo-side toggles enabled** — Secret scanning + push protection (blocks
  commits that contain leaked secrets) + Dependabot security updates +
  branch protection on `main` (required CI checks before merge)

## Best Practices

- Never commit `.env` files or API keys
- Keep dependencies up to date via Dependabot PRs
- Validate all tool inputs with type hints and explicit schemas
- Use environment variables for sensitive configuration
- **Shell command injection** — If your MCP tools execute shell commands, always escape or sanitize user input. Never pass raw tool arguments to `os.system()` or `subprocess.run(..., shell=True)`. Use `subprocess.run([...], shell=False)` with explicit argument lists instead.
- **Async safety** — Avoid blocking I/O in async tool handlers; use `asyncio.to_thread()` or async libraries (httpx, aiofiles) to prevent starving the event loop.
