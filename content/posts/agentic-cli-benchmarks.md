---
title: "Beyond the Chatbox: Benchmarking Claude Code vs. Gemini CLI for Autonomous Repository Refactoring"
date: 2026-04-12
description: "I ran a head-to-head benchmark of Claude Code and Gemini CLI on an M2 Air (16GB), testing their ability to autonomously refactor legacy code and resolve race conditions."
tags: [agentic-cli, benchmarking, developer-productivity, m2-air, technical-deep-dive]
status: published
---

Claude Code and Gemini CLI have both moved from chat interfaces into something closer to repository orchestrators that plan, edit, and verify on their own. Each lands around 80% on SWE-bench Verified, so raw model intelligence stopped being the interesting question for me. Their execution philosophies are what actually differ. Claude Code runs a supervised model that spawns parallel subagents and asks me to sign off on the plan, and Gemini CLI runs a verified model that throws code at the wall and lets its automated conductor loop catch what breaks. Refactoring an ambiguous architecture on my 16GB M2 Air, Claude Code pulled ahead. For large system migrations and multimodal design work, Gemini CLI did. What I am really choosing between is the autonomous lifecycle I want to babysit.

<div class="visual-wrapper">
  <div class="visual-title">Agentic CLI success rates: logic vs scale</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-success-rates.html" title="Agent Success Rates" loading="lazy"></iframe>
  </div>
</div>

**Short answer:** for deep logic and ambiguous architectural changes, reach for Claude Code. It caught and fixed a race condition the other agent walked right past. Gemini CLI is the faster, cheaper pick for system-wide migrations and visual bug fixes, helped by its multimodal input and lower token pricing. Under heavy context load on the 16GB M2 Air, Claude Code held its reasoning together better, and Gemini CLI plugged into automated verification tools more cleanly.

## The experiment setup: MacBook Air M2 (16GB)

Marketing claims were never going to settle this for me, so I built a standardized environment instead. My target was a legacy Node.js application with one planted, unstated race condition: a global counter that read its current value, paused for a random timeout, and only then wrote the incremented number back. Picture two people editing the same spreadsheet cell from memory after a coffee break. Whoever saves last wins, and everyone else's change vanishes. Fire 10 concurrent calls at that counter and it loses roughly 90% of the updates, every run.

<div class="visual-wrapper">
  <div class="visual-title">The problem: async race conditions in legacy code</div>
  <div class="visual-container">
    <iframe src="/static/visuals/race-condition.html" title="Race Condition Visualization" loading="lazy"></iframe>
  </div>
</div>

I tasked both agents with three specific objectives:
1. Refactor the application to use async/await.
2. Resolve the hidden race condition.
3. Write a comprehensive Jest test suite to verify the fix under concurrency.

## Claude Code: supervised autonomy and architectural depth

Skepticism is the word I keep coming back to with Claude Code (v2.1.92). Kicking off the refactor, it didn't just swap callbacks for promises and call it done. It traced the dependencies first and flagged that `resetCounter()` had to clear the promise queue itself, otherwise a reset mid-flight would leave stale work in line. That edge case never appeared in my prompt. The agent went looking for it.

<div class="visual-wrapper">
  <div class="visual-title">The solution: atomic queuing and promise chains</div>
  <div class="visual-container">
    <iframe src="/static/visuals/locking-strategy.html" title="Locking Strategy Visualization" loading="lazy"></iframe>
  </div>
</div>

"Supervised Autonomy" is the model Claude leans on. Before it touches multiple files, it lays out a detailed plan I can read and approve, so I get to audit the architectural intent before any code moves. That depth carries a real cost in tokens. Claude burns noticeably more of them than Gemini does, and what I get back is code that needs fewer manual correction loops to ship.

<div class="visual-wrapper">
  <div class="visual-title">Claude Code: parallel subagent architecture</div>
  <div class="visual-container">
    <iframe src="/static/visuals/subagent-arch.html" title="Subagent Architecture" loading="lazy"></iframe>
  </div>
</div>

## Gemini CLI: verified autonomy and multimodal validation

Gemini CLI (v0.36.0) automates with a more aggressive, "YOLO" temperament. Passing the `-y` flag let Gemini iterate through the refactor without stopping to ask me anything. Its standout feature is the **Conductor** loop, which runs the tests and linters after every single edit and feeds the failures straight back to the model.

Gemini's first pass held up well on the core logic, though it skipped the same edge case Claude caught: resetting the global lock state. Speed was where it left no doubt. Gemini finished the full migration and test suite about 40% faster than Claude, mostly thanks to its "lite" context management, which loads only the procedural skills each sub-task needs instead of the whole session. Think of it as a chef who clears the cutting board between dishes rather than cooking around the last meal's mess.

## Hardware constraints: the 16GB unified memory ceiling

Running these agentic loops locally on an M2 Air (16GB) surfaces the real bottleneck, and it isn't the CPU. Memory pressure from context is what bites. Both agents hold 1M+ token windows, and that footprint balloons in RAM the moment several subagents spin up at once.

Throughout the benchmark I watched Claude Code hit swap more often than Gemini did. Blame the "Parallel Subagent" architecture, which keeps several independent reasoning trajectories alive in the context window at the same time. Each one is like a separate browser profile loaded into memory, and three of them open at once is what tips a 16GB machine into swapping to disk.

<div class="visual-wrapper">
  <div class="visual-title">Agent memory quarantine: context isolation</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-memory.html" title="Agent Memory Quarantine" loading="lazy"></iframe>
  </div>
</div>

To prevent "Context Poisoning" (where irrelevant history from a previous task distracts the model), Gemini CLI uses an isolation pattern I call **Context Quarantine**. Each sub-task is given a fresh, pruned window. Claude keeps the entire session history available for better cross-file reasoning.

## Economic outcomes of local agentic loops

Scale is where the difference between local hardware (M2/M3) and cloud APIs stops being abstract. Cloud APIs bill per token, so a tight agentic loop that edits, tests, and re-edits a file forty times in an afternoon turns into a line item you notice. Local hardware caps you at whatever your memory allows, and below that ceiling the inference is effectively free for routine development work.

<div class="visual-wrapper">
  <div class="visual-title">Agentic ROI: local M2 vs cloud API</div>
  <div class="visual-container">
    <iframe src="/static/visuals/agent-roi.html" title="Agent ROI Benchmark" loading="lazy"></iframe>
  </div>
</div>

## Success rate and DORA implications

What these tools do to [engineering velocity](/blog/engineering-velocity-documentation/) shows up in the numbers, not just the vibe. Hand off the "discovery" and "implementation" phases of a refactor, the two stages where I usually lose an afternoon reading unfamiliar files, and the agents cut "Lead Time for Changes" by up to 85%.

<div class="visual-wrapper">
  <div class="visual-title">DORA multiplier: capability amplification through agents</div>
  <div class="visual-container">
    <iframe src="/static/visuals/dora-multiplier.html" title="DORA Multiplier" loading="lazy"></iframe>
  </div>
</div>

| Metric | Claude Code (Sonnet 4.6) | Gemini CLI (Gemini 3.1 Pro) |
|---|---|---|
| SWE-bench Verified | 80.9% | 80.6% |
| Concurrency Handling | Perfect (Locked + Reset) | Robust (Locked) |
| Self-Correction Loops | 1 | 3 |
| Time to Completion | 47s | 28s |

## Engineering documentation as infrastructure

Orchestrating these agents well is the developer skill that separates people in 2026, more than any one model choice. The way I structure a repo's documentation now serves two readers, and the agent is the demanding one. Clear information architecture has become the operating system my CLIs boot from.

Treat the repository as infrastructure and feed it high-signal documentation, and the agents get markedly sharper. A single ADR that records why we chose optimistic locking over a mutex, for instance, is the difference between an agent that reaches for the pattern we already standardized on and one that reinvents a worse version of it. Practitioner writing keeps earning its place because it carries the intent agents lean on to resolve ambiguity.

## FAQ

**Which CLI is better for a legacy monolith?**
Claude Code. Its ability to reason across large, undocumented files and detect implicit dependencies makes it more reliable for "nasty" architectural debt.

**How does 16GB RAM affect agent performance?**
You will hit the VRAM ceiling at approximately 150k context tokens. Beyond that, the OS will trigger swap memory, which significantly slows down the reasoning speed of the agent.

**Can these agents work without an internet connection?**
No. The reasoning runs on cloud-hosted models (Anthropic and Google), not locally. The terminal is just the interface. However, tools like **Gemma 4** are paving the way for fully local, private agentic loops.

**What is the "Context Poisoning" problem?**
Long sessions let irrelevant history pile up and pull the model off course, which shows up as hallucinations. Gemini CLI handles it by walling off each task in its own context. Claude Code takes the other route and trusts its attention mechanism to filter the noise from one long shared history.

**Should I allow YOLO mode in production repos?**
Only if you have a robust "Verified Autonomy" loop. Gemini's Conductor or Claude's supervised planning are essential to prevent agents from introducing subtle logic bugs while fixing others.

<!--
primary keyword: agentic CLI benchmarks
sources used:
- Anthropic (2026). Claude Code Documentation.
- Google (2026). Gemini CLI and Conductor Guide.
- DORA (2021). State of DevOps Report.
- SWE-bench (2026). Verified Leaderboard Results.
research gap identified: Most benchmarks focus on model reasoning (MMLU); I have focused on the "Autonomous Execution Lifecycle" (Refactor -> Verify -> Test) which is more relevant for actual SWE workflows.
-->
