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

Databases went through this in the early nineties. Every application needed its own code for every database until [ODBC](https://en.wikipedia.org/wiki/Open_Database_Connectivity) put a driver in between in 1992, and after that an application written against the driver interface could reach any database that shipped one.

Anthropic [open-sourced the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) on November 25, 2024 to make the same trade for the tools layer of [AI agent architecture](/articles/ai-agents/). So far, so familiar.

What's less familiar is that the protocol changed shape this year. The [2026-07-28 revision](https://modelcontextprotocol.io/specification/2026-07-28/changelog) removed the connection handshake, so a good share of the explainers you'll find describe a protocol that no longer exists, and I've written this page against the current spec with messages printed from a server on my machine.

## What is the Model Context Protocol?

MCP is a client-server protocol built on JSON-RPC 2.0. The [architecture page](https://modelcontextprotocol.io/docs/learn/architecture) names the parties:

- **Host:** the AI application a person uses, such as Claude Code or Visual Studio Code.
- **Client:** a component inside the host that holds the connection to one server. The host creates one client per server.
- **Server:** a program that provides tools and data to clients. It can run on your machine or on someone else's.

The spec says MCP "takes some inspiration from the Language Server Protocol", and the comparison holds up. An editor that speaks LSP gets every language that has a server, and a host that speaks MCP gets every tool that has one.

The protocol stops at the exchange. The same architecture page says MCP "does not dictate how AI applications use LLMs or manage the provided context", so what the model does with a tool list is the host's business.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/model-context-protocol/mcp-architecture.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/model-context-protocol/mcp-architecture.narrow.svg" width="288" height="688"><img class="np-has-narrow" src="/static/images/diagrams/model-context-protocol/mcp-architecture.svg" width="720" height="264" alt="An MCP round trip drawn left to right. The host holds a client, the client sends a request to the server, and the server runs one of its tools and returns the result along the same path." loading="lazy" decoding="async"></picture></a>
  <figcaption>The host creates one client per server. Each request carries its own protocol version, so the server keeps no memory of the client between calls.</figcaption>
</figure>

## What can an MCP server offer?

An MCP server can offer tools, resources and prompts, and each has a list method that a client calls to find out what's there:

| Primitive | What it is | Methods |
|---|---|---|
| Tools | Functions the model can call | `tools/list`, `tools/call` |
| Resources | Data the application can read, such as a file or a database schema | `resources/list`, `resources/read` |
| Prompts | Reusable prompt templates | `prompts/list`, `prompts/get` |

Tools get nearly all the attention, and I think that's fair. A tool carries a name, a description and an `inputSchema` written in JSON Schema, which is the same mechanism behind [structured outputs and function calling](/articles/llm-structured-outputs/).

Clients have one feature of their own left, called elicitation, which lets a server ask the user a question in the middle of a call. Roots, sampling and protocol logging are deprecated as of the 2026-07-28 revision, so a tutorial that leans on them is teaching the old protocol.

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

The first message that server saw was a tool call, and it answered. There's no handshake to run first, because each request carries its protocol version and the client's capabilities in `_meta`.

That has a price you can read in the byte counts. Of the 255 bytes in the `tools/list` request, 181 are `_meta`.

The fourth call is the one I'd show a new MCP author. A wrong argument name comes back as an ordinary result with `isError` set to true and a message the model can read, and the [tools spec](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) says such errors exist so that a model can correct its arguments and try again.

Now look at the last call. I asked for the list again with a 2024 version string, and the server refused with error `-32022` and the one version it supports, so an old client gets a clear answer and nothing else from this SDK release.

## What changed in MCP in 2026?

The 2026-07-28 revision made MCP stateless. The changelog lists the pieces, and these are the ones that change how you'd explain the protocol:

- The `initialize` handshake is gone. Every request now carries the protocol version and client capabilities in `_meta`.
- Protocol-level sessions and the `Mcp-Session-Id` header are gone from the HTTP transport. A server that needs state across calls hands out its own handle and takes it back as a tool argument.
- Servers must implement `server/discover`, which reports versions and capabilities. Clients may call it or skip it.
- Change notifications moved to a single opt-in stream called `subscriptions/listen`.

I read the revision as the protocol admitting where it runs now. A handshake and a session suit one process talking to another on a laptop, and they're a burden for a server behind a load balancer, where the next request may land on a different machine.

It's also why the output above shows `ttlMs` and `cacheScope` on every list. A response that doesn't depend on the connection can be cached like any other HTTP response.

## Should an MCP server run locally or remotely?

Run it locally over stdio when it touches files on one machine, and remotely over Streamable HTTP when many clients need the same server. The architecture page puts it this way: a local stdio server "typically" serves a single client, and a remote one serves many.

The messages are the same on both transports. On stdio the host launches the server as a child process, and on Streamable HTTP the client sends each message as an HTTP POST, with OAuth as the recommended way to get a token.

The [MCP server tutorial](/articles/mcp-server-tutorial/) builds the local kind, a read-only server that can't read outside one docs folder.

## Is MCP better than a CLI or a plain API?

It depends on whether the host has a shell. When [MCP Explained](https://news.ycombinator.com/item?id=50379249) reached the Hacker News front page on November 5, the thread spent less time on the explainer than on whether the protocol is needed at all.

A commenter there [called MCP](https://news.ycombinator.com/item?id=50379528) "basically just a REST API with standardized endpoints for discovery aimed at agents". I think that description is accurate, and I'd take it as the case for the protocol.

Discovery in a known place is the whole product. A coding agent with a terminal can run `--help` on a CLI and work the rest out, but a chat application has no terminal, so a standard way to ask a server what it can do is how it gets tools at all.

The other half of the thread's complaint holds too. For one application with a few fixed tools, plain function calling does the job with nothing to deploy, and I wouldn't add a server for it.

## Where does MCP fit in an agent harness?

MCP is the part of the harness that reaches tools it doesn't own. The [agent harness](/articles/agent-harnesses/) still runs the loop, decides what goes into the context window and asks the user before a risky call.

That last duty can't be handed to the protocol. The [spec's security section](https://modelcontextprotocol.io/specification/2026-07-28) says "Tools represent arbitrary code execution and must be treated with appropriate caution", and it adds that MCP can't enforce its own consent rules at the protocol level.

So a server's description of its tool is a claim, and the host decides how far to trust it. I'd keep that in mind before pointing an agent at a server someone else runs.

## FAQ

**Is MCP the same as function calling?**

No. Function calling is how a model asks its own application for a tool, and MCP is how that application finds and calls tools that live in another program.

**Does MCP handle security?**

Partly. The transport layer covers authorization and recommends OAuth for remote servers, and the spec leaves consent and access control to the host and the server.

**Can I run an MCP server locally?**

Yes. A local server runs as a child process of the host and talks over stdin and stdout, so nothing is exposed on the network.

**Do I have to call `server/discover` first?**

No. Servers must implement it, and a client is free to send any request directly and handle a version error if one comes back.

**Where is MCP defined?**

The specification lives at modelcontextprotocol.io, and its current version is 2026-07-28. The [glossary entry for the Model Context Protocol](/glossary/model-context-protocol/) has the short definition.
