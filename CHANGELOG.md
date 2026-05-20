# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file is **append-only**. Each release on
[GitHub Releases](https://github.com/starter-series/python-mcp-server-starter/releases) is the
authoritative source — `.github/workflows/update-changelog.yml` prepends a
new entry here when a release is published, so the file mirrors the
release feed without duplicating maintenance.

The `[Unreleased]` section below is **informational**. The auto-generated
release notes from GitHub (PR titles since the last tag) are what actually
get prepended; hand-written `[Unreleased]` bullets are a courtesy for
people reading this file directly. Clear them by hand when cutting a release.

## [Unreleased]

### Added
- `actions/attest-build-provenance@v3` step in `cd.yml` — wheel/sdist now
  ship with sigstore-signed SLSA build provenance attestations; PyPI surfaces
  this as "Build attestations: verified".
- CodeQL now scans `actions` workflows in addition to `python` source, so
  workflow injection / missing-permissions issues are caught alongside code
  issues.
- `pytest-cov` to `[dev]` deps + `--cov-fail-under=70` baseline in `pyproject.toml`
  (matches measured 71% coverage; bump only upward).
- Ruff rule set extended with `B` (bugbear), `S` (bandit subset), `ASYNC`,
  `RUF`, `SIM` — security/correctness checks beyond the previous style-only set.
- `.github/CODEOWNERS` — solo-dev auto-assignment for Dependabot PRs and outside
  contributions.
- `.github/ISSUE_TEMPLATE/{bug_report,feature_request,config}.yml` +
  `.github/PULL_REQUEST_TEMPLATE.md` — minimal templates with scope checks.
- `.python-version` (pyenv/uv users).

### Changed
- Third-party Actions are now SHA-pinned (with `# vX.Y.Z` comment for human
  legibility): `softprops/action-gh-release` v3.0.0, `actions/stale` v10.2.0,
  `actions/github-script` v9.0.0, `actions/attest-build-provenance` v3.2.0.
  First-party `actions/*`, `github/codeql-action/*`, and
  `pypa/gh-action-pypi-publish@release/v1` keep tag pinning per their respective
  publisher guidance.
- Dev tooling now has major-version bounds: `ruff>=0.15,<1`, `mypy>=2,<3`,
  `pytest>=8,<10`, `pytest-asyncio>=1,<2`. Prevents a surprise major release
  from turning CI red overnight.
- `SECURITY.md` documents the full feature set including the GitHub repo-side
  toggles (secret scanning + push protection + Dependabot security updates +
  branch protection on `main`).

### Fixed
- Stop tracking `.coverage` and add coverage artifacts (`.coverage*`, `htmlcov/`,
  `coverage.xml`) to `.gitignore` so local test runs no longer pollute commits.
- Replace EN DASH (`–`) with hyphen-minus in `greet` field description
  (`server.py:71`) — ruff `RUF001` flagged the ambiguous character.

