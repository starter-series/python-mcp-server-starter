"""Tests for runtime metadata and startup contracts."""

from __future__ import annotations

import logging
import tomllib
from pathlib import Path

from my_mcp_server import server


def _project_table() -> dict[str, object]:
    root = Path(__file__).resolve().parents[1]
    with (root / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)["project"]


def test_console_script_uses_exit_code_wrapper() -> None:
    """The installed command should use the same error-handling wrapper as
    ``python -m my_mcp_server`` instead of calling the server loop directly."""
    project = _project_table()
    assert project["scripts"]["my-mcp-server"] == "my_mcp_server.__main__:run"


def test_project_metadata_has_real_public_owner() -> None:
    """The starter's package metadata should not ship the template placeholder."""
    project = _project_table()
    assert project["authors"] == [{"name": "Heznpc"}]
    assert "Homepage" in project["urls"]


def test_main_runs_stdio_transport(monkeypatch) -> None:
    """MCP clients expect the packaged command to start the stdio transport."""
    calls: list[dict[str, str]] = []

    def fake_run(**kwargs: str) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(server.mcp, "run", fake_run)
    server.main()

    assert calls == [{"transport": "stdio"}]


def test_resolve_log_level_defaults_to_info(monkeypatch) -> None:
    monkeypatch.delenv("MCP_DEBUG", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.setattr(server, "DEBUG", False)

    assert server.resolve_log_level() == "INFO"


def test_resolve_log_level_honors_debug_flag(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    monkeypatch.setattr(server, "DEBUG", True)

    assert server.resolve_log_level() == "DEBUG"


def test_resolve_log_level_rejects_unknown_values(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "NOPE")
    monkeypatch.setattr(server, "DEBUG", False)

    assert server.resolve_log_level() == "INFO"


def test_resolve_log_level_accepts_known_values(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "warning")
    monkeypatch.setattr(server, "DEBUG", False)

    assert server.resolve_log_level() == "WARNING"


def test_logging_level_is_known_to_stdlib() -> None:
    assert getattr(logging, server.resolve_log_level())
