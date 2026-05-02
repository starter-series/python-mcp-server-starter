"""MCP server entry point.

Registers tools, resources, and prompts via FastMCP.
Add your own tools in the tools/ directory following the greet.py pattern.
"""

import logging
import os
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

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
async def greet(
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=200,
            description="Name to greet (1–200 characters).",
        ),
    ],
) -> str:
    """Greet someone by name.

    The Annotated[..., Field(...)] form propagates the constraint into
    FastMCP's generated JSON schema, so empty strings and oversized inputs
    are rejected by the protocol layer before the handler runs. The TS
    sibling enforces the same shape via Zod.
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
