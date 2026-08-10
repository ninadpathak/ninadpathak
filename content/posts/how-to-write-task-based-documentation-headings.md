---
title: "How to Write Task-Based Documentation Headings"
date: 2026-08-10
updated: 2026-08-10
description: "Write documentation headings that tell a reader which task, decision, concept, or recovery path a section covers."
tags: ["technical-writing", "documentation", "developer-experience"]
takeaways:
  - "Use a task heading when a section tells the reader how to reach a specific result."
  - "Use a descriptive noun phrase when a section explains a concept or documents a reference item."
  - "Review the heading outline separately from the body copy before publishing."
status: published
slug: "how-to-write-task-based-documentation-headings"
---

A heading should tell a scanning reader what the section contains. For a procedure, name the result or task.

For a concept, name the concept. For a failure, name the condition and the recovery path.

That is the whole rule. Task-based headings are not a mandate to put a verb in every heading.

<div class="visual-wrapper">
  <div class="visual-title">An illustrative heading rewrite</div>
  <picture>
    <img src="/static/images/articles/how-to-write-task-based-documentation-headings/task-heading-anatomy.svg" width="1344" height="640" alt="An illustrative example rewrites the label Setup as Configure the client with an API key, identifying an action, object, and context." loading="lazy" decoding="async">
  </picture>
</div>
<p class="visual-caption">This example shows the difference between a topic label and a heading that states the work the section covers.</p>

## Match the heading to the section's job

A heading is a navigation label, a link target, and a promise about the content below it. [Google's documentation style guide](https://developers.google.com/style/headings) recommends descriptive, unique headings and task-based tutorial titles when a document primarily guides work.

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

The right-hand column is not a universal template. It shows how the heading can name the reader's task or the subject of the section instead of only naming a broad topic.

## Write task headings for procedural sections

Use a task heading when the section tells the reader how to change a system or reach a checked result. The heading should usually make the outcome visible before the reader opens the section.

For example, `Configure the client with an API key` tells the reader what they will do and what it applies to. `Configuration` tells them only that the topic is configuration.

Add context when it changes the next action. An environment, prerequisite, failure condition, or target object belongs in the heading only if omitting it would make the task ambiguous.

[Diátaxis describes how-to guides as goal-oriented directions](https://diataxis.fr/how-to-guides/). That is a useful check for documentation headings: prefer the reader's goal over a list of product controls.

For example, `Delay retries after a rate-limit response` explains the intended behavior. `Set the retry_after field` can be correct, but it makes the reader inspect the section before learning why that setting matters.

## Use descriptive noun phrases for concepts and references

A verb makes sense when the reader is meant to act. It becomes awkward when the section exists to explain a concept or document a specific item.

Use a descriptive noun phrase for those sections. `Token scopes and integration access` gives the reader a clear subject and boundary. `Overview` does not.

The same rule applies to reference material. `Webhook signature headers` is a useful anchor because it names the object being documented. `Details` forces the reader to open the section to learn what those details are about.

A practical test is simple: can someone predict the section's subject from the heading alone? If the best answer is only "information about this topic," the label needs more work.

## Keep heading hierarchy separate from heading wording

A precise heading can still be placed at the wrong level. [The World Wide Web Consortium's headings tutorial](https://www.w3.org/WAI/tutorials/page-structure/headings/) explains that heading ranks communicate page structure and support in-page navigation for browsers and assistive technology.

Use one page title for the page's primary job. Use major section headings for the main tasks or concepts, then nest headings only for work that belongs within a parent section.

Do not choose a heading level because of its visual size. CSS can change how a heading looks.

Its level still changes the document outline and navigation structure.

## Review the outline before the prose

Read the headings without the body copy. The review asks a narrower question than an editorial review: does the outline show the tasks, concepts, decisions, and recovery paths that the page promises to cover?

A procedural guide might have an outline like this:

```text
Configure webhooks
Create the endpoint that receives events
Verify the endpoint accepts a signed test event
Recover when signature verification fails
```

This is an example outline, not a claim about every webhook guide. It works because each heading names a distinct part of the reader's path.

Compare it with labels such as `Setup`, `Testing`, and `Errors`. Those labels may be acceptable inside a tightly scoped interface, but they do not describe a task or subject by themselves.

## Rewrite headings where the reader needs to choose a next step

Start with the headings that carry the most navigation work: the first action, prerequisites, verification, risky decisions, and recovery. Those sections are where a reader is most likely to scan for a specific answer.

Do not rewrite every heading into an imperative. A section that explains token scopes should say so.

A section that documents a request field should name that field. A section that guides a reader through a result should state the result.

For a full tutorial structure, see [How to Write a Technical Tutorial That Actually Teaches](/articles/how-to-write-a-technical-tutorial-that-actually-teaches/). Before publishing, use the [documentation review checklist](/articles/documentation-review-checklist-before-you-publish/) to check the rendered outline, links, and navigation.

The useful standard is not "every heading starts with a verb." It is simpler: a reader should be able to tell why a section exists before they have to read it.
