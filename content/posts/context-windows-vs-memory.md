---
category: agent-memory
primary_query: context window vs memory
siblings:
- memory-compression
- ai-memory-management
- hyperagents-memory
bridges:
- slug: claude-code-memory
  reason: A coding agent is the memory system a developer uses every day.
- slug: kv-cache-eviction
  reason: The KV cache is a third thing that gets called memory, and it stores computation.
date: '2026-04-19'
description: "Context window vs memory: a context window is what a model can see during one request, and memory is
  state an application stores and brings back later. Why a bigger window doesn't replace
  memory, with the token cost of replaying a conversation counted."
status: published
work_note: "Building an AI product whose readers are engineers? I'm Ninad Pathak, a freelance technical writer, and I write tutorials and technical articles for companies like yours after running the product myself. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Context Window vs Memory'
updated: '2026-08-18'
slug: context-windows-vs-memory
video: context-windows-vs-memory
---

On November 7 someone [asked Hacker News](https://news.ycombinator.com/item?id=50403153) how people manage their AI agents' context across clients and projects. The poster's complaint was the time spent re-explaining past decisions and client rules to the agent at the start of every session.

The poster asked about "context", and what they were missing was memory. People use the word context for both things.

Context window vs memory comes down to this: the context window is the text a model can see during one request, and memory is information your application stores and puts back into a later request.

Psychology, seventy years ago, separated holding something in mind from remembering it. George Miller's 1956 paper, [The Magical Number Seven, Plus or Minus Two](https://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two), is about how few items a person can hold in mind at once, roughly seven, and nobody reads the paper as a limit on what a person can remember for years.

A model's context window is a limit of Miller's kind, on what can be held at once. Remembering across sessions is a separate job called [agent memory](/articles/agent-memory/), and the code that stores a fact and brings it back is code you write.

## What is the difference between a context window and memory?

A context window holds the tokens of one request, and memory holds whatever has to outlive that request. The model reads the context window, and your application owns the memory.

| | Context window | Memory |
|---|---|---|
| Lifetime | One request | Across requests and sessions |
| Who fills it | The code that builds the prompt | The code that writes to a store |
| What goes wrong | The needed fact isn't there, or the model doesn't use it | The wrong fact is stored, or a stored fact is out of date |

A model can answer perfectly in one request and know nothing about that exchange in the next request. The model didn't forget the exchange, because the model never stored it anywhere.

## How does a chat app seem to remember?

A chat app seems to remember because it resends the conversation. The app puts every earlier turn back into the context window along with each new message, so the model rereads the whole conversation every time.

The script below counts what resending costs. It builds a 40-turn support conversation and counts the tokens sent, using the `o200k_base` tokenizer from tiktoken 0.14.0:

```python
"""Count the tokens a chat app sends when it replays the conversation on every turn."""
import tiktoken

enc = tiktoken.get_encoding("o200k_base")
USER = "Can you check the status of order {n} and tell me when it will arrive?"
REPLY = "Order {n} left the warehouse this morning and should arrive within three business days."

history, sent_total = [], 0
print("turn  tokens sent this turn  tokens sent so far")
for turn in range(1, 41):
    history.append(USER.format(n=1000 + turn))
    sent = sum(len(enc.encode(message)) for message in history)   # the whole history goes in again
    sent_total += sent
    history.append(REPLY.format(n=1000 + turn))
    if turn in (1, 10, 20, 40):
        print(f"{turn:>4}  {sent:>21,}  {sent_total:>18,}")
new_text = sum(len(enc.encode(message)) for message in history)
print(f"tokens of new text in the whole conversation: {new_text:,}")
```

Running it printed:

```text
turn  tokens sent this turn  tokens sent so far
   1                     18                  18
  10                    333               1,755
  20                    683               7,010
  40                  1,383              28,020
tokens of new text in the whole conversation: 1,400
```

The 40-turn conversation contains 1,400 tokens of new text, and resending the history on every turn meant sending 28,020 tokens in total. At turn 40 a single message carries 1,383 tokens of history to deliver a question of about 18.

Resending everything works until the history no longer fits in the window or costs too much. After that point the application has to choose which earlier turns go back in, and [memory compression](/articles/memory-compression/) covers how to make that choice.

## Does a bigger context window replace memory?

No, for two separate reasons. A context window of any size is empty at the start of the next session, and a fact that fits inside the window isn't guaranteed to be used by the model.

[Lost in the Middle](https://arxiv.org/abs/2307.03172), a 2023 paper, tested the second reason. Its authors moved the relevant passage around inside a long input and found that accuracy "significantly degrades when models must access relevant information in the middle of long contexts".

Suppose a contract fits in the window and the clause you need sits halfway through. The API accepts every page, and the clause sits in the position where the paper's models did worst.

[RULER](https://arxiv.org/abs/2404.06654), a 2024 benchmark, measured how much of an advertised context window a model can use well. Its authors tested 17 long-context models that all claimed 32K tokens or more, and report that only half kept satisfactory performance at 32K.

Lost in the Middle is from 2023 and RULER from 2024, so I wouldn't quote their figures against a current model. I'd keep their method: test your model with inputs as long as your real ones, and with the needed fact placed in the middle.

## What belongs in the context window, and what belongs in memory?

Decide by asking how long the information has to survive. Information that only the current request needs goes in the context window, and information that a later request will need gets stored outside the model.

The material for a code change belongs in the context window. The model needs the function, its tests and the instruction in the same request, and none of those has to be remembered tomorrow.

A customer's subscription plan belongs in memory, and so do the client rules from the Hacker News question. A plan and a client rule both have to survive into a new session, so your application has to decide when to write each one down and how to find it again.

Writing and finding are two different jobs, and a vector search over old messages does only the finding. [AI memory management](/articles/ai-memory-management/) covers the rest, including when to write a fact and when to expire it.

## Is the KV cache a kind of memory?

No. The [KV cache](/articles/kv-cache-eviction/) stores the computation a model has already done over a run of tokens, so that the model can avoid doing the same computation again.

The KV cache gets called memory because it lives in GPU memory, and it holds no facts your application can look up. A cached prompt prefix makes the next request faster, and it can't tell you which plan a customer is on.

## How do coding agents handle the split?

Coding agents write notes to files and read the files back at the start of a session. Claude Code, for example, loads a file named `CLAUDE.md` into the context window when a session starts, and that file is memory in the sense this page uses.

Each coding agent names and loads its files differently. [Claude Code's memory](/articles/claude-code-memory/) and [memory in HyperAgents](/articles/hyperagents-memory/) are two worked cases, and several replies in the Hacker News thread describe building the same thing by hand, with a wiki or an Obsidian vault of Markdown notes.

A current model such as Claude Fable 5.2 [lists a context window of 1M tokens](https://artificialanalysis.ai/models/claude-fable-5-2), and the developers in that thread still keep their client rules in Markdown files that they load by hand. I think that is where agent memory stands in 2026.

## FAQ

**Is a longer context window always better?**

No. A longer context window helps a task that needs more evidence in one request, and it also adds cost and gives the model more unrelated text to read past.

**Does an LLM remember previous conversations?**

No, not without help from the application. Each request starts with only what the application puts in the context window, so anything remembered was stored and sent again by the application.

**Can a vector database be the memory?**

A vector database can be one part of the memory. Similarity search finds related passages, and facts like a user's identity or which version is current need structured fields and filters.

**Why does a model miss information that fits in its context window?**

A model can miss it because fitting in the window isn't the same as being used. Lost in the Middle showed that the position of a fact in a long input changes whether a model uses it.

**How do I decide between context and memory?**

Ask whether a later request will need the information. If a later request will need it, store the information outside the model and decide how it gets retrieved.
