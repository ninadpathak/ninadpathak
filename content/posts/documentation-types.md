---
category: technical-documentation
primary_query: types of documentation
siblings:
- internal-vs-external-docs
- design-doc-template
- documentation-template
bridges:
- slug: agents-reading-docs
  reason: A docs page now has agent readers.
- slug: claude-md
  reason: Instruction files for coding agents are documentation.
date: 2026-08-05
description: The eight types of technical documentation and the question each one answers
  for its reader, plus the instruction files coding agents now read.
slug: documentation-types
status: published
work_note: "Got a README and not sure which page comes next? This post sorts the kinds a product ends up needing. I'm Ninad Pathak, a freelance technical writer, and I can write them while you keep shipping. [Let's work together](/services/)."
takeaways:
- Each type of technical documentation answers one reader question, such as how to get
  a first result or why a call failed.
- A document type earns its place when a reader has a question no other page answers.
- Agent instructions add a new audience to a documentation system without replacing
  human-facing docs.
title: 'Types of Technical Documentation: 8 Essential Types, Plus Agent Instructions'
updated: 2026-11-17
---

Technical documentation is the set of documents that help someone use a product, understand a system, operate it safely, or change it without losing context. The types below differ by the reader's task, and this year they also started to differ by who reads them and by whether a model can write them.

[Technical documentation](/articles/technical-documentation/) sorted this way gives each page one reader and one job.

| Type | The reader's question | Group |
| --- | --- | --- |
| Getting-started guide or quickstart | How do I get a first result? | User-facing |
| Tutorial | How do I learn this capability? | User-facing |
| How-to guide | How do I do this one job? | User-facing |
| Reference | What exactly does this accept and return? | User-facing |
| Troubleshooting guide | Why did this fail, and what is safe to try? | User-facing |
| Release notes and migration guide | What changed, and what must I do? | User-facing |
| Architecture and design document | Why is the system built this way? | Process |
| Runbook, onboarding guide, test plan, standard | How do we do this safely again? | Process |
| Agent instructions | What must a coding agent know before editing here? | Agent |

[Fern's State of Docs report](https://buildwithfern.com/post/state-of-docs) from November 10 puts agent reading of API reference at 31%, against 18% for people. Rachel Andrew [wrote on September 30](https://rachelandrew.co.uk/archives/2026/09/30/more-than-words/) about tutorials and how-to content that "AI seems to be particularly bad at creating this kind of content."


## Who technical documentation is for

The classification I use separates technical documentation by the person who needs it, and [what technical documentation should include](/articles/technical-docs/) lists what each of them has to find.

That gives the groups in the table above: user-facing, process and agent. User-facing documents help customers or developers adopt a product.

Process documents help the people building and operating it. Agent instructions give coding agents repository-specific context that would be distracting or irrelevant in a human-facing guide.

## User-facing documentation helps someone use the product

User-facing documents are the ones a customer, developer or administrator opens to get started, finish a task, look up an exact answer or fix a failure.

### Type 1: Getting-started guides and quickstarts

A getting-started guide takes someone from no working setup to a first result. It should list what to install first, show the shortest supported path, and end on output the reader can check.

React's [Learn section](https://react.dev/learn) opens with a Quick Start page and follows it with a tic-tac-toe tutorial.

A quickstart's job is to get one result working and point the reader to the next page, and it leaves the full manual to other pages.

### Type 2: Tutorials

A tutorial teaches a capability through a guided sequence. It can combine several tasks because the reader is learning a skill, not only changing one setting.

A tutorial demonstrates a use case or concept, while a how-to guide completes one bounded task.

After each step, show the output the reader should see, so they know whether they are still on track.

Tutorials, with how-to guides, are the types Andrew finds models worst at. Andrew's explanation is that "The majority of the time I spend writing a tutorial, isn't spent writing", because the work is understanding the subject and the audience before any words exist.

<!-- evidence-three: Type 3 is the heading's number in the list of eight types, not a count -->

### Type 3: How-to guides

A how-to guide answers a specific operational question such as "rotate an API key", "configure single sign-on" or "add a webhook endpoint". The reader already understands enough of the product to name the job.

A strong guide says where the reader starts and what access they need, gives the steps, and ends with how to confirm the change and what to do if a step fails. It does not repeat the product introduction or explain every adjacent feature.

### Type 4: Reference documentation

Reference is where exact details live. An endpoint's request fields, a setting's default value and the error a call can return all belong here, because readers look them up and rely on them.

Stripe's [API reference](https://docs.stripe.com/api) is organized by object. A reader can move from an object to its endpoints and fields without reading a tutorial first.

Reference can include examples, as long as each one shows a single request and its response and doesn't grow into a tutorial.

Reference is now the type agents read hardest, by the Fern figures above, and [my reading of that agent traffic report](/articles/agents-reading-docs/) looks at how far its figures go.

### Type 5: Troubleshooting guides

Troubleshooting starts with a symptom, not a feature. The reader has already hit a failure and needs a way to identify the cause, recover safely, or know when to escalate.

Kubernetes' [troubleshooting documentation](https://kubernetes.io/docs/tasks/debug/) splits into debugging your application and debugging your cluster, with pages such as Debug Pods and Debug Services. A good troubleshooting page has:

- The symptom the reader sees
- A check to run
- The likely causes
- A fix that is safe to try
- When to stop and escalate

My [troubleshooting guide template](/articles/troubleshooting-guide-template/) turns that list into a Markdown file, with a filled example made from four SQLite failures and a script that checks each entry.

### Type 6: Release notes and migration guides

Release notes tell people what changed. Migration guides tell them what they need to do about that change.

A release note can announce a deprecated API version or a changed permission model.

A migration guide should say which versions are affected, what replaces the old call, how long the old call keeps working, and how to confirm the change.

The same Fern report has agents reading the changelog twice as much as people do, which makes dated, per-endpoint entries worth the effort.

## Process documentation helps a team build and operate the system

Product documentation is only one part of technical documentation. Teams also need durable records that explain why a system exists in its current form and how to maintain it.

My page on the [internal vs. external documentation decision](/articles/internal-vs-external-docs/) covers which of these stay private, starting from XScreenSaver's AGENTS.md, which turns AI contributions away.

### Type 7: Architecture and design documents

Architecture documents describe the parts of a system, how data moves between them and why they were built that way. A design document is often narrower, explaining a proposed change before implementation begins.

Architecture and design documents should answer questions that source code cannot answer quickly.

For example, explain why a queue was selected over a synchronous call, which service owns a data set, and what assumptions make a deployment safe. A diagram can help, but it does not replace those decisions and constraints.

### Type 8: Runbooks, onboarding guides, test plans, and standards

Some process documents exist because somebody must perform the same work safely more than once. Runbooks describe routine or incident procedures.

Onboarding guides give a new teammate the systems, access, and conventions they need. Test plans say what will be tested, how, and what result counts as a pass.

Style guides and contribution guides belong here too. They write a team's conventions down, so a contributor reads them before opening a pull request and doesn't learn them from review comments.

Tango's [collection of technical document types](https://www.tango.ai/blog/types-of-technical-documents) goes wider than this page: its 15 types include project plans and roadmaps.

## The newer type: instructions for coding agents

A repository can now have another reader that needs documentation: a coding agent. The convention settled further on September 18, 2026, when Claude Code 2.1.277 shipped with the [changelog line](https://code.claude.com/docs/en/changelog) "Added AGENTS.md support: in a project with no CLAUDE.md, Claude Code reads AGENTS.md instead".

[AGENTS.md](https://agents.md/) is an open Markdown convention for repository instructions aimed at coding agents. It sits beside a README and doesn't replace it.

A README still gives a person the project overview and the way to contribute. An AGENTS.md file holds what an agent needs before it edits, such as the exact build and test commands and the changes it must not make.

For the README itself, my [README template](/articles/readme-template/) has six parts and a checker that runs the commands the file shows.

A repository can hold several AGENTS.md files, and agents.md says "the closest one takes precedence", so a package can carry its own rules.

Keep the two files separate. Do not hide human onboarding inside an agent file, and do not expect a long README to provide the focused instruction an agent needs during an edit.

If both audiences work in the repository, maintain both documents and link between them where the information overlaps.

An agent file in a public repository is also published, whatever its intended reader, and my page on internal and external documentation works through that case.

[CLAUDE.md and AGENTS.md](/articles/claude-md/) covers which agent reads which instruction file, with a template you can copy.

## Build documentation from the work people need to finish

You do not need every document type on launch day. Start by listing the moments where users and operators need an answer that cannot safely remain in chat history, a ticket, or one person's memory.

For a public API, that first package may include a quickstart, API reference, authentication guide, error guide, and release notes. For an internal service, it may start with an architecture document, onboarding guide, deployment runbook, and incident procedure.

A [design doc template](/articles/design-doc-template/) gives an architecture change its own page before the code exists, with the alternatives it beat.

For an agent-enabled repository, add AGENTS.md when the agent needs instructions that should remain close to the code.

Then give each document an owner and a change that triggers its review:

| Change | Document to review |
| --- | --- |
| An API schema change | Reference |
| A revised deployment flow | Runbook |
| A recurring support issue | Troubleshooting |
| A changed build command | README and agent instructions |

Documentation costs less to maintain when each type has a named audience, a distinct job, and a change that tells its owner when to revisit it.

To see finished pages before you write your own, my [technical writing examples](/articles/technical-writing-examples/) are ten samples, from a quickstart to a postmortem, each with the check that ran on it.

Use the [technical documentation template](/articles/documentation-template/) to turn that inventory into a working plan. Then use the [technical documentation best practices](/articles/documentation-best-practices/) to test whether each page helps someone complete the job it promises.
