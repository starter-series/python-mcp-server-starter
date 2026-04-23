"""Tests for the server-info resource."""

import json
import sys
import tomllib
from pathlib import Path

from my_mcp_server.resources.server_info import (
    DESCRIPTION,
    MIME_TYPE,
    NAME,
    URI,
    server_info,
)


def _pyproject_project() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    with (root / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)["project"]


def test_identity_metadata_is_stable() -> None:
    """Name, URI, and mime type are part of the public contract."""
    assert NAME == "server-info"
    assert URI == "info://server/status"
    assert MIME_TYPE == "application/json"
    assert isinstance(DESCRIPTION, str) and DESCRIPTION


async def test_returns_json_with_expected_shape() -> None:
    """Handler returns a JSON string shaped per the MCP resource contract."""
    raw = await server_info()
    assert isinstance(raw, str)

    payload = json.loads(raw)
    assert set(payload) == {"name", "version", "runtime"}
    assert set(payload["runtime"]) == {"python", "platform", "arch"}

    assert isinstance(payload["name"], str) and payload["name"]
    assert isinstance(payload["version"], str) and payload["version"]


async def test_version_matches_pyproject() -> None:
    """Version field reflects pyproject.toml, not a hardcoded constant."""
    project = _pyproject_project()
    payload = json.loads(await server_info())

    assert payload["name"] == project["name"]
    assert payload["version"] == project["version"]


async def test_runtime_reflects_current_interpreter() -> None:
    """Python version in runtime matches sys.version."""
    payload = json.loads(await server_info())
    assert payload["runtime"]["python"] == sys.version.split()[0]


async def test_registered_on_server() -> None:
    """The resource is wired into the server at import time."""
    from my_mcp_server.server import mcp

    resources = await mcp.list_resources()
    uris = [str(r.uri) for r in resources]
    assert URI in uris
