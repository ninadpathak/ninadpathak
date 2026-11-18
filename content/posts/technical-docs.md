---
category: technical-documentation
primary_query: what is technical documentation
siblings:
- documentation-types
- internal-vs-external-docs
- runbook-template
date: 2026-08-05
description: 'Technical documentation explained: the document types it includes and the reader task each one owns, in a table you can check a docs set against.'
slug: technical-docs
status: published
work_note: "A product needs more documents than a README, and each one owes a different reader a different task. I'm Ninad Pathak, a freelance technical writer, and working out that list and then writing the pages is the work companies bring to me. [Let's talk about your docs](/services/)."
takeaways:
- Technical documentation gives each reader task one useful home.
- Start with orientation, one verified success path, and the reference that path needs.
- Give every document an owner and a product change that triggers review.
title: What Is Technical Documentation, and What Should It Include?
updated: 2026-11-17
---

Technical documentation is the written material that explains how a product works and how to use it, from a first install to the exact behavior of each API field. I give each [type of documentation](/articles/documentation-types/) one reader task, and the list of types is the same one it was before assistants started reading docs on people's behalf.

An assistant reading on a person's behalf is a new reader. Matt Cockayne [reported on November 11](https://phpboyscout.uk/answer-first-then-everything-else/) that pages on his projects' docs sites sitting at search positions four to ten "were clicked 0.31% of the time", while assistants kept fetching them for a person who "quite possibly never sees the page at all".

A later section runs his check on seven real pages to see what that reader changes inside each document.

[Technical documentation](/articles/technical-documentation/) of every type now has that second reader.

## What technical documentation should include

Technical documentation should include one document for each task a reader brings to the product, with nothing else on that page. A developer evaluating a product needs different information from someone sending a first API request or investigating an error.

| Reader task | Document that owns it | What must be visible | What shows it is enough |
| --- | --- | --- | --- |
| Decide whether the product fits | Orientation or README | Scope, non-scope, supported use cases, and a starting link | The reader can name the first relevant path |
| Complete a first integration | Quickstart or tutorial | Prerequisites, one supported path, expected output, and a failure link | The reader reaches a recognizable result |
| Understand a system choice | Explanation | Terms, model, constraints, and links to task pages | The reader can explain the choice before implementing it |
| Change an existing behavior | How-to guide | Starting state, procedure, success state, and recovery boundary | The reader can perform the change safely |
| Look up an exact question | Reference | Names, types, defaults, constraints, and exceptions | The reader can find the answer without inference |
| Diagnose a failure | Troubleshooting | Symptom, diagnostic check, cause, recovery, and escalation boundary | The reader can choose the next safe action |
| Respond to a product change | Release note or migration guide | Impact, required action, version or date, and a migration path | The reader can decide whether action is required |

A single page that teaches a beginner and also documents every field does neither job well. Split the jobs so each page can answer its own question completely.

The [Diátaxis framework](https://diataxis.fr/) makes the same cut and says it "identifies four distinct needs, and four corresponding forms of documentation - tutorials, how-to guides, technical reference and explanation." The names help, and the reader's task is what decides which form a page takes.

## Build the smallest package that lets someone succeed

A small team can launch with less than the full table. The first reader needs to understand the product and finish one supported task, and needs the stable details that task depends on.

For an API, that often means an orientation page, a quickstart, and reference for the endpoint or SDK the quickstart uses. Add troubleshooting when a failed setup has a diagnostic path worth writing down, then release material once product changes can affect an existing integration.

For a CLI, orientation should explain the tool's job and its supported environments. The quickstart should produce one visible command result, and reference owns the commands and flags.

An internal platform may need a different starting package, since access and ownership can matter before any public-style portal does. Use the [internal vs. external documentation decision](/articles/internal-vs-external-docs/) when the same subject needs a private operating record and a public task page.

Google's [technical writing course](https://developers.google.com/tech-writing/one/documents) puts the first decision in two sentences: "A good document begins by defining its scope." and "A better document additionally defines its non-scope". That decision keeps a page from collecting unrelated jobs as it grows.

## Give each document a boundary

Each document type has one job and hands the reader to another type when the job ends.

- **Orientation** helps a reader decide where to begin, so it says what the product does and where the first supported task starts.
- **A quickstart** proves one supported path, and links to reference when exact options matter.
- **An explanation** gives a model for a design choice, and it should make the next task simpler without asking the reader to learn every concept first.
- **A how-to guide** changes one behavior from a known starting state.
- **Reference** owns the public API surface.
- **Troubleshooting** starts from a symptom the reader can recognize and ends in a safe recovery or an escalation, and its internal counterpart is the [runbook](/articles/runbook-template/).
- **Release notes** explain changed behavior and the action it requires, and link to the migration page for the full instructions.

Reference is where exactness is the whole job. Google's [API reference guidance](https://developers.google.com/style/api-reference-comments) says "API documentation must include descriptions for every class, constant, method, and parameter", because an implementation depends on exact behavior and a narrative approximation won't do.

A generic support link can't tell someone whether a retry is safe, and a troubleshooting page can.

## What should the first screen of each document hold?

A how-to guide should open with the command or call that does the job, and a reference page with the thing people came to look up. Tutorials and explanations keep their lead-in, because their reader chose to sit down and learn.

That is Cockayne's rule, and the reason behind it is what assistants fetched on his sites: "it was the pages whose first screen was a quotable command". His wording for the two page types is exact enough to review against.

A how-to, in his words, "opens with whatever does the job, directly under the heading", and he caps that opening at ten lines. "A reference page opens with whatever a person came to look up, the table or the field list or the exit codes."

The evidence is one person's sites and one month of reports, and the post publishes no data beyond the figures it quotes. What it does publish is a check anyone can run: "Count the words between the page's title and its first code block or table".

I saved the Markdown version of five vendor pages and two of my own as `page.md` in turn, and ran his one-liner on each.

```sh
awk '/^# /{h=1; next} h && /^(```|\|)/{print n+0; exit} h{n+=NF}' page.md
```

| Page | Kind, by my classification | Words before the first code block or table |
| --- | --- | --- |
| Stripe, [Create a charge](https://docs.stripe.com/api/charges/create) | Reference | 33 |
| Cohere, [Chat API](https://docs.cohere.com/docs/chat-api) | How-to | 77 |
| Cohere, [Rerank overview](https://docs.cohere.com/docs/rerank-overview) | How-to | 108 |
| Stripe, [subscription quickstart](https://docs.stripe.com/billing/quickstart) | Tutorial | 633 |
| LiveKit, [Turns overview](https://docs.livekit.io/agents/build/turns/) | Explanation | 656 |
| This site, [quickstart guide template](/articles/quickstart-guide/) | How-to | 376 |
| This site, runbook template | How-to | 499 |

Cockayne's threshold is "Under a hundred is answer-first, several hundred is a page that explains before it helps." Stripe's reference page passes at 33 words, and those words are a deprecation notice, which a developer needs before the request.

The two vendor pages over 600 are a tutorial and an explanation, the kinds his rule leaves alone. His post says "A tutorial shouldn't open with the finished command.", so the count only means something beside the page type.

Both of my pages fail. Each count includes between thirty and forty words of description and byline that this site adds to its Markdown files, and the rest is explanation I put ahead of the template the reader came for.

The check suits pages with one job, and it belongs in a review with the page type written next to it. A word count gives an author and a reviewer a number to argue over in place of taste.

## Assign an owner and an update trigger

Give each document an owner and a product change that requires review. A review date alone doesn't keep documentation current, and a trigger such as a schema change or a new permission does.

GitLab's contributor guide opens by calling its documentation ["the single source of truth (SSoT) for information about how to configure, use, and troubleshoot GitLab."](https://docs.gitlab.com/development/documentation/) A page can only hold that status if someone updates it when product behavior makes its instructions unsafe or incomplete.

A useful trigger connects the document to the change that can invalidate it. A schema change should prompt reference review, and a recurring failure should prompt troubleshooting work.

Use a [technical documentation template](/articles/documentation-template/) when you are ready to turn these decisions into a repository. Then [test whether a page helps someone finish a task](/articles/documentation-best-practices/) before calling it complete.

Use the [documentation review checklist](/articles/documentation-review/) before publication. If duplicate or stale answers are the problem, start by [organizing documentation that has drifted](/articles/documentation-structure/) instead of adding another page.

Keep each page short, for the reasons in [the case for shorter documentation](/articles/shorter-documentation/).
