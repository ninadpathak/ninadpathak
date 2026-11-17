---
category: agent-memory
primary_query: short term memory ai agents
siblings:
- context-windows-vs-memory
- ai-memory-management
- rag-vs-memory
bridges:
- slug: llm-context-windows
  reason: The context window limit is the reason an agent needs memory.
date: 2026-04-19
description: 'Short-term memory for AI agents is the context window during one run. What compaction keeps and loses, with a tested example of a dropped instruction.'
status: published
work_note: "I'm Ninad Pathak. I work with AI companies as a freelance technical writer on setup tutorials, concept explainers and comparisons, and I run each product before I write about it. [See the work and get in touch](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Short-Term Memory for AI Agents: A Practical Guide'
slug: short-term-agent-memory
updated: 2026-11-17
---

Short-term memory for an AI agent is whatever sits in the context window during the current run, and on Anthropic's API, for one, the step that manages it can now run on the server. A hand-written sliding window with a scoring function for each message, which this page used to teach, is the wrong place to start there.

The model reads this part of [AI agent memory](/articles/agent-memory/) directly, and everything else has to be loaded into it.

The risk moved with it. Claude Code 2.1.323, released on November 12, [fixed a bug](https://code.claude.com/docs/en/changelog) in which running `/compact` a second time could end up "summarizing away a message that Claude had not answered yet".

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/short-term-agent-memory/context-fill.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/short-term-agent-memory/context-fill.narrow.svg" width="288" height="632"><img class="np-has-narrow" src="/static/images/diagrams/short-term-agent-memory/context-fill.svg" width="720" height="424" alt="A fixed-size context window is filled by four inputs: the system prompt, the conversation history, retrieved documents, and the agent's scratchpad. Whatever capacity is left is the headroom for the model's next response and tool calls. When it overflows, naive truncation cuts the oldest messages first." loading="lazy" decoding="async"></picture></a>
  <figcaption>The context window is a fixed buffer, and short-term memory is whatever it holds during one run.</figcaption>
</figure>

## What is short-term memory in an AI agent?

Short-term memory is the working state of one run: the instructions, the conversation so far, tool results and any notes the agent has written to itself, all held as tokens in the context window. It ends when the run ends, unless something copies it out.

That makes it a budget before it is anything else. Every tool result and every reply spends from the same window, and how models use a long one is the subject of [the context window guide](/articles/llm-context-windows/).

Anything meant to outlive the run belongs to long-term memory, which has its own decisions about what to write and when to replace it. [Context windows vs memory](/articles/context-windows-vs-memory/) draws that line, and [AI memory management for LLMs](/articles/ai-memory-management/) covers the storage side.

## What happens when short-term memory fills up?

Something has to leave the window, and there are two ways to choose it: drop the oldest turns, or replace them with a summary. Dropping is simple and loses whatever was said early, which is often where the instructions were.

The script below builds a 40-message conversation whose first message is a rule, then fits it into a 400-token budget twice.

```python
"""Fit a conversation into a token budget, with and without a pinned instruction."""
import tiktoken

encoding = tiktoken.get_encoding("o200k_base")


def tokens(text):
    return len(encoding.encode(text))


def window(messages, budget, pinned=()):
    """Keep pinned messages, then the newest others that still fit."""
    kept = [m for m in messages if m["turn"] in pinned]
    used = sum(tokens(m["text"]) for m in kept)
    for message in reversed(messages):
        if message["turn"] in pinned:
            continue
        cost = tokens(message["text"])
        if used + cost > budget:
            break
        kept.append(message)
        used += cost
    return sorted(kept, key=lambda m: m["turn"]), used


rule = "The production database is a read replica. Never write to it."
messages = [{"turn": 1, "text": rule}]
for turn in range(2, 41):
    messages.append({"turn": turn, "text": f"Turn {turn}: the user asks about report {turn} and the agent "
                                           f"answers with a summary of its columns, filters and row counts."})

total = sum(tokens(m["text"]) for m in messages)
print(f"conversation: {len(messages)} messages, {total} tokens")
for label, pinned in (("newest first", ()), ("turn 1 pinned", (1,))):
    kept, used = window(messages, budget=400, pinned=pinned)
    turns = [m["turn"] for m in kept]
    print(f"{label:<14} keeps {len(kept):>2} messages, {used} tokens, oldest turn {turns[0]}, "
          f"rule present: {rule in [m['text'] for m in kept]}")
```

With `tiktoken` installed, `python3 window_demo.py` gives two result lines that differ in one word.

```text
conversation: 40 messages, 1066 tokens
newest first   keeps 14 messages, 378 tokens, oldest turn 27, rule present: False
turn 1 pinned  keeps 15 messages, 391 tokens, oldest turn 1, rule present: True
```

The plain window keeps the newest fourteen messages, the oldest of them turn 27, and the rule is gone. Pinning turn 1 costs thirteen tokens and keeps it, which is the whole case for deciding what is exempt before deciding what to drop.

## What does compaction keep, and what does it lose?

Compaction keeps a model-written summary of the older turns and loses whatever the summary leaves out. Anthropic's [compaction documentation](https://platform.claude.com/docs/en/build-with-claude/compaction) describes the feature this way.

"Compaction replaces the older turns of a conversation with a summary that Claude writes on the server, so you need no summarization code of your own."

It gives a second reason to use it, saying it keeps the active context small "because response quality degrades as a conversation grows". Both of its modes "are in beta".

The page's own advice is "Use on-demand compaction wherever it is available", a mode it describes as "A compaction loop that requests the summary and swaps it in". The other mode fires when "input tokens reach the trigger you set" and is the one that takes "One parameter on your ordinary requests".

Either way the summarizer is no longer code you write. I think that is the right default, and the changelog is a useful record of how the step fails.

The `/compact` fix above is one case. Another, in version 2.1.326 from November 16, fixed compaction on Bedrock, Vertex and Foundry "sometimes replying to one of your messages instead of summarizing, or leaving Claude's last reply out of the summary".

Both bugs lost recent material, the part a summary is supposed to protect. A summary is a lossy copy made by a model, so anything that must survive word for word needs to live outside it.

## How do you keep an instruction from being lost?

Put it where compaction doesn't reach, and keep the raw history so a summary can be checked. Standing instructions belong in the system prompt or an instruction file, which is reloaded whole on every request.

The compaction page lists two options for the rest. "Compaction that keeps recent turns" leaves the last few turns word for word, and a custom summarization prompt is for the case "when the default summary drops something a later turn needs."

For facts that come up mid-conversation, the habits worth copying come from replies posted on November 9 to a Hacker News thread titled ["How do you manage your AI agents' context across clients and projects?"](https://news.ycombinator.com/item?id=50403153) A commenter there wrote "I let agents read their own pre-compaction history often", which treats the transcript as the record and the summary as an index to it.

Another ends each session by asking the agent to "prep a handoff so we can resume from here in a fresh session". A handoff note is short-term memory written down on purpose, by the model before the full context is gone.

A third practice in the thread is less comfortable: "at the end ask the agent to summarize what it learned and write it down." Anything written that way has crossed into long-term memory, and a note that was wrong when it was written will be loaded as fact next time.

The commenter's answer is to keep decisions as records with a state such as approved or rejected, and both this commenter and the previous one link tools of their own.

## How does short-term memory relate to long-term memory?

Short-term memory is what the model can see now, and long-term memory is what the application chooses to store and bring back later. The handoff note and the compaction summary are the two places where one turns into the other.

Long-term memory comes in more than one kind, and the [types of agent memory](/articles/agent-memory-types/) differ in how they're read back.

That crossing is where to spend review effort. Stored state differs from retrieved documents in ways [RAG vs memory](/articles/rag-vs-memory/) sets out, and the [state of agent memory](/articles/agent-memory-2026/) surveys the products that manage it.

## FAQ

**Is the context window the same thing as short-term memory?**

The window is the container and short-term memory is its contents during one run. A larger window holds more, and it doesn't decide what stays when the limit is reached.

**Do I still need my own summarization code?**

Not where the API offers compaction. Anthropic's documentation says the summary is written on the server "so you need no summarization code of your own", and what remains yours is deciding what must never be summarized.

**How do I add memory to an AI agent?**

Start with short-term memory, since the agent already has it: pin the instructions, turn on compaction and keep the transcript. Add long-term storage when a fact has to survive the session, and decide then who is allowed to write it.
