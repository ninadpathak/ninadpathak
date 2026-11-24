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
description: "Anthropic's post on code review for Claude Code leaves a person evidence to read on an ordinary change, in place of the diff. On a branch with three planted defects, /code-review caught all three, and a one-line skip rule hid two."
slug: claude-code-team-code-review
status: published
title: "What the Claude Code team's code review leaves a person to read"
work_note: "Behind this essay are three planted bugs and four runs of the review command on a scratch repository. I'm Ninad Pathak, a freelance technical writer for AI companies, and I write tutorials and technical articles the same way, on a product I've run myself. [Ask me about yours](/services/freelance-technical-writer-for-ai-companies/)."
---

On October 15, Addy Osmani and two co-authors published [How the Claude Code team does code review](https://claude.dev/blog/solving-code-review-at-anthropic/) on the claude.dev blog, and by November 23 it had 488 points [on Hacker News](https://news.ycombinator.com/item?id=50122951). The post's goal is for a majority of pull requests in the Claude Code repositories to merge with no more than "one human in the loop, who can be the author".

My earlier essays borrowed the post's headline figures twice, and neither asked what that one person reads. Review is the step where a person checks the work of [coding agents](/articles/coding-agents/), so on November 23 I read the post against Claude Code's documentation and ran the review command it recommends.

I think the post leaves a person the right thing to read on an ordinary change, which is the evidence that the change works. I'd also put a person on every documentation change, which the post's process doesn't require, and I'd make the reviewer report the findings it withholds.

## A person reads the evidence that a change works

The post lists reading the evidence among the jobs people keep, and its examples include the command that ran and what it returned. People on the team still review risky code such as billing and the auto-updater.

My [agentic workflows](/articles/agentic-workflows/) page says to review the diff, because a summary reports what the agent believes it did. Test output is different from a summary, since something had to run to produce it.

I'd still have the author read the diff, because the post says Claude can fill in the pull request template that records how a change was tested. The post has the person who asked for the change sign off on that template and counts them as a required reviewer, without saying whether they read the code.

The post tells an approver who can't say what the checks would miss to "ask for a real review rather than a quick approval", and I'd put that sentence in your pull request template.

A Hacker News commenter, RGS1811, [objected on October 16](https://news.ycombinator.com/item?id=50124069) that a person who hasn't worked in the code can't judge a complex diff. I think that's right, and it matters on the highest-risk code, where the post still requires two people to approve.

## The post prints no figure for human time

The post's goal is less human review time, and it prints no number for that time. It says the team tracks human approvals per pull request at the median and the 95th percentile, and neither value appears.

Its headline pair is that merged pull requests more than doubled from June to September while the share that had to be reverted fell by more than 40 percent, and the post gives no starting share. Take the lowest figures that wording allows, exactly twice the pull requests and a reverted share exactly 40 percent lower.

Reverted pull requests then come to 1.2 times the June count, because 2 times 0.6 is 1.2. Larger figures could move that count either way, so the two figures can't show whether the team reverts fewer changes than it did in June.

That count matters because the post itself treats the time people spend fixing what bad code breaks as part of review's cost.

Anthropic is describing its own product here, and the post's checklist for other teams names Code Review, which is billed by token on Team and Enterprise plans. The [March 9 launch article](https://claude.com/resources/articles/code-review) put an average review at fifteen to twenty-five dollars, and the October post never says what its own reviews cost.

## Docs changes need a person

I wouldn't let a documentation change merge without a person reading it, and the post's risk table does. The lowest of its risk tiers lists docs first and requires no human approval once the automated review and the security checks are green.

The same post says a good `REVIEW.md`, the file that tells the reviewer what matters in one repository, defines failure for docs as "it lies". A false sentence in the docs breaks no build and causes no revert, so the revert rate and the incident rate, which the post calls its guardrail, can't register one.

For the same reason a false sentence never joins the set of past incidents that the team reruns the reviewer against daily.

Sarah Deaton, who works on the Claude Code docs at Anthropic, said on a podcast Tom Johnson published on August 2 that a person approves each docs pull request before it merges and that errors have still slipped through. [My comparison of pitfalls lists](/articles/pitfalls-list-for-ai-drafted-docs/) covers that episode, and the October post doesn't say whether its lowest tier includes those pages.

A commenter, koolba, [objected to that row](https://news.ycombinator.com/item?id=50124042) on October 16, and I agree for any sentence that states what the product does. That row also lists additive changes behind a feature flag, which I'd leave there, since the benchmark in my essay on [new code versus change](/articles/coding-models-new-code-vs-change/) had models adding features far more reliably than they changed code without breaking it.

## What the local review command caught on a planted branch

The local `/code-review` command caught every planted defect on its first run. The post tells teams to run it before a pull request, so the command ran with Claude Code 2.1.330 on a scratch repository that holds a 17-line Python retry helper with a README and its tests.

The branch under review carries three planted defects, and the three tests pass with all of them in place:

- The retry loop starts at 1, so the helper makes four calls where its default promises five.
- A new README section says the helper returns `None` after the last failed call, and the code raises the error.
- The default timeout drops to 10 seconds from 30, and a README line outside the diff still says 30.

```bash
claude -p "/code-review medium main...tune-retry" --model haiku \
  --setting-sources project --allowedTools "Bash(git *)" "Read" "Grep" "Glob" \
  --output-format json --max-budget-usd 1.50
```

Haiku 5.5 returned six findings in about 25 seconds, and they covered the off-by-one and both README defects. A finding among the six said the old loop waited 15 seconds in total when every call fails, and when I patched `time.sleep` and summed the waits, the old loop slept for 23.

So the reviewer's findings, which the post asks a person to read as evidence, need checking like any other draft.

The post says good review files list paths to skip, so I added a `REVIEW.md` with one rule, to report no findings in `README.md` or any other Markdown file. Both README findings disappeared in two runs out of two, and one of the two reports ended with this note:

```text
- Per the repo's REVIEW.md ("Do not report: Findings in README.md or any other Markdown file"), I left out the README mismatches (the "returns None" claim and the "30 seconds" default), which contradict the code.
```

Claude Code's [page for the command](https://code.claude.com/docs/en/code-review-local) says it follows `CLAUDE.md` and doesn't read `REVIEW.md`. The tool trace from the second of those runs shows the review subagent running `cat REVIEW.md` unprompted, and with the same rule moved to `CLAUDE.md` the README findings were gone with no note.

Those are four runs of one model on a diff of six added and two removed lines, so they give no rate. I couldn't run the managed Code Review service, which needs a Team or Enterprise organisation, and [its docs](https://code.claude.com/docs/en/code-review) say a review there works without building or running the code.

## The record keeps only the findings that survived

I think this process writes down more about how a change shipped than a colleague's approval did, and it keeps nothing about what the reviewer dropped. A posted finding has to be fixed or closed with a reason, and the team turns each incident into a test case that engineers confirm.

That's the record of how things shipped that [my essay on code nobody understands](/articles/nobody-understands-the-code/) said a team should keep writing.

The reviewer posts a finding only when enough verifying agents vote for it, and it discards findings that are only about style or cleanup. <!-- evidence-three: the post's list of re-review changes has a round cap that begins "After three rounds" --> Dropping those is the rationing I argued for in [my essay on a build that is always red](/articles/red-build-nobody-reads/), and the post has a figure for it, with pull requests that passed after one round of review up to 78% from 65% after changes that include a cap of three rounds.

<!-- evidence-three: the skip rule ran three times in the section above (twice in REVIEW.md and once in CLAUDE.md) and one of those reports carried a note --> But my one-line rule removed two true findings, and two of the three reports written under it gave no sign that anything was withheld. I'd have the review summary count what its rules left out, beside the count of findings that the post says good review files already ask for.

A line such as "2 findings in README.md skipped by rule" would let a person audit a path rule after the fact.
