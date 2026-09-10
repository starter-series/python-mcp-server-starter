import runpy
from pathlib import Path

find_issues = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/check_template_ready.py")
)["find_issues"]


def test_rejects_template_metadata():
    issues = find_issues(
        {
            "name": "my_mcp_server",
            "authors": [{"name": "Your Name"}],
            "urls": {"Repository": "https://github.com/starter-series/python-mcp-server-starter"},
            "scripts": {"my-mcp-server": "sample.__main__:run"},
        }
    )
    assert len(issues) == 6


def test_accepts_customized_metadata():
    assert (
        find_issues(
            {
                "name": "sample-mcp",
                "authors": [{"name": "Heznpc"}],
                "urls": {
                    "Homepage": "https://github.com/sample/sample-mcp",
                    "Repository": "https://github.com/sample/sample-mcp",
                    "Issues": "https://github.com/sample/sample-mcp/issues",
                },
                "scripts": {"sample-mcp": "sample.__main__:run"},
            }
        )
        == []
    )
