---
category: agent-memory
primary_query: shared memory multi agent
siblings:
- ai-memory-management
- context-windows-vs-memory
- memory-serialization
bridges:
- slug: multi-agent-vs-single-agent
  reason: Whether agents share memory only matters once a task has more than one agent, which that page weighs.
- slug: agent-error-handling
  reason: A rejected write to a shared store is an error the orchestrator has to handle.
date: '2026-05-11'
description: 'Shared memory lets every agent in a multi-agent system read one store. Isolated memory passes artifacts between them. What OpenAI''s Agents SDK and Claude Code do by default, and a lost-update run.'
slug: shared-vs-isolated-memory
status: published
work_note: "I'm Ninad Pathak, and I freelance as a technical writer for AI companies. I build the example and run it before I draft a tutorial, so your engineers review working code. [Here's how we'd work together](/services/freelance-technical-writer-for-ai-companies/)."
title: Shared Memory vs Isolated Memory in Multi-Agent Workflows
updated: 2026-11-17
---

Shared memory in a multi-agent system means every agent reads and writes one common store. Isolated memory means each agent keeps its own context and passes a finished artifact to the next, and that's the safer default.

Go programmers have a line for this choice. Andrew Gerrand's 2010 post on the Go blog is titled with its second half, [Share Memory By Communicating](https://go.dev/blog/codelab-share), and the first half is "Do not communicate by sharing memory".

Agents aren't goroutines, and a model can't take a lock. But two agents writing to one store can lose each other's work in the way two threads can, and the run further down shows it.

The choice only comes up once a system has more than one agent, and it's one of the later ones in [AI agent memory](/articles/agent-memory/).

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/shared-vs-isolated-memory/memory-architectures.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/shared-vs-isolated-memory/memory-architectures.narrow.svg" width="288" height="1120"><img class="np-has-narrow" src="/static/images/diagrams/shared-vs-isolated-memory/memory-architectures.svg" width="720" height="640" alt="Two pipelines of the same three agents. In isolated memory the extractor hands its output to the validator, which hands its output to the summary agent, and nothing else passes between them. In shared memory all three use one common store: the extractor writes to it and the validator and summary agent read from it, so the validator can act on a conclusion the extractor later revises, marked as a failure on the store." loading="lazy" decoding="async"></picture></a>
  <figcaption>Isolated memory passes artifacts along the line. Shared memory lets every agent read what any agent wrote, including drafts.</figcaption>
</figure>

## What is the difference between shared and isolated memory?

The difference is where coordination lives. With isolated memory it lives in the pipeline: an orchestrator hands each agent an input, and the agent's output is the only thing the next one sees.

With shared memory it lives in the store. Any agent can look up what any other agent wrote, drafts included, so the order of writes starts to matter.

So isolated memory gives you a record of exactly what each agent saw, which is what you need to explain or debug a decision afterwards. Shared memory gives each agent more to work with, and makes that record harder to rebuild.

## What do agent frameworks do by default?

They offer both, under other names. OpenAI's Agents SDK has two ways to bring in a second agent, and they differ on exactly this point.

A handoff shares. The [handoffs documentation](https://openai.github.io/openai-agents-python/handoffs/) says the new agent "gets to see the entire previous conversation history", unless you pass an input filter to trim it.

An agent used as a tool is isolated. The manager agent keeps the conversation and calls the specialist for a bounded subtask, so the specialist sees only what it's handed.

Claude Code's subagents are the isolated kind as well. Each runs in its own context window and returns a summary to the main conversation.

## What goes wrong with shared memory?

A pair of agents read the same value, both write, and one write disappears. Databases call it a lost update, and a shared agent store has no defence against it unless you build one.

The script below has an extractor and a validator read one note, then write to it in turn. It runs once with no check and once with a version check on each write.

```python
"""Two agents update one shared note. Run it with and without a version check."""


class SharedStore:
    def __init__(self):
        self.value, self.version = "amount: 1200", 1

    def read(self):
        return self.value, self.version

    def write(self, value, seen_version, check):
        if check and seen_version != self.version:
            return False                      # someone wrote since this agent read
        self.value, self.version = value, self.version + 1
        return True


def run(check):
    store = SharedStore()
    extractor_view = store.read()             # both agents read version 1
    validator_view = store.read()
    store.write("amount: 1250 (corrected by extractor)", extractor_view[1], check)
    accepted = store.write(validator_view[0] + " | validated", validator_view[1], check)
    return store.value, accepted


for check in (False, True):
    value, accepted = run(check)
    print(f"version check {'on ' if check else 'off'}: final note = {value!r}; validator's write accepted: {accepted}")
```

`python3 shared_memory_demo.py` prints the two outcomes.

```text
version check off: final note = 'amount: 1200 | validated'; validator's write accepted: True
version check on : final note = 'amount: 1250 (corrected by extractor)'; validator's write accepted: False
```

With no check, the validator stamped "validated" on the amount it had read, and the extractor's correction to 1250 was gone. With the check, the stale write was refused and the correction survived.

A refused write is the better failure, since something now knows there was a conflict. What the orchestrator does about it is a question for [error handling](/articles/agent-error-handling/).

The other shared-memory failure is a stale read. An agent acts on a draft another agent later revises, and nothing in its output says which version it used.

## What goes wrong with isolated memory?

Information gets left behind. If the extractor notices a caveat and the artifact has no field for it, the summary agent two steps later never hears of it.

The fix is a contract for the artifact, with a place for caveats and a version number. [Memory serialization](/articles/memory-serialization/) covers how to write state down so another process can read it back.

A retry causes the other failure. If the extractor reruns and corrects a field after the validator has finished, the validator's verdict describes an artifact that no longer exists.

## When should agents share memory?

Share when agents work at the same time on parts of one problem and a finding from one should stop another. A research task split across several agents is the usual case, since one agent's dead end saves the others the trip.

Even then I'd share less than everything. Keep each agent's working notes private, and let agents read a common store of confirmed facts that only the orchestrator writes to.

That gives every write one author and one order. It also keeps other agents' drafts out of each context window, which matters for the reasons in [context windows vs memory](/articles/context-windows-vs-memory/).

And check first that the task needs several agents at all. [Multi-agent vs single-agent systems](/articles/multi-agent-vs-single-agent/) goes through what the extra agents cost.

## How do you decide?

Ask three questions in order.

1. Do the agents run one after another? If so, pass artifacts and keep memory isolated.
2. Do they run at once and need each other's findings? If so, add a shared store for confirmed facts, with one writer.
3. Does any agent need another's drafts? If it does, they're probably one agent, and the split is costing you.

Whatever you choose sits inside the larger design of what the system remembers, which [AI memory management](/articles/ai-memory-management/) lays out in layers.

## FAQ

**What is shared memory in a multi-agent system?**

It's a store that every agent can read and write, such as a database or a message log. Agents coordinate through what's in the store.

**Is shared or isolated memory better for multi-agent workflows?**

Isolated memory is the safer default, because each agent's input is a known artifact you can replay. Shared memory is worth its cost when agents work at once and need each other's confirmed findings.

**How does shared versus isolated memory affect explaining an agent's decision?**

With isolated memory you can explain a decision from one artifact, the input that agent was handed. With shared memory you also need the state of the store at the moment the agent read it.

**How do you stop agents overwriting each other in shared memory?**

Give each record a version and refuse a write based on an old one, or route every write through a single orchestrator.
