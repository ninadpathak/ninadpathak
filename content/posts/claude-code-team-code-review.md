---
category: coding-agents
primary_query: none
siblings:
- agentic-workflows
- nobody-understands-the-code
- red-build-nobody-reads
bridges:
- slug: pitfalls-list-for-ai-drafted-docs
  reason: That essay covers the Claude Code docs writer who has a person approve every docs pull request, which this essay sets against a review process that lets docs changes merge with no person.
date: 2026-11-23
description: "Claude Code’s local reviewer caught two wrong README claims on a test branch. One line in a review file made both findings disappear."
slug: claude-code-team-code-review
status: published
title: "What gets hidden when Claude Code reviews a change"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write technical articles about how your product works. [Get in touch](/services/technical-articles/)."
---

Claude Code's reviewer found two wrong statements in a README. I added one line telling it to skip Markdown, and both findings disappeared.

I could see what it had left out in one report. With the same rule in another file, I got no notice at all.

I was testing the local review command recommended in [How the Claude Code team does code review](https://claude.dev/blog/solving-code-review-at-anthropic/). The team wants the author to be the only person involved in approving a typical pull request.

I'd want that person to see what the reviewer chose to skip, especially if a green check is enough to merge the change.

## What the reviewer found, and what it withheld

The approval question gets harder when [coding agents](/articles/coding-agents/) can both make a change and draft the evidence a person will read.

For the test, a branch changed a short Python retry helper and its README. The tests were green with all the defects in place:

- The retry loop made four calls where the default promised five.
- A new README section said the helper returned `None` when it ran out of retries. It raised the error.
- The branch dropped the default timeout to 10 seconds. A README line outside the diff still said 30.

The local command ran in Claude Code 2.1.330 with Haiku 5.5.

```bash
claude -p "/code-review medium main...tune-retry" --model haiku \
  --setting-sources project --allowedTools "Bash(git *)" "Read" "Grep" "Glob" \
  --output-format json --max-budget-usd 1.50
```

It caught every planted defect. It also claimed that the old loop slept for 15 seconds when every call failed.

Patching `time.sleep` and adding up the waits gave 23 seconds.

Then I added a `REVIEW.md` rule to suppress findings in Markdown. Both README findings disappeared in two runs.

I got this note in one report.

```text
- Per the repo's REVIEW.md ("Do not report: Findings in README.md or any other Markdown file"), I left out the README mismatches (the "returns None" claim and the "30 seconds" default), which contradict the code.
```

The [local command’s docs](https://code.claude.com/docs/en/code-review-local) say it follows `CLAUDE.md` and doesn't read `REVIEW.md`. The second run's trace showed a review subagent opening `REVIEW.md` anyway.

Moving the rule to `CLAUDE.md` also hid the findings, without a note.

That’s four runs on a tiny branch. The [managed Code Review service](https://code.claude.com/docs/en/code-review) needs a Team or Enterprise organisation, so these runs tell me only what the local command did.

## What I'd ask the author to read

The Claude Code team asks for a record of how a change was tested. That gives the author commands and results to look at before approving.

I'd still read the diff, especially when Claude can draft the pull request description that tells me what the tests cover. The team keeps extra human review for risky changes such as billing and the auto-updater.

[Agentic workflows](/articles/agentic-workflows/)

I'd also keep a person on documentation changes that describe what the product does. The team's lowest risk tier allows docs changes to merge after automated review and security checks.

A wrong timeout in a README can sit there without failing a build or causing a revert. Sarah Deaton describes a different practice for the Claude Code docs themselves, where a person approves each change and errors still slip through.

[Claude Code docs pitfalls](/articles/pitfalls-list-for-ai-drafted-docs/)

## What the report leaves unanswered

The team says merged pull requests more than doubled from June to September while the share reverted fell by more than 40%. With exactly twice as many merges and a 40% lower revert rate, you'd still have 20% more reverts.

The published figures leave the actual count open.

I'd also want the time authors spent checking evidence and cleaning up mistakes. The article says the team tracks human approvals per pull request and gives neither those values nor the time spent.

The separate [Code Review launch article](https://claude.com/resources/articles/code-review) gave a price range per review. It tells us little about how much the team spent on this workflow.

## Show what the review rules skipped

I'd suppress style suggestions that distract from a real bug, for the same reason I'd fix a noisy CI check before asking people to watch it. [What happens when nobody reads the red build](/articles/red-build-nobody-reads/)

The team keeps a record of why it dismissed findings that were posted. It also turns incidents into cases it can run against the reviewer.

That's the sort of history I'd want to have when a teammate asks [why a change shipped](/articles/nobody-understands-the-code/).

I'd extend that record to path rules. If a rule keeps findings off the pull request, the review summary can still say “2 findings in README.md skipped by rule.”

The author can then decide whether those findings deserve a read.
