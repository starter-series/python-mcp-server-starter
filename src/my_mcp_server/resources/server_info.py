"""Example MCP Resource — exposes server metadata (name, version, runtime) at a
fixed URI.

Resources are how you expose data to the client (in contrast to Tools which
perform actions). Replace with your own resource.

Identity (dist name + version) is NOT re-derived here. It comes from the
package root (:mod:`my_mcp_server`), which is the single source of truth:
``importlib.metadata`` first (authoritative for an installed distribution),
then this package's own ``pyproject.toml`` as a dev fallback, then
``FALLBACK_VERSION``. Routing through that one helper means the version the
server *reports* can never drift from the version the package *is*, and a
foreign / monorepo-parent ``pyproject.toml`` found on a walk-up can never
masquerade as this server's identity. See ``my_mcp_server/__init__.py``.
"""

from __future__ import annotations

import json
import platform
import sys

from mcp.server.fastmcp import FastMCP

from my_mcp_server import DIST_NAME, FALLBACK_VERSION, resolve_version

NAME = "server-info"
URI = "info://server/status"
TITLE = "Server Info"
DESCRIPTION = "Server metadata: name, version, Python runtime, and platform."
MIME_TYPE = "application/json"

# Back-compat alias: the dist name lives in the package root now. Kept so any
# external consumer that imported ``server_info.PKG_NAME`` still resolves.
PKG_NAME = DIST_NAME

__all__ = [
    "DESCRIPTION",
    "FALLBACK_VERSION",
    "MIME_TYPE",
    "NAME",
    "PKG_NAME",
    "TITLE",
    "URI",
    "register",
    "server_info",
]


def _server_metadata() -> dict[str, object]:
    return {
        "name": DIST_NAME,
        "version": resolve_version(),
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
