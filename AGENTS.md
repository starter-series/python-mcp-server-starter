# Python MCP Server Starter

Python MCP server template with FastMCP, stdio transport, CI checks, and OIDC
trusted publishing to PyPI.

## Project Structure

```
src/my_mcp_server/
├── __main__.py              # python -m entry point
├── server.py                # FastMCP server plus inline greet tool example
├── resources/
│   └── server_info.py       # Example resource (info://server/status)
└── prompts/
    └── code_review.py       # Example validated prompt
scripts/
└── smoke_stdio.py           # Stdio smoke test against the installed server
tests/                       # pytest suite for tools, resources, prompts, config
pyproject.toml               # Package metadata, dev deps, ruff/mypy/pytest config
```

## First User Path

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src/
python -m build
python scripts/smoke_stdio.py
```

Use Python 3.11+ if 3.12 is not available locally. CI tests 3.11, 3.12, and
3.13.

## Adding a Tool

For simple tools, add the decorated function in `src/my_mcp_server/server.py`:

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
    """Describe what the tool does."""
    return f"Processed: {input}"
```

For larger servers, copy the `register(mcp)` pattern from
`src/my_mcp_server/resources/server_info.py` or
`src/my_mcp_server/prompts/code_review.py`, then import and call it from
`server.py`.

## CI/CD Pipeline

- **ci.yml**: gitleaks, large-file check, license check, dependency audit,
  ruff, pytest across supported Python versions, build, mypy, stdio smoke.
- **cd.yml**: manual PyPI publish with OIDC trusted publishing and GitHub
  Release creation.
- **setup.yml**: first-push setup checklist.

## Release Constraints

- PyPI package names are unscoped product nouns. Do not introduce npm-style or
  organization-scoped package naming.
- OIDC trusted publishing replaces long-lived `PYPI_TOKEN` secrets.
- Keep `project.urls` aligned with the final repository before publishing.
- Keep the `my-mcp-server` console script aligned with the package name or
  document any intentional divergence.

## Do Not Regress

- Do not remove tool safety annotations. MCP clients use them to decide how to
  call tools.
- Do not make tool names generic. Prefix real tools with the module or product
  domain so they stay unique across connected MCP servers.
- Do not weaken ruff, mypy, pytest, license, dependency-audit, or stdio-smoke
  checks without documenting the tradeoff.
- Do not add required secrets for normal CI. Publishing may require platform
  setup, but CI should stay secret-free.
