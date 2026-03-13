# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public issue
2. Email the maintainer or use GitHub's private vulnerability reporting

## Security Features

This template includes several security measures:

- **gitleaks** — Scans for accidentally committed secrets on every push
- **npm audit** — Checks for known vulnerabilities in dependencies
- **License compliance** — Blocks copyleft licenses (GPL/AGPL)
- **Dependabot** — Automated dependency updates for npm and GitHub Actions
- **OIDC publishing** — No npm tokens stored as secrets
- **Zod validation** — Runtime input validation on all tool parameters

## Best Practices

- Never commit `.env` files or API keys
- Keep dependencies up to date via Dependabot PRs
- Validate all tool inputs with Zod schemas
- Use environment variables for sensitive configuration
- **Shell command injection** — If your MCP tools execute shell commands, always escape or sanitize user input. Never pass raw tool arguments to `child_process.exec()` or template strings in shell commands. Use `execFile()` with explicit argument arrays instead.
