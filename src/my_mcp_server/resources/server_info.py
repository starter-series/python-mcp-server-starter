"""Example MCP Resource — exposes server metadata (name, version, runtime) at a
fixed URI.

Resources are how you expose data to the client (in contrast to Tools which
perform actions). Replace with your own resource.
"""

from __future__ import annotations

import json
import platform
import sys
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from mcp.server.fastmcp import FastMCP

NAME = "server-info"
URI = "info://server/status"
TITLE = "Server Info"
DESCRIPTION = "Server metadata: name, version, Python runtime, and platform."
MIME_TYPE = "application/json"


def _read_pyproject() -> dict[str, str] | None:
    """Walk up from this file to locate pyproject.toml and parse it.

    Returns the ``[project]`` table as a dict, or None if not found
    (e.g. when installed from a wheel without the source tree).
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            with candidate.open("rb") as fh:
                data = tomllib.load(fh)
            project = data.get("project")
            if isinstance(project, dict):
                return project
            return None
    return None


def _server_metadata() -> dict[str, object]:
    project = _read_pyproject()
    if project is not None:
        pkg_name = str(project.get("name", "my-mcp-server"))
        pkg_version = str(project.get("version", "0.0.0"))
    else:
        # Fallback for wheel installs where pyproject.toml isn't shipped.
        pkg_name = "my-mcp-server"
        try:
            pkg_version = version(pkg_name)
        except PackageNotFoundError:
            pkg_version = "0.0.0"

    return {
        "name": pkg_name,
        "version": pkg_version,
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.system().lower(),
            "arch": platform.machine(),
        },
    }


async def server_info() -> str:
    """Return server metadata as a JSON string."""
    return json.dumps(_server_metadata(), indent=2)


def register(mcp: FastMCP) -> None:
    """Register the server-info resource on the server."""
    mcp.resource(
        URI,
        name=NAME,
        title=TITLE,
        description=DESCRIPTION,
        mime_type=MIME_TYPE,
    )(server_info)
