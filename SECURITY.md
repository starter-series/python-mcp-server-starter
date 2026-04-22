# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue
2. Email the maintainer or use GitHub's private vulnerability reporting

## Security Features

This template includes several security measures:

- **gitleaks** — Scans for accidentally committed secrets on every push
- **pip-licenses** — Blocks copyleft licenses (GPL/AGPL)
- **CodeQL** — Static analysis for Python code on every push, PR, and weekly
- **Dependabot** — Automated dependency updates for pip and GitHub Actions
- **OIDC publishing** — No PyPI tokens stored as secrets (Trusted Publishers)
- **Ruff** — Lint rules include security-relevant checks (imports, naming, upgrades)

## Best Practices

- Never commit `.env` files or API keys
- Keep dependencies up to date via Dependabot PRs
- Validate all tool inputs with type hints and explicit schemas
- Use environment variables for sensitive configuration
- **Shell command injection** — If your MCP tools execute shell commands, always escape or sanitize user input. Never pass raw tool arguments to `os.system()` or `subprocess.run(..., shell=True)`. Use `subprocess.run([...], shell=False)` with explicit argument lists instead.
- **Async safety** — Avoid blocking I/O in async tool handlers; use `asyncio.to_thread()` or async libraries (httpx, aiofiles) to prevent starving the event loop.
