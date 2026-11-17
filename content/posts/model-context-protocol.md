---
category: ai-agents
primary_query: model context protocol
siblings:
- agent-harnesses
- mcp-server-tutorial
bridges:
- slug: llm-structured-outputs
  reason: An MCP tool declares its arguments in the same JSON Schema that structured outputs use.
date: 2026-03-11
description: The Model Context Protocol (MCP) is an open standard that lets AI applications
  list and call tools on any server. How it works after the 2026 stateless revision,
  with the messages printed from a running server.
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. I write developer documentation, tutorials and technical articles, and I run the product before I write about it. [See how I work](/services/freelance-technical-writer-for-ai-companies/) and tell me what you're shipping."
title: 'What the Model Context Protocol (MCP) Is and How It Works'
slug: model-context-protocol
---

The Model Context Protocol (MCP) is an open standard for connecting AI applications to tools and data. A server describes what it offers in one fixed format, and any application that speaks the protocol can list those tools and call them.

Databases had the same many-to-many problem in the early nineties. Every application needed its own code for every database until [ODBC](https://en.wikipedia.org/wiki/Open_Database_Connectivity) put a driver in between in 1992, and after that an application written against the ODBC interface could reach any database that shipped an ODBC driver.

Anthropic [open-sourced the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) on November 25, 2024 to do for tools what ODBC did for databases. Under MCP a tool such as a GitHub connector is written once as a server, and every AI application that speaks MCP can use it, which makes the protocol one layer of [AI agent architecture](/articles/ai-agents/).

The protocol itself changed in 2026. The [2026-07-28 revision](https://modelcontextprotocol.io/specification/2026-07-28/changelog) removed the `initialize` handshake that used to open every connection, so an explainer written before July describes a step that no longer exists.

I've written this page against the 2026-07-28 spec, and the JSON messages further down were printed by a server running on my machine.

## What is the Model Context Protocol?

MCP is a client-server protocol built on JSON-RPC 2.0. The [architecture page](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture) names the parties:

- **Host:** the AI application a person uses, such as Claude Code or Visual Studio Code.
- **Client:** a component inside the host that holds the connection to one server. The host creates one client per server.
- **Server:** a program that provides tools and data to clients. A server can run on your machine or on someone else's.

The spec says MCP "takes some inspiration from the Language Server Protocol", and the two protocols solve the same shape of problem. An editor that speaks LSP can support Rust or Python by connecting to that language's server, and a host that speaks MCP can use GitHub or a Postgres database by connecting to that tool's server.

MCP covers the messages between client and server and nothing after them. The same architecture page says MCP "does not dictate how AI applications use LLMs or manage the provided context", so whether a host shows the model all 40 tools from a server or only 5 of them is the host's decision.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/model-context-protocol/mcp-architecture.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/model-context-protocol/mcp-architecture.narrow.svg" width="288" height="688"><img class="np-has-narrow" src="/static/images/diagrams/model-context-protocol/mcp-architecture.svg" width="720" height="264" alt="An MCP round trip drawn left to right. The host holds a client, the client sends a request to the server, and the server runs one of its tools and returns the result along the same path." loading="lazy" decoding="async"></picture></a>
  <figcaption>The host creates one client per server. Each request carries its own protocol version, so the protocol keeps no session between calls.</figcaption>
</figure>

## What can an MCP server offer?

An MCP server can offer tools, resources and prompts, and each has a list method that a client calls to find out what's there:

| Primitive | What it is | Methods |
|---|---|---|
| Tools | Functions the model can call | `tools/list`, `tools/call` |
| Resources | Data the application can read, such as a file or a database schema | `resources/list`, `resources/read` |
| Prompts | Reusable prompt templates | `prompts/list`, `prompts/get` |

Tools are the primitive that MCP tutorials spend nearly all their time on, and I think that's fair, because a tool is the only primitive that lets the model act. A tool carries a name, a description and an `inputSchema` written in JSON Schema, which is the same mechanism behind [structured outputs and function calling](/articles/llm-structured-outputs/).

A client can offer one feature back to the server, called elicitation, which lets a server ask the user a question in the middle of a tool call, such as "delete all 14 files?". Roots, sampling and protocol logging are deprecated as of the 2026-07-28 revision, so a tutorial that leans on them is teaching features that still work and are on their way out.

## How does an MCP call work?

A client sends a JSON-RPC request naming a method, and the server sends back a result. I wanted to see the messages themselves, so I wrote a one-tool server with the MCP Python SDK 2.3.0 and a script that talks to it over stdio with no SDK on the client side.

The server, `server.py`:

```python
"""A one-tool MCP server, used to watch the messages a client and server exchange."""
from mcp.server import MCPServer

mcp = MCPServer("wire-demo")


@mcp.tool()
def word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The client, `wire.py`, writes one JSON object per line to the server's stdin and reads one line back, which is all the [stdio transport](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio) asks for:

```python
"""Speak raw JSON-RPC to an MCP server over stdio and print what crosses the pipe."""
import json
import subprocess
import sys

META = {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": {"name": "wire", "version": "0.1"},
    "io.modelcontextprotocol/clientCapabilities": {},
}
server = subprocess.Popen(
    [sys.executable, "server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
)


def call(request_id, method, meta=META, **params):
    request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": {**params, "_meta": meta}}
    server.stdin.write(json.dumps(request) + "\n")
    server.stdin.flush()
    reply = json.loads(server.stdout.readline())
    shown = {key: value for key, value in params.items()}
    print(f"-> {method} {json.dumps(shown)}  ({len(json.dumps(request))} bytes, {len(json.dumps(meta))} of them _meta)")
    body = reply.get("result", reply.get("error"))
    body.pop("_meta", None)
    print("<-", "error" if "error" in reply else "result", json.dumps(body)[:330], "\n")


# No handshake: the first message this server sees is a tool call.
call(1, "tools/call", name="word_count", arguments={"text": "one protocol, many servers"})
call(2, "server/discover")
call(3, "tools/list")
call(4, "tools/call", name="word_count", arguments={"txt": "wrong argument name"})
call(5, "tools/list", meta={**META, "io.modelcontextprotocol/protocolVersion": "2024-11-05"})
server.stdin.close()
server.wait(timeout=5)
```

Running `uv run python wire.py` on 2026-11-17 printed this:

```text
-> tools/call {"name": "word_count", "arguments": {"text": "one protocol, many servers"}}  (330 bytes, 181 of them _meta)
<- result {"content": [{"text": "4", "type": "text"}], "isError": false, "resultType": "complete", "structuredContent": {"result": 4}} 

-> server/discover {}  (260 bytes, 181 of them _meta)
<- result {"cacheScope": "private", "capabilities": {"prompts": {"listChanged": true}, "resources": {"listChanged": true, "subscribe": true}, "tools": {"listChanged": true}}, "resultType": "complete", "supportedVersions": ["2026-07-28"], "ttlMs": 0} 

-> tools/list {}  (255 bytes, 181 of them _meta)
<- result {"cacheScope": "private", "resultType": "complete", "tools": [{"description": "Count the words in a piece of text.", "inputSchema": {"type": "object", "properties": {"text": {"title": "Text", "type": "string"}}, "required": ["text"], "title": "word_countArguments"}, "name": "word_count", "outputSchema": {"properties": {"result": 

-> tools/call {"name": "word_count", "arguments": {"txt": "wrong argument name"}}  (322 bytes, 181 of them _meta)
<- result {"content": [{"text": "Error executing tool word_count: 1 validation error for word_countArguments\ntext\n  Field required [type=missing, input_value={'txt': 'wrong argument name'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.14/v/missing", "type": "text"}], "isError": true, "resultType": "c 

-> tools/list {}  (255 bytes, 181 of them _meta)
<- error {"code": -32022, "message": "Unsupported protocol version", "data": {"supported": ["2026-07-28"], "requested": "2024-11-05"}}
```

The first message `wire.py` sent was a `tools/call` request, and the server answered it with the word count of 4. The client didn't have to run a handshake first, because each request carries its protocol version and the client's capabilities in the `_meta` field.

Sending `_meta` on every request costs bytes, and the output shows how many. Of the 255 bytes in the `tools/list` request, 181 are the `_meta` field.

The fourth call, where I sent the argument as `txt` when the tool expects `text`, is the one I'd show someone writing their first MCP server. The wrong argument name comes back as an ordinary result with `isError` set to true and a message the model can read, and the [tools spec](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) says such errors exist so that a model can correct its arguments and try again.

The fifth call asks for the tool list again with the protocol version set to `2024-11-05`. The server refused with error `-32022` and named `2026-07-28` as the only version it supports, so a client that still speaks a 2024 version can't use a server built on SDK 2.3.0.

## What changed in MCP in 2026?

The 2026-07-28 revision made MCP stateless, which means a server no longer has to remember anything about a client between two requests. The changelog lists every change, and these four are the ones that make older explanations of MCP wrong:

- The `initialize` handshake is gone. Every request now carries the protocol version and client capabilities in `_meta`.
- Protocol-level sessions and the `Mcp-Session-Id` header are gone from the HTTP transport. A server that needs state across calls hands out its own handle and takes it back as a tool argument.
- Servers must implement `server/discover`, which reports versions and capabilities. Clients may call it or skip it.
- Change notifications moved to a single opt-in stream called `subscriptions/listen`.

I read the 2026-07-28 revision as MCP adjusting to remote servers. A handshake and a session work well when Claude Desktop talks to one process on the same laptop, and they get in the way when a server runs on ten machines behind a load balancer, because the second request may reach a machine that never saw the handshake.

Statelessness also explains the `ttlMs` and `cacheScope` fields on the `tools/list` result in the output above. A tool list that is the same for every connection can be cached like any other HTTP response, and those two fields tell a client how long to keep it and who may reuse it.

## Should an MCP server run locally or remotely?

Run it locally over stdio when it touches files on one machine, and remotely over Streamable HTTP when many clients need the same server. The architecture page puts it this way: a local stdio server "typically" serves a single client, and a remote one serves many.

A `tools/call` request is the same JSON on both transports, and only the delivery differs. On stdio the host launches the server as a child process, and on Streamable HTTP the client sends each message as an HTTP POST, with OAuth as the recommended way to get a token.

The [MCP server tutorial](/articles/mcp-server-tutorial/) builds the local kind, a read-only server that can't read outside one docs folder.

## Is MCP better than a CLI or a plain API?

MCP is the better choice when the AI application can't run shell commands, and a CLI is often enough when it can. When [MCP Explained](https://news.ycombinator.com/item?id=50379249) reached the Hacker News front page on November 5, the thread spent less time on the explainer than on whether the protocol is needed at all.

A commenter there [called MCP](https://news.ycombinator.com/item?id=50379528) "basically just a REST API with standardized endpoints for discovery aimed at agents". I think that description is accurate, and the "standardized endpoints for discovery" in it are the reason to use MCP.

A coding agent with a terminal, such as Claude Code, can run `gh --help` and learn the GitHub CLI's commands from the output. A chat application such as Claude Desktop has no terminal, so the `tools/list` method is the only way it can find out what a server offers.

Other commenters in the thread said a good CLI or an ordinary API does the same job, and for a small case they're right. An application with two fixed tools can define them with plain function calling and deploy nothing extra, and I wouldn't add an MCP server to it.

## Where does MCP fit in an agent harness?

Inside an agent harness, MCP is how the tool registry gets tools that somebody else wrote and runs. The rest of the [agent harness](/articles/agent-harnesses/) is still your code: it runs the loop, decides what goes into the context window and asks the user before a risky tool call.

Asking the user before a risky call is a job MCP leaves to the host. The [spec's security section](https://modelcontextprotocol.io/specification/2026-07-28) says "Tools represent arbitrary code execution and must be treated with appropriate caution", and it adds that MCP can't enforce its own consent rules at the protocol level.

So when a server describes its `delete_file` tool as read-only, that description is the server author's claim and nothing in MCP checks it. I'd read a third-party server's code, or run it in a sandbox, before connecting an agent to it.

## FAQ

**Is MCP the same as function calling?**

No. Function calling is how a model asks its own application for a tool, and MCP is how that application finds and calls tools that live in another program.

**Does MCP handle security?**

MCP handles part of it. The transport layer covers authorization and recommends OAuth for remote servers, and the spec leaves consent and access control to the host and the server.

**Can I run an MCP server locally?**

Yes. A local server runs as a child process of the host and talks over stdin and stdout, so nothing is exposed on the network.

**Do I have to call `server/discover` first?**

No. Servers must implement it, and a client is free to send any request directly and handle a version error if one comes back.

**Where is MCP defined?**

The specification lives at modelcontextprotocol.io, and its current version is 2026-07-28. The [glossary entry for the Model Context Protocol](/glossary/model-context-protocol/) has the short definition.
