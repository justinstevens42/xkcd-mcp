"""Entry point: stdio MCP server."""

from __future__ import annotations

from xkcd_mcp.server import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
