"""An MCP server whose one tool calls the HTTP API in api.py, which must be running. Run: uv run wrap_api.py"""
import json
import urllib.error
import urllib.parse
import urllib.request

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

API = "http://127.0.0.1:8000"
mcp = MCPServer("docs-search-wrapper")


@mcp.tool()
def search_docs(query: str, limit: int = 5) -> list[dict]:
    """Find lines in the docs that contain the query, ignoring case."""
    url = f"{API}/search?{urllib.parse.urlencode({'q': query, 'limit': limit})}"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return json.load(response)["matches"]
    except urllib.error.HTTPError as error:
        raise ToolError(f"docs API returned {error.code}: {json.load(error)['message']}")


if __name__ == "__main__":
    mcp.run(transport="stdio")
