---
title: "Types of Technical Documentation: Choose the Right Format"
date: 2026-08-05
updated: 2026-08-05
description: "Choose tutorials, how-to guides, reference, and explanation by the reader's next job, then keep each page focused enough to finish it."
tags: ["documentation", "technical-writing", "developer-experience"]
takeaways:
  - "Choose a format from the reader's next job, not the label your team already uses."
  - "A tutorial teaches a path, a how-to changes one known state, reference answers an exact question, and explanation builds a model."
  - "Keep formats connected by links, but do not make one page perform all four jobs."
status: published
slug: "types-of-technical-documentation"
---

Technical documentation has many forms, but the name on a page is a poor starting point. Start with the question a reader needs answered before they can move.

A tutorial, how-to guide, reference page, and explanation can all cover the same product. They differ in the kind of help the reader needs at that moment.

## Choose a documentation format by the reader's next job

| If the reader needs to... | Use this format | The page succeeds when... | Do not use it when... |
| --- | --- | --- | --- |
| Learn a capability through a guided path | Tutorial | They finish a working result and can adapt a nearby variation | They already know the system and need one focused change |
| Complete one known task | How-to guide | They reach the stated outcome from a known starting condition | They need to learn the underlying model first |
| Look up an exact name, type, default, or limit | Reference | They find the answer without inferring it from prose | They need an end-to-end path or a design rationale |
| Understand how or why a system behaves a certain way | Explanation | They can reason about the mechanism and its tradeoffs | They only need the next command or field value |

The [Diátaxis framework](https://diataxis.fr/) makes this distinction through tutorials, how-to guides, reference, and explanation. It is useful because it separates learning, task completion, lookup, and understanding instead of treating every page as a smaller version of a user manual.

## A tutorial teaches a path, not a collection of steps

A tutorial is for a reader who cannot yet complete the work alone. It should begin from a stated starting point, move through a supported sequence, show checkpoints, and leave the reader with a result they can inspect.

For example, a webhook tutorial might take a developer from a new project to a verified event. It can introduce signing only when that decision becomes necessary, then show the expected event or response that proves the path worked.

A long setup guide is not automatically a tutorial. If it only lists configuration options without helping the reader build capability, it is closer to reference or a collection of how-to pages.

The [technical tutorial guide](/articles/how-to-write-a-technical-tutorial-that-actually-teaches/) covers the test that matters: a reader should be able to finish the path in a clean environment and know what a successful result looks like.

## A how-to guide changes one known state

A how-to guide is for a reader who already understands the product well enough to name the job. They need a reliable route from a known condition to a new one.

“Rotate an API key,” “enable audit logs,” and “add a webhook endpoint” are how-to jobs. Each page needs prerequisites, a focused procedure, the success state, and the condition that makes recovery or retry unsafe.

The competent objection is that narrow guides can create too many pages. That is true if each one only renames the same procedure.

Split a guide when the starting state, required permissions, success check, or failure boundary changes. Otherwise, keep related steps together and use headings that let the reader find the one action they need.

## Reference answers an exact question without a story

Reference is the lookup layer. A reader often arrives from an editor, terminal, error message, or code review with a precise question and little patience for an introduction.

A configuration reference should show names, accepted values, defaults, constraints, and exceptions. API reference should make methods, parameters, response fields, and errors easy to scan.

Google's [API reference guidance](https://developers.google.com/style/api-reference-comments) calls out the same need for precise descriptions of methods, parameters, returns, and exceptions.

Reference can include an example when an exact value is still hard to interpret. It should not turn that example into a full learning path.

Link to a tutorial or how-to guide when the reader needs context beyond the stable contract.

## Explanation builds the model behind a decision

Explanation helps when a reader asks why a system is designed a certain way or which tradeoff applies to their case. It gives them a model they can carry into nearby decisions.

A page about rate limiting can explain quotas, burst behavior, and backoff so a developer can reason about a new endpoint. It should link to the request guide or reference page where they configure the behavior, rather than hiding every operational detail in the conceptual page.

Explanation is allowed to take time, but it should still have a boundary. Once the reader can understand the mechanism and choose the next relevant task page, the rest belongs in a deeper explanation or a distinct system-design document.

## Keep formats connected without mixing their jobs

Documentation types are not four isolated shelves. One product task often moves through them.

A developer might begin with a tutorial, return later to reference for a parameter, open an explanation when a design choice becomes unclear, and use a how-to guide to change production behavior. The goal is not a perfect taxonomy but a page that answers its question completely enough for the reader to know where to go next.

This also means a format is not the same as a delivery channel. A documentation site, README, knowledge base, or internal handbook can contain each of these formats.

An internal page may need a runbook or onboarding guide as well, but the same test still applies: what does the reader need to accomplish after reading?

## Test the format before you draft the page

<!-- receipt-backed-first-person -->

I ran a small [documentation format selector](/static/templates/documentation-format-selector.py) against four reader needs and saved its [raw test receipt](/static/templates/documentation-format-selector-receipt.txt). It maps learning to tutorial, a known task to how-to, exact lookup to reference, and a mental-model question to explanation.

```bash
python3 documentation-format-selector.py --need lookup
```

The selector's three tests passed, and its output makes the contract visible before a draft starts. It cannot decide what your product supports or whether a page is accurate, so treat it as a planning check rather than a substitute for product review.

<div class="visual-wrapper">
  <div class="visual-title">Documentation format selector validation</div>
  <div class="visual-container">
    <img src="/static/images/articles/types-of-technical-documentation/documentation-format-selector.png" alt="Terminal output showing three passing tests and documentation format choices for tutorial, how-to guide, reference, and explanation">
  </div>
</div>
<p class="visual-caption">The selector makes the reader state, completion signal, and required page contents explicit for four common documentation formats.</p>

Use the selector before you open a blank page. Then use the [technical documentation template](/articles/technical-documentation-template/) to give the chosen page a home, and use the [technical documentation best practices](/articles/technical-documentation-best-practices-tested-real-developer-docs/) to test whether the finished page can carry its promised task.
