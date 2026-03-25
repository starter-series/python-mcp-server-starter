"""Tests for MCP server tools."""

from my_mcp_server.server import greet


async def test_greet():
    """Greet returns a greeting."""
    result = await greet(name="World")
    assert result == "Hello, World!"


async def test_greet_custom_name():
    """Greet handles custom names."""
    result = await greet(name="Ploidy")
    assert result == "Hello, Ploidy!"
