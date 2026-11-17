---
category: technical-documentation
primary_query: none
siblings:
- documentation-review
- documentation-structure
bridges:
- slug: agent-harnesses
  reason: The essay is about how vendors use the word that page defines.
date: 2026-11-18
description: An essay on vocabulary. Vendor docs use the word harness for a layer you build, a program you install and a service you rent, and I think a product's docs should define it on first use and say what's inside.
slug: what-agent-harness-means
status: published
title: "Agent docs don't agree on what a harness is"
work_note: "I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. I write developer documentation and define its terms on the page, after running the product myself. [Get in touch](/contact/)."
---

On November 17, under a Hacker News post about a benchmark of agent harnesses, [a commenter asked](https://news.ycombinator.com/item?id=50534879) whether the distinction between "harness" and "agent" still exists, since people use the two interchangeably. The two replies that came back disagreed.

I went through the vendor pages that use the word, and I think the commenter was right to ask. The word is doing different jobs in different docs, and catching that is what [technical documentation](/articles/technical-documentation/) is for.

If you came for the definition and the parts, that's my explainer on the [agent harness](/articles/agent-harnesses/). What follows is about the wording.

## What Runta, Anthropic and LangChain each call a harness

Start with the benchmark the Hacker News thread was about. Runta's [FrontierHarness Eval](https://runta.com/blog/introducing-frontierharness-eval-v1-1/) ranks 22 harness configurations, and the names on its leaderboard are Codex CLI, OpenCode and Pi.

Codex CLI, OpenCode and Pi are coding agents that you install and launch from a terminal. So on Runta's leaderboard, a harness is a finished program with its own prompt and its own tools.

Anthropic uses the word for a product you never install. Its [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) describes Managed Agents as "A hosted agent harness that runs the agent loop", which means the loop runs on Anthropic's servers and you configure it through the Claude API.

LangChain uses the word for a Python package. Its [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview) calls Deep Agents the agent harness for multi-step work, and using it means writing `from deepagents import create_deep_agent` and passing in your own model and tools.

My explainer uses the word a fourth way, for code you write yourself: the loop that calls the model, the list of tools and the file where a run saves its progress. That code has no product name and nobody ships it to you.

Now put a developer who learned the word from Runta's leaderboard in front of LangChain's docs. They read that Deep Agents is a harness, look for a program to launch the way they launch Codex CLI, and find an import statement.

## I'd keep the equation

Of the two replies, the one to keep [fits in a line](https://news.ycombinator.com/item?id=50534958): "harness + model = agent (plus sub-agents)". The other reply asked whether the words mean the same thing, which is a fair report of how people talk and no use as a definition.

The equation holds up against the benchmark too. Its method is to fix a model and swap the harness around it, across 5 models, so the leaderboard treats a harness as the agent minus the model.

And it gives a writer a test. If a sentence in your docs still makes sense after you replace "harness" with "agent", the sentence hasn't said which one it means.

## What's inside is the part the docs leave to you

The equation settles what a harness is, and I don't think it settles what's in one. Read what each project says it includes:

| Project | What it calls a harness | What it says that includes |
|---|---|---|
| [Anthropic Managed Agents](https://code.claude.com/docs/en/agent-sdk/overview) | A hosted service, with a self-hosted sandbox as an option | The agent loop, with sessions in a sandbox |
| [LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) | A library, also offered managed | Planning, a virtual filesystem, subagents and long-term memory |
| [DeerFlow](https://github.com/bytedance/deer-flow) | An open-source application | Sandboxes, memories, tools, skills, subagents and a message gateway |

Memory is in two of those lists and missing from Anthropic's one-line description, though Managed Agents has a [memory stores page](https://platform.claude.com/docs/en/managed-agents/memory) of its own. A description that leaves out something the product documents is the problem in miniature.

DeerFlow's repository calls the project a "long-horizon SuperAgent harness", which stretches the word to cover a whole application.

So the word tells a reader there's a loop and some tools, and it says nothing about memory or sandboxing or who hosts it. A pair of products that both call themselves a harness can share very little.

## What I'd put on the page

Define the word the first time it appears, in one sentence, and then list what's inside. A sentence like "the harness in these docs is the loop and the tool registry, and you host it" takes one line.

Terminology already sits on the editor's side of a [documentation review](/articles/documentation-review/), next to structure and links. For an agent product this word belongs on that list, because it's the one a reader is likeliest to bring a different meaning to.

Some readers will arrive with the benchmark's sense and some with Anthropic's. My rule in [documentation structure](/articles/documentation-structure/) is to split audiences only when their routes differ, and here they don't, so one page with the word defined serves both.

Until the word settles, the definition has to travel with the page: what's in your harness, and who runs it.
