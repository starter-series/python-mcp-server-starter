"""MCP server entry point.

Registers tools, resources, and prompts via FastMCP.
Add your own tools in the tools/ directory following the greet.py pattern.
"""

import logging
import os

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from my_mcp_server.prompts.code_review import register as register_code_review
from my_mcp_server.resources.server_info import register as register_server_info

logger = logging.getLogger("my_mcp_server")

# ---------------------------------------------------------------------------
# Configuration — add your env vars here
# ---------------------------------------------------------------------------

DEBUG = os.environ.get("MCP_DEBUG", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "my-mcp-server",
    instructions="An MCP server. Replace this with your description.",
)


# ---------------------------------------------------------------------------
# Helpers — use ok() and err() for consistent tool responses
# ---------------------------------------------------------------------------


def ok(data: str | dict[str, object]) -> dict[str, object]:
    """Return a successful tool response."""
    text = data if isinstance(data, str) else str(data)
    return {"content": [{"type": "text", "text": text}]}


def err(message: str) -> dict[str, object]:
    """Return an error tool response."""
    return {"content": [{"type": "text", "text": message}], "isError": True}


# ---------------------------------------------------------------------------
# Tools — add your own in tools/ and import here
# ---------------------------------------------------------------------------


@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def greet(name: str) -> str:
    """Greet someone by name.

    Args:
        name: Name to greet.

    Returns:
        A greeting message.
    """
    logger.info("Greeting %s", name)
    return f"Hello, {name}!"


# To add more tools, create files in tools/ and register them:
#
#   from my_mcp_server.tools.your_tool import register
#   register(mcp)
#
# See tools/greet.py for the modular pattern.


# ---------------------------------------------------------------------------
# Resources — expose data to the client at a stable URI
# ---------------------------------------------------------------------------

register_server_info(mcp)


# ---------------------------------------------------------------------------
# Prompts — reusable, parameterized message templates
# ---------------------------------------------------------------------------

register_code_review(mcp)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server."""
    log_level = "DEBUG" if DEBUG else os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    mcp.run()
