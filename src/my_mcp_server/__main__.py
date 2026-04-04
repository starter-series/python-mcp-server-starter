"""Allow running as ``python -m my_mcp_server``."""

import sys
import logging

from my_mcp_server.server import main

try:
    main()
except KeyboardInterrupt:
    sys.exit(0)
except Exception:
    logging.exception("Fatal error running MCP server")
    sys.exit(1)
