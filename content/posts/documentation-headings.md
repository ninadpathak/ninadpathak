---
category: technical-documentation
date: 2026-08-10
description: Write documentation headings that tell a reader which task, decision,
  concept, or recovery path a section covers.
slug: documentation-headings
status: published
work_note: 'I checked the heading rule on this page against the outline of Stripe''s webhook guide, pulled with one command. [My portfolio](/portfolio/) has guides where you can see whether I follow the rule myself.'
takeaways:
- Use a task heading when a section tells the reader how to reach a specific result.
- Use a descriptive noun phrase when a section explains a concept or documents a reference
  item.
- Review the heading outline separately from the body copy before publishing.
title: How to Write Task-Based Documentation Headings
updated: 2026-11-17
video: documentation-headings
---

Stripe's [webhook guide](https://docs.stripe.com/webhooks) has nine second-level headings. Of those, six name an action, such as "Create a handler", and the rest name a subject, such as "Event delivery behaviours", which is the British spelling Stripe served to my region.

That split is the rule for documentation headings, taken from a page built on it. A heading should tell a scanning reader what the section contains.

- For a procedure, name the result or task.
- For a concept, name the concept.
- For a failure, name the condition and the recovery path.

A task-based heading belongs on a section that holds a task, and the rule stops there. It doesn't ask for a verb in every heading.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/documentation-headings/task-heading-anatomy.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/documentation-headings/task-heading-anatomy.narrow.svg" width="288" height="376"><img class="np-has-narrow" src="/static/images/diagrams/documentation-headings/task-heading-anatomy.svg" width="720" height="480" alt="An illustrative example rewrites the topic label Configuration as the task heading Configure the client with an API key. Brackets under the heading mark its three parts: the action Configure, the object the client, and the context with an API key, each drawn as a play head, a cube, and a key." loading="lazy" decoding="async"></picture></a>
  <figcaption>A topic label names a subject. A task heading names the work: an action, an object, and the context that changes the next step.</figcaption>
</figure>

## Match the heading to the section's job

A heading is a navigation label and a link target, and it promises what the content below it will be. [Google's documentation style guide](https://developers.google.com/style/headings) gives the instruction as "Write section headings based on the type of content that's in the section."

Start by deciding what the section does. A procedure helps a reader reach a result, while an explanation answers a conceptual question.

A reference section identifies a field, object, or API behavior. A recovery section handles a known failure condition.

| Section job | Generic label | Illustrative rewrite |
| --- | --- | --- |
| Procedure | Setup | Create the project and install the CLI |
| Configuration | Configuration | Configure the client with an API key |
| Verification | Testing | Verify the endpoint accepts a signed test event |
| Recovery | Errors | Recover when signature verification fails |
| Explanation | Authentication | Token scopes and integration access |
| Reference | Options | Retry policy options for background jobs |

The right-hand column shows how a heading can name the reader's task or the section's subject where the middle column names only a broad topic. Treat it as a set of examples, since the wording depends on the product.

## Write task headings for procedural sections

Use a task heading when the section tells the reader how to change a system or reach a checked result. Google's guide gives the form: "For a task-based heading, start with a bare infinitive", the plain verb with no "to" or "-ing".

For example, `Configure the client with an API key` tells the reader what they will do and what it applies to. `Configuration` tells them only that the topic is configuration.

Add context when it changes the next action. A detail such as the environment or a prerequisite belongs in the heading only if omitting it would make the task ambiguous.

Diátaxis says ["How-to guides are goal-oriented."](https://diataxis.fr/how-to-guides/) That is a useful check for a heading: prefer the reader's goal over a list of product controls.

For example, `Delay retries after a rate-limit response` explains the intended behavior. `Set the retry_after field` can be correct, but it makes the reader inspect the section before learning why that setting matters.

## Does a task heading beat a noun heading every time?

No. A verb helps when the reader is meant to act, and a section that explains a concept or documents one item needs a descriptive noun phrase.

The opposite advice is a staple of help-centre marketing. Dedox, which sells help-centre software, put it this way in a promotional post on November 1: ["How to change your plan" beats "Plan management" every time.](https://mastodon.social/@dedox/117540805753181893)

The example is right, because a help-centre article about changing a plan is a task.

The words "every time" are where I disagree. The same post grounds the tip in search, saying task titles "match what people actually type into search", and people also type the names of things.

Claude Code's [hooks reference](https://code.claude.com/docs/en/hooks) shows the other case. Its sections are named for what a developer looks up, such as "Hook input and output" and "Matcher patterns", and each hook event is a heading that is only the event's name, `PreToolUse` among them.

A developer arriving there has the name already and wants its fields. `Webhook signature headers` works for the same reason, and `Details` fails because it forces the reader to open the section to learn what the details are about.

A practical test covers both kinds. If someone can predict the section's subject from the heading alone, the heading works, and if the best they can say is "information about this topic", it needs another pass.

## Keep heading hierarchy separate from heading wording

A precise heading can still be placed at the wrong level. The World Wide Web Consortium's [headings tutorial](https://www.w3.org/WAI/tutorials/page-structure/headings/) says "Headings communicate the organization of the content on the page", and that browsers and assistive technologies use them for in-page navigation.

Use one page title for the page's primary job. Use major section headings for the main tasks or concepts, then nest headings only for work that belongs within a parent section.

Choose a level for the structure it declares. CSS can change how a heading looks, and its level still sets the document outline that navigation tools read.

## Review the outline before the prose

Read the headings without the body copy. The review asks a narrower question than an editorial review: does the outline show the tasks and recovery paths that the page promises to cover?

Where a site publishes its pages as Markdown, one command pulls the second-level outline.

```sh
curl -sL https://docs.stripe.com/webhooks.md | grep '^## '
```

```text
## Set up your endpoint
## Create a handler
## Test your handler
## Optional: Create an event destination for Connect
## Optional: Create an event destination for Organisations
## Debug webhook integrations
## Event delivery behaviours
## Best practices for using webhooks
## See also
```

The outline reads as the job in order: set up, create, test, debug. The reference material sits under "Event delivery behaviours", and its own subheadings are noun phrases such as "Automatic retries" and "Event ordering".

Compare that with labels such as `Setup`, `Testing`, and `Errors`. Those labels may be acceptable inside a tightly scoped interface, but they do not describe a task or subject by themselves.

## Rewrite headings where the reader needs to choose a next step

Start with the headings that carry the heaviest navigation work, which are the first action and the recovery path. The verification step comes next, since it tells the reader whether to go on.

Leave the rest in the form that fits them. A section that explains token scopes should say so, and a section that documents a request field should name that field.

For a full tutorial structure, see [How to Write a Technical Tutorial That Actually Teaches](/articles/writing-technical-tutorials/). Before publishing, use the [documentation review checklist](/articles/documentation-review/) to check the rendered outline, links, and navigation.

The standard to hold a page to is that a reader can tell why a section exists before reading it. Stripe's outline passes with verbs where the reader acts and nouns where the reader looks something up.
