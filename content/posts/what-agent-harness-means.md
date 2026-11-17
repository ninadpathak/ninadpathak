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
description: An essay on vocabulary. Runta's benchmark calls Codex CLI a harness, Anthropic uses the word for its hosted Managed Agents and LangChain for its Deep Agents package. I think a product's docs should define the word on first use and list what's inside.
slug: what-agent-harness-means
status: published
title: "Agent docs don't agree on what a harness is"
work_note: "I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. I write developer documentation and define its terms on the page, after running the product myself. [Get in touch](/contact/)."
---

On November 17, under a Hacker News post about a benchmark of agent harnesses, [a commenter named samueloph asked](https://news.ycombinator.com/item?id=50534879) whether the distinction between "harness" and "agent" still exists, since people use the two words interchangeably. A reply from ogmutlu asked whether the two words mean the same thing, and a reply from layer8 gave a formula for telling them apart.

I opened the docs of the companies that use the word, and samueloph was right to ask. Runta, Anthropic and LangChain each call a different kind of thing a harness, and a reader moving from one company's page to the next gets no warning that the meaning has changed.

Pinning down a word like harness is a job for [technical documentation](/articles/technical-documentation/), and this essay is about how I'd do it. If you came for the definition of a harness and the parts inside one, my explainer on the [agent harness](/articles/agent-harnesses/) has both.

## What Runta, Anthropic and LangChain each call a harness

The benchmark that thread was about, Runta's [FrontierHarness Eval](https://runta.com/blog/introducing-frontierharness-eval-v1-1/), ranks 22 harness configurations, and the names on its leaderboard include Codex CLI, OpenCode and Pi.

Codex CLI, OpenCode and Pi are coding agents that you install and launch from a terminal. So on Runta's leaderboard, a harness is a finished program with its own prompt and its own tools.

Anthropic uses the word for a product you never install. Its [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) describes Managed Agents as "A hosted agent harness that runs the agent loop", which means the loop runs on Anthropic's servers and you configure it through the Claude API.

LangChain uses the word for a Python package. Its [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview) calls Deep Agents the agent harness for multi-step work, and using it means writing `from deepagents import create_deep_agent` and passing in your own model and tools.

My explainer uses the word a fourth way, for code you write yourself: the loop that calls the model, the list of tools and the file where a run saves its progress. The loop, the tool list and the progress file have no product name, and nobody ships them to you.

Now put a developer who learned the word from Runta's leaderboard in front of LangChain's docs. That developer reads that Deep Agents is a harness, looks for a program to launch the way they launch Codex CLI, and finds an import statement.

## I'd keep the reply that says harness plus model equals agent

Of the two replies to samueloph, I'd keep [the one from layer8](https://news.ycombinator.com/item?id=50534958): "harness + model = agent (plus sub-agents)". Under that formula, Codex CLI running the GLM-5.3 model is an agent, and Codex CLI with the model taken out is the harness.

The other reply, from ogmutlu, asked whether harness and agent mean the same thing. That matches how people use the words in a comment thread, and it can't work as a definition, because a definition has to tell the two words apart.

Runta's benchmark already works the way layer8's formula says. The benchmark runs Codex CLI with the GLM-5.3 model, runs Codex CLI again with DeepSeek, and treats the part that stayed the same across both runs as the harness.

The formula also gives a writer a check to run on a draft. Take a sentence such as "configure the harness to retry failed tool calls" and replace "harness" with "agent": if the sentence still reads as correct, it never said whether the retry setting belongs to the harness or to the whole agent.

## The formula doesn't say whether memory is part of the harness

Layer8's formula says a harness is everything in the agent except the model. The formula doesn't say whether one product's harness includes memory, a sandbox or hosting, and the vendors' own descriptions give different answers:

| Project | What the project is | What its description says the harness includes |
|---|---|---|
| Anthropic Managed Agents | A service Anthropic hosts, with a self-hosted sandbox as an option | The agent loop, with sessions in a sandbox |
| LangChain Deep Agents | A Python package, also offered as a managed service | Planning, a virtual filesystem, subagents and long-term memory |
| [DeerFlow](https://github.com/bytedance/deer-flow) | An open-source application from ByteDance | Sandboxes, memories, tools, skills, subagents and a message gateway |

LangChain lists long-term memory as part of Deep Agents, and DeerFlow lists memories among its parts. Anthropic's one-line description of Managed Agents mentions only the agent loop and a sandbox, although the same docs have a [memory stores page](https://platform.claude.com/docs/en/managed-agents/memory) for Managed Agents.

So a developer comparing Managed Agents with Deep Agents from those two descriptions would conclude that only Deep Agents has memory. That conclusion is wrong, and the one-line description is what produced it.

DeerFlow stretches the word furthest. Its repository describes the whole application, which does research, writes code and includes a message gateway, as a "long-horizon SuperAgent harness".

Put Codex CLI next to DeerFlow and the part they share is small: each runs a model in a loop and gives it tools. Memory, sandboxing and hosting differ between the two, and both Codex CLI and DeerFlow are called a harness.

## What I'd write in a product's docs

If I were writing the docs for one of these products, I'd define harness in one sentence the first time the word appears. For Managed Agents that sentence could be "the harness is the agent loop and the sandbox it runs in, and Anthropic hosts both".

Under that sentence I'd put a short list of what the harness includes and what it leaves to the developer. Memory and hosting would each get a line in that list, whether the answer is yes or no.

Checking a term like harness is already part of an editor's job. The reviewer table on my [documentation review](/articles/documentation-review/) page gives the technical writer or editor four things to check, and terminology is one of the four.

I wouldn't write separate pages for readers who learned the word from Runta and readers who learned it from Anthropic. My rule in [documentation structure](/articles/documentation-structure/) is to split audiences only when their tasks differ, and both groups have the same task and need the same page with harness defined at the top.

Until Runta, Anthropic and LangChain mean the same thing by harness, each product's docs have to say which parts are in its harness and who runs it.
