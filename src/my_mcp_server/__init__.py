"""My MCP Server.

Single source of truth for this package's distribution identity (name +
version). ``server_info`` (the MCP resource) and any other consumer import
from here rather than re-deriving the dist name or re-reading metadata, so
the two can never drift apart.

Resolution order, deliberately metadata-first:

1. ``importlib.metadata`` — authoritative for an *installed* distribution
   (wheel or ``pip install -e .``). This is what the running server actually
   is, regardless of what files happen to sit on disk above it.
2. pyproject ``[project].version`` — dev fallback for a source checkout that
   was never installed. Accepted *only* when ``[project].name`` matches this
   package, so a foreign / monorepo-parent ``pyproject.toml`` encountered on
   the walk-up can never masquerade as this server's identity.
3. ``FALLBACK_VERSION`` — last resort (renamed clone, neither source usable).

The dist name is derived from ``__package__`` (not a hardcoded literal) so a
clone that renames ``src/my_mcp_server/`` picks the new name up automatically
and does not crash on import.
"""

from __future__ import annotations

import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

# Convention: PyPI distribution name = import package name with underscores
# rewritten as hyphens. Derived from ``__package__`` so a renamed clone does
# not have to update a hardcoded literal here AND in server_info.
DIST_NAME = (__package__ or "my_mcp_server").replace("_", "-")
FALLBACK_VERSION = "0.0.0"


def _read_own_pyproject() -> dict[str, str] | None:
    """Walk up from this file and return the FIRST ``[project]`` table whose
    ``name`` matches this package's :data:`DIST_NAME`.

    A non-matching ``[project]`` table (a foreign or monorepo-parent
    ``pyproject.toml``) is skipped — the walk continues — so a parent project
    can never be served as this server's identity. Returns ``None`` if no
    matching pyproject is reachable (e.g. installed from a wheel without the
    source tree).
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "pyproject.toml"
        if not candidate.is_file():
            continue
        with candidate.open("rb") as fh:
            data = tomllib.load(fh)
        project = data.get("project")
        if isinstance(project, dict) and project.get("name") == DIST_NAME:
            return project
        # Foreign / parent pyproject (or one without a matching [project]):
        # keep walking — do NOT let it stand in for this package.
    return None


def resolve_version() -> str:
    """Return this distribution's version, metadata-first.

    See the module docstring for the full resolution order. This is the single
    function every consumer (``__version__`` below, ``server_info``) routes
    through, so there is exactly one place that decides what "the version" is.
    """
    try:
        return version(DIST_NAME)
    except PackageNotFoundError:
        pass

    project = _read_own_pyproject()
    if project is not None:
        return str(project.get("version", FALLBACK_VERSION))

    return FALLBACK_VERSION


__version__ = resolve_version()

__all__ = ["DIST_NAME", "FALLBACK_VERSION", "__version__", "resolve_version"]
