"""Tests for the server-info resource.

Identity resolution (metadata-first, foreign-pyproject guard, fallback) lives
in the package root now and is tested in ``test_version_resolution.py``. These
tests cover the resource contract and that the resource *consumes* that single
source of truth rather than re-deriving identity on its own.
"""

import json
import sys
import tomllib
from pathlib import Path

import my_mcp_server
from my_mcp_server.resources.server_info import (
    DESCRIPTION,
    MIME_TYPE,
    NAME,
    PKG_NAME,
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


async def test_name_and_version_come_from_package_single_source() -> None:
    """The resource reports the package's own identity, not a re-derivation.

    ``name`` is the package's ``DIST_NAME`` and ``version`` is whatever
    ``resolve_version()`` returns — so the value the server reports can never
    drift from the value the package is.
    """
    payload = json.loads(await server_info())
    assert payload["name"] == my_mcp_server.DIST_NAME
    assert payload["version"] == my_mcp_server.resolve_version()


async def test_version_matches_pyproject_for_editable_install() -> None:
    """For this source checkout (installed editable in CI), the metadata-first
    version coincides with pyproject's — a regression guard that the reported
    version is the real one, not a hardcoded constant."""
    project = _pyproject_project()
    payload = json.loads(await server_info())

    assert payload["name"] == project["name"]
    assert payload["version"] == project["version"]


async def test_resource_tracks_resolve_version(monkeypatch) -> None:
    """If ``resolve_version()`` changes, the resource changes with it — proves
    the resource routes through the single source instead of reading metadata
    or pyproject on its own."""
    from my_mcp_server.resources import server_info as mod

    monkeypatch.setattr(mod, "resolve_version", lambda: "9.9.9-sentinel")
    payload = json.loads(await mod.server_info())
    assert payload["version"] == "9.9.9-sentinel"


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


def test_pkg_name_is_back_compat_alias_of_dist_name() -> None:
    """``PKG_NAME`` is retained as a back-compat alias of the package's
    ``DIST_NAME`` (the dist-name form, hyphens) so external importers of
    ``server_info.PKG_NAME`` keep working after identity moved to the root."""
    assert PKG_NAME == "my-mcp-server"
    assert PKG_NAME == my_mcp_server.DIST_NAME
