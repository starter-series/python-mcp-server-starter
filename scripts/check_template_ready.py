"""Reject uncustomized package metadata before publishing to PyPI."""

import re
import sys
import tomllib
from pathlib import Path
from typing import Any


def find_issues(project: dict[str, Any]) -> list[str]:
    issues = []
    name = project.get("name", "")
    if not name or re.sub(r"[-_.]+", "-", name).lower() == "my-mcp-server":
        issues.append("project.name: replace my-mcp-server with your package name")
    authors = project.get("authors", [])
    if not authors or any(not a.get("name") or a["name"] == "Your Name" for a in authors):
        issues.append("project.authors: set the package author")
    urls = project.get("urls", {})
    for field in ("Homepage", "Repository", "Issues"):
        value = urls.get(field, "")
        if (
            not value
            or "starter-series/python-mcp-server-starter" in value.lower()
            or "YOUR_" in value
        ):
            issues.append(f"project.urls.{field}: set your project's URL")
    if "my-mcp-server" in project.get("scripts", {}):
        issues.append("project.scripts: rename the my-mcp-server console command")
    return issues


def main() -> int:
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parents[1] / "pyproject.toml"
    )
    with path.open("rb") as stream:
        issues = find_issues(tomllib.load(stream).get("project", {}))
    if issues:
        print("Template metadata is not ready to publish:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1
    print("Template metadata is ready to publish.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
