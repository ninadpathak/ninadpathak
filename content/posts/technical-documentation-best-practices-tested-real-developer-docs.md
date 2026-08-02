---
title: "Technical Documentation Best Practices, Tested on Real Developer Docs"
date: 2026-08-02
updated: 2026-08-02
description: "A practical documentation review built from how Stripe, FastAPI, and GitHub make reader tasks, failures, and limits visible."
tags: ["documentation", "technical-writing", "developer-experience"]
takeaways:
  - "Give each page one reader task and one observable success state."
  - "Put failure handling beside the action that can fail."
  - "Use limits and recovery steps as part of the interface, not as footnotes."
status: published
slug: "technical-documentation-best-practices-tested-real-developer-docs"
---

Good technical documentation doesn't become useful when every endpoint has a page. It becomes useful when a developer can complete a task, recognize the result, and recover when the first attempt fails.

I reviewed three documentation systems that make those jobs unusually clear: [FastAPI's error-handling guide](https://fastapi.tiangolo.com/tutorial/handling-errors/), [Stripe's idempotency reference](https://docs.stripe.com/api/idempotent_requests), and [GitHub's REST API rate-limit guide](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api). They cover different products, but they converge on the same rule: the documentation has to describe the state change and its boundary together.

## Start with the task, not the product map

A new reader doesn't arrive looking for your internal taxonomy. They arrive with a job such as “return a useful 404,” “retry a network failure safely,” or “find out why this request stopped working.”

FastAPI's error guide starts with a missing item and shows the response state directly. The important design choice isn't the `HTTPException` import.

The reader sees the condition, status code, and response body in one small path. That gives the page a finish line.

Use that test when you review a page:

| Page type | Reader task | What proves completion |
| --- | --- | --- |
| Tutorial | Complete the first useful action | A command, request, or screen state the reader can recognize |
| How-to | Change one system behavior | The exact input and the expected result |
| Reference | Resolve a stable question | A field, default, constraint, or type with its boundary |
| Troubleshooting | Recover from a known failure | Symptom, diagnostic check, cause, and recovery |

A page can include more detail later. It should not make the reader infer the first successful state.

## Put failure handling beside the risky action

The weakest documentation teaches the happy path, then hides recovery in a distant FAQ. That structure looks clean until a developer gets a timeout, a duplicate request, or a rate-limit response in production.

Stripe's idempotency documentation makes retry behavior part of the request contract. An idempotency key lets a client repeat a request after a connection failure without accidentally creating the object twice, provided the request is retried with the same key and parameters.

The boundary matters as much as the recommendation. A reader needs to know what retry is safe, what input identifies the operation, and which mismatch invalidates that assumption.

Write error guidance where the action appears when the answer changes the implementation. For an API request, that normally means showing:

1. the expected success response
2. the failure shape or status range
3. the retry, backoff, or repair decision
4. the condition that makes the repair unsafe

That is not extra support content. It is part of the interface a client is implementing.

## Make limits observable before they become incidents

Rate limits are another documentation test. A vague warning that an API “may throttle traffic” doesn't help a developer decide whether to queue work, slow down, or investigate an account configuration.

GitHub's REST API documentation names the relevant headers and distinguishes primary from secondary limits. Its troubleshooting guide also connects a limit response to an observable state such as `x-ratelimit-remaining: 0`.

That detail turns a support symptom into a check a developer can automate.

Your own limit pages should answer four questions without sending the reader hunting across product marketing and support articles:

- Which resource is limited?
- How can the client observe the remaining capacity?
- What response or error marks exhaustion?
- What should the client do next, and when should it not retry?

The strongest objection is that this makes a quickstart longer. It can, especially for a small product with one uncomplicated endpoint.

Keep the first path short when the failure mode is genuinely obvious. Once retries, permissions, asynchronous work, or quotas can change the result, brevity becomes concealment.

## Give each page an owner

Documentation starts to drift when tutorials, reference pages, release notes, and support articles all explain the same behavior differently. The fix is not more navigation.

It is deciding which page owns which reader question.

Use the [documentation organization guide](/articles/how-to-organize-a-documentation-site/) to settle overlapping page roles before you add new sections. Then use the [documentation review checklist](/articles/documentation-review-checklist-before-you-publish/) before release to confirm that each page still has a reader task, evidence, and a useful last move.

A useful documentation review ends with a smaller, sharper system. Keep the page that can prove a reader task.

Move duplicate detail to the page that owns it. Add failure guidance wherever the action can fail.

That is how documentation becomes dependable under pressure, not just readable in a calm demo.
