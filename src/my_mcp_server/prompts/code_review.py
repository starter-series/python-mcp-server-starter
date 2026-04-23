"""Example MCP Prompt — a templated code review prompt.

Prompts are reusable, parameterized message templates the client can surface to
the user or feed to the model. Arguments are validated via pydantic so empty
code or unsupported languages are rejected before the handler runs.
"""

from __future__ import annotations

from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import UserMessage
from pydantic import Field, validate_call

NAME = "code-review"
TITLE = "Code Review"
DESCRIPTION = "Ask the model to review a snippet of code in the given language."

Language = Literal["py", "js", "ts", "go"]

_LANGUAGE_LABEL: dict[str, str] = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "go": "Go",
}


@validate_call
def code_review(
    language: Language,
    code: Annotated[str, Field(min_length=1, description="Source code to review.")],
) -> list[UserMessage]:
    """Render a code-review prompt as a single-user-message template.

    Args:
        language: Programming language of the snippet (one of py/js/ts/go).
        code: Source code to review. Must be non-empty.

    Returns:
        A list containing one user message with a language-labeled fenced
        code block.
    """
    label = _LANGUAGE_LABEL[language]
    text = (
        f"Review this {label} code for bugs, readability, and idiomatic style. "
        "Be specific and actionable.\n\n"
        f"```{language}\n{code}\n```"
    )
    return [UserMessage(content=text)]


def register(mcp: FastMCP) -> None:
    """Register the code-review prompt on the server."""
    mcp.prompt(name=NAME, title=TITLE, description=DESCRIPTION)(code_review)
