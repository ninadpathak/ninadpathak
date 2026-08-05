---
title: "Types of Technical Documentation: Choose the Right Format"
date: 2026-08-05
updated: 2026-08-05
description: "Learn when a tutorial, how-to guide, reference page, or explanation is the useful document for a reader’s next task."
tags: ["documentation", "technical-writing", "developer-experience"]
takeaways:
  - "A documentation type is a promise about the help a page provides next."
  - "The same product capability can need a tutorial, how-to guide, reference page, and explanation at different moments."
  - "Choose the document from the reader’s unfinished question, then make its boundary visible."
status: published
slug: "types-of-technical-documentation"
---

A tutorial, how-to guide, reference page, and explanation can describe the same product capability without doing the same work. The useful type is the one that answers the reader’s unfinished question before they have to guess, search again, or turn a conceptual page into an improvised procedure.

## A documentation type is a promise

A page’s label matters less than its promise. If it calls itself a tutorial, the reader should leave with a working capability, not a catalogue of settings.

Reference should let the reader find an exact fact without reading a story around it.

The [Diátaxis framework](https://diataxis.fr/) names four useful promises: tutorials help someone learn, how-to guides help them complete a known task, reference gives precise facts, and explanation builds understanding. Those distinctions hold because each reader arrives with a different amount of context and needs a different kind of help.

A product can need all four. The mistake is asking one page to perform all four jobs, then leaving the reader unable to tell which part is safe to follow.

## Follow one integration from first attempt to production change

Consider a developer adding a webhook to an application. The endpoint, signature, and event payload may appear in every document below, but the reader’s question changes as their work progresses.

### A tutorial makes the first success repeatable

At the start, the reader may not know which event to choose, where the endpoint belongs, or how a successful delivery should appear. A tutorial gives them one supported path from a stated starting point to a visible result.

It can introduce signature verification when the reader reaches that decision, then show the event or response that confirms the integration worked. The sequence teaches capability, which is different from listing every possible configuration.

A long setup page is not automatically a tutorial. If it presents options without helping the reader reach a first outcome, it is closer to reference or a set of how-to guides.

### A how-to guide changes one known condition

Later, the same reader may know the integration already works and need to rotate a signing secret. They need the safe path from an existing configuration to a changed one, not another introduction to webhooks.

That is a how-to guide. State the required starting condition, the focused procedure, the success check, and the condition that makes a retry or recovery unsafe.

Do not create a new page every time a button label changes. Split a guide when the starting state, permission model, success check, or recovery boundary changes.

Otherwise, keep related changes together under headings that let the reader find the action they came for.

### Reference removes inference from exact details

During implementation, the reader may need to know the accepted signature algorithm, a payload field’s type, or the limit on a retry setting. That question needs an answer that is easy to scan and stable enough to depend on, not a guided narrative.

Reference owns names, values, defaults, constraints, exceptions, and the contract that code must satisfy. Google’s [API reference guidance](https://developers.google.com/style/api-reference-comments) similarly focuses on methods, parameters, returns, and exceptions because those details are not safe to infer from a prose example.

An example still belongs in reference when it makes a value understandable. It should stop before it becomes a second tutorial hidden inside an API page.

### Explanation lets the reader reason beyond one page

A reader can configure retries correctly and still ask why the system uses exponential backoff, or why event delivery is at least once rather than exactly once. Those are explanation questions.

Explanation gives the reader a model for the mechanism and its tradeoffs. It should make the next task easier, then link to the how-to guide or reference page where the reader applies the model.

That boundary is important. Explanation can take time when the idea needs it, but it should not bury a required field value or deployment step inside a conceptual discussion.

## Start with the reader’s unfinished sentence

Before writing, complete the sentence the page must answer. The wording usually tells you which format the reader needs.

- “I want to learn how this capability works” points to a tutorial.
- “I need to change this existing configuration” points to a how-to guide.
- “What value, limit, type, or error applies here?” points to reference.
- “Why does the system behave this way?” points to explanation.

This is not a rigid classification exercise. A page may link into another format when the reader needs more context, but its primary promise should stay clear.

A tutorial can link to reference for exact options. A how-to guide can link to explanation when a design decision changes the safe path.

## Use the boundary to decide what stays out

A focused document is not a thin document. It can define the problem, show an example, explain a limitation, and point to the next useful page when each passage changes what the reader understands or can do.

What it should not do is repeat the same definition in several forms, surround a direct answer with empty setup, or expand into unrelated product background. The extra material earns its place when it turns a definition into a usable picture, a procedure into a safe choice, or a claim into something the reader can check.

For example, a tutorial about webhook verification should explain what it proves, show the verification step, and name the failure condition. It does not need to document every event field.

That material belongs in reference, where a reader can return to it without retracing the tutorial.

## Test the document choice before drafting

<!-- receipt-backed-first-person -->

I ran a small [documentation format selector](/static/templates/documentation-format-selector.py) for this article and saved its [raw test receipt](/static/templates/documentation-format-selector-receipt.txt). It maps learning to tutorial, a known task to how-to, exact lookup to reference, and a mental-model question to explanation.

```bash
python3 documentation-format-selector.py --need lookup
```

The selector’s three tests passed. It makes the choice and completion condition visible before a draft starts, but it cannot decide what your product supports or whether the finished page is accurate.

<div class="visual-wrapper">
  <div class="visual-title">Documentation format selector validation</div>
  <div class="visual-container">
    <img src="/static/images/articles/types-of-technical-documentation/documentation-format-selector.png?v=939750bd" alt="Terminal output showing three passing tests and format choices for tutorial, how-to guide, reference, and explanation" loading="lazy">
  </div>
</div>
<p class="visual-caption">The selector records the reader need, chosen format, and completion condition for four common documentation forms.</p>

Use the [technical documentation template](/articles/technical-documentation-template/) when you are ready to give the chosen page a home. Then use the [technical documentation best practices](/articles/technical-documentation-best-practices-tested-real-developer-docs/) to test whether that page carries its promise for someone doing the task.