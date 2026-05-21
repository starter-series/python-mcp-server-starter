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


# --- wheel-install fallback path ---------------------------------------------
# When the package is installed from a wheel, pyproject.toml is NOT shipped,
# so `_read_pyproject()` returns None and `_server_metadata()` must fall back
# to `importlib.metadata.version()`. The tests above all exercise the source
# tree (where pyproject.toml IS reachable) — without these two cases, the
# production install path is 0% covered.


async def test_falls_back_to_importlib_metadata_when_pyproject_missing(
    monkeypatch,
) -> None:
    """Wheel install: _read_pyproject() returns None, version comes from metadata."""
    from my_mcp_server.resources import server_info as mod

    monkeypatch.setattr(mod, "_read_pyproject", lambda: None)
    payload = json.loads(await mod.server_info())

    # Package is installed editable in tests; importlib.metadata can find it.
    project = _pyproject_project()
    assert payload["name"] == "my-mcp-server"
    assert payload["version"] == project["version"]


async def test_falls_back_to_zero_version_when_package_not_installed(
    monkeypatch,
) -> None:
    """Edge of the edge: pyproject missing AND importlib.metadata can't find
    the dist. Should return '0.0.0' instead of raising PackageNotFoundError."""
    from my_mcp_server.resources import server_info as mod

    def raise_not_found(_name: str) -> str:
        raise mod.PackageNotFoundError("simulated wheel-install-without-metadata")

    monkeypatch.setattr(mod, "_read_pyproject", lambda: None)
    monkeypatch.setattr(mod, "version", raise_not_found)

    payload = json.loads(await mod.server_info())
    assert payload["version"] == "0.0.0"


def test_read_pyproject_returns_none_when_project_table_missing(tmp_path, monkeypatch) -> None:
    """Walk-up finds a pyproject.toml with no [project] table — exit path
    at line 41 (the `return None` inside the `is_file` branch)."""
    from my_mcp_server.resources import server_info as mod

    # Build a fake directory tree: tmp_path/pkg/server_info.py with a
    # pyproject.toml at tmp_path that lacks [project].
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (tmp_path / "pyproject.toml").write_text("[build-system]\nrequires = []\n")
    fake_file = pkg / "server_info.py"
    fake_file.write_text("")

    monkeypatch.setattr(mod, "__file__", str(fake_file))
    assert mod._read_pyproject() is None
