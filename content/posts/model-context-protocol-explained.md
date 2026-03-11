---
title: "The Model Context Protocol explained: why MCP matters architecturally"
date: 2026-03-09
description: "A practical explanation of the Model Context Protocol, why it matters architecturally, how FastAPI MCP fits in, and how to avoid framework lock-in in agent systems."
tags: [ai, agents, mcp, fastapi]
status: published
---

If your agent stack feels one framework swap away from a rewrite, you are running into the same interface problem behind the [Unix philosophy](https://archive.computerhistory.org/resources/access/text/2019/11/102740539-05-01-acc.pdf): components stay useful when they can work together through a stable boundary. That is why MCP matters.

MCP gives agents a standard way to talk to tools, data, and prompts without hard-wiring those integrations to one SDK or framework. If that boundary is clean, you can swap runtimes and reuse tools. If it is not, the tool layer turns into framework-specific glue.

**The short version:** if you are building agents that need to call internal APIs, run actions, or work with business data, you should care about the Model Context Protocol for the same reason you care about clean API design. It separates the agent from the implementation details of the tools it uses.

| Question | Short answer |
| --- | --- |
| What is MCP? | A standard for how hosts and agents connect to tools, resources, and prompts |
| Why does it matter? | It reduces framework lock-in at the tool layer |
| Where does FastAPI MCP fit? | It turns an existing FastAPI app into an MCP server with much less custom glue |
| Who should care? | Anyone building agent products, internal AI tools, or reusable tool layers |

## What the Model Context Protocol actually is

The [official MCP overview](https://modelcontextprotocol.io/) describes it as an open protocol for connecting models to external systems. That is accurate. For implementation work, it helps to make it more concrete.

A more useful definition is this:

**MCP is a standard contract between an agent host and the things that agent can use.**

Those things fall into three buckets:

- **Tools** for taking actions
- **Resources** for exposing structured or unstructured data
- **Prompts** for reusable interaction templates

<figure class="post-figure">
  <img src="/static/images/posts/model-context-protocol-explained/mcp-server-concepts.png" alt="Model Context Protocol servers page showing tools resources and prompts">
  <figcaption>The official MCP servers page shows the three capability types clearly: tools, resources, and prompts.</figcaption>
</figure>

That matters because agent systems stop being simple the moment they need to do real work. The model has to call tools. Tools need typed inputs. Results have to come back in a predictable format. Permissions matter. Discovery matters. Tool descriptions matter. At that point, you are no longer just prompting a model. You are designing an interface between reasoning and execution.

<figure class="post-figure">
  <img src="/static/images/posts/model-context-protocol-explained/mcp-homepage-live.png" alt="Live Model Context Protocol overview page">
  <figcaption>The official MCP overview page frames MCP as the connection layer between AI applications and external systems.</figcaption>
</figure>

## Why MCP matters architecturally

If you define your tools in a framework-specific way, you are making an architectural choice whether you mean to or not. Your agent might work fine inside Framework A. Then six months later you want to move to Framework B, or a new SDK, or a different host like Claude Desktop, Cursor, or the OpenAI Agents SDK. Suddenly your tools are not really tools. They are wrappers tied to the first orchestration layer you picked.

That is lock-in.

MCP gives you a cleaner boundary:

- the **host** decides how to run the agent
- the **client/runtime** decides how to communicate with servers
- the **server** exposes capabilities in a standard format

That separation is the real value. Without it, the tool layer becomes hidden coupling. With it, the tool layer becomes infrastructure.

I wrote earlier about [agent harnesses](/blog/agent-harnesses/). MCP fits directly into that picture. The model handles reasoning. The harness handles execution and orchestration. MCP gives the harness a standard way to discover and call tools. That means the harness does not need bespoke integration code for every tool surface in your system.

## The host, client, and server model in plain English

The [MCP architecture spec](https://modelcontextprotocol.io/specification/draft/architecture/) uses a host, client, and server model. Once you understand that split, the whole protocol becomes much easier to reason about.

- **Host**: the application where the agent experience lives
- **Client**: the MCP connection manager inside that host or runtime
- **Server**: the process exposing tools, resources, and prompts

A simple mental model:

- Cursor or Claude Desktop is the **host**
- the MCP integration inside it is the **client**
- your internal docs server, billing server, or FastAPI MCP server is the **server**

That is why I keep calling MCP an architectural boundary. It formalizes the separation between the place where reasoning happens and the place where capabilities are exposed.

<figure class="post-figure">
  <img src="/static/images/posts/model-context-protocol-explained/mcp-architecture.png" alt="Model Context Protocol architecture page">
  <figcaption>The architecture view is the useful part of MCP. It shows the boundary between host, client, and server.</figcaption>
</figure>

## What goes wrong when you skip MCP

If you skip MCP, you can still build agent tools. The problem is what that code turns into over time.

Here is the usual path:

1. You add tool calling in one framework
2. You define tool schemas in that framework's preferred format
3. You bolt custom auth, validation, and response formatting onto each tool
4. You add more tools
5. You realize the tool layer cannot move without a rewrite

Now your agents are tied to the framework, and your tools are tied to the agents. That is backwards.

The better pattern is the opposite:

- tools should outlive agent frameworks
- APIs should not need to be redesigned every time the orchestration stack changes
- hosts should be replaceable without rebuilding the tool surface

This is why MCP matters even if you only use one framework today. The cost shows up when you want to change the host, adopt a new SDK, or expose the same tools to a second agent environment.

## MCP versus direct framework tool calling

This is where the tradeoff becomes concrete.

| Approach | Good at | Problem |
| --- | --- | --- |
| Direct framework tool calling | Fastest way to prototype | Tools are tied to one runtime |
| Custom internal tool layer | Maximum flexibility | High maintenance and no standard boundary |
| MCP server | Portability and reuse | More structure upfront |
| FastAPI MCP | Turning existing APIs into MCP tools quickly | Best when you already have a FastAPI backend |

If you are prototyping a single agent inside one environment, direct framework tool calling is fine.

If you are building systems that need to survive framework changes, host changes, or multiple agent entry points, MCP is the better long-term decision.

## Where FastAPI MCP fits

FastAPI MCP is practical for one simple reason: many teams already have APIs, business logic, auth, validation, and routing inside an existing FastAPI app.

The [FastAPI MCP docs](https://thedocs.io/fastapi_mcp/) show the basic idea clearly: you can expose FastAPI routes as MCP tools instead of rebuilding everything in a separate tool registry from scratch.

That means you can take an existing application surface and make it agent-usable with much less glue code.

Architecturally, that is a strong move because it keeps the boundary clean:

- FastAPI remains your application surface
- MCP becomes the tool interface layer
- the agent host can change without forcing a rewrite of the API

<figure class="post-figure">
  <img src="/static/images/posts/model-context-protocol-explained/fastapi-mcp-docs.png" alt="FastAPI MCP documentation page">
  <figcaption>FastAPI MCP matters because it lets existing FastAPI endpoints become agent-usable tools instead of forcing a second tool system.</figcaption>
</figure>

## Why FastAPI MCP is more important than it looks

FastAPI MCP is more than a convenience wrapper. It is an architectural shortcut. It lets you move from "we have APIs" to "our agents can use these capabilities through a standard protocol" without hand-authoring every tool definition in a separate agent framework.

That reduces three kinds of duplication:

- duplicated validation logic
- duplicated route-to-tool mapping
- duplicated business capability layers

That kind of duplication increases maintenance cost quickly in internal AI products.

The [FastMCP FastAPI integration docs](https://fastmcp.wiki/en/integrations/fastapi) reinforce the same pattern from another angle. The story is not just "you can expose tools." The story is that you can treat your application and your agent interface as adjacent layers rather than two disconnected systems.

<figure class="post-figure">
  <img src="/static/images/posts/model-context-protocol-explained/fastmcp-fastapi.png" alt="FastMCP FastAPI integration documentation">
  <figcaption>FastMCP's FastAPI integration shows the same larger idea: keep the application layer and tool layer connected, but not tightly coupled.</figcaption>
</figure>

## MCP inside an agent harness

A production agent system has at least three layers:

- **the model** for reasoning
- **the harness** for orchestration, retries, state, and observability
- **the tool boundary** for capabilities and data access

MCP belongs in the third layer.

That distinction matters because the framework, the tool boundary, and the runtime do different jobs.

The harness should own:

- execution loop
- retry logic
- checkpointing
- prompt assembly
- trace logging

MCP should own:

- capability discovery
- typed tool exposure
- resource access patterns
- prompt exposure where needed
- a standard contract between host and server

Seen that way, MCP is not competing with the harness. It reduces how tightly the harness is coupled to tool implementations.

## OpenAI Agents SDK support is a good signal

The [OpenAI Agents SDK MCP docs](https://openai.github.io/openai-agents-python/mcp/) are a useful signal because they show MCP support in a mainstream agent runtime. Standards matter once tooling ecosystems adopt them.

<figure class="post-figure">
  <img src="/static/images/posts/model-context-protocol-explained/openai-agents-mcp.png" alt="OpenAI Agents SDK MCP documentation page">
  <figcaption>Support in the OpenAI Agents SDK is one of the strongest signals that MCP is becoming infrastructure, not just a side protocol.</figcaption>
</figure>

## When MCP is worth it and when it is overkill

You probably should use MCP if:

- your agents need more than a couple of tools
- you want the same tools available across multiple hosts
- you expect your orchestration layer to change over time
- you already have APIs and want a cleaner path to agent access
- portability matters more than shaving a day off the first prototype

You probably do not need MCP yet if:

- you are building a one-off prototype
- your tool layer is tiny and unlikely to grow
- the agent will only ever run inside one tightly controlled framework
- you are still trying to prove the workflow itself is useful

MCP is not mandatory on day one. It becomes more useful as the tool layer grows and the system needs to last.

## Why MCP adoption makes sense

MCP addresses a straightforward engineering problem: multiple hosts and runtimes need to talk to the same capabilities, and custom glue does not scale well. A standard interface is a cleaner answer than repeating the same integration work in each framework.

## Frequently asked questions

**Is MCP only useful for desktop clients like Claude Desktop?**

No. That is one visible use case, not the whole point. The larger value is that MCP gives agent hosts and runtimes a shared way to talk to external capabilities.

**Is FastAPI MCP worth using if I already have a FastAPI backend?**

Yes, in many cases. If your team already has routes, validation, and business logic in FastAPI, FastAPI MCP is one of the cleanest ways to expose those capabilities to agents without rebuilding the same surface in a second tool system.

**Does MCP replace an agent framework?**

No. MCP is not a harness and not an orchestration framework. It standardizes the capability boundary. You still need a runtime or harness to manage the execution loop, state, retries, and observability.

**Can I ship agents without MCP?**

Absolutely. The question is not whether you can. The question is how much custom glue you want to own six months from now.

**What is the practical takeaway?**

Treat MCP as an interface boundary. If your agents are going to live longer than a prototype, that boundary is worth designing on purpose.
