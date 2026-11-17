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

RTFM is the oldest reply in developer support. It stands for "read the manual", with a ruder word in the middle, and [Wikipedia's entry](https://en.wikipedia.org/wiki/RTFM) describes it as the answer given when a question is already covered in the documentation.

The insult assumes the manual works. A page can be accurate in every sentence and still fail the moment a reader leaves the happy path, and nobody learns that by proofreading it.

So my version of technical documentation best practices is one test: can someone finish a task, see that it worked, and recover from the failure likeliest to interrupt them? I've checked it below against real [technical documentation](/articles/technical-documentation/): FastAPI's and Stripe's docs and GitHub's rate-limit guide, all read again on November 18.

There's a [review card](/static/templates/documentation-review-card.md) to go with it. It's one page, and you fill it in against a single important page of your own docs.

## What are the best practices for technical documentation?

I'd put four ahead of everything else, and each one answers a question a stuck reader is asking:

| Practice | The reader's question |
| --- | --- |
| Start with a task and a visible result | Did it work? |
| Put recovery beside the action that can fail | It didn't work, so what now? |
| Make limits something a client can inspect | How close am I to being cut off? |
| Give every question one page that owns it | Which of these pages is right? |

Style guides cover tone and terminology, and those matter. These four come first for me because a reader who can't finish the task never gets far enough to notice the tone.

## How do you start a page with a task?

Name the job the reader came with and show what done looks like. People don't arrive to learn your content model, and they do arrive needing to return an error or retry a request safely.

[FastAPI's error-handling guide](https://fastapi.tiangolo.com/tutorial/handling-errors/) is my example. It opens with the errors a client has to be told about, reaches `HTTPException` after that, and then shows the response the client receives.

What done looks like depends on the kind of page:

| Page type | Reader task | What proves completion |
| --- | --- | --- |
| Tutorial | Complete a first useful action | A command, response, or screen state |
| How-to | Change one system behavior | The input and expected result |
| Reference | Resolve a stable question | A field, default, constraint, or type |
| Troubleshooting | Recover from a known failure | Symptom, diagnostic, cause, and recovery |

## Where should recovery guidance go?

Put it beside the action that can fail. The costly version of this mistake is distance: a reader sees a request in one guide, hits a timeout, and has to search a separate FAQ to learn whether retrying will charge the customer twice.

[Stripe's idempotency reference](https://docs.stripe.com/api/idempotent_requests) makes the retry part of the request's contract. It tells you that with an idempotency key you can "safely repeat the request without risk of creating a second object", and it says what happens when a retry arrives with different parameters.

That's the structure I'd copy for any step with a real failure mode:

1. Show the expected success state.
2. Name the response or error that signals failure.
3. Explain the repair, the retry or the backoff.
4. State the condition that makes that repair unsafe.

Yes, it makes a quickstart longer. For a simple, reversible step that's a fair objection, and for anything involving permissions, retries or quotas, leaving recovery elsewhere just moves the decision onto the reader.

## How should documentation describe a limit?

Give the reader a signal they can check before they hit it. A sentence saying an API "may throttle traffic" doesn't help anyone decide whether to queue work or slow down.

[GitHub's rate-limit guide](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) lists the response headers that carry the state, including `x-ratelimit-remaining`. It also says what to do at zero, which is to wait until the time in `x-ratelimit-reset`.

For each limit, I'd answer these in one place:

- What resource is limited?
- Which header, field or dashboard value shows what's left?
- What marks exhaustion?
- What should the client do next, and when should it stop retrying?

The review card has a table for this. If you can't fill in the signal and recovery columns, the page hasn't given the reader enough control yet.

## Who should own each question?

A single page should, and the others should link to it. Docs drift when a tutorial, a reference page and a support article each explain the same behavior in slightly different words.

Pick the owner, then link outward for prerequisites and parameter detail. [Documentation structure](/articles/documentation-structure/) covers how to split those roles, and [documentation review](/articles/documentation-review/) covers the checks before release.

The owner also needs to know what makes the page stale. A changed permission or a new response shape should send it back for review, and a calendar reminder won't catch either.

## How do you test documentation against these practices?

Run the task. The card has a row for each thing covered above, from the reader and the task down to the limit signal and the owner, and every blank cell is a change to make.

I'd start with the riskiest page you have. A payment request or an authentication guide will teach you more than a glossary entry.

You can also hand the task to a machine now. A tool called [Gauge](https://github.com/gauge-sh/gauge-cli), posted to Hacker News on November 4, "runs real agents against your product, captures where they get stuck", which is the same test with a different reader.

Either way the aim isn't longer documentation. It's a page that doesn't leave the reader guessing whether the next step is safe, and you can [download the review card](/static/templates/documentation-review-card.md) to find out where yours does.

## FAQ

**What makes technical documentation good?**

A reader can finish the task it describes and tell that it worked. Accuracy is required for that and doesn't guarantee it.

**Should a quickstart include error handling?**

For the failure a reader is likeliest to hit, yes. A quickstart that shows only the happy path sends the first stuck reader to support.

**How often should documentation be reviewed?**

When the product changes under it. A renamed field or a revised quota is a better trigger than a date.

**What is a documentation review card?**

It's a one-page form that records a page's reader and task, along with its success state and its owner. Filling it in shows which of those the page doesn't state.
