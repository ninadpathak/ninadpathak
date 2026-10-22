---
category: technical-documentation
date: 2026-10-22
description: A design doc template in Markdown with goals, non-goals and a required "do nothing" alternative, a filled example, and a checker to run before review.
slug: design-doc-template
status: published
takeaways:
- A design doc states the problem, goals and non-goals, the proposal, the alternatives, the rollout and the decision.
- Every alternative needs a reason it was rejected, and one of them should be doing nothing.
- Run the checker before review, so a doc marked Accepted with open questions fails.
title: 'Design Doc Template: Sections, a Filled Example and a Review Check'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for engineering teams, including the design docs that record why a system was built the way it was.'
---

Under "Rationale and alternatives", the [Rust RFC template](https://github.com/rust-lang/rfcs/blob/master/0000-template.md) asks "What is the impact of not doing this?" The [Kubernetes KEP template](https://github.com/kubernetes/enhancements/blob/master/keps/NNNN-kep-template/README.md) gives Non-Goals its own heading next to Goals, and Alternatives a section of its own.

Both make the author argue with their own proposal before a reviewer has to. My template keeps those sections, and its checker fails a doc with no "Do nothing" entry or an alternative with no reason for rejecting it.

## What a design doc template contains

A design doc template is a fixed outline for proposing a technical change before it is built, so reviewers can compare the proposal with the options it beat. It has a short header and eight sections:

1. **Header:** status, author, reviewers and date.
2. **Problem:** what is broken or missing, for whom, and the evidence.
3. **Goals:** outcomes someone could check after the change ships.
4. **Non-goals:** what a reviewer might expect the change to do that it will not.
5. **Proposal:** the design, its interfaces and the order of the work.
6. **Alternatives considered:** each option with what would happen and why it was rejected, starting with doing nothing.
7. **Risks and rollout:** each risk with its mitigation, the release order and how to roll back.
8. **Open questions:** what must be answered before the doc is accepted.
9. **Decision:** what was decided, by whom and when.

## Copy the template and the checker

The checker needs only Python 3, and it reads the file you give it and nothing else:

- [Design doc template (Markdown)](/static/templates/design-doc-template.md)
- [Checker script](/static/templates/check_design_doc.py)
- [Filled example: keep export records across restarts](/static/examples/design-doc-persist-exports.md)

The header uses `Field: value` lines, and placeholders use double braces so a reader can tell them from code:

```markdown
Status: {{Draft | In review | Accepted | Rejected | Superseded by <link>}}
Author: {{name}}
Reviewers: {{names}}
Date: {{YYYY-MM-DD}}
```

## Start the alternatives with doing nothing

Each alternative gets two lines, and the first entry states the cost of leaving things as they are:

```markdown
### Do nothing

What happens: {{the cost of leaving things as they are}}
Rejected because: {{why that cost is not acceptable}}
```

I made the "Do nothing" entry required because it is the Rust template's question written as a section. If the author can't say what doing nothing costs, the reviewers have no way to weigh the proposal against it.

## A filled example: keep export records across restarts

The example proposes a change to the writing-lab service from the [technical documentation template](/articles/documentation-template/), whose export records live only in memory. Its problem statement names the failure a client of that service would hit:

```markdown
## Problem

`POST /exports` stores records in a `Map` inside the process, so a restart loses every record and every idempotency key. A client that retries with the key it used before the restart gets a new `exp_1` instead of its original record, which breaks the retry promise in the reference.
```

Its non-goals rule out generating export files and running several instances. Without those two lines, a reviewer could reasonably ask why the proposal ignores both.

## Check the doc before review

Run the checker with `--filled` on the finished doc, before the [product-first review](/articles/documentation-review/) where people read it. It checks the header, each section, each alternative and the open questions, and it fails on any `{{placeholder}}` left in the text:

```bash
python3 check_design_doc.py --filled design-doc-persist-exports.md
```

```text
design-doc-persist-exports.md: PASS
  sections: 8/8
  alternatives with a reason: 2
  unfilled placeholders: 0
```

Copy the example to `draft2.md`, change the status to "Approved", empty the Non-goals list and delete the reason under "SQLite database", then check the copy:

```text
draft2.md: FAIL (3 problem(s))
  - Status must start with one of Draft, In review, Accepted, Rejected, Superseded by: 'Approved'
  - section '## Non-goals' is empty (write None if it has nothing to say)
  - alternative 'SQLite database' has no 'Rejected because:' reason
```

A failing doc exits with status 1, so fix each listed line and rerun until it prints PASS. The checker also fails a doc marked Accepted or Rejected that still lists an open question, because that decision depends on an answer nobody has given.

## Design doc or RFC

An RFC, in projects like Rust, is a design doc that goes through public review, and the Rust template has header fields for the RFC pull request and the tracking issue. Use the RFC form when people outside the team review the change, and this template when the reviewers sit on the team that will build it.

## FAQ

### What should a design doc include?

It needs a problem statement, goals and non-goals, the proposal and the alternatives considered. Add risks with a rollout and rollback plan, the open questions and the final decision.

### What is the difference between goals and non-goals?

Goals are outcomes someone can check after the change ships. Non-goals are things a reviewer might expect the change to do that it deliberately leaves out.

### Why include a "do nothing" alternative?

It states the cost of leaving things as they are, which is the baseline every other option is measured against. Rust's RFC template asks the same question as "What is the impact of not doing this?"

### When is a design doc finished?

When its status is Accepted or Rejected, the Decision section records who decided and when, and no open question remains. The checker enforces the last two once the status changes.
