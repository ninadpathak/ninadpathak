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
description: "MCP vs API, compared by exposing one search function both ways and capturing every request and response with curl, plus a rule for when to build which."
slug: mcp-vs-api
status: published
takeaways:
- An MCP server is called by a model that picks a tool at run time, and an HTTP API is called by code a developer wrote in advance, so MCP doesn't replace the API.
- The same search returned 197 bytes from a plain HTTP API and 651 bytes over MCP, and the MCP tool list for two tools was 1,340 bytes.
- A bad argument got HTTP 400 from the API and HTTP 200 with isError set to true from the MCP server, so a monitor that counts status codes misses failed tool calls.
title: "MCP vs API: How They Differ, With One Function Built Both Ways"
work_note: "Need a comparison that engineers will trust? I'm Ninad Pathak, a freelance technical writer for AI companies, and I build the example and run it before I draft, as I did with both servers here. [Talk to me about yours](/services/freelance-technical-writer-for-ai-companies/)."
---

MCP doesn't replace a REST API. An API is called by code that a developer wrote in advance, and an MCP server is called by a model that picks a tool at run time from a list the server sends it.

So build the API when your own code or a customer's code makes the call, and add an MCP server when a model inside an application you didn't write, such as Claude Code, has to find the capability and call it. An MCP server can call your existing API underneath, so adding one leaves the API in place.

Tools are the layer of [AI agent architecture](/articles/ai-agents/) where this choice comes up. I exposed one docs search function both ways, and in this article I'll walk you through what each side sent back.

## What is the difference between MCP and an API?

An API is an interface that a developer reads about once and then calls from code, and MCP is a protocol through which an AI application lists a server's tools and calls the one its model chose. MCP, the Model Context Protocol, fixes the method names for every server, so the application sends `tools/list` to get the tools and `tools/call` to run one.

An MCP server reached over the network is itself an HTTP API, with one POST endpoint and the same method names on every server. The [Model Context Protocol explainer](/articles/model-context-protocol/) has the full definition.

## The same search function as an HTTP API and an MCP server

The function is `search_docs` from the [MCP server tutorial](/articles/mcp-server-tutorial/), which returns the lines in a docs folder that contain a query. I kept that tutorial's `server.py` unchanged as the MCP side.

For the API side I wrote a 34-line [api.py](/static/examples/mcp-vs-api/api.py) with Python's standard library, which puts the same function behind `GET /search`. Its handler returns 400 when `q` is missing or `limit` isn't an integer, and otherwise ends on this line:

```python
        self.reply(200, {"matches": search_docs(params["q"][0], limit)})
```

A short [serve_http.py](/static/examples/mcp-vs-api/serve_http.py) starts the tutorial's server over MCP's Streamable HTTP transport, so curl can reach both sides. Every command on this page ran on November 23, 2026, with these versions:

- uv 0.13.8 and Python 3.13.18
- MCP Python SDK 2.3.0, which reported protocol version `2026-07-28`
- MCP Inspector 2.16.0
- curl 8.5.0 and jq 1.7

[calls.sh](/static/examples/mcp-vs-api/calls.sh) sends every curl request on this page.

### Calling the HTTP API

The API call is a single URL with the search term in its query string:

```bash
curl -s -w '\nHTTP %{http_code}, %{size_download} bytes\n' "http://127.0.0.1:8000/search?q=rate+limit"
```

```text
{"matches": [{"path": "guides/errors.md", "line": 3, "text": "A 429 response means you hit the rate limit. Wait and retry."}, {"path": "guides/quickstart.md", "line": 6, "text": "## Rate limits"}]}
HTTP 200, 197 bytes
```

I knew to send `q` because I wrote the handler. Nothing in that exchange tells a new caller that `/search` exists or that it takes a `limit`.

### Calling the MCP server

The MCP call is a POST with a JSON-RPC body, and every request states its protocol version in a `_meta` block:

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

`/mcp` is the only URL this server has, so the method name travels in the JSON body and again in the `Mcp-Method` header. The specification's [Streamable HTTP page](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http), read on November 23, 2026, requires that header so a load balancer can route a request without parsing the body.

The response is 651 bytes against the API's 197, because the two matches arrive twice. `content` carries them as text and `structuredContent` carries them again as JSON, which the specification's [tools page](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) recommends for backward compatibility.

## How a caller discovers an API and an MCP server

An MCP client discovers tools by sending `tools/list`, and the caller of an HTTP API learns its endpoints from documentation that a person wrote. Here is this server's `search_docs` entry, cut down with `jq -c '.result.tools[0] | {name, description, inputSchema}'` to the fields a model needs to call the tool:

```json
{"name":"search_docs","description":"Find lines in the docs that contain the query, ignoring case.\n\nReturns up to `limit` matches (no more than 50), each with the file path relative\nto the docs folder, the line number and the line text.\n","inputSchema":{"type":"object","properties":{"query":{"title":"Query","type":"string"},"limit":{"default":5,"title":"Limit","type":"integer"}},"required":["query"],"title":"search_docsArguments"}}
```

The description is the function's docstring and the schema comes from its type hints, so the model learns that `query` is a required string and that `limit` is an integer defaulting to 5. `api.py` describes nothing about itself, and its caller needs [API documentation](/articles/api-documentation/) or an [OpenAPI](https://spec.openapis.org/oas/latest.html) file that someone on the team writes and keeps current.

Self-description costs context when a model is the reader, and these are the measured sizes for this server:

| Message | Bytes | Tokens |
|---|---|---|
| Full `tools/list` response for the two tools | 1,340 | 319 |
| `name`, `description` and `inputSchema` of both tools, as compact JSON | 706 | 165 |
| `tools/call` response for the search | 651 | 196 |
| HTTP API response for the same search | 197 | 64 |

The token counts come from tiktoken 0.14.0 and its `o200k_base` encoding, which is an OpenAI tokenizer, so I'd read that column as an estimate for other models.

Whether a model pays for the definitions in every conversation depends on the host. The specification's [client best practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices) describe hosts that "pass the tool definitions of every connected server directly to the model at the start of each conversation", and recommend loading them on demand once they fill a significant part of the context window.

An API called by code costs no tokens, because no model reads the request or the response.

## Is MCP stateful or stateless?

MCP is stateless as of its 2026-07-28 revision, so each request stands alone the way a REST request does. The [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) removed the `initialize` handshake and the `Mcp-Session-Id` header, which is why the curl call above needed no setup request.

Comparisons written before that revision describe the older design. [TrueFoundry's comparison](https://www.truefoundry.com/blog/mcp-vs-api), last updated on June 30, 2026, says MCP supports multi-step workflows "by maintaining context across tasks", and sets that against "traditional stateless APIs".

The handshake still works for older clients on this SDK. SDK 2.3.0 answered an `initialize` request in the older format with a server-sent event and an `mcp-session-id` header, and it answered `initialize` sent as a 2026-07-28 request with a 404:

```text
data: {"jsonrpc":"2.0","id":1,"result":{"capabilities":{"prompts":{"listChanged":false},"resources":{"listChanged":false,"subscribe":false},"tools":{"listChanged":false}},"protocolVersion":"2025-11-25","serverInfo":{"name":"docs-search","version":""}}}
HTTP 200, 272 bytes

{"jsonrpc":"2.0","id":1,"error":{"code":-32601,"message":"Method not found","data":"initialize"}}
HTTP 404, 97 bytes
```

The MCP Inspector is one of those older clients unless you tell it otherwise. Its [documentation](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/protocol-eras) makes the handshake the default, and Inspector 2.16.0's `initialize` probe reported `2025-11-25` for my server until I added `--protocol-era modern`.

MCP also has a transport that needs no network. Over stdio the host starts `server.py` as a subprocess and writes the same JSON to its stdin, and when I piped the `tools/call` body above into `uv run server.py`, the reply matched the HTTP response body byte for byte.

## How MCP and an API report errors

An HTTP API reports a bad input with a status code, and an MCP server reports it inside a successful response. I sent `limit` as the word `five` to both, and the API's answer comes first:

```text
{"error": "invalid_parameter", "message": "limit must be an integer"}
HTTP 400, 69 bytes

{"jsonrpc":"2.0","id":1,"result":{"content":[{"text":"Error executing tool search_docs: 1 validation error for search_docsArguments\nlimit\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='five', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.14/v/int_parsing","type":"text"}],"isError":true,"resultType":"complete","_meta":{"io.modelcontextprotocol/serverInfo":{"name":"docs-search","version":""}}}}
HTTP 200, 489 bytes
```

The MCP reply is HTTP 200 with `isError` set to true, because the specification treats a bad argument as a tool execution error and returns it as a result. A model can read that message and resend `limit` as a number, and a developer who gets the 400 fixes the calling code once.

Faults in the request itself come back as JSON-RPC errors with an HTTP error status, and `tools/search`, a method that doesn't exist, returned HTTP 404 with code `-32601`. The tools page lists an unknown tool among those protocol errors too, but SDK 2.3.0 answered a call to `search_everything` with HTTP 200 and an `isError` result.

A monitor that counts 4xx and 5xx responses won't see failed tool calls on an MCP endpoint, so you'd have to log `isError` results yourself. Deciding whether the agent should retry after one is covered in [error handling for AI agents](/articles/agent-error-handling/).

## How authentication works in MCP and in an API

An HTTP API authenticates however its team decides, and MCP defines one optional scheme for HTTP, built on OAuth 2.1. The specification's [authorization page](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) says "Authorization is OPTIONAL for MCP implementations", and it says a stdio server should skip the scheme and "retrieve credentials from the environment".

An HTTP server that does use the scheme acts as an OAuth 2.1 resource server, and the client sends `Authorization: Bearer <access-token>` on every request.

Neither of my servers asks for a credential, and both listen on 127.0.0.1 only. The SDK did refuse a `tools/list` request carrying `Origin: https://evil.example` with HTTP 403, while `api.py` answered the same header with 200.

## Does an MCP server replace the API underneath?

No. An MCP server can sit in front of the API and call it, and [wrap_api.py](/static/examples/mcp-vs-api/wrap_api.py) is that arrangement in one tool, an MCP server whose `search_docs` sends its request to `api.py`:

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

I called the tool through the Inspector CLI with an empty query, and the API's log shows the request the MCP server made:

```text
127.0.0.1 - - [23/Nov/2026 19:22:21] "GET /search?q=&limit=5 HTTP/1.1" 400 -
```

The wrapper passed the 400 on as an `isError` result whose text ends `docs API returned 400: q is required`. An MCP server doesn't need an API behind it, though, and the tutorial's `server.py` reads its Markdown files directly.

## MCP vs API comparison table

MCP and an HTTP API differ in who calls them and in how that caller learns the interface:

| | HTTP API (`api.py`) | MCP server (`server.py`) |
|---|---|---|
| Who calls it | Code a developer wrote after reading the docs | A model that picks `search_docs` at run time |
| Address | One URL per operation, here `GET /search` | One endpoint, `POST /mcp`, for every method |
| How the caller learns it | Docs or an OpenAPI file the team writes | `tools/list`, 1,340 bytes for two tools |
| Response for the search | 197 bytes of JSON | 651 bytes, as text and again as JSON |
| Bad argument | HTTP 400 and an error body | HTTP 200 and `isError: true` |
| State between calls | None | None, though SDK 2.3.0 still answers the old handshake |
| Authentication | Whatever the team chooses | Optional, and OAuth 2.1 bearer tokens on HTTP |

## When to build an API, an MCP server or both

I'd build the function first and the HTTP API second, and add an MCP server only once a model in an application I don't control has to call it:

| Who calls the capability | What I'd build |
|---|---|
| Code that you or a customer wrote | The HTTP API and its documentation |
| A model inside a host you don't control, such as Claude Code | The API, and an MCP server as thin as `wrap_api.py` in front of it |
| A model inside an agent you wrote yourself | The function, passed to the model as a function-calling tool |

<!-- evidence-three: 165 tokens for two definitions is 82.5 each and 40 times 82.5 is 3,300 --> For an API with many endpoints, I'd expose one tool per task a user asks for and leave the rest in the API. The two tool definitions here measured 165 tokens, so 40 tools of that size would come to about 3,300 tokens on a host that loads every definition.

## FAQ

Each answer rests on the run on this page.

### Does MCP replace REST APIs?

No. A model calls an MCP tool at run time and code calls a REST API, and an MCP server can call that API underneath, as `wrap_api.py` does here.

### Is MCP a REST API?

No. Over Streamable HTTP, MCP uses one POST endpoint and JSON-RPC 2.0 method names such as `tools/call`, and over stdio it uses no HTTP.

### Does MCP use more tokens than an API call?

It does when a model reads the result. The search result here was 196 tokens over MCP against 64 for the API's JSON, and an API called by code uses no tokens.
