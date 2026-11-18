---
category: technical-documentation
primary_query: internal vs external documentation
siblings:
- documentation-types
- documentation-structure
date: 2026-08-06
description: 'Internal vs. external documentation, with a decision table for incidents,
  architecture, auth and releases: what goes public, what stays private, what splits.'
slug: internal-vs-external-docs
status: published
work_note: "This post is about deciding what goes in the public docs and what stays internal when a subject has both readers. If you'd rather someone else write the public half while your team keeps the private one, that's what I do. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. [Tell me about your docs](/contact/)."
takeaways:
- Choose internal or external documentation by the reader's task, not by the file's
  technical depth.
- Split a subject such as authentication into a public task page and a private runbook
  when customers and operators both need it.
- Give every page an owner and a change that triggers its review.
title: 'Internal vs. External Documentation: What Belongs Where'
updated: 2026-11-17
---

Internal documentation helps your team operate the system, and external documentation helps customers, partners and public developers use the supported product. When a subject has both readers, write two pages: a public one for the customer's task and a private one for the team that runs the system.

The rest of the page sorts every subject into **internal**, **external** or **split**. Authentication is the split I'll use as the example, with a public page for the OAuth flow and its error codes and a private key-rotation runbook behind it.

Where the line between internal and external falls is one of the first decisions in any set of [technical documentation](/articles/technical-documentation/).

That line used to follow access, and a file that surfaced this autumn shows why access no longer settles it. The XScreenSaver source release ships an [AGENTS.md](https://github.com/Zygo/xscreensaver/blob/master/AGENTS.md), mirrored to GitHub on September 4, that opens "You are in a project that does not want AI contributions of any kind."

A contribution policy is about as internal as documentation gets, and this one sits in a public tarball addressed to a reader who is neither a team member nor a customer. Coding agents are that third reader, and the section on agent instructions below covers where their files belong.

## Internal vs. external documentation: choose by reader task

Google's [technical writing guidance on audience](https://developers.google.com/tech-writing/one/audience) defines an audience by the knowledge and skills it needs for a task. Use that task, not a person's job title, to decide where a page belongs.

Ask four questions:

1. Does someone outside the organization need this to use the product, at any point from evaluating it to recovering from a failure?
2. Does the subject contain anything that must stay private, such as credentials or a candid incident analysis?
3. Does an internal operator need implementation context that an external reader does not?
4. Who owns the source of truth, and which product or process change makes it stale?

For question two, private material means:

- Credentials
- The private network layout
- Unpublished plans
- Exploit detail
- Personnel information
- Candid incident analysis

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/internal-vs-external-docs/documentation-placement.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/internal-vs-external-docs/documentation-placement.narrow.svg" width="288" height="792"><img class="np-has-narrow" src="/static/images/diagrams/internal-vs-external-docs/documentation-placement.svg" width="720" height="672" alt="Documentation placement decision tree. If no outside reader needs the information, keep it internal when an operator needs it; otherwise review whether the page has a task. If an outside reader needs it, split it into a public task page and a private record when private context remains; otherwise publish it externally." loading="lazy" decoding="async"></picture></a>
  <figcaption>Each path ends in one of four results: internal, external, split, or review, which means nobody has a task for the page yet. A split is two documents, a public task page and a private record, and never a redacted internal page.</figcaption>
</figure>

## Internal vs. external documentation comparison

| Signal | Internal documentation | External documentation | Split documentation |
| --- | --- | --- | --- |
| Primary reader | Employee, contractor, or approved operator | Customer, partner, public developer, or product administrator | Both groups |
| Reader task | Deploy the billing service | Add a webhook endpoint | Rotate an API key: the customer follows the public steps, and the team follows the runbook |
| Typical detail | Why the team chose a queue, which dashboards to watch | Request fields, error codes, rate limits | The OAuth flow in public, key handling in private |
| Access | Identity and role based | Public or customer authenticated | Separate access and separate documents |
| Update trigger | The on-call rotation or the deploy process changes | An endpoint, a limit or an error code changes | Either side changes |

IBM's [code documentation overview](https://www.ibm.com/think/topics/code-documentation) draws the same line: coding standards serve the team, and a public API reference serves outside developers.

## What belongs in internal documentation

Internal documentation is everything the team needs to build, operate and change the system that an outside reader has no task for. It can be candid, because only the team reads it.

### Architecture decisions and system design

Keep architecture decision records and anything that maps the private network, such as a topology diagram or capacity plan, with the team that operates the system. A public architecture page should explain only what changes a customer's decision, say where their data is stored and which parts they deploy themselves.

### Runbooks and internal recovery procedures

Keep the commands that need production access, the escalation contacts and the candid write-up of what failed behind the team's login. The public troubleshooting page starts from the symptom a customer sees, such as a `401` on every request, gives a fix that is safe to try, and says when to contact support.

### Employee onboarding and working agreements

How to get repository access, who approves a deploy and which team owns which service belong in contributor onboarding. Atlassian's [internal documentation guidance](https://www.atlassian.com/work-management/knowledge-sharing/documentation) treats this material as living team knowledge, which means it still needs ownership and review.

## What belongs in external documentation

External documentation is what an outside reader needs to use the product: a quickstart, the API reference, release notes and troubleshooting pages. It stops at the supported contract, so the reader learns what the product promises without seeing the system that keeps the promise.

### Product scope and getting started

Publish what the reader has to install, the first call to make, the response they should see and a link to the next page. A reader should be able to finish that first call without writing to support.

### Public interfaces and product contracts

Publish everything a caller can depend on, such as an endpoint's fields and its error codes, along with limits and the authentication flows you support. The reader needs the request, the response and what happens on failure, and has no use for the list of internal services behind the endpoint.

### Releases, migrations, and customer recovery

Publish a release note when behavior changes and a migration guide when the reader has to act. The page must answer:

- Whether the reader is affected
- What to change
- When to change it
- How to confirm the change worked

## When to split internal and external documentation

A split is two documents: a public page built around a customer task, and a private page with the operating detail needed to keep the public page's promise.

| Shared subject | Internal documentation | External documentation |
| --- | --- | --- |
| Production incident | Timeline, what caused it, what the team is changing | Who was affected and when, what customers should do, what happens next |
| System architecture | Why it was built this way, the private network layout, what it depends on | Where the product runs, where customer data goes, what the customer deploys |
| Authentication | Where keys are stored, how they are rotated, who to page | The OAuth flow, the scopes, the error codes, how a customer rotates a key |
| Product release | Rollout plan, known risks, who decides on a rollback | What changed, who is affected, what to do before upgrading |

Link the private page to the public page it supports. Give each page its own owner and update trigger, because a supported authentication flow can change without changing the internal key-rotation runbook.

The same split applies when an AI agent resolves a production incident, and [my essay on agents on call](/articles/agents-on-call-runbooks/) argues that the agent's account of what it did belongs on the internal side.

## Where do AGENTS.md and other agent instructions belong?

Agent instruction files are internal documentation by task and often external by access, so treat them as a split. The task is internal because the file tells a contributor how to work in the repository, and the access is whatever the repository's is.

A private monorepo never raises the question. Nathan Broadbent [described DocSpring's setup](https://docspring.com/blog/posts/ponytail-vs-agents-md/) on November 13 as "42 AGENTS.md files, about 65,000 words in all", which is a large body of internal documentation that happens to have agents as its heaviest readers.

A public repository publishes every line of the file. Question two from the list above (credentials, private topology, unpublished plans) applies to it exactly as it applies to a README, and it is the check an agent-written instruction file is least likely to have had.

<!-- evidence-three: October 3, 2026 is the publication date printed on liao.gg/blog/agents-dont-need-memory -->
Kevin Liao's Operator, a documentation workspace for coding agents, applies the same split inside the agent's own files. [Liao's post of October 3](https://liao.gg/blog/agents-dont-need-memory) separates an agent's private working notes from what a team shares, through "an explicit .operator-shared/ shared partition that you can commit with the repository, so that specs, guides, and standards can be shared with every coworker, intern, or cloud AI agent."

| Agent instruction content | Placement | Why |
| --- | --- | --- |
| Build, test and style rules a new contributor also needs | Committed file in the repository | Safe to publish and useful to people |
| Internal hostnames, credentials handling, escalation paths | Private file or internal docs | Fails question two |
| Contribution policy, including whether agents may contribute | Committed file | It is addressed to outsiders, as XScreenSaver's is |

## Documentation placement audit template

Start with an inventory: for every page, record the answers to the four questions above.

<!-- receipt-backed-first-person -->

I encoded that inventory in a small [documentation placement audit](/static/templates/documentation_placement_audit.py) and ran it against an eight-artifact [sample manifest](/static/templates/documentation-placement-audit.json). The run sorted the eight artifacts into internal, external and split, with the counts in the output below.

```bash
python3 documentation_placement_audit.py
```

```text
AUDIT PASSED: 8 artifacts, internal=3, external=3, split=2, review=0
```

Inspect the generated [CSV report](/static/templates/documentation-placement-audit-report.csv) before adapting the fields to your own inventory. The script exposes mixed audiences and missing ownership, but a security or legal reviewer still decides what the organization may publish.

## Documentation ownership and update triggers

| Placement | Primary owner | Useful update triggers | Completion signal |
| --- | --- | --- | --- |
| Internal | Team closest to the system or process | A deploy process change, an incident, or a new owner | An operator can complete the internal job safely |
| External | Product documentation, developer experience, or product team | A changed endpoint, limit or error code, or a support question that keeps recurring | An outside reader can complete the promised task |
| Split | A named owner for each page, and a link between the two | Any change that makes the public promise and private operation disagree | Both pages agree on supported behavior without sharing private context |

GitLab's [documentation style guide](https://docs.gitlab.com/development/documentation/styleguide/) treats product documentation as a maintained source of truth for implementation, use, and troubleshooting. Give a private runbook the same treatment: a named owner, and a review whenever the system it describes changes.

Start with the external task. If answering it also takes private detail, write the second page, as with the key-rotation runbook behind the public authentication guide.

Use the [types of technical documentation](/articles/documentation-types/) to choose the artifact each reader needs. If readers already can't tell which of two pages is current, [organize the documentation site](/articles/documentation-structure/) before adding more.
