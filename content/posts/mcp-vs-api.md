---
category: ai-agents
primary_query: mcp vs api
siblings:
- model-context-protocol
- mcp-server-tutorial
- agent-error-handling
bridges:
- slug: api-documentation
  reason: An HTTP API is learned from documentation a person reads, and that page lays the documentation out page by page.
date: 2026-11-23
description: "The same docs search behind an HTTP API and an MCP server shows what an agent needs to discover and call a tool."
slug: mcp-vs-api
status: published
takeaways:
- "An MCP client can ask a server what tools it offers and what arguments they take. Your application can keep using the HTTP routes it already knows."
- "The two search requests gave back the same matches. The MCP reply carried them as both text and structured data."
- "A bad tool argument came back as HTTP 200 with isError set. Track the tool result as well as the status code."
title: "MCP vs API: How They Differ, With One Function Built Both Ways"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write comparisons and explainers for your API or agent product. [Talk to me](/services/technical-articles/)."
---

I put the same docs search behind an HTTP endpoint and an MCP server. Both found the same lines, but only the MCP server gave a caller a list of tools and the arguments each one took.

That’s what I’d look at before choosing what to build. My own application can call a search route I already know.

A model choosing among tools in someone else’s application needs a way to learn that the search exists.

## The same search, called two ways

For [AI agents](/articles/ai-agents/) that choose tools during a run, the discovery step is where I'd start the comparison.

To run the examples, put the files from the MCP tutorial and the two launchers in the same folder. Start `uv run python api.py` and `uv run python serve_http.py` in separate terminals.

Then run the calls from a third. [Request script](/static/examples/mcp-vs-api/calls.sh)

The function came from my [MCP server tutorial](/articles/mcp-server-tutorial/). It looks for the query in a folder of Markdown files.

I put it behind `GET /search` in [api.py](/static/examples/mcp-vs-api/api.py), so a caller who knows the route and argument names can make this request.

```bash
curl -s -w '\nHTTP %{http_code}, %{size_download} bytes\n' "http://127.0.0.1:8000/search?q=rate+limit"
```

```text
{"matches": [{"path": "guides/errors.md", "line": 3, "text": "A 429 response means you hit the rate limit. Wait and retry."}, {"path": "guides/quickstart.md", "line": 6, "text": "## Rate limits"}]}
HTTP 200, 197 bytes
```

The [MCP HTTP launcher](/static/examples/mcp-vs-api/serve_http.py) puts the same function behind a `tools/call` request. The body names the tool and supplies the arguments.

```bash
META='"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"curl","version":"8.5.0"},"io.modelcontextprotocol/clientCapabilities":{}}'
curl -s -w '\nHTTP %{http_code}, %{size_download} bytes\n' http://127.0.0.1:8001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2026-07-28" \
  -H "Mcp-Method: tools/call" \
  -H "Mcp-Name: search_docs" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_docs","arguments":{"query":"rate limit"},'"$META"'}}'
```

```text
{"jsonrpc":"2.0","id":1,"result":{"content":[{"text":"{\n  \"path\": \"guides/errors.md\",\n  \"line\": 3,\n  \"text\": \"A 429 response means you hit the rate limit. Wait and retry.\"\n}","type":"text"},{"text":"{\n  \"path\": \"guides/quickstart.md\",\n  \"line\": 6,\n  \"text\": \"## Rate limits\"\n}","type":"text"}],"isError":false,"resultType":"complete","structuredContent":{"result":[{"path":"guides/errors.md","line":3,"text":"A 429 response means you hit the rate limit. Wait and retry."},{"path":"guides/quickstart.md","line":6,"text":"## Rate limits"}]},"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"docs-search","version":""}}}}
HTTP 200, 651 bytes
```

Both replies contain the same two matches. The MCP reply is longer because it sends them as text in `content` and as JSON in `structuredContent`.

MCP, the Model Context Protocol, standardizes messages like `tools/call`. An MCP server over HTTP is itself an API.

The practical difference is that each MCP client can use the same discovery and call methods across servers. [Model Context Protocol explainer](/articles/model-context-protocol/)

## Where the caller learns the argument names

The HTTP route still needs [API documentation](/articles/api-documentation/) or a schema that says what a request should look like.

A developer using the HTTP route learns the arguments from its docs or schema. The MCP client sends `tools/list` and gets definitions it can put in front of the model.

Here is the definition for the search, with its description and input schema.

```json
{"name":"search_docs","description":"Find lines in the docs that contain the query, ignoring case.\n\nReturns up to `limit` matches (no more than 50), each with the file path relative\nto the docs folder, the line number and the line text.\n","inputSchema":{"type":"object","properties":{"query":{"title":"Query","type":"string"},"limit":{"default":5,"title":"Limit","type":"integer"}},"required":["query"],"title":"search_docsArguments"}}
```

The docstring supplies the description, and the parameter types supply the schema. The model learns that `query` is required and `limit` is an integer.

I'd spend time on that description if the model needs to choose this search among several other tools.

## What happens when a caller gets it wrong

I sent `five` as the limit. The HTTP endpoint returned status 400.

```text
{"error": "invalid_parameter", "message": "limit must be an integer"}
HTTP 400, 69 bytes

{"jsonrpc":"2.0","id":1,"result":{"content":[{"text":"Error executing tool search_docs: 1 validation error for search_docsArguments\nlimit\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='five', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.14/v/int_parsing","type":"text"}],"isError":true,"resultType":"complete","_meta":{"io.modelcontextprotocol/serverInfo":{"name":"docs-search","version":""}}}}
HTTP 200, 489 bytes
```

The MCP server returned HTTP 200 with `isError: true` inside the result. The tool had been called and its arguments were wrong.

An invalid protocol method was a different case. Sending `tools/search` returned HTTP 404 and JSON-RPC code `-32601`.

In the July 28, 2026 protocol revision used for this comparison, a request can stand alone. Older clients could start with an `initialize` handshake and carry a session ID.

When a comparison mentions sessions, check which protocol version it describes. [MCP revision changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

The two examples listen on localhost and ask for no credentials. For a remote MCP server, the specification describes an optional HTTP authorization flow using OAuth.

A stdio server typically gets its credentials from the environment. [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

## Keep the API when you add MCP

An MCP tool can call an existing API. In [wrap_api.py](/static/examples/mcp-vs-api/wrap_api.py), the tool sends the search to the HTTP route.

```python
@mcp.tool()
def search_docs(query: str, limit: int = 5) -> list[dict]:
    """Find lines in the docs that contain the query, ignoring case."""
    url = f"{API}/search?{urllib.parse.urlencode({'q': query, 'limit': limit})}"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return json.load(response)["matches"]
    except urllib.error.HTTPError as error:
        raise ToolError(f"docs API returned {error.code}: {json.load(error)['message']}")
```

An empty query produced a 400 in the API log. The wrapper passed that information back to the model as a tool error.

```text
127.0.0.1 - - [23/Nov/2026 19:22:21] "GET /search?q=&limit=5 HTTP/1.1" 400 -
```

| Who calls the capability | What I'd build |
|---|---|
| Code that you or a customer wrote | The HTTP API and its documentation |
| A model inside a host you don't control, such as Claude Code | The API, and an MCP server as thin as `wrap_api.py` in front of it |
| A model inside an agent you wrote yourself | The function, passed to the model as a function-calling tool |

I'd expose a tool for something the user asks the agent to do. A request to find help in the docs needs a search tool with a useful description.

It doesn't need every endpoint a developer might call while implementing search.

I'd also log whether a call worked at the tool level. A dashboard that only counts HTTP 4xx and 5xx responses would miss the MCP tool error above.

[Error handling for AI agents](/articles/agent-error-handling/)
