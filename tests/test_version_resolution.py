"""Tests for distribution-identity resolution in the package root.

``my_mcp_server.resolve_version()`` is the single source of truth for the
version the server reports. Resolution order (see ``__init__.py``):

1. ``importlib.metadata`` — authoritative for an installed distribution.
2. this package's own ``pyproject.toml`` — dev fallback, accepted ONLY when
   ``[project].name`` matches ``DIST_NAME`` (the foreign-pyproject guard).
3. ``FALLBACK_VERSION`` — last resort.

These tests pin each branch, with particular attention to the guard: a
foreign / monorepo-parent ``pyproject.toml`` encountered on the walk-up must
never be served as this package's identity.
"""

import textwrap
from pathlib import Path

import my_mcp_server as pkg


def test_dist_name_is_hyphenated_form_of_package() -> None:
    """DIST_NAME is the PyPI-style (hyphenated) form of the import package,
    derived from ``__package__`` — not a stray hardcoded literal."""
    assert pkg.DIST_NAME == "my-mcp-server"
    assert (pkg.__package__ or "").replace("_", "-") == pkg.DIST_NAME


def test_resolve_version_prefers_installed_metadata(monkeypatch) -> None:
    """importlib.metadata wins outright; pyproject is not even consulted."""

    def boom() -> dict[str, str] | None:  # pragma: no cover - must not run
        raise AssertionError("pyproject must not be read when metadata resolves")

    monkeypatch.setattr(pkg, "version", lambda _name: "7.7.7")
    monkeypatch.setattr(pkg, "_read_own_pyproject", boom)
    assert pkg.resolve_version() == "7.7.7"


def test_resolve_version_falls_back_to_matching_pyproject(monkeypatch) -> None:
    """Source checkout, not installed: version comes from the OWN pyproject."""

    def raise_not_found(_name: str) -> str:
        raise pkg.PackageNotFoundError(_name)

    monkeypatch.setattr(pkg, "version", raise_not_found)
    monkeypatch.setattr(pkg, "_read_own_pyproject", lambda: {"version": "2.3.4"})
    assert pkg.resolve_version() == "2.3.4"


def test_resolve_version_uses_fallback_when_no_source(monkeypatch) -> None:
    """Neither metadata nor a matching pyproject reachable (e.g. renamed clone,
    wheel without source) → FALLBACK_VERSION, never an exception."""

    def raise_not_found(_name: str) -> str:
        raise pkg.PackageNotFoundError(_name)

    monkeypatch.setattr(pkg, "version", raise_not_found)
    monkeypatch.setattr(pkg, "_read_own_pyproject", lambda: None)
    assert pkg.resolve_version() == pkg.FALLBACK_VERSION


def _write_pyproject(path: Path, name: str | None, version: str) -> None:
    if name is None:
        body = f'[project]\nversion = "{version}"\n'
    else:
        body = f'[project]\nname = "{name}"\nversion = "{version}"\n'
    path.write_text(textwrap.dedent(body))


def test_read_own_pyproject_returns_matching_project(tmp_path, monkeypatch) -> None:
    """Walk-up finds a pyproject whose [project].name == DIST_NAME → returned."""
    pkgdir = tmp_path / "my_mcp_server"
    pkgdir.mkdir()
    _write_pyproject(tmp_path / "pyproject.toml", pkg.DIST_NAME, "5.6.7")
    fake_file = pkgdir / "__init__.py"
    fake_file.write_text("")

    monkeypatch.setattr(pkg, "__file__", str(fake_file))
    project = pkg._read_own_pyproject()
    assert project is not None
    assert project["name"] == pkg.DIST_NAME
    assert project["version"] == "5.6.7"


def test_read_own_pyproject_skips_foreign_and_finds_own(tmp_path, monkeypatch) -> None:
    """THE GUARD. A foreign/parent pyproject sits ABOVE the package's own one
    on the walk-up. The walk must SKIP the nearer foreign table and keep going
    until it finds the table whose name matches DIST_NAME — a monorepo parent
    can never masquerade as this server's identity.

    Layout (walk goes child -> parent):
        tmp/foreign-parent/pyproject.toml        name = "some-monorepo-root"
        tmp/foreign-parent/proj/pyproject.toml   name = DIST_NAME  <- ours
        tmp/foreign-parent/proj/my_mcp_server/__init__.py
    """
    parent = tmp_path / "foreign-parent"
    proj = parent / "proj"
    pkgdir = proj / "my_mcp_server"
    pkgdir.mkdir(parents=True)

    # Nearer on the walk-up: a FOREIGN pyproject that must be skipped.
    _write_pyproject(proj / "pyproject.toml", pkg.DIST_NAME, "1.1.1")  # ours (nearest)
    _write_pyproject(parent / "pyproject.toml", "some-monorepo-root", "0.0.1")  # foreign

    fake_file = pkgdir / "__init__.py"
    fake_file.write_text("")
    monkeypatch.setattr(pkg, "__file__", str(fake_file))

    project = pkg._read_own_pyproject()
    assert project is not None
    assert project["name"] == pkg.DIST_NAME
    assert project["version"] == "1.1.1"


def test_read_own_pyproject_skips_foreign_then_exhausts(tmp_path, monkeypatch) -> None:
    """Only a foreign pyproject is reachable (no own one anywhere) → the guard
    skips it and the walk exhausts to ``None``. This is exactly the case the
    old (unguarded) code got wrong: it would have returned the foreign table."""
    parent = tmp_path / "foreign-parent"
    pkgdir = parent / "my_mcp_server"
    pkgdir.mkdir(parents=True)
    _write_pyproject(parent / "pyproject.toml", "some-other-dist", "9.9.9")

    fake_file = pkgdir / "__init__.py"
    fake_file.write_text("")
    monkeypatch.setattr(pkg, "__file__", str(fake_file))

    assert pkg._read_own_pyproject() is None


def test_read_own_pyproject_skips_table_without_name(tmp_path, monkeypatch) -> None:
    """A [project] table that has no ``name`` key is non-matching → skipped,
    walk continues / exhausts to None (covers the isinstance/name branch)."""
    pkgdir = tmp_path / "my_mcp_server"
    pkgdir.mkdir()
    _write_pyproject(tmp_path / "pyproject.toml", None, "3.3.3")  # no name key
    fake_file = pkgdir / "__init__.py"
    fake_file.write_text("")

    monkeypatch.setattr(pkg, "__file__", str(fake_file))
    assert pkg._read_own_pyproject() is None


def test_read_own_pyproject_returns_none_when_no_pyproject_anywhere(tmp_path, monkeypatch) -> None:
    """Walk-up exhausts the parent chain without finding any pyproject.toml →
    outer ``return None`` (system tmp dirs contain no pyproject.toml)."""
    pkgdir = tmp_path / "my_mcp_server"
    pkgdir.mkdir()
    fake_file = pkgdir / "__init__.py"
    fake_file.write_text("")

    monkeypatch.setattr(pkg, "__file__", str(fake_file))
    assert pkg._read_own_pyproject() is None
