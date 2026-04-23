<div align="center">

# Python MCP Server Starter

**Python + OIDC PyPI Publishing + CI/CD.**

Build your MCP server. One-click publish. Zero secrets needed.

[![CI](https://github.com/starter-series/python-mcp-server-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/starter-series/python-mcp-server-starter/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/my-mcp-server.svg)](https://pypi.org/project/my-mcp-server/)

**English** | [한국어](README.ko.md)

</div>

---

> **Part of [Starter Series](https://github.com/starter-series/starter-series)** — Stop explaining CI/CD to your AI every time. Clone and start.
>
> [Docker Deploy](https://github.com/starter-series/docker-deploy-starter) · [Discord Bot](https://github.com/starter-series/discord-bot-starter) · [Telegram Bot](https://github.com/starter-series/telegram-bot-starter) · [Browser Extension](https://github.com/starter-series/browser-extension-starter) · [Electron App](https://github.com/starter-series/electron-app-starter) · [npm Package](https://github.com/starter-series/npm-package-starter) · [React Native](https://github.com/starter-series/react-native-starter) · [VS Code Extension](https://github.com/starter-series/vscode-extension-starter) · [MCP Server (TS)](https://github.com/starter-series/mcp-server-starter) · **MCP Server (Python)** · [Cloudflare Pages](https://github.com/starter-series/cloudflare-pages-starter)

---

## What You Get

- **MCP SDK** — `mcp` (FastMCP) with stdio transport
- **Python 3.11+** — Type hints, async/await, hatchling build
- **All three MCP primitives** — Tools, Resources, and Prompts with working examples
- **Safety Annotations** — readOnly/destructive/idempotent hints on every tool
- **Validated Prompts** — pydantic `@validate_call` rejects bad args before the handler runs
- **Response Helpers** — `ok()` and `err()` for consistent tool responses
- **Config** — Environment variable parsing pattern
- **CI** — gitleaks, ruff, license compliance, pytest (3.11/3.12/3.13)
- **CD** — OIDC trusted publishing to PyPI (zero secrets needed)
- **Dependabot** — Automated dependency + GitHub Actions updates

## Quick Start

```bash
git clone https://github.com/starter-series/python-mcp-server-starter.git my-mcp-server
cd my-mcp-server
rm -rf .git && git init

pip install -e ".[dev]"
python -m my_mcp_server
```

## Adding Tools

> **Tool names must be globally unique** across all MCP servers a client connects to. Prefix with your module name (e.g., `mymodule_action` instead of `action`).

### Inline (simple)

Add directly to `src/my_mcp_server/server.py`:

```python
@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
async def your_tool(input: str) -> str:
    """What your tool does.

    Args:
        input: Input parameter.
    """
    return f"Processed: {input}"
```

### Modular (recommended for larger servers)

Create `src/my_mcp_server/tools/your_tool.py`:

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
        ),
    )
    async def your_tool(input: str) -> str:
        """What your tool does."""
        return f"Processed: {input}"
```

Then in `server.py`:

```python
from my_mcp_server.tools.your_tool import register
register(mcp)
```

## Adding Resources

Resources expose read-only data to the client at a stable URI (contrast with Tools, which perform actions).

See `src/my_mcp_server/resources/server_info.py` for the example. Pattern:

```python
from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.resource(
        "info://your/resource",
        name="your-resource",
        description="What this resource exposes.",
        mime_type="application/json",
    )
    async def your_resource() -> str:
        return "..."  # str, bytes, or JSON-serializable object
```

Then in `server.py`:

```python
from my_mcp_server.resources.your_resource import register as register_your_resource
register_your_resource(mcp)
```

## Adding Prompts

Prompts are reusable, parameterized message templates. Arguments are validated via pydantic before the handler runs.

See `src/my_mcp_server/prompts/code_review.py` for the example. Pattern:

```python
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import UserMessage
from pydantic import Field, validate_call


@validate_call
def your_prompt(
    mode: Literal["short", "long"],
    topic: Annotated[str, Field(min_length=1)],
) -> list[UserMessage]:
    return [UserMessage(content=f"Write a {mode} note about {topic}.")]


def register(mcp: FastMCP) -> None:
    mcp.prompt(name="your-prompt", title="Your Prompt")(your_prompt)
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_DEBUG` | `false` | Enable debug logging |
| `LOG_LEVEL` | `INFO` | Log level (DEBUG/INFO/WARNING/ERROR) |

Add your own in `server.py`.

## Testing Locally

```bash
# Run tests
pytest -v

# Lint
ruff check .

# Run the server (stdio)
python -m my_mcp_server
```

## CI/CD

### CI (runs on every push/PR)

| Check | Tool |
|-------|------|
| Secret scanning | gitleaks |
| Large file detection | find (>5 MB) |
| License compliance | pip-licenses (blocks GPL/AGPL) |
| Lint + format | ruff |
| Tests | pytest (Python 3.11, 3.12, 3.13) |

### CD (publish to PyPI)

1. Bump version in `pyproject.toml`
2. Go to **Actions → Publish to PyPI → Run workflow**
3. OIDC handles auth — no `PYPI_TOKEN` secret needed

Setup: [PyPI OIDC trusted publishing docs](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)

## Project Structure

```
src/my_mcp_server/
├── __init__.py          # Version
├── __main__.py          # python -m entry point
├── server.py            # FastMCP server + inline tools + helpers
├── tools/
│   ├── __init__.py
│   └── greet.py          # Example modular tool
├── resources/
│   ├── __init__.py
│   └── server_info.py    # Example resource (info://server/status)
└── prompts/
    ├── __init__.py
    └── code_review.py    # Example prompt (validated args)
tests/
├── test_tools.py         # Tool tests
├── test_server_info.py   # Resource tests
└── test_code_review.py   # Prompt tests
.github/
├── workflows/
│   ├── ci.yml            # Lint, test, security
│   ├── cd.yml            # PyPI OIDC publish
│   ├── stale.yml         # Stale issue management
│   └── maintenance.yml   # Weekly health check
└── dependabot.yml        # Dependency updates
```

## Scripts

```bash
pip install -e ".[dev]"   # Install with dev deps
python -m my_mcp_server   # Run server
pytest -v                 # Run tests
ruff check .              # Lint
ruff format .             # Format
```

## License

MIT
