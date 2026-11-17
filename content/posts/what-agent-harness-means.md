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
description: The word harness now names a layer you build, a program you install and a service you rent. I think the equation from a Hacker News reply is the definition to keep, and docs should say what their harness includes.
slug: what-agent-harness-means
status: published
title: "What people mean when they say agent harness"
work_note: "Agent products pick up new vocabulary every month, and the docs are where it gets pinned down. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies, and I run the product before I write about it. [Get in touch](/contact/)."
---

On November 17, under a Hacker News post about a benchmark of agent harnesses, [a commenter asked](https://news.ycombinator.com/item?id=50534879) whether the distinction between "harness" and "agent" still exists, since people use the two interchangeably. The two replies that came back disagreed.

I went through the vendor pages that use the word, and I think the commenter was right to ask. The word is doing different jobs in different docs, and catching that is what [technical documentation](/articles/technical-documentation/) is for.

## The word names a layer, a program and a service

I'd separate the uses by what you do with the thing. You build the first, install the second and rent the last.

- **A layer you build.** The sense I use on my own page about [agent harnesses](/articles/agent-harnesses/): the code around a model that runs the loop and calls the tools.
- **A program you install.** The [benchmark in that thread](https://runta.com/blog/introducing-frontierharness-eval-v1-1/) ranks 22 harnesses, and the names on its leaderboard include Codex CLI and Pi.
- **A service you rent.** Anthropic's [Agent SDK docs](https://platform.claude.com/docs/en/agent-sdk/overview) describe Managed Agents as "A hosted agent harness that runs the agent loop".

None of these is wrong. They're the same idea at different distances from your own code, and a reader who learned the word from one of them will misread the other two.

## I'd keep the equation

Of the two replies, I'd keep [the one that fits in a line](https://news.ycombinator.com/item?id=50534958): "harness + model = agent". The other reply asked whether the words mean the same thing, which is a fair report of how people talk and no use as a definition.

The equation holds up against the benchmark too. Its method is to fix a model and swap the harness around it, across 5 models, so the leaderboard treats a harness as the agent minus the model.

And it gives a writer a test. If a sentence in your docs still makes sense after you replace "harness" with "agent", the sentence hasn't said which one it means.

## What's inside is the part the docs leave to you

The equation settles what a harness is, and I don't think it settles what's in one. Read what each project says it includes:

| Project | What it calls a harness | What it says that includes |
|---|---|---|
| [Anthropic Managed Agents](https://platform.claude.com/docs/en/agent-sdk/overview) | A hosted service | The agent loop, with sessions in a sandbox |
| [LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) | A library, also offered managed | Planning, a virtual filesystem, subagents and long-term memory |
| [DeerFlow](https://github.com/bytedance/deer-flow) | An open-source application | Sandboxes, memories, tools, skills, subagents and a message gateway |

Memory is in two of those lists and absent from the first. DeerFlow's repository calls the project a "long-horizon SuperAgent harness", which stretches the word to cover a whole application.

So the word tells a reader there's a loop and some tools, and it says nothing about memory or sandboxing or who hosts it. A pair of products that both call themselves a harness can share very little.

## What I'd put on the page

I'd define the word the first time it appears, in one sentence, and then list what's inside. A sentence like "the harness in these docs is the loop and the tool registry, and you host it" takes one line.

Terminology already sits on the editor's side of a [documentation review](/articles/documentation-review/), next to structure and links. I'd add this word to that list for any agent product, because it's the one a reader is likeliest to bring a different meaning to.

Some readers will arrive with the benchmark's sense and some with Anthropic's. When vocabularies diverge that far, [documentation structure](/articles/documentation-structure/) gives the answer I'd reach for, which is a separate route for each reader.

Until the word settles, the definition has to travel with the page: what's in your harness, and who runs it.
