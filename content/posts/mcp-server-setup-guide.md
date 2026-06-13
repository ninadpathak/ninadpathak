---
title: "Wiring Tools into Your Agent with MCP: A Practical Setup"
date: 2026-06-12
slug: "mcp-server-setup-guide"
description: "A hands-on guide to connecting an AI agent to your own tools and data with the Model Context Protocol. The client-server shape, a minimal working server, tool design, and the guardrails that keep it safe."
tags: [ai, agents, developer-experience]
status: published
---

An agent that cannot touch the outside world is a very expensive autocomplete. Tools are what let it read a database, hit an API, or run a command, and the Model Context Protocol is the cleanest way I have found to wire those tools in. I went deep on the concept in [the Model Context Protocol explained](/blog/model-context-protocol-explained/). Here I want to show the practical setup, the parts you actually build and run.

The promise of MCP is simple. You write a tool once, expose it through a standard interface, and any MCP-aware agent can call it without a custom integration. The same server that powers a coding agent today works with a different agent tomorrow. That portability is the reason I reach for it instead of bolting tools directly into one agent.

## What MCP actually gives you

MCP is a protocol that sits between an agent and the tools it wants to use. The agent is the client. Your tool runs inside a server. The protocol defines how the two talk, so neither side needs to know the other's internals.

The payoff is that the integration stops being one-off. Before MCP, every tool I wanted an agent to use meant gluing an API into that specific agent's tool-calling format. Each new agent meant doing it again. With MCP, the tool lives in a server that speaks the protocol, and the agent discovers what it offers at connection time.

A server can expose three kinds of thing. Tools, which the agent calls to do work. Resources, which the agent reads for context. Prompts, which are reusable templates. For most setups the tools are the part that matters, so that is where I will spend the rest of this guide.

<div class="visual-wrapper">
  <div class="visual-title">THE MCP CLIENT-SERVER SETUP</div>
  <div class="visual-container">
    <iframe src="/static/visuals/mcp-setup-architecture.html" title="An agent acting as MCP client connecting over a transport to an MCP server, which exposes tools that reach a database and an external API, with request and response flowing along the link" loading="lazy"></iframe>
  </div>
</div>

## The shape of an MCP setup

Three pieces make up a working setup. The client is the agent, or the harness around it, that wants to call tools. The server is the process you write that exposes those tools. The transport is the channel between them.

The transport is usually one of two things. A local server runs as a subprocess and talks over standard input and output, which is the common choice for tools that live on the same machine as the agent. A remote server talks over HTTP, which suits tools that run as a shared service many agents connect to. For a first setup, the local subprocess transport is the path of least resistance.

The agent connects, asks the server what it offers, and gets back a list of tools with their names, descriptions, and argument schemas. From then on the agent can call any of those tools by name, and the server runs the real work and returns the result.

## Building a minimal server

A working MCP server is smaller than people expect. The Python SDK does the protocol plumbing, so the code I write is mostly the tool itself. Here is a server that exposes one tool for looking up an order.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("orders")

ORDERS = {
    "1001": {"status": "shipped", "carrier": "UPS"},
    "1002": {"status": "processing", "carrier": None},
}

@mcp.tool()
def get_order_status(order_id: str) -> dict:
    """Look up the status of an order by its ID."""
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"No order found for {order_id}"}
    return order

if __name__ == "__main__":
    mcp.run()
```

The decorator is doing the heavy work. It registers the function as a tool, reads its type hints to build the argument schema, and uses the docstring as the description the agent sees. The agent learns that an order ID is a string and that the tool returns a status, all from the function signature and a one-line docstring.

Calling `mcp.run()` with no arguments starts the server on the standard input and output transport, ready for a local agent to connect as a subprocess. A real server swaps the dictionary for a database call or an API request, and the rest of the structure stays the same.

## Designing the tools so the agent calls them right

A tool the agent calls wrong is worse than no tool at all. Good tool design is the part of MCP that decides whether the setup helps or hurts, and it comes down to the same principles I covered in [structured outputs and function calling](/blog/structured-outputs-llms-json-mode-function-calling/).

The name and description are the agent's only guide to when a tool applies. I name tools for what they do in plain terms, `get_order_status` rather than `fetch_data`, and I write the description for the agent rather than for a human reading the source. The agent reads that description on every decision about which tool to call, so an ambiguous one produces wrong calls.

The argument schema is the contract. Clear types and required fields let the agent build a valid call on the first try. A tool that takes a vague blob of text invites the agent to stuff the wrong thing into it. The tighter the schema, the fewer malformed calls I see.

The return value matters as much as the input. I return structured data the agent can reason about, and I make errors explicit rather than silent. A tool that returns an error message the agent can read leads to a recovery. A tool that returns nothing on failure leads to the agent assuming success and moving on with a wrong picture.

## Connecting the server to your agent

The agent side is configuration, not code. An MCP client reads a config that tells it which servers to launch and how. For a local server the config names the command to run and its arguments.

```json
{
  "mcpServers": {
    "orders": {
      "command": "python",
      "args": ["orders_server.py"]
    }
  }
}
```

When the agent starts, it launches that command as a subprocess, connects over the transport, and asks the server for its tools. From the agent's point of view the order-status tool now sits alongside its built-in ones. The agent decides when to call it based on the name and description the server reported.

The same server config works across MCP-aware agents, which is the portability paying off. I wire the server once and reuse it wherever I need those tools, including inside the harness I run around my coding agents, which I described in [agent harnesses](/blog/agent-harnesses/).

## Guardrails for tool access

A tool gives the agent reach into real systems, so the guardrails are not optional. The first rule I follow is that a tool does exactly one thing with a narrow scope. A tool that can read one customer's order is safe. A tool that can run arbitrary database queries is a liability waiting for a confident wrong call.

Read and write deserve different treatment. I let read tools run freely, because the worst case is wasted tokens. Write tools, anything that changes data or reaches a production system, sit behind explicit approval, so the agent proposes the action and a human confirms it before it runs.

Validation lives in the server, not in the prompt. I never trust that the agent sent good arguments. The server checks them, rejects bad ones with a clear error, and never assumes the input is well-formed because a model produced it. Treating tool input as untrusted is the same discipline I would apply to any input crossing a boundary.

## When MCP is worth it

MCP earns its place the moment you want the same tools available to more than one agent, or you want tools you can maintain separately from the agent that uses them. A single throwaway script with one tool does not need it. A growing set of tools that several agents share is exactly what it was built for.

The setup cost is real but small. A server is a few lines around the tool you were going to write anyway, and the config is a handful of lines on the agent side. What you get back is tools that outlive any single agent and an integration you write once. For anyone building real AI workflows, that portability is worth the small amount of structure it asks for up front.

## FAQ

**What is the Model Context Protocol?**

MCP is a standard that connects AI agents to external tools and data through a common interface. The agent acts as a client, your tools run inside a server, and the protocol defines how they talk, so you can write a tool once and use it with any MCP-aware agent.

**How do I build an MCP server?**

Write your tool as a function, register it with the SDK, and run the server. The SDK reads the function's type hints to build the argument schema and uses the docstring as the description the agent sees, so a minimal server is only a few lines around the tool itself.

**What transport should I use for a local setup?**

The standard input and output transport, where the agent launches the server as a subprocess on the same machine. It is the simplest option and the right default for tools that live next to the agent. Use HTTP when the server runs as a shared service many agents connect to.

**How do I keep an agent from misusing a tool?**

Give each tool one narrow job, validate every argument inside the server, and put write actions behind explicit approval. Let read-only tools run freely and require a human to confirm anything that changes data or reaches production.

**Why use MCP instead of building tools into the agent directly?**

MCP makes the integration portable. A tool in an MCP server works with any MCP-aware agent without a custom rewrite, and you can maintain the tools separately from the agents that use them. For one throwaway tool it is overkill, and for a shared, growing set it pays off quickly.
