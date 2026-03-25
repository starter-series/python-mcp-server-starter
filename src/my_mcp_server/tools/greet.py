"""Example tool module.

This shows the modular pattern for organizing tools in separate files.
Use this when your server grows beyond a few tools.

Usage in server.py:
    from my_mcp_server.tools.greet import register
    register(mcp)
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations


def register(mcp: FastMCP) -> None:
    """Register greet tools on the server."""

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def greet_formal(name: str, title: str = "Mr.") -> str:
        """Greet someone formally.

        Args:
            name: Name to greet.
            title: Honorific title (default: Mr.).

        Returns:
            A formal greeting.
        """
        return f"Good day, {title} {name}."
