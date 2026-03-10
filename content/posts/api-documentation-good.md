---
title: "What Makes API Documentation Good: Lessons From Stripe, Twilio, and Resend"
date: 2026-03-20
description: "Most API documentation fails developers in the same three ways. Stripe, Twilio, and Resend figured out what good looks like. Here's what they got right."
tags: [technical-writing, api-docs, developer-experience, documentation]
status: published
---

API documentation is the most consequential writing in software. I say this with the passion of someone who has both been saved by good docs and ruined entire weekends wrestling with bad ones. A developer who can't figure out your API in 20 minutes will either give up or find a workaround that haunts your support queue for years. A developer who gets to a working implementation in 10 minutes will recommend your product to three colleagues. I've been both of these developers.

The difference between those outcomes is almost entirely documentation quality. I've spent six years reading, writing, and debugging API docs for DevTools companies. Some teams have figured this out. Most haven't, and you can feel the difference immediately. The distance between the good and the mediocre is not effort, since both sides have worked hard on their docs. The distance is understanding what developers actually need at each stage of the integration journey. It's empathy, applied systematically.

## The three audiences your API docs serve

Every API has three distinct audiences that need different things. I learned this the hard way after writing docs that served one audience well and completely failed the other two.

The evaluator is deciding whether to use your API at all. They have 15 minutes and a GitHub tab open. They want to know: what does this API actually do, how is it authenticated, and can they see a working example before committing to a deeper read. They will not read conceptual documentation at this stage. They want evidence that the API does what it says. I've been this person dozens of times. The API that gets me to "hello world" fastest usually wins.

The implementer is integrating the API into a production system. They need accurate reference documentation for every endpoint, comprehensive error codes, rate limit behavior, and enough worked examples to cover their specific use case. They'll hit edge cases that the happy-path docs don't cover. The quality of your docs here determines how many support tickets you receive. I've opened too many of those tickets. I've also been the one answering them, and I know the pain on both sides.

The debugger has something broken and is trying to figure out why. They need error codes with specific explanations, not just "invalid request." They need response examples for error states, and information about API behavior under edge conditions: what happens when a rate limit is hit, what happens during a provider outage, what the retry behavior should be. This is where most docs fail, and it's so frustrating because it's where developers are often most desperate for help.

Most API docs are written for the implementer and fail the evaluator and debugger. The best docs serve all three. When I find docs that do this well, I bookmark them and study them. They're rarer than they should be.

## What Stripe got right

Stripe's API documentation is widely cited as the gold standard. Having spent significant time in it while writing integration guides, I want to be specific about what actually makes it excellent, because "it's good" isn't actionable advice.

Every endpoint has a working curl example. Not pseudocode, not YOUR_SECRET_KEY, but a real curl command you can run after swapping in your test key. This sounds obvious. Walk through the docs for 20 APIs and count how many actually do it. I've done this exercise. The number is depressingly low. Stripe does it for every single endpoint, and that consistency matters. It tells developers that every endpoint is equally real, equally supported.

The reference and the guide are genuinely separate. Stripe's reference documentation is a machine-readable index of every endpoint, parameter, and response field. The guides are prose explanations of how to accomplish specific goals: accept a payment, set up subscriptions, handle disputes. The two formats serve different readers and aren't muddled together. I know exactly where to go depending on what I need. That clarity is a gift.

Error handling is documented at the same level as success cases. Every Stripe error has a code, a category, and specific guidance on how to handle it. The card_declined error, for instance, distinguishes between insufficient_funds, do_not_honor, and fraud_block and explains what each means for retry logic. That's the level of detail that saves developers from shipping bad retry implementations. I've implemented those retry logics. Having that guidance upfront is the difference between a confident implementation and a nervous one.

The changelog is a first-class document. Breaking changes are announced with migration guides. Versioning behavior is explicit. Developers building on Stripe know what to expect when things change, which removes a category of anxiety from the integration. I cannot overstate how much this matters. The APIs I've integrated that don't have this leave me constantly worried that something will break without warning.

## What Resend got right

Resend launched in 2023 and quickly earned a reputation for excellent developer experience. Their approach is different from Stripe's, and worth studying for the specific things they prioritize.

SDK-first documentation means Resend documents every integration from the SDK perspective, not the raw HTTP perspective. If you're building in TypeScript, the TypeScript examples are first-class, not an afterthought. The code you copy is idiomatic for your language. As someone who has spent too much time translating Java examples into Python, this feels like being seen.

Copy-paste completeness means every code example in Resend's docs is complete: imports included, error handling included, environment variable setup shown. You can paste it into an empty file and run it. The psychological effect of documentation that actually works on first try is significant. It builds trust that the rest of the docs are also accurate. I remember the first time I tried Resend's quickstart. It worked on the first try, and I felt a little rush of joy. That's the feeling you want to give developers.

Minimal prose means Resend's docs are short. They don't explain email infrastructure theory before showing you how to send an email. The explanation of DKIM, SPF, and DMARC exists, but it's behind a link, not between the developer and their working example. This respects the developer's time and their ability to find context when they need it.

## What Twilio got right and what they struggled with

Twilio built enormous market share on the strength of developer experience in their early years. Their quickstart guides are still useful to study: they start with the absolute minimum viable implementation like sending one SMS or making one phone call, verify that it works, and then layer in complexity.

The quickstart philosophy matters because developers don't learn APIs by reading reference documentation. They learn by getting something working and then extending it. A quickstart that gets to "it worked" in under 10 minutes is worth more than 100 pages of comprehensive reference docs for a developer evaluating whether to build on your platform. I've abandoned APIs because I couldn't get to "it worked" quickly enough. It doesn't matter how powerful your API is if developers can't experience that power.

Twilio's struggle as they scaled was consistent quality across a large surface area. The core voice and SMS docs are excellent. The peripheral products are uneven. Maintaining documentation quality across a growing API surface is an organizational problem as much as a writing problem. The team maintaining the documentation needs to be as close to the product as the team building it. I've seen this pattern repeat at other companies. The initial docs are great because they're written by the founders. Then the API grows, the docs team gets bigger, and the connection to the product gets weaker.

## The documentation patterns that consistently fail

"See our GitHub repository for examples" is not documentation. The examples in the repository are not documentation. They're examples. Without context, navigation, and explanation, they serve the developer who already understands the API, not the one trying to learn it. I've been that confused developer too many times, staring at example code that assumes knowledge I don't have.

Long conceptual intros before working code fail because developers do not read 1,500 words of conceptual explanation before seeing an example. They skip to the code. If the conceptual explanation is necessary for the code to make sense, put the explanation adjacent to the code, not before it. I skip those intros. Everyone I know skips those intros. Write for how developers actually read.

Response schemas without examples fail because listing every field in an API response is necessary but not sufficient. Show the actual JSON. Show what a nested object looks like when populated. Show what an empty array response looks like. Documentation that describes structure without showing it makes developers write their own test scripts just to see what the data looks like. I've written those scripts. They're annoying and unnecessary.

Error codes without severity or handling guidance fail because "Error 422: Unprocessable Entity" tells a developer nothing useful. What caused it, which field was invalid, what's the expected format, and should they retry or fix the request? Those questions need answers in the error documentation. I've been stuck on bugs for hours because the error documentation didn't tell me what the error actually meant.

Docs that assume the happy path fail because real integrations encounter rate limits, authentication expiration, partial failures, and concurrent request conflicts. Documentation that only covers the success case leaves developers writing defensive code against behaviors they can't predict. Production systems are built on handling failures gracefully. The docs should help with that.

## The practical writing process for API docs

When I write API documentation, my process starts with the implementation, not the outline. I have to use the API myself to know where the confusion points are.

Build the integration myself from the raw reference. Document every point of confusion: where did the reference docs fail me, what did I have to figure out by trial and error, what error did I get before I got the success response? Every point of confusion is a documentation gap. I keep a running list of these as I work. They're gold for the writing process.

Write the quickstart first. Get a developer from zero to working in as few steps as possible. Time how long it takes someone unfamiliar with the API to follow the quickstart and reach success. That's your baseline. If it takes more than 10 minutes, something is wrong. I've had clients where we got it down to 3 minutes. That should be the goal.

Write the reference from the API behavior, not the internal implementation. The reference docs describe the API's contract: inputs, outputs, errors, constraints. They're not an explanation of how the API works internally. Developers don't care about your internal architecture. They care about what they can rely on.

Then add the guides for the specific use cases developers will actually implement. Not "introduction to our payments API" but "implement a subscription with a free trial period" or "migrate from PayPal to our checkout." Specific, actionable, named outcomes.

The test of whether API documentation is good: can a competent developer reach a working production integration without asking your support team a question? If yes, the docs are doing their job. That's the standard I hold myself to.

## What this means for teams building developer products

API documentation is not a marketing problem. It's not a design problem. It's a technical writing problem that requires someone who has built integrations, who knows what questions developers actually ask, and who cares whether the example code runs.

Teams that treat API docs as a checklist item, something that needs to exist rather than something that needs to be good, will pay for it in support volume, integration abandonment, and developer advocacy that goes negative rather than positive. I've seen the analytics on this. Bad docs are expensive in ways that don't show up in the documentation budget line.

The competitive advantage of excellent API docs compounds. A developer who had a good experience with your documentation will give you the benefit of the doubt the next time they're evaluating your product. They'll recommend you specifically because "their docs are actually good." That word-of-mouth is free and it's driven entirely by documentation quality.

Stripe built a company culture where documentation quality is treated as seriously as product quality. That's not a coincidence. It's why they're the reference point everyone uses. I want every client I work with to have that ambition.
