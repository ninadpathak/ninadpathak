---
title: "The HERMES.md Bug That Silently Burned $200 in Claude Code Credits"
date: 2026-04-30
description: "A case-sensitive string in git commit messages routes Claude Code API requests through extra usage billing instead of plan quota. Here is how it works and what it means for teams."
tags: [claude, anthropic, billing, devtools, bugs]
status: published
---

The bug report has a score of 995 on Hacker News. It describes something genuinely unsettling: a string of characters in a git commit message, `"HERMES.md"`, silently routes your API requests to Anthropic's extra usage billing instead of your included Max plan quota. The Max plan dashboard shows 86% of your weekly capacity untouched. Your actual requests still fail with "out of extra usage" because they were never touching that quota to begin with.

The issue was found by a developer who systematically binary-searched their git history to isolate the trigger. Here is what they found and why it matters for any team running Claude Code in CI or shared development environments.

## What the Bug Actually Does

When Claude Code sends an API request, it includes recent git commit messages in the system prompt. Something on Anthropic's server side reads that content and uses it as a routing signal. The exact trigger is the case-sensitive string `HERMES.md` appearing anywhere in a recent commit message.

The routing is binary and silent. Requests either go to your plan quota or to extra usage billing. There is no error, no warning, no indication in the Claude Code output that the routing decision was made based on commit message content. You only find out when your extra usage credits are gone and your plan quota sits at 13% consumed.

## The Minimal Reproduction

The reporter reduced it to a clean test case that requires no project files at all:

```bash
mkdir /tmp/test-fail && cd /tmp/test-fail
git init && echo test > test.txt && git add . && git commit -m "add HERMES.md"
claude -p "say hello" --model "claude-opus-4-6[1m]"
# => API Error: 400 "You're out of extra usage..."

mkdir /tmp/test-pass && cd /tmp/test-pass
git init && echo test > test.txt && git add . && git commit -m "add hermes.md"
claude -p "say hello" --model "claude-opus-4-6[1m]"
# => "Hello!"
```

The only difference is the casing of `hermes.md` in the commit message. Lowercase passes. The extension matters. `HERMES.txt` works. `HERMES` without an extension works. The specific sequence of characters `HERMES.md` in that exact case is the trigger.

What does not trigger it: a file named `HERMES.md` on disk with a clean commit message, the same string on an orphan branch with no history, or any other `.md` file name tested in isolation.

## Why This Is a Team-Level Risk

In isolation, a developer who accidentally types `HERMES.md` in a commit message will burn some extra usage credits. Painful but contained. The real exposure is in automated workflows and shared repositories.

If your team runs Claude Code in CI pipelines, every pull request that touches a repo with `HERMES.md` in its commit history will route to extra usage billing. Multiple projects can become unusable simultaneously once extra usage is depleted, even though the plan quota across all of them is largely untouched. The error message gives no indication that commit message content is the cause.

Any contractor, open source contributor, or automated tool that writes commit messages in a repository can introduce this trigger. You do not need to intentionally write `HERMES.md`. You need only to write it incidentally, and it propagates through the full git history of that repository.

The reporter estimated $200.98 in extra usage credits consumed for requests that should have been covered by their included Max 20x plan quota. For teams running multiple concurrent agents across many repos, the exposure scales with usage.

## What the Routing Mechanism Implies

The fact that commit message content influences billing routing suggests that Anthropic's server-side request handling uses content signals to determine which billing bucket a request belongs to. This is architecturally distinct from authentication and plan validation. Authentication confirms you are who you say you are. Plan validation confirms your plan includes the requested tier. Content-based routing is a third layer that operates on the actual prompt content.

This implies the routing decision is made after the prompt is constructed and before it is processed. The commit messages enter the system prompt. Something reads that content and flips a routing flag. That flag determines which billing infrastructure handles the request.

Whether this is intentional behavior with an undocumented trigger, a broken content filter that coincidentally matches `HERMES.md`, or a deliberate routing mechanism that uses arbitrary content signals is not clear from the outside. The issue was filed with Anthropic and they acknowledged it. The fix is their responsibility.

What is clear is that any LLM provider with usage-based billing has an economic incentive to route requests to the higher-margin bucket when possible. The bug manifests in the direction that benefits Anthropic. This does not mean the bug is intentional. It means the failure mode is directionally worse than random.

## What Teams Should Do Now

Audit your git history. If `HERMES.md` (exact case, with the extension) appears in any commit message in any repo where Claude Code runs, that repo is affected. The string does not need to be recent. Claude Code reads the full recent commit history, not just the last commit.

```bash
git log --all --oneline | grep -i "HERMES\.md"
```

If this returns results, those repos are routing to extra usage billing. Rebasing to rewrite the commit messages is the only client-side fix. `git filter-branch` or `git filter-repo` can rewrite history across all branches.

For CI workflows, audit what tools write commit messages in your repos. Any automated tool that generates commit messages with arbitrary content is a potential trigger vector. Consider constraining automated commit messages to a known-safe character set that excludes `.md` file name patterns.

If you have already burned credits you believe should have been covered by your plan, Anthropic's support team has been responsive to these reports according to the HN thread. The bug is acknowledged. Disputed charges have been credited in at least some cases.

## The Deeper Problem

Billing systems that route based on prompt content are fragile in ways that are difficult to audit from the client side. You can observe the outcome, but you cannot observe the decision mechanism. When the decision mechanism produces counterintuitive results, like a plan quota sitting at 13% while requests fail with out-of-credits errors, diagnosing the cause requires access to server-side routing logs that only Anthropic can see.

The routing should be determined by the authenticated identity and the plan associated with that identity. Not by content that happens to appear in a system prompt assembled from git history. If Anthropic's infrastructure is making routing decisions based on prompt content, that is a separation of concerns violation at the billing layer. The billing bucket should be determined before the prompt is constructed, based on the API key and plan, not after.

This is the same class of problem as prompt injection attacks that manipulate downstream system behavior through crafted input. The defense is proper input sanitization at the routing layer, not content-based routing decisions that can be influenced by arbitrary text in the prompt.

I have written before about [how Claude Code manages memory across sessions](/articles/how-memory-works-in-claude-code/) and the complexities of [token budgeting in LLM cost control](/articles/llm-token-budgets-cost-control/). This bug is a reminder that the boundary between prompt content and system behavior is thinner than it appears, and billing systems are not exempt from that boundary being violated.

---

*If you found this useful, you might also want to read about [semantic caching strategies for RAG optimization](/articles/semantic-caching-rag-optimization/) or [structured outputs and JSON mode in LLM APIs](/articles/structured-outputs-llms-json-mode-function-calling/).*
