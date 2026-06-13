# Cluster 7 — AI Workflows & Automation (the hybrid expansion)

**Created:** 2026-06-14. Status: pillar live at `/ai-workflows/`, spokes below to be written.

## Why this cluster exists

The corpus (clusters 1–6) is deep on AI *infrastructure*: agent memory, RAG, inference
internals. That proves domain authority to an ML-engineer audience. But the brand goal is
to be the authority on **AI workflows, automation, speeding up work, and agentic workflow
setups** — a *practitioner / work-faster* audience (developers, technical founders, DevRel,
ops) who want to get real work done, not study the internals.

The hybrid play: keep the infra moat AND build this practitioner cluster, with the
`/ai-workflows/` pillar bridging into the infra hubs. The infra posts become the "proof of
depth" that makes the workflow advice credible. A reader who lands on "set up a coding
agent" is two clicks from the memory/architecture deep-dives that prove I actually know how
the thing works.

## Audience and intent

- **Who:** developers and technical founders adopting AI to ship faster; ops/DevRel
  building internal automation; people who already use Claude Code / Cursor / CLI agents and
  want them to work better.
- **Search intent:** "how to", "best setup", "X vs Y for coding", "automate Z with AI",
  "claude code workflow", "agentic workflow", "mcp server for". Higher commercial intent and
  higher volume than the infra long-tail.
- **Differentiator stays the same:** I run these workflows myself and show the real setup,
  real output, and what broke. No "10 ways AI will change everything" fluff.

## Keyword / head terms to own

agentic workflow, AI coding workflow, coding agent setup, automate with AI agents, MCP
server setup, AI workflow automation, Claude Code workflow, AI pair programming setup,
agent guardrails, AI for developer productivity.

## Existing posts already pulled into the pillar (adjacent spokes)

best-llms-for-coding, agentic-cli-benchmarks, how-memory-works-in-claude-code,
why-coding-agents-lose-their-memory, agent-harnesses, model-context-protocol-explained,
structured-outputs-llms-json-mode-function-calling, agent-vs-ai-assistant,
the-agent-design-space, multi-agent-vs-single-agent-tradeoffs, uv-package-manager-benchmark,
how-to-write-a-changelog-developers-actually-read, writing-release-notes-that-developers-trust.

These give the hub real content on day one. The briefs below are the *native* spokes that
make it a genuine cluster instead of a re-tag of existing infra posts.

## New post briefs (write in this order)

Priority = search demand × proof-of-practice value × how well it anchors the cluster.
Every post follows house rules: explicit `slug:`, 2–3 in-cluster internal links, a `## FAQ`
section (auto-becomes FAQPage schema), one visual, first-person, linter-clean. Tag every
post with `workflows` plus `automation`/`agents` so the related-footer and llms.txt cluster
grouping pick it up. Add `workflows` to the cluster tag map in `build.py:build_llms_txt`
once posts exist.

### Tier 1 — anchor the cluster (WRITTEN + published 2026-06-14)

1. **How I Set Up a Coding Agent That Actually Finishes the Task** — DONE
   - slug: `coding-agent-setup-that-works`
   - angle: real coding-agent setup end to end — rules file, repo context, tools,
     permissions, guardrails. Links to best-llms-for-coding, how-memory-works-in-claude-code,
     structured-outputs, agent-harnesses, why-coding-agents-lose-their-memory, agentic-workflow-playbook.
   - intent: "coding agent setup", "claude code workflow". High.

2. **The Agentic Workflow Playbook: From Prompt to Shipped PR** — DONE
   - slug: `agentic-workflow-playbook`
   - angle: the five-stage loop (frame, scope, work, review, land) to take intent to a
     shipped PR with an agent. Links to agent-loop-anatomy, multi-agent-vs-single-agent,
     agent-harnesses, why-ai-agents-keep-failing-in-production, the-agent-design-space.
   - intent: "agentic workflow". The head-term anchor for the cluster.

3. **Wiring Tools into Your Agent with MCP: A Practical Setup** — DONE
   - slug: `mcp-server-setup-guide`
   - angle: client-server shape, a minimal FastMCP server, tool design, connecting to an
     agent, guardrails. Links to model-context-protocol-explained, structured-outputs, agent-harnesses.
   - intent: "mcp server setup", "connect agent to tools". Rising, high.

All three are linter-clean, carry a `## FAQ` (FAQPage schema), a pure-CSS/SVG visual, and are
slotted into the `/ai-workflows/` pillar. Next up: Tier 2 (#4–7).

### Tier 2 — breadth and comparisons (high traffic)

4. **Claude Code vs Cursor vs CLI Agents: Which Setup for Which Work**
   - slug: `claude-code-vs-cursor-vs-cli-agents`
   - angle: comparison grounded in real runs (extends agentic-cli-benchmarks). Decision
     framework by task type. Links to agentic-cli-benchmarks, best-llms-for-coding.

5. **Guardrails for AI Automation: Letting Agents Act Without Breaking Things**
   - slug: `ai-agent-guardrails`
   - angle: permissions, sandboxing, dry-runs, observability. The "can I trust it" post.
     Links to production-ai-agent-errors, why-ai-agents-keep-failing-in-production.

6. **Automating Code Review with an AI Agent: What Works, What Doesn't**
   - slug: `automating-code-review-with-ai`
   - angle: a real review workflow, false-positive rate, where it helps vs noise.
     Links to ai-agent-guardrails, agentic-workflow-playbook.

7. **Multi-Agent Workflows: When Splitting the Job Actually Pays Off**
   - slug: `multi-agent-workflows-when-they-pay-off`
   - angle: practitioner framing of multi-agent (extends multi-agent-vs-single-agent-tradeoffs)
     with a concrete fan-out task and the wall-clock numbers.

### Tier 3 — applied automation (long-tail, conversion-adjacent)

8. **Drafting Release Notes from a Git Diff with an AI Agent**
   - slug: `ai-generated-release-notes-from-diff`
   - angle: end-to-end automation; bridges into the technical-writing cluster.
     Links to writing-release-notes-that-developers-trust.

9. **Automating Your Docs Pipeline with AI: Drafts Engineers Will Accept**
   - slug: `automating-docs-with-ai`
   - angle: AI-assisted doc drafting that passes engineering review. The clearest
     infra→workflow→service bridge. Links to technical-writing-for-ai-products, the-case-for-shorter.

10. **A Research Agent That Reads 20 Sources While You Work**
    - slug: `research-agent-workflow`
    - angle: build a fan-out research workflow, dedup, synthesize, cite. Links to
      agentic-workflow-playbook, rag-evaluation-metrics.

11. **Speeding Up Your Dev Loop with AI: The Boring Wins That Add Up**
    - slug: `ai-developer-productivity-wins`
    - angle: small, real automations (scaffolding, test stubs, refactors) with time saved.
      Links to coding-agent-setup-that-works, uv-package-manager-benchmark.

12. **Prompt and Context Files That Make Agents Reliable**
    - slug: `agent-context-files-that-work`
    - angle: CLAUDE.md / rules / context-file patterns that change agent reliability.
      Links to how-memory-works-in-claude-code, mcp-server-setup-guide.

## Conversion mapping (how the cluster sells)

Workflow readers have high commercial intent. Each post's CTA and at least one in-body link
routes toward the technical-writing pillar and the contact CTA: "I automate and document
these workflows for DevTools teams." The `/ai-workflows/` pillar already bridges to
`/technical-writing/`. Posts 8–9 are the explicit bridge from automation into the paid
writing service.

## Build/infra follow-ups when posts ship

- Add `workflows` to the cluster tag map in `build.py` `build_llms_txt()` so the cluster
  groups correctly in llms.txt.
- Add new slugs to the `/ai-workflows/` pillar sections as they publish.
- Each post: `## FAQ` section + `updated:` discipline on revisions (see [[seo-infrastructure]]).
