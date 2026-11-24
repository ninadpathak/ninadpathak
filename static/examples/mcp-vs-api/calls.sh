#!/usr/bin/env bash
# Call the docs search as a plain HTTP API and as an MCP server, and print what comes back.
# Start both first:  uv run python api.py   (port 8000)   and   uv run python serve_http.py   (port 8001)
API=http://127.0.0.1:8000
MCP=http://127.0.0.1:8001/mcp
SHOW='\nHTTP %{http_code}, %{size_download} bytes\n\n'
META='"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"curl","version":"8.5.0"},"io.modelcontextprotocol/clientCapabilities":{}}'

# mcp <method> <params without _meta> [extra curl arguments]
mcp() {
  local method=$1 params=$2
  shift 2
  curl -s -w "$SHOW" "$MCP" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "MCP-Protocol-Version: 2026-07-28" \
    -H "Mcp-Method: $method" "$@" \
    -d '{"jsonrpc":"2.0","id":1,"method":"'"$method"'","params":{'"$params$META"'}}'
}

echo "1. HTTP API: search"
curl -s -w "$SHOW" "$API/search?q=rate+limit"

echo "2. HTTP API: limit is not a number"
curl -s -w "$SHOW" "$API/search?q=rate+limit&limit=five"

echo "3. MCP: tools/call search_docs"
mcp tools/call '"name":"search_docs","arguments":{"query":"rate limit"},' -H "Mcp-Name: search_docs"

echo "4. MCP: tools/list"
mcp tools/list ''

echo "5. MCP: tools/call with limit as a word"
mcp tools/call '"name":"search_docs","arguments":{"query":"rate limit","limit":"five"},' -H "Mcp-Name: search_docs"

echo "6. MCP: tools/call on a tool that does not exist"
mcp tools/call '"name":"search_everything","arguments":{"query":"rate limit"},' -H "Mcp-Name: search_everything"

echo "7. MCP: a method that does not exist"
mcp tools/search ''

echo "8. MCP: Mcp-Name header that disagrees with the body"
mcp tools/call '"name":"search_docs","arguments":{"query":"rate limit"},' -H "Mcp-Name: read_doc"

echo "9. MCP: initialize, sent the way a client from before 2026-07-28 sends it"
curl -s -w "$SHOW" -D - "$MCP" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"8.5.0"}}}'

echo "10. MCP: initialize, sent as a 2026-07-28 request"
mcp initialize ''

echo "11. A request that carries another site's Origin header, to each server"
mcp tools/list '' -H "Origin: https://evil.example"
curl -s -w "$SHOW" -H "Origin: https://evil.example" "$API/search?q=rate+limit&limit=1"
