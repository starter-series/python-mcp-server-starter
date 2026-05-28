"""Allow running as ``python -m my_mcp_server``.

The wrap-and-exit logic lives in ``run()`` so it can be tested directly
(``import my_mcp_server.__main__`` no longer blocks on the server loop).
"""

import logging
import sys

from my_mcp_server.server import main


def run() -> int:
    """Run ``server.main()`` and translate termination into a process exit code.

    Returns:
        ``0`` on clean return or Ctrl-C, ``1`` on any other exception
        (logged via ``logging.exception`` so the traceback hits stderr).
    """
    try:
        main()
    except KeyboardInterrupt:
        return 0
    except Exception:
        logging.exception("Fatal error running MCP server")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
