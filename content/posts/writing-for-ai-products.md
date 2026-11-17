---
category: developer-experience
primary_query: technical writing for ai products
siblings:
- stripe-technical-blog
- devtools-documentation
- technical-writing-for-engineers
bridges:
- slug: writing-changelogs
  reason: Documentation is the content developers trust first.
- slug: llm-structured-outputs
  reason: Writing about an AI product starts from how the model behaves.
- slug: agents-reading-docs
  reason: A docs page now has agent readers.
date: 2026-03-31
description: 'Technical writing for AI products documents a contract the model can change: what a model name pins, the output contract and how to judge a writer.'
status: published
work_note: "A model update can leave every example in your docs showing output the product no longer gives. I'm Ninad Pathak, a freelance technical writer for AI companies, and rerunning and rewriting those examples is work I take on. [Hire me](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Technical Writing for AI Products: The New Rules'
slug: writing-for-ai-products
updated: 2026-11-17
---

A thread on Hacker News on November 8 gathered user reports that Claude Opus 5.5 had been "nerfed", and the reply that stayed with me asked a documentation question: ["Do you run evals as a matter of course?"](https://news.ycombinator.com/item?id=50420515)

The commenter's next sentence is the awkward one for anyone who does: "Everyone I know that does shows high levels of variance across them under the best case." The comment allows that labs sometimes downgrade a model, and ends that "without any measurement it's a non-interesting assertion".

Documenting that variance is the hard part of [developer content](/articles/developer-experience/) for an AI product.

Technical writing for AI products exists to make that argument answerable. A reader of ordinary API docs needs to know what a call returns, and a reader of AI product docs also needs to know what stays fixed behind a model name and how to check it.

## What does a model name promise in the docs?

It promises only what the page says it does, so the page has to say. OpenAI's [prompt engineering guide](https://developers.openai.com/api/docs/guides/prompt-engineering) is direct about the risk: "Even different snapshots of models within the same family could produce different results."

It recommends "Pinning your production applications to specific model snapshots", and tests that "measure prompt behavior".

That gives the writer a rule for every page with a model identifier on it. State whether the identifier is a snapshot or a moving alias, and give the date the example was last run against it.

Retirement dates belong in the docs too. Anthropic's [model deprecations page](https://platform.claude.com/docs/en/about-claude/model-deprecations) commits to "at least 60 days' notice before model retirement for publicly released models", and my post on [writing a changelog](/articles/writing-changelogs/) looks at one deprecation entry that carries its dates and its failure mode in two sentences.

## What is the output contract of an AI feature?

It is the schema the output follows, the cases where it won't, and what the caller has to check itself. OpenAI's [structured outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) puts all of that in two sentences, which I hold up as the model for any AI reference page.

"Structured Outputs constrains completed, non-refusal model output to your supplied JSON Schema. Your application still needs to handle refusals, incomplete responses, and API errors, and validate any business rules that the schema does not express."

A writer working from that standard documents which fields the schema guarantees and how a refusal arrives. My guide to [structured outputs](/articles/llm-structured-outputs/) goes through those cases for each vendor.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/writing-for-ai-products/example-pattern.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/writing-for-ai-products/example-pattern.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/writing-for-ai-products/example-pattern.svg" width="720" height="256" alt="The preferred pattern for an AI documentation example has four parts in order: a minimal working request, the exact output contract the response must follow, one failure or refusal case, and the production caveat that changes implementation choices." loading="lazy" decoding="async"></picture></a>
  <figcaption>Show the request, the contract, a refusal, and the caveat. Anything less demos well and deploys badly.</figcaption>
</figure>

The pattern in the figure is the smallest complete example for an AI endpoint. It has the request, the contract, one refusal and the caveat that changes how the caller builds.

## What makes a code sample trustworthy in AI docs?

It runs, its output is shown, and the page says which model produced that output.

Google's [technical writing course](https://developers.google.com/tech-writing/two/sample-code) lists what a correct sample must do, starting with "Build without errors." and "Perform the task it claims to perform."

An AI sample needs one thing more, because the same code returns different text next quarter. Print the output the sample produced, with the model snapshot and the date, so a reader whose result differs can tell a changed model from a broken integration.

A docs page can also ship a small eval, a set of prompts with expected properties, which gives every user the measurement that commenter asked for. The variance in the same comment sets its size.

My arithmetic for a prompt set scored pass or fail at a true rate of 80% gives a standard error near nine points at 20 runs and 2.8 points at 200. A handful of prompts run once can't show a five-point drop, so the page should say how many runs its numbers rest on.

## Who reads AI product docs besides developers?

Coding agents and retrieval systems read them, a paragraph at a time and without the surrounding page. A sentence such as "rate limits apply" sends a person to look up the number, and gives a coding assistant nothing to put in the client it is generating.

Writing for that reader means stating defaults and limits in the sentence where they matter, and showing the exact shape of an error. My [reading of Fern's agent traffic report](/articles/agents-reading-docs/) looks at how much of docs traffic is agents.

## How I would evaluate a technical writer for an AI company

Ask for evidence in five areas before looking at a general portfolio.

1. A prompt or system instruction documented with the precision of an API method.
2. A JSON schema explained with its refusal case and its validation boundary.
3. An example complete enough to run, with its output and model version shown.
4. A migration note for a model change that says what will behave differently.
5. A record of getting the real contract from engineers, in place of a paraphrase of the launch brief.

A further quality rarely appears in a job description, which is judgment about what to leave out. Strong AI writing omits guarantees the product can't keep and states uncertainty where the behavior is experimental.

The habits carry over from older developer products. [Stripe's engineering blog](/articles/stripe-technical-blog/) is my reference for explaining the hard part to the person integrating, and [documentation for developer tools](/articles/devtools-documentation/) names the pages to fix first on a startup's docs site.

Engineers writing these pages themselves can start from [technical writing for engineers](/articles/technical-writing-for-engineers/).

My page as a [freelance technical writer for AI companies](/services/freelance-technical-writer-for-ai-companies/) links the work I've published for Firecrawl and OpenComputer. The [Centus case study](/work/centus/) covers the localization guides, and [my work page](/work/) has the rest.

## FAQ

**How is technical writing for AI products different from ordinary API documentation?**

AI docs still need reference accuracy, and they also have to document behavior. That covers prompts, schemas, refusals, model versions and the evidence that an example was run.

**Should a technical writer for an AI company know how to run evals?**

Yes, at a practical level. A writer who can't read eval output can't say accurately what changed between two model versions.

**Do AI product docs need more tutorials or more reference pages?**

Fix reference first. Parameter defaults, schema guarantees and refusal handling are the details an integration depends on.

**Should writers own prompt libraries and system prompts?**

Shared ownership works best. Engineering owns runtime behavior, and writers own clarity and upgrade notes, which requires that writers can see the real prompts.

**What is the fastest way to tell whether an AI writer is strong?**

Ask them to rewrite one weak API page for an LLM feature, and give them the schema, a prompt template and a model upgrade note. A strong writer's version gets more specific.
