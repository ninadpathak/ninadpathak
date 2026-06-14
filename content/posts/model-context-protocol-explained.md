---
date: 2026-03-11
description: Model Context Protocol (MCP) is the new standard for connecting AI models
  to data sources and tools. Here is why it matters, how it works, and why it is the
  missing link for agentic infrastructure.
status: published
tags:
- ai
- agents
- infrastructure
- mcp
title: 'The Model Context Protocol (MCP) Explained: A Universal Language for AI Tools'
---

Wiring an AI model up to external data has always been a messy engineering chore. The last time I did it, I wrote one connector to read a GitHub repo, a second to pull docs out of Google Drive, and a third to query our Postgres logs, each with its own auth dance and its own way of describing what the model was allowed to do. Every one of those integrations needed custom glue to translate a model request into an actual API call, and every new tool meant starting that work over from scratch. That fragmentation slows you down and quietly raises the odds that the model reasons over malformed or half-translated data.

The Model Context Protocol (MCP) attacks the problem from the other side by giving everyone one standard to write against. Any AI host can talk to any data server through a single shared language, so the connector you build for one agent works for the next one without changes. I think of MCP as the plumbing layer that the current generation of agents has been missing.



## What the Model Context Protocol actually is

At its core, MCP is an open standard that separates the AI application from the tools it reaches for. It spells out a consistent way for a host to discover what functions a remote server offers and then call them. The protocol carries those interactions over JSON-RPC, and it guarantees that data and tool definitions arrive in a shape the model can read natively, with no bespoke parsing step in the middle.

Three parts make up the system. A host is the primary AI surface a person interacts with, like Claude Desktop or an IDE plugin. A server is whatever provides the data or tools, say a wrapper around your Jira board or your local filesystem. A client sits between them as the bridge that opens and manages the connection. Keeping those concerns apart is what lets you build a tool once and run it on any MCP-compliant platform, the same way a USB keyboard works on any laptop without a driver written for that specific machine.

Where the server actually runs is a choice you make per connection. A local server typically talks to the client over stdio, the same pipe a shell uses to feed input and read output from a child process, which is what I use when I want a model poking at files on my own machine. A remote server runs somewhere else and speaks over HTTP, which is what you reach for when several people or several agents need the same Jira or database server. The protocol on the wire stays identical either way, so the tool definitions and call format do not change when you move a server from your laptop to a shared host.



## Why MCP matters architecturally

Standardizing the boundary between models and tools collapses a lot of duplicated work across the whole stack. You stop writing a custom Slack connector for your research agent and then writing a second, slightly different Slack connector for your coding assistant six weeks later. One MCP server for Slack, and every agent you own can post messages or read channels through it immediately.

That modularity is also what makes dynamic tool discovery possible. An agent can ask an MCP server at runtime which capabilities it exposes, then plan around whatever it finds, so adding a new data source becomes a matter of pointing the agent at a new server rather than recompiling its tool list. I have watched this change the shape of the work itself: integrating a tool drops from a coding task with a pull request and a deploy down to a configuration task you can finish in a config file.

The same standardization pays off in surprising places, like upgrades. When the team that maintains your Slack server adds a new tool for scheduling messages, every agent pointed at that server can call it the next time it lists capabilities, with no change on your side. Compare that to the old world, where a new endpoint on a vendor API meant I had to crack open each integration I owned, add the wiring, test it, and ship it. One server improving lifts every consumer at once, which is the kind of compounding return that makes a shared protocol worth its overhead.

## How the protocol works

Walk through one round trip and the flow is easy to follow. The host opens a connection to the server, and the server answers with a catalog of the resources and tools it offers. Every tool in that catalog carries a name, a plain-language description, and a JSON Schema that pins down exactly which input arguments it expects, the same mechanism behind [structured outputs and function calling in LLMs](/blog/structured-outputs-llms-json-mode-function-calling/).

Working from those definitions, the model produces a tool call, for instance a request to run `search_issues` with a `status` of `open` and an `assignee` of my username. The host hands that request to the MCP server, the server runs the function and returns the result, and the model picks up where it left off. Because the schema constrains what a valid call looks like, a loop like this sharply cuts down on hallucinated arguments such as a field name the API never had. It also gives you one clean choke point to enforce auth, rate limits, and audit logging.

<div class="visual-wrapper">
  <div class="visual-title">REQUEST FLOW: HOST &rarr; CLIENT &rarr; SERVER &rarr; BACK</div>
  <div class="visual-container">
    <iframe src="/static/visuals/mcp-architecture.html" title="MCP request flowing from host through the client bridge to a server and back" loading="lazy"></iframe>
  </div>
</div>

## MCP inside an agent harness

Where MCP really earns its place is inside [an agent harness, the infrastructure layer your LLM agent actually needs](/blog/agent-harnesses/). The harness runs the high-level reasoning loop, deciding what to do next and when the task is finished, and MCP handles the granular work underneath it: executing a tool, fetching a record, returning the bytes. Pair the two and you get something solid enough to run in production rather than a demo that falls over the first time a tool times out.

A harness leans on MCP whenever it needs live context. Mid-task, it might query a database for the current order state or pull the last hundred lines of logs from a monitoring server, then drop that data into the prompt assembler before the next model call. MCP lays the pipes that move the data around. The harness supplies the judgment about what to ask for and what to do with the answer.



## When to use MCP

Reach for MCP when you are building a set of tools that more than one AI application has to share. It pays off in companies where data lives scattered across a dozen SaaS platforms, your CRM here, your ticketing system there, your data warehouse somewhere else, and several agents all need to read from the same sources without each team rebuilding the connectors. Local development is another sweet spot, when you want to hand an LLM scoped access to your filesystem or terminal and keep tight control over what it can touch.

For a single-purpose app with one or two fixed tools, plain function calling is honestly simpler and I would not bother with the protocol. Standing up an MCP server, wiring the client, and managing the handshake only starts to pay back once you care about scale and reuse across applications. Spending that effort early is a bet on flexibility you will want later, not a fix for anything you have today.

## Why adoption is accelerating

Big model providers like Anthropic and OpenAI have thrown their weight behind MCP, and the catalog of pre-built servers grows every week. Developers keep contributing connectors for everything from PostgreSQL to linear.app, which means the server you need often already exists by the time you go looking for it.

All that momentum points toward MCP becoming the USB port for AI models, a standard socket that any tool can plug into and expect to work. We are leaving behind the era where every integration was a one-off you wrote and maintained yourself, and heading into one where connecting a model to a new source is as routine as plugging in a cable.

## Frequently asked questions

**Is MCP a replacement for LangChain?**

No, and I see this confusion often. MCP is a transport protocol, so frameworks like LangChain or LangGraph sit a layer above it and can use MCP as the channel they talk to tools through.

**Does MCP handle security?**

Partly. The protocol gives you the structure for tool execution and a single place to enforce rules, and the host and server still have to bring their own authentication and authorization on top of that. I treat MCP as the frame around the door and leave the actual lock to my own code.

**Can I run MCP servers locally?**

Yes, and it is how I run them most of the time. A local MCP server is the easiest way to give an AI model scoped access to your development environment or private files without anything leaving your machine.