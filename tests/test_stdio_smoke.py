from __future__ import annotations

import sys

import pytest

from scripts.smoke_stdio import run_stdio_smoke


@pytest.mark.asyncio
async def test_python_module_entrypoint_speaks_stdio_mcp() -> None:
    await run_stdio_smoke(sys.executable, ("-m", "my_mcp_server"))
