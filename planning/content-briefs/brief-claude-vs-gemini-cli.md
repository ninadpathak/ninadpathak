# Content Brief: Beyond the chatbox — Claude Code vs. Gemini CLI

**Topic**: Quantified head-to-head benchmark of autonomous repository refactoring
**Primary Keyword**: agentic CLI benchmarks
**LSI Keywords**: Claude Code vs Gemini CLI, autonomous file manipulation, SWE-bench verified, verified autonomy, agentic coding interfaces, repository-scale reasoning.
**Target Audience**: CTOs, AI Architects, Senior Software Engineers.
**Content Type**: Engineering Post-mortem / Benchmark Analysis.
**Word Count Target**: 3000+ words.

---

## Direct Answer for the Introduction
Claude Code and Gemini CLI have moved from simple chat interfaces to autonomous repository orchestrators. While both achieve ~80% on SWE-bench Verified, they diverge in execution philosophy: Claude Code uses "Supervised Autonomy" through parallel subagents, while Gemini CLI employs "Verified Autonomy" with its automated Conductor feedback loop. In my 16GB M2 Air benchmark, Claude Code excelled at ambiguous architectural refactors, while Gemini CLI won on large-scale system migrations and multimodal design implementation. The choice is no longer about model intelligence, but about the specific autonomous lifecycle you want to manage.

---

## The Experiment Setup (Hardware: M2 Air 16GB)

### Task 1: Ambiguous Refactor (The "Logic" Test)
- **Goal**: Refactor a legacy 10k LOC Node.js app to use Virtual Threads (simulated in JS) and resolve a hidden race condition.
- **Benchmark**: Success rate, tokens used, and number of self-correction loops.

### Task 2: System Migration (The "Scale" Test)
- **Goal**: Migrate a 50-file Python repo from Poetry to uv and update all CI/CD pipelines.
- **Benchmark**: Time to completion and context window stability.

### Task 3: Design-to-Code (The "Multimodal" Test)
- **Goal**: Take a screenshot of a UI bug and have the agent identify the CSS/Logic source and fix it.
- **Benchmark**: Accuracy of visual source identification.

---

## Planned Visuals (12+ assets)
1. **SVG Table: Head-to-Head 2026 Specs** (SWE-bench, Context, Cost).
2. **SVG Chart: Success Rate by Task Type** (Logic vs Scale vs UI).
3. **3D Visual: The Parallel Subagent Tree (Claude)** vs **The Verified Conductor Loop (Gemini)**.
4. **Screenshot: Claude Code's `plan.md`** for architectural changes.
5. **Screenshot: Gemini CLI's Conductor verification logs**.
6. **2D Graph: Memory Pressure (Activity Monitor)** during 1M token context usage.
7. **SVG Sequence Diagram: Autonomous File-System Manipulation**.
8. **Screenshot: Terminal output of a successful self-correction loop**.
9. **2D Chart: Tokens/sec vs Context Size** on 16GB Unified Memory.
10. **Screenshot: Multimodal bug identification (Gemini CLI)**.
11. **SVG Decision Tree: When to Escalate to Claude Opus 4.6**.
12. **SVG Table: ROI of Local Inference vs Cloud API for Agentic Loops**.

---

## Strict Writing Constraints
- **Title Case Titles / sentence case headings.**
- **NO Emdashes (—)**. Use commas or periods.
- **NO Semicolons (;)**.
- **No Contrastive Parallelism**: Avoid "not X but Y."
- **Tone**: Cynical, practitioner-first, Hacker News style.
- **Hardware Proof**: Real-time stats from the M2 Air (16GB).
