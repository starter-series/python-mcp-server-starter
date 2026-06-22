"""MCP server entry point.

Registers tools, resources, and prompts via FastMCP. Add your own tools
inline below the existing `greet` example, or split them into modules.
"""

import logging
import os
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import StringConstraints

from my_mcp_server.prompts.code_review import register as register_code_review
from my_mcp_server.resources.server_info import register as register_server_info

logger = logging.getLogger("my_mcp_server")

# ---------------------------------------------------------------------------
# Configuration — add your env vars here
# ---------------------------------------------------------------------------

DEBUG = os.environ.get("MCP_DEBUG", "false").lower() == "true"
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def resolve_log_level() -> str:
    """Return a logging level name accepted by ``logging``."""
    if DEBUG:
        return "DEBUG"

    candidate = os.environ.get("LOG_LEVEL", "INFO").upper()
    if candidate not in VALID_LOG_LEVELS:
        return "INFO"
    return candidate


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

SERVER_NAME = "my-mcp-server"
SERVER_INSTRUCTIONS = "An MCP server. Replace this with your description."

mcp = FastMCP(
    SERVER_NAME,
    instructions=SERVER_INSTRUCTIONS,
)


# ---------------------------------------------------------------------------
# Tools — FastMCP wraps return values automatically (return value for success,
# raise for errors). Add your own in tools/ and import here.
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
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=200,
        ),
    ],
) -> str:
    """Greet someone by name.

    The Annotated[..., Field(...)] form propagates the constraint into
    FastMCP's generated JSON schema, so empty strings and oversized inputs
    are rejected by the protocol layer before the handler runs. The TS
    sibling enforces the same shape via Zod.
    """
    normalized = name.strip()
    if not normalized:
        raise ValueError("name must contain at least one non-whitespace character")

    logger.info("Greeting %s", normalized)
    return f"Hello, {normalized}!"


# To add more tools, either decorate inline above or split them into modules
# (see resources/server_info.py and prompts/code_review.py for the `register(mcp)`
# pattern this repo applies to resources and prompts).


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
    logging.basicConfig(
        level=getattr(logging, resolve_log_level()),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    mcp.run(transport="stdio")
