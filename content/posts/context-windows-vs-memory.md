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
description: A context window is what a model can see during one request, and memory is
  state an application stores and brings back later. Why a bigger window doesn't replace
  memory, with the token cost of replaying a conversation counted.
status: published
work_note: "Building an AI product whose readers are engineers? I'm Ninad Pathak, a freelance technical writer, and I write tutorials and technical articles for companies like yours after running the product myself. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Context Window vs Memory, and What Each One Is For'
updated: '2026-08-18'
slug: context-windows-vs-memory
video: context-windows-vs-memory
---

On November 7 someone [asked Hacker News](https://news.ycombinator.com/item?id=50403153) how people manage their AI agents' context across clients and projects. The cost they described was re-explaining past decisions and client rules at the start of every session.

Read the question again and it's about memory. The word "context" is doing both jobs in it, and that mix-up is the reason context window vs memory is worth a page: the context window is what a model can see during one request, and memory is state your application stores and brings back in a later one.

Psychology drew the same line a long time ago. George Miller's 1956 paper, [The Magical Number Seven, Plus or Minus Two](https://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two), is about how little a person can hold in mind at once, and nobody reads it as a claim about what a person can remember for years.

A model's window is the first kind of limit. Everything on the second side, the storing and the bringing back, is [agent memory](/articles/agent-memory/), and it's code you write.

## What is the difference between a context window and memory?

A context window holds the tokens of one request, and memory holds whatever has to outlive that request. The model reads the first, and your application owns the second.

| | Context window | Memory |
|---|---|---|
| Lifetime | One request | Across requests and sessions |
| Who fills it | The code that builds the prompt | The code that writes to a store |
| What goes wrong | The needed fact isn't there, or the model doesn't use it | The wrong fact is stored, or an old one outlives the truth |

A model can answer perfectly in one request and know nothing about the exchange in the next. Nothing was forgotten, because nothing was kept.

## How does a chat app seem to remember?

It resends the conversation. Every earlier turn goes back into the context window with each new message, so the continuity you see is replay.

Replay has a price that's simple to count. The script below builds a 40-turn support conversation and counts what gets sent, using the `o200k_base` tokenizer from tiktoken 0.14.0:

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

The conversation contains 1,400 tokens of new text, and replaying it meant sending 28,020. At turn 40 a single message carries 1,383 tokens of history to deliver a question of about 18.

So replay works until it doesn't fit or costs too much, and then something has to choose what goes back in. [Memory compression](/articles/memory-compression/) is that choice, and it's the first step from replay toward a memory system.

## Does a bigger context window replace memory?

No, for two separate reasons. A window of any size is empty at the start of the next session, and a fact that fits in the window isn't guaranteed to be used.

The second reason has a paper behind it. [Lost in the Middle](https://arxiv.org/abs/2307.03172) moved the relevant passage around inside a long input and found that accuracy "significantly degrades when models must access relevant information in the middle of long contexts".

Suppose a contract fits in the window and the clause you need sits halfway through. The model accepted every page, and the paper's result says that clause sits where models did worst.

[RULER](https://arxiv.org/abs/2404.06654) put a number on the difference between accepted and usable. Its authors tested 17 long-context models that all claimed 32K tokens or more, and report that only half kept satisfactory performance at 32K.

Both papers measured the models of their day, so I wouldn't quote their figures against a current one. What I'd keep is the habit: test at the lengths and positions your own task will hit.

## What belongs in the context window, and what belongs in memory?

Ask how long the information has to survive. If only this request needs it, it goes in the context, and if a later request will need it, it gets stored outside the model.

A code change is a context job. The function, its tests and the instruction are all needed now, and none of them has to be remembered tomorrow.

A customer's plan is a memory job, and so are the client rules from that Hacker News question. They have to survive a new session, which means somebody decides what gets written and how it's found again.

That second list is longer than it looks. [AI memory management](/articles/ai-memory-management/) covers the policies for writing and expiring, and a vector search over old messages handles only the finding.

## Is the KV cache a kind of memory?

Not in this sense. The [KV cache](/articles/kv-cache-eviction/) stores the computation a model has already done over a run of tokens, so it can avoid doing it again.

It's the third thing people call memory, and the name hides where a fact was lost. A cached prefix makes a request faster, and it can't tell you what plan a customer is on.

## How do coding agents handle the split?

They write notes to files and read them back at the start of a session. That's memory in the plain sense used here, kept outside the window and loaded into it on purpose.

The details differ by tool. [Claude Code's memory](/articles/claude-code-memory/) and [memory in HyperAgents](/articles/hyperagents-memory/) are two worked cases, and the Hacker News thread is full of people building the same thing by hand with a wiki or a folder of Markdown.

I think that thread is the honest state of things. Windows have grown a great deal, and people still ended up writing things down.

## FAQ

**Is a longer context window always better?**

No. It helps a task that needs more evidence at once, and it also adds cost and gives the model more unrelated text to wade through.

**Does an LLM remember previous conversations?**

Not by itself. Each request starts with only what the application puts in the context window, so anything remembered was stored and sent again by the application.

**Can a vector database be the memory?**

It can be one part. Similarity search finds related passages, and facts like a user's identity or which version is current need structured fields and filters.

**Why does a model miss information that fits in its context window?**

Because fitting isn't the same as being used. Lost in the Middle showed that the position of a fact in a long input changes whether a model uses it.

**How do I decide between context and memory?**

Ask whether a later request will need the information. If it will, store it outside the model and decide how it gets retrieved.
