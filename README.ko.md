<div align="center">

# Python MCP Server Starter

**Python + OIDC PyPI 배포 + CI/CD.**

MCP 서버를 만들고, 원클릭 배포. 시크릿 불필요.

[![CI](https://github.com/starter-series/python-mcp-server-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/starter-series/python-mcp-server-starter/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/my-mcp-server.svg)](https://pypi.org/project/my-mcp-server/)

[English](README.md) | **한국어**

</div>

---

> **[Starter Series](https://github.com/starter-series/starter-series)의 일부** — AI에게 매번 CI/CD를 설명하지 마세요. 클론하고 시작하세요.

---

## 포함 사항

- **MCP SDK** — `mcp` (FastMCP) + stdio 전송
- **Python 3.11+** — 타입 힌트, async/await, hatchling 빌드
- **MCP 3대 프리미티브** — Tools, Resources, Prompts 예제 전부 포함
- **Safety Annotations** — 모든 도구에 readOnly/destructive/idempotent 힌트
- **검증된 Prompt** — pydantic `@validate_call`로 핸들러 실행 전 인자 검증
- **응답 헬퍼** — `ok()`, `err()`로 일관된 응답
- **CI** — gitleaks, ruff, 라이선스 검증, pytest (3.11/3.12/3.13)
- **CD** — OIDC trusted publishing으로 PyPI 배포 (시크릿 불필요)
- **Dependabot** — 의존성 + GitHub Actions 자동 업데이트

## 빠른 시작

```bash
git clone https://github.com/starter-series/python-mcp-server-starter.git my-mcp-server
cd my-mcp-server
rm -rf .git && git init

pip install -e ".[dev]"
python -m my_mcp_server
```

## 도구 추가

`src/my_mcp_server/server.py`에 직접 추가:

```python
@mcp.tool(
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
    ),
)
async def your_tool(input: str) -> str:
    """도구 설명."""
    return f"처리 완료: {input}"
```

## Resource 추가

Resource는 고정된 URI로 클라이언트에 데이터를 노출합니다 (동작을 수행하는 Tool과 대비).

예시: `src/my_mcp_server/resources/server_info.py`

```python
from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.resource(
        "info://your/resource",
        name="your-resource",
        description="리소스가 노출하는 데이터.",
        mime_type="application/json",
    )
    async def your_resource() -> str:
        return "..."  # str, bytes, 또는 JSON 직렬화 가능한 객체
```

`server.py`에서:

```python
from my_mcp_server.resources.your_resource import register as register_your_resource
register_your_resource(mcp)
```

## Prompt 추가

Prompt는 파라미터화된 재사용 가능한 메시지 템플릿입니다. pydantic으로 인자를 검증합니다.

예시: `src/my_mcp_server/prompts/code_review.py`

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
    return [UserMessage(content=f"{topic}에 대한 {mode} 노트를 작성해주세요.")]


def register(mcp: FastMCP) -> None:
    mcp.prompt(name="your-prompt", title="Your Prompt")(your_prompt)
```

## CI/CD

### CI (push/PR마다 실행)

| 검사 | 도구 |
|------|------|
| 시크릿 스캔 | gitleaks |
| 대용량 파일 감지 | find (>5 MB) |
| 라이선스 검증 | pip-licenses (GPL/AGPL 차단) |
| 린트 + 포맷 | ruff |
| 테스트 | pytest (Python 3.11, 3.12, 3.13) |

### CD (PyPI 배포)

1. `pyproject.toml`에서 버전 올리기
2. **Actions → Publish to PyPI → Run workflow**
3. OIDC가 인증 처리 — `PYPI_TOKEN` 시크릿 불필요

## 라이선스

MIT
