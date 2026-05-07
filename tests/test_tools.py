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


async def test_greet_rejects_oversize_name():
    """max_length=200 — long strings must be rejected."""
    with pytest.raises(ValidationError):
        await _validated_greet(name="x" * 201)


async def test_greet_accepts_boundary_lengths():
    """1 and 200 are inclusive bounds and must pass."""
    assert await _validated_greet(name="a") == "Hello, a!"
    long_name = "a" * 200
    assert await _validated_greet(name=long_name) == f"Hello, {long_name}!"
