---
category: technical-documentation
primary_query: technical documentation best practices
siblings:
- documentation-structure
- documentation-review
date: 2026-08-02
description: Technical documentation best practices come down to one test. Can a reader
  finish a task, see that it worked, and recover from the likeliest failure? Checked
  against FastAPI, Stripe and GitHub docs, with a review card.
slug: documentation-best-practices
status: published
work_note: "This post tests the usual documentation advice against real developer docs, for the team that has read the advice and still isn't sure its pages work. If you'd rather have someone run your product and rewrite the pages that fail, that's what I do. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. [Work with me on it](/services/)."
takeaways:
- Give every page one reader task and an observable success state.
- Put recovery guidance beside the action that can fail.
- Make limits inspectable and assign each reader question to one page owner.
title: Technical Documentation Best Practices, Tested on Real Developer Docs
updated: 2026-08-02
video: documentation-best-practices
---

[RTFM](https://en.wikipedia.org/wiki/RTFM) is the oldest reply in developer support, and it assumes the manual answers the question. A documentation page can be accurate in every sentence and still fail the moment a reader leaves the happy path, for example when their first request returns a 401, and proofreading the page won't reveal that failure.

So my version of technical documentation best practices is one test: can a reader finish a task, see that it worked, and recover from the failure likeliest to interrupt them? I've applied that test below against real [technical documentation](/articles/technical-documentation/): FastAPI's and Stripe's docs and GitHub's rate-limit guide, all read again on November 18.

I've also turned the test into a [review card](/static/templates/documentation-review-card.md) that you can download. The card is one page long, and you fill it in while reading one important page of your own docs, such as your authentication guide.

## What are the best practices for technical documentation?

I'd put four practices ahead of everything else, and each of the four answers a question that a stuck reader is asking:

| Practice | The reader's question |
| --- | --- |
| Start with a task and a visible result | Did it work? |
| Put recovery beside the action that can fail | It didn't work, so what now? |
| Make limits something a client can inspect | How close am I to being cut off? |
| Give every question one page that owns it | Which of these pages is right? |

A style guide such as [Google's developer documentation style guide](https://developers.google.com/style) covers tone and terminology, and both matter. The four practices in the table come first for me because a reader who can't finish the task stops reading before tone makes any difference.

## How do you start a page with a task?

Start a page by naming the job the reader came to do and showing the result that proves the job is done. A reader opens your docs needing to return an error from an endpoint or retry a payment safely.

[FastAPI's error-handling guide](https://fastapi.tiangolo.com/tutorial/handling-errors/) is my example of a page that starts with the task. The guide opens with the errors a client has to be told about, introduces the `HTTPException` class after that, and then shows the JSON response the client receives.

The result that proves the job is done depends on the type of page:

| Page type | Reader task | What proves completion |
| --- | --- | --- |
| Tutorial | Complete a first useful action | A command, response, or screen state |
| How-to | Change one system behavior | The input and expected result |
| Reference | Look up a fact that stays the same between tasks | A field, default, constraint, or type |
| Troubleshooting | Recover from a known failure | Symptom, diagnostic, cause, and recovery |

## Where should recovery guidance go?

Put recovery guidance on the same page as the action that can fail, directly under it. When recovery lives elsewhere, a reader copies a payment request from one guide, gets a timeout, and has to search a separate FAQ to learn whether retrying will charge the customer twice.

[Stripe's idempotency reference](https://docs.stripe.com/api/idempotent_requests) documents the retry in the same place as the request. The page tells you that with an idempotency key you can "safely repeat the request without risk of creating a second object", and it says that a retry with different parameters returns an error.

I'd copy Stripe's structure for any step that can fail in a way the reader has to handle:

1. Show the expected success state.
2. Name the response or error that signals failure.
3. Explain the repair, the retry or the backoff.
4. State the condition that makes that repair unsafe.

Adding recovery guidance does make a quickstart longer. For a simple step that the reader can undo, such as creating a test project, the extra length isn't worth it.

For a step that involves permissions, retries or quotas, leaving out the recovery guidance forces the reader to decide alone whether a retry is safe.

## How should documentation describe a limit?

Documentation should describe a limit by naming a signal the reader can check before they hit the limit. A sentence saying an API "may throttle traffic" doesn't help anyone decide whether to queue work or slow down.

[GitHub's rate-limit guide](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) lists the response headers that report how much of the limit is left, including `x-ratelimit-remaining`. The guide also says what a client should do when `x-ratelimit-remaining` reaches zero, which is to wait until the time given in `x-ratelimit-reset`.

For each limit in your product, I'd answer these four questions on one page:

- What resource is limited?
- Which header, field or dashboard value shows what's left?
- What marks exhaustion?
- What should the client do next, and when should it stop retrying?

The review card has a table with one row per limit. If you can't fill in the signal column and the next-action column for a limit, the page doesn't yet tell a reader how to see the limit coming or what to do after hitting it.

## Who should own each question?

A single page should own each question, and every other page that touches the question should link to the owner. Docs drift apart when a tutorial, a reference page and a support article each explain the same behavior in slightly different words.

Pick the owning page for a question such as "how do I rotate an API key?", then link from it to the pages that hold prerequisites and parameter detail. [Documentation structure](/articles/documentation-structure/) covers how to split one topic across a tutorial, a how-to and a reference page, and [documentation review](/articles/documentation-review/) covers the checks before release.

The person who owns a page also needs to know which product changes make the page wrong. A changed permission or a new response shape should send the page back for review on the day it ships, and a calendar reminder every six months would catch neither change in time.

## How do you test documentation against these practices?

Test a page by doing the task it describes, from a clean account, while filling in the review card. The card has a row for each thing covered above, from the reader and the task down to the limit signal and the owner, and every blank cell is a change to make.

I'd start with the page where a reader's mistake is costliest. Testing a payment guide or an authentication guide will show you more missing recovery steps than testing a glossary entry.

You can also give the task to a coding agent and watch where the agent fails. A tool called [Gauge](https://github.com/gauge-sh/gauge-cli), posted to Hacker News on November 4, "runs real agents against your product, captures where they get stuck", which is my one-task test with an agent as the reader.

Whether a person or an agent runs the test, the goal is a page that tells the reader whether the next step is safe. [Download the review card](/static/templates/documentation-review-card.md) to find the steps where your page doesn't.

## FAQ

**What makes technical documentation good?**

Good technical documentation lets a reader finish the task it describes and tell that the task worked. An accurate page can still fail that test if it never shows what success looks like.

**Should a quickstart include error handling?**

Yes, for the failure a reader is likeliest to hit, such as an invalid API key. A quickstart that shows only the happy path sends the first stuck reader to support.

**How often should documentation be reviewed?**

Review a documentation page when the product it describes changes. A renamed field or a revised quota is a better trigger for a review than a date on a calendar.

**What is a documentation review card?**

A documentation review card is a one-page form that records a page's reader and task, along with its success state and its owner. Filling in the card shows which of those four things the page doesn't state.
