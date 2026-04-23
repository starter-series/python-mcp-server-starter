"""Tests for the code-review prompt."""

import pytest
from mcp.server.fastmcp.prompts.base import UserMessage
from pydantic import ValidationError

from my_mcp_server.prompts.code_review import (
    DESCRIPTION,
    NAME,
    TITLE,
    code_review,
)


def test_identity_metadata_is_stable() -> None:
    """Name, title, and description are part of the public contract."""
    assert NAME == "code-review"
    assert TITLE == "Code Review"
    assert isinstance(DESCRIPTION, str) and DESCRIPTION


def test_rejects_empty_code() -> None:
    """Empty ``code`` fails pydantic validation before the handler runs."""
    with pytest.raises(ValidationError):
        code_review(language="py", code="")


def test_rejects_unsupported_language() -> None:
    """Language outside the Literal enum is rejected."""
    with pytest.raises(ValidationError):
        code_review(language="ruby", code="puts 1")  # type: ignore[arg-type]


def test_rejects_missing_fields() -> None:
    """Both arguments are required."""
    with pytest.raises(ValidationError):
        code_review(language="py")  # type: ignore[call-arg]
    with pytest.raises(ValidationError):
        code_review(code="x = 1")  # type: ignore[call-arg]


def test_happy_path_returns_single_user_message() -> None:
    """Valid input produces one user message with the expected shape."""
    code = "def add(a, b):\n    return a + b"
    messages = code_review(language="py", code=code)

    assert isinstance(messages, list)
    assert len(messages) == 1

    msg = messages[0]
    assert isinstance(msg, UserMessage)
    assert msg.role == "user"
    assert msg.content.type == "text"  # type: ignore[union-attr]
    text = msg.content.text  # type: ignore[union-attr]
    assert "Python" in text
    assert "```py" in text
    assert code in text


def test_language_label_interpolated_per_enum_value() -> None:
    """Each supported language maps to a human-readable label."""
    code = "x = 1"
    cases = {"py": "Python", "js": "JavaScript", "ts": "TypeScript", "go": "Go"}
    for lang, label in cases.items():
        messages = code_review(language=lang, code=code)  # type: ignore[arg-type]
        text = messages[0].content.text  # type: ignore[union-attr]
        assert label in text
        assert f"```{lang}\n{code}\n```" in text


async def test_registered_on_server() -> None:
    """The prompt is wired into the server at import time."""
    from my_mcp_server.server import mcp

    prompts = await mcp.list_prompts()
    names = [p.name for p in prompts]
    assert NAME in names
