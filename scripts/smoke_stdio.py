"""Stdio smoke test for the packaged MCP entrypoint."""

from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import Sequence

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


async def run_stdio_smoke(
    command: str = sys.executable,
    args: Sequence[str] = ("-m", "my_mcp_server"),
) -> None:
    params = StdioServerParameters(
        command=command,
        args=list(args),
        env={**os.environ, "MCP_DEBUG": "false"},
    )

    async with (
        stdio_client(params) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()

        tools = await session.list_tools()
        tool_names = {tool.name for tool in tools.tools}
        check("greet" in tool_names, f"greet tool missing from {sorted(tool_names)}")

        result = await session.call_tool("greet", {"name": "Smoke"})
        check(not bool(result.isError), "greet tool returned an MCP error")
        check(bool(result.content), "greet tool returned no content")
        first = result.content[0]
        check(first.type == "text", f"unexpected content type: {first.type}")
        check(first.text == "Hello, Smoke!", f"unexpected greeting text: {first.text}")

        resources = await session.list_resources()
        resource_uris = {str(resource.uri) for resource in resources.resources}
        check("info://server/status" in resource_uris, "server-info resource missing")

        prompts = await session.list_prompts()
        prompt_names = {prompt.name for prompt in prompts.prompts}
        check("code-review" in prompt_names, "code-review prompt missing")


def main() -> int:
    asyncio.run(run_stdio_smoke())
    print("stdio smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
