"""Serve the docs-search MCP server over Streamable HTTP. Run: uv run python serve_http.py"""
# Needs server.py from https://ninadpathak.com/articles/mcp-server-tutorial/ in the same folder.
from server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)
