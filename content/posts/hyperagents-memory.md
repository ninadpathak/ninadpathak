---
category: agent-memory
primary_query: hyperagents memory
siblings:
- short-term-agent-memory
- memory-versioning
- ai-memory-management
bridges:
- slug: claude-code-memory
  reason: Claude Code is a shipped product that also keeps agent-written notes in plain files.
date: 2026-04-19
description: 'HyperAgents memory was written by the agent itself: a key-value JSON store printed in the paper. This page runs it and shows what it keeps and omits.'
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer for AI companies that build agents, agent memory and LLM infrastructure. I write their tutorials and technical articles, and I run each product before I write about it. [Let's work on yours](/services/freelance-technical-writer-for-ai-companies/)."
title: How Memory Works in HyperAgents
slug: hyperagents-memory
updated: 2026-11-17
---

Nobody on the research team designed the memory system in HyperAgents. The [paper](https://arxiv.org/abs/2603.19461), first posted on March 19 and revised on November 1, reports that the agent wrote one for itself: "Without explicit instruction to do so, the agent creates mechanisms for storing and retrieving insights across sessions."

Jürgen Schmidhuber proposed the [Gödel machine](https://en.wikipedia.org/wiki/G%C3%B6del_machine) in 2003, which Wikipedia describes as a program that "rewrites its own code when it can prove the new code provides a better strategy". The system in this paper descends from it by way of the Darwin Gödel Machine.

So what does a self-rewriting agent build when it wants to remember something? The paper prints one answer in [its appendix](https://arxiv.org/html/2603.19461v1), a short Python class that keeps notes in a JSON file, and in this article I'll run it and look at what the agent chose to build as its own [AI agent memory](/articles/agent-memory/), and what it left out.

That link goes to the March version, the only one arXiv renders as a web page, and the section reads the same in the November PDF.

## What is a hyperagent?

A hyperagent is a program made of two agents that can both be edited. The abstract defines the pair as "a task agent (which solves the target task) and a meta agent (which modifies itself and the task agent)".

The meta agent's own procedure is open to change as well, so the system can improve how it improves. The authors, with Jenny Zhang as first author and the work done at Meta, build it on the Darwin Gödel Machine and call the result DGM-H.

Memory comes into the paper as one of the things the meta agent gave itself. The abstract lists "persistent memory, performance tracking" among the improvements the system made to its own process.

## What memory did the agent build?

It built a key-value store with a timestamp on each entry. The class below is the one printed in Appendix E.3.7, with a loader added, since the paper doesn't print that method.

```python
"""The MemoryTool printed in Appendix E.3.7 of the Hyperagents paper, run on a temp file.

The class body is the paper's. _load_memory is not printed there, so the
version below is mine, as are the three calls at the bottom.
"""
import json
import os
import tempfile
from datetime import datetime
from typing import List, Optional


class MemoryTool:
    """Tool for persistent memory storage across agent interactions."""

    def __init__(self, memory_file: str = './memory.json'):
        self.memory_file = memory_file
        self.memory = self._load_memory()

    def _load_memory(self) -> dict:  # not shown in the paper
        if os.path.exists(self.memory_file):
            with open(self.memory_file) as f:
                return json.load(f)
        return {}

    def store(self, key: str, value: any) -> None:
        """Store information with timestamp for temporal tracking."""
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._save()

    def retrieve(self, key: str) -> Optional[any]:
        """Retrieve stored information by key."""
        return self.memory.get(key, {}).get("value")

    def list_keys(self) -> List[str]:
        """List all stored memory keys."""
        return list(self.memory.keys())

    def _save(self):
        """Persist memory to disk."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)


path = os.path.join(tempfile.mkdtemp(), "memory.json")

first = MemoryTool(path)
first.store("best_generation", "Gen55: 63% accuracy, too harsh")
first.store("best_generation", "Gen64: 61% accuracy, best balance")
first.store("gen66_results", "52% accuracy, worse than gen64")

second = MemoryTool(path)  # a new process would start here
print("keys after reload:   ", second.list_keys())
print("best_generation:     ", second.retrieve("best_generation"))
print("unknown key:         ", second.retrieve("gen55_results"))
print("entries on disk:     ", len(json.load(open(path))))
```

The three `store` calls and the reload at the bottom are mine, and so is the choice to reuse a key. `python3 hyper_memory.py` gives this.

```text
keys after reload:    ['best_generation', 'gen66_results']
best_generation:      Gen64: 61% accuracy, best balance
unknown key:          None
entries on disk:      2
```

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/hyperagents-memory/memory-layers.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/hyperagents-memory/memory-layers.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/hyperagents-memory/memory-layers.svg" width="720" height="256" alt="A meta agent calls a MemoryTool that it wrote for itself. The tool saves each insight under a key in a memory.json file, and the next generation of the agent consults that file when it modifies itself." loading="lazy" decoding="async"></picture></a>
  <figcaption>The hyperagent's memory is one JSON file, written through a tool the agent added to its own code.</figcaption>
</figure>

The reload works, which is all persistence means here: a second instance reads the file and finds the notes. The paper's description of the real file is "structured storage of performance insights", and the entries it prints are paragraphs of analysis filed under keys such as `best_performers_analysis`.

## What does the agent write down?

It writes conclusions and leaves the raw numbers to the logs. The authors make the distinction themselves: "Instead of merely logging numerical scores, the hyperagent stores synthesized insights, causal hypotheses, and forward-looking plans".

A printed entry records that a later generation scored worse and names the cause, in the agent's words: "gen65 changes over-corrected." Another sets a plan for the next attempt.

Why does that matter? Because raw scores can be read again from the logs, and a conclusion exists only if somebody writes it down.

A summary can drop it just as a missing note can, the failure [short-term agent memory](/articles/short-term-agent-memory/) describes for compaction.

## What did the agent leave out?

Everything a memory system grows later, starting with history. My run stores two notes under `best_generation`, and the second replaces the first with no trace that Gen55 was once the answer.

Now, the agent's own file avoids that, and it's worth seeing how. Each event in the printed entries gets a key of its own, such as `gen66_results`, so the naming does the work the class doesn't.

But a convention can be broken by one careless call, and an overwrite with no history is the design that [memory versioning](/articles/memory-versioning/) argues against, since nobody can ask later what the agent believed at an earlier point. The timestamp records when the surviving value was written and nothing about the one it replaced.

The class also has no way to search. `retrieve` needs the exact key, and `list_keys` returns every key, so recall depends on the agent choosing names it will recognise later.

Nothing is forgotten on purpose either, and the whole file is rewritten on every `store`. Neither matters at the scale of the runs the paper reports, and both would in a system that ran for months.

## Does the memory make the agent better?

The paper credits it with part of the gain and doesn't isolate it. Its transfer experiment moves a trained hyperagent to a new domain, and the authors write that "the transfer hyperagents have features such as performance tracking and persistent memory", which they call a qualitative attribution.

The measured result is about the meta agent as a whole.

Moving only the meta agent to the new domain scored 0.620 on the paper's improvement measure against 0.630 for moving both agents. Moving only the task agent scored 0.100, with a confidence interval the paper gives as 0.0 to 0.560.

So the evidence says the self-improvement machinery transfers, and that memory is one visible part of that machinery. A claim that the memory file alone caused the gain would go past what the paper shows.

## What should a builder take from it?

Start with less than the frameworks offer. An agent that could have written anything wrote a class of 22 lines and a JSON file, and that was enough for its notes to shape the next generation.

The omissions are the list of what to add when the simple version stops being enough: history, search and forgetting. Those layers are laid out in [AI memory management](/articles/ai-memory-management/), and [Claude Code's memory](/articles/claude-code-memory/) is a shipped product that also keeps its notes in plain files.

## FAQ

**Does HyperAgents ship with a memory system?**

No. The public repository holds the starting agents with two tools, for shell commands and file edits, and the memory tool exists only in the paper's appendix and its experiment logs.

**Where does a hyperagent store its memory?**

In the printed example, in a `memory.json` file in the working directory. Each key holds a value and the time it was written.

**Is HyperAgents the same as the Darwin Gödel Machine?**

It extends it. The paper's system, DGM-H, adds a meta agent whose own improvement procedure can be edited.
