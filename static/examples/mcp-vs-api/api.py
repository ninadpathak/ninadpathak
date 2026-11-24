"""A plain HTTP API for the docs search in server.py. Run: uv run python api.py"""
# Needs server.py from https://ninadpathak.com/articles/mcp-server-tutorial/ in the same folder.
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from server import search_docs


class Handler(BaseHTTPRequestHandler):
    def reply(self, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        url = urlparse(self.path)
        params = parse_qs(url.query)
        if url.path != "/search":
            return self.reply(404, {"error": "not_found", "message": f"no route for {url.path}"})
        if "q" not in params:
            return self.reply(400, {"error": "missing_parameter", "message": "q is required"})
        try:
            limit = int(params.get("limit", ["5"])[0])
        except ValueError:
            return self.reply(400, {"error": "invalid_parameter", "message": "limit must be an integer"})
        self.reply(200, {"matches": search_docs(params["q"][0], limit)})


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
