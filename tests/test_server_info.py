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
# tree (where pyproject.toml IS reachable).


async def test_falls_back_to_importlib_metadata_when_pyproject_missing(
    monkeypatch,
) -> None:
    """Wheel install: _read_pyproject() returns None, both name and version
    come from importlib.metadata (both sides of the equality below resolve
    against the SAME source, not pyproject-on-disk — so a maintainer who
    bumps pyproject.toml's version without re-running ``pip install -e .``
    won't see a misleading failure here)."""
    from importlib.metadata import version as imp_version

    from my_mcp_server.resources import server_info as mod

    monkeypatch.setattr(mod, "_read_pyproject", lambda: None)
    payload = json.loads(await mod.server_info())

    # `mod.PKG_NAME` is derived from `__package__` — survives a clone rename
    # without re-hardcoding the literal in the test.
    assert payload["name"] == mod.PKG_NAME
    assert payload["version"] == imp_version(mod.PKG_NAME)


async def test_falls_back_to_zero_version_when_package_not_installed(
    monkeypatch,
) -> None:
    """Edge of the edge: pyproject missing AND importlib.metadata can't find
    the dist. Should return FALLBACK_VERSION instead of raising
    PackageNotFoundError."""
    from my_mcp_server.resources import server_info as mod

    def raise_not_found(*_args: object, **_kw: object) -> str:
        # Tolerant signature in case `version()` ever gets called with kwargs.
        raise mod.PackageNotFoundError("simulated wheel-install-without-metadata")

    monkeypatch.setattr(mod, "_read_pyproject", lambda: None)
    monkeypatch.setattr(mod, "version", raise_not_found)

    payload = json.loads(await mod.server_info())
    assert payload["version"] == mod.FALLBACK_VERSION


def test_read_pyproject_returns_none_when_project_table_missing(tmp_path, monkeypatch) -> None:
    """Walk-up finds a pyproject.toml with no [project] table — must exit at
    the inner `return None` (NOT continue walking — that's the contract).

    Strengthened with a tomllib.load spy so a future refactor that drops the
    explicit inner return and falls through to keep walking gets caught here
    (the spy would see >1 load) instead of silently passing because no other
    pyproject.toml is reachable on the way to /.
    """
    from my_mcp_server.resources import server_info as mod

    pkg = tmp_path / "pkg"
    pkg.mkdir()
    fake_pyproject = tmp_path / "pyproject.toml"
    fake_pyproject.write_text("[build-system]\nrequires = []\n")
    fake_file = pkg / "server_info.py"
    fake_file.write_text("")

    loaded_paths: list[str] = []
    original_load = mod.tomllib.load

    def spy_load(fh):  # type: ignore[no-untyped-def]
        loaded_paths.append(getattr(fh, "name", ""))
        return original_load(fh)

    monkeypatch.setattr(mod.tomllib, "load", spy_load)
    monkeypatch.setattr(mod, "__file__", str(fake_file))

    assert mod._read_pyproject() is None
    assert loaded_paths == [str(fake_pyproject)], (
        f"_read_pyproject must stop at the first pyproject.toml encountered; "
        f"saw {len(loaded_paths)} load(s): {loaded_paths}"
    )


def test_read_pyproject_returns_none_when_no_pyproject_anywhere(tmp_path, monkeypatch) -> None:
    """Walk-up exhausts the parent chain without finding any pyproject.toml —
    exercises the outer `return None` after the loop (server_info.py:42).

    Without this test the loop-exhaustion path is 0% covered: the
    "fallback" tests above bypass the walk entirely by monkeypatching
    `_read_pyproject` itself.
    """
    from my_mcp_server.resources import server_info as mod

    pkg = tmp_path / "pkg"
    pkg.mkdir()
    fake_file = pkg / "server_info.py"
    fake_file.write_text("")
    # Deliberately no pyproject.toml anywhere in tmp_path or its ancestors
    # (system tmp dirs don't contain one), so the walk reaches root.

    monkeypatch.setattr(mod, "__file__", str(fake_file))
    assert mod._read_pyproject() is None


def test_pkg_name_derived_from_package() -> None:
    """PKG_NAME is the dist-name form (hyphens) of the import package name —
    pins the rename-safety contract documented in server_info.py."""
    from my_mcp_server.resources import server_info as mod

    assert mod.PKG_NAME == "my-mcp-server"
    # Sanity: derivation tracks __package__, not a stray literal somewhere.
    root_import = (mod.__package__ or "").split(".")[0]
    assert root_import.replace("_", "-") == mod.PKG_NAME
