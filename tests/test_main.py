"""Tests for the ``python -m my_mcp_server`` entry-point wrapper.

These exercise ``__main__.run()`` directly — the body of __main__.py is
guarded by ``if __name__ == "__main__":`` so importing the module no
longer blocks on the server loop, which is what makes these tests possible.
"""

from __future__ import annotations

import logging

from my_mcp_server import __main__ as entry


def test_run_returns_zero_on_clean_exit(monkeypatch) -> None:
    """main() returns normally → run() returns 0."""
    monkeypatch.setattr(entry, "main", lambda: None)
    assert entry.run() == 0


def test_run_returns_zero_on_keyboard_interrupt(monkeypatch) -> None:
    """Ctrl-C during main() → run() exits cleanly with 0."""

    def raise_keyboard_interrupt() -> None:
        raise KeyboardInterrupt()

    monkeypatch.setattr(entry, "main", raise_keyboard_interrupt)
    assert entry.run() == 0


def test_run_returns_one_and_logs_on_unhandled_exception(monkeypatch, caplog) -> None:
    """Any other exception → run() returns 1 AND logs the traceback. Both
    halves are part of the contract: silently exiting 1 without the log
    would make production debugging much harder."""

    def boom() -> None:
        raise RuntimeError("simulated server crash")

    monkeypatch.setattr(entry, "main", boom)

    with caplog.at_level(logging.ERROR):
        rc = entry.run()

    assert rc == 1
    assert "Fatal error running MCP server" in caplog.text
    assert "simulated server crash" in caplog.text
