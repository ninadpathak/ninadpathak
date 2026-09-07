---
title: "Technical Writing Is Deciding What the Reader Can Assume"
date: 2026-09-07
description: "A timeout can hide a completed operation. Good technical writing gives readers the facts that let them choose what to do next."
category: technical-documentation
tags: [technical-writing, documentation, api-documentation]
status: published
slug: technical-writing-is-deciding-what-the-reader-can-assume
---

An API request times out, and the troubleshooting page tells you to try again. Before doing that, you need to know whether the first request did anything.

The server might have rejected it before work began, or completed it just before the connection broke. The same instruction describes a reasonable recovery in one case and a possible duplicate operation in the other.

I think this is a useful place to judge technical writing. The sentence is readable, but the reader still has to discover the fact that decides whether to follow it.

## Giving a reader permission to proceed

A reference page can tell you what an endpoint accepts without telling you what to assume after a failure. That leaves an engineer to reconstruct behavior from experiments, or to ask someone who understands the server.

Stripe's [idempotent request documentation](https://docs.stripe.com/api/idempotent_requests) addresses the ambiguity directly: a retry with the same key returns the saved result, including an error result. It also describes when results begin to be saved and what happens when a retained key is reused with different parameters.

Those details change how you would implement a retry. They give you a reason to keep the operation's identity across attempts, plus conditions under which the guarantee applies.

Compare that with a page that says the API supports safe retries. A reader can understand those words and still generate a new key for each attempt, defeating the behavior the page meant to describe.

The writing has to reach the decision the reader will actually make. A definition of idempotency helps, but a definition alone does not tell someone where in their program to create the key.

Here is the sentence I would want beside that code: generate the key when you create the operation, and reuse it for retries of that operation within the service's retention rules. If the next attempt is a different operation, it needs its own identity.

That sentence carries a small design decision. Technical writing becomes valuable when it preserves decisions like this at the point where a reader might otherwise have to derive them again.

## Discovering what the product has promised

Consider a hypothetical export service whose reference says that a successful request returns a job ID. The team wants a quickstart, and the writer has enough information to show a request followed by a polling loop.

Then the writer asks what the ID means. The answer might be that the job has been stored durably, or only that a worker has accepted it in memory.

That distinction changes the recovery instructions after a restart. It also changes whether the client should keep waiting when its job disappears from the status endpoint.

If the team has not decided what acceptance promises, an elegant paragraph cannot settle it. The writer has found an unfinished product decision while trying to explain the product.

The unresolved statement belongs in the review itself: “After the server returns a job ID, a restart will not lose the accepted job.” Someone responsible for the service must either support that promise or replace it with the behavior the client can depend on.

A test might submit an export and restart the worker before it finishes. If the job remains available and completes, the test supports that behavior for the conditions tested.

If it disappears, the proposed guarantee needs a product change or a narrower sentence.

The test cannot establish behavior under every possible failure. It can stop a writer from quietly turning an expectation into a promise, and it gives the engineer a concrete claim to review.

I want technical writers involved before a feature's description is considered finished. Their questions can reveal that the interface lets a caller perform an action whose consequences the team has not agreed to explain.

The [division between code comments and written guides](/articles/code-documentation/) matters here. A comment can explain why a worker writes to storage before acknowledging a request, while a guide explains what that ordering permits the caller to do.

## Choosing which uncertainty belongs on the page

Taken too far, this argument would produce documentation that explains the whole service before letting someone call it. A quickstart would become an exhausting account of things that could go wrong.

Changing one assumption at a time helps decide what belongs. If that change would alter the reader's next action, the assumption needs to be stated before the action depends on it.

For the export example, the job's durability affects whether to resubmit it after a restart. The internal name of the queue can stay out of the guide if changing the name leaves the client's behavior unchanged.

The appropriate detail also depends on who is reading. Someone trying an export against disposable sample data can tolerate a loss that would be unacceptable to the operator exporting a customer's records.

A quickstart can state that its example uses disposable data and link to the operating procedure before inviting production use. The operating procedure then owes the reader a recovery path for the failure the quickstart set aside.

Brevity deserves a more demanding test than word count. Removing a sentence saves reading time only if the reader does not have to recover its information elsewhere before proceeding.

The reverse is true as well: adding an explanation costs attention when it cannot change the decision in front of the reader. A complete account of queue internals can obscure the single guarantee the caller needs.

The [API documentation template](/articles/api-documentation-template-the-pages-every-api-needs/) separates the initial request from recovery guidance, while keeping a direct link between them. The organization should follow the dependency between decisions.

## Reviewing the decision the prose supports

A useful review can begin with a failure report and the page meant to answer it. Ask a reviewer to choose the next action using only the page, then identify the sentence that justifies that choice.

If the reviewer has to inspect source code or ask the author whether the operation already happened, the documentation still depends on knowledge it has not supplied. That is a specific defect a writer can investigate.

If the page supplies the guarantee but the implementation contradicts it, the team has a different defect. Editing the prose to conceal the contradiction would leave the reader making the same unsupported decision.

The review should also allow the answer that the system cannot tell. The documentation then needs to explain how to investigate the result, or when to stop and seek help, instead of manufacturing certainty.

I would trust an export guide that tells me where its knowledge ends more than one that sends me into a retry loop with a reassuring adjective. When the first request times out, I need enough information to decide what to do with the second.
