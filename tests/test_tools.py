"""Tests for MCP server tools."""

import pytest
from pydantic import ValidationError, validate_call

from my_mcp_server.server import greet


async def test_greet():
    """Greet returns a greeting."""
    result = await greet(name="World")
    assert result == "Hello, World!"


async def test_greet_custom_name():
    """Greet handles custom names."""
    result = await greet(name="Ploidy")
    assert result == "Hello, Ploidy!"


async def test_greet_strips_surrounding_whitespace():
    """Whitespace around a valid name is normalization, not part of the name."""
    result = await _validated_greet(name="  World  ")
    assert result == "Hello, World!"


# --- input bound enforcement -----------------------------------------------
# Calling the tool function directly bypasses FastMCP's protocol-level
# schema validation. Wrapping with `validate_call` is the same enforcement
# FastMCP applies, so we cover Annotated[..., Field(min_length, max_length)]
# without spinning up the MCP transport.

_validated_greet = validate_call(greet)


async def test_greet_rejects_empty_name():
    """min_length=1 — empty string must be rejected at the protocol layer."""
    with pytest.raises(ValidationError):
        await _validated_greet(name="")


async def test_greet_rejects_whitespace_only_name():
    """strip_whitespace + min_length=1 rejects blank-looking input."""
    with pytest.raises(ValidationError):
        await _validated_greet(name="   ")


async def test_greet_rejects_oversize_name():
    """max_length=200 — long strings must be rejected."""
    with pytest.raises(ValidationError):
        await _validated_greet(name="x" * 201)


async def test_greet_accepts_boundary_lengths():
    """1 and 200 are inclusive bounds and must pass."""
    assert await _validated_greet(name="a") == "Hello, a!"
    long_name = "a" * 200
    assert await _validated_greet(name=long_name) == f"Hello, {long_name}!"


# --- protocol-level contract --------------------------------------------------
# Parallels test_server_info.py::test_registered_on_server and
# test_code_review.py::test_registered_on_server — without this, the tool's
# JSON Schema generation (the actual MCP wire contract) is never exercised.


def _schema_constraint(prop: dict, key: str) -> object:
    """Read a JSON Schema keyword that may sit at the top of a property OR
    inside an ``anyOf`` branch (which is how pydantic emits constraints once
    a field gains a union type, e.g. ``Annotated[str | None, Field(...)]``).
    Returns the first match; raises a clear AssertionError if neither shape
    contains the key."""
    if key in prop:
        return prop[key]
    for sub in prop.get("anyOf", []):
        if key in sub:
            return sub[key]
    raise AssertionError(f"{key!r} not found in property schema {prop!r}")


async def test_greet_registered_on_server():
    """The greet tool is wired into the server and its JSON Schema reflects
    the Annotated[..., Field(min_length, max_length)] constraints."""
    from my_mcp_server.server import mcp

    tools = await mcp.list_tools()
    by_name = {t.name: t for t in tools}
    assert "greet" in by_name, f"greet missing from list_tools(); got {list(by_name)}"

    schema = by_name["greet"].inputSchema
    name_prop = schema["properties"]["name"]
    assert _schema_constraint(name_prop, "type") == "string"
    assert _schema_constraint(name_prop, "minLength") == 1
    assert _schema_constraint(name_prop, "maxLength") == 200
    assert "name" in schema["required"]
