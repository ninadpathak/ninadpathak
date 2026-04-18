---
title: "Technical Writing for Engineers: The 80/20 Guide"
date: 2026-04-18
description: Most engineering documentation fails for the same reasons. Here is what actually moves the needle.
tags: [technical-writing, developer-experience, engineering-culture]
status: published
---

Documentation debt accumulates silently. It starts when a project ships without a README. It compounds when features get added but never explained. It becomes critical when a new engineer joins and spends three days reconstructing knowledge that existed in someone's head. I watched this happen at my last job. The senior engineer who built the entire auth system left. Three new engineers spent two weeks rebuilding knowledge that was documented nowhere.

This is the default trajectory for most engineering teams. Documentation gets treated as a post-launch chore rather than a first-class engineering artifact. The result is a consistent failure mode: technical writers who cannot keep up with the pace of development, and engineers who do not trust documentation because it is perpetually out of date.

The 80/20 rule applies here. Twenty percent of documentation practices deliver eighty percent of the value. The rest is ceremony.

## The core problem

Most technical writing fails because it is written for the wrong audience. The author writes to demonstrate understanding rather than transfer it. Every sentence is written from the author's perspective — what the author knows, what the author thinks is important, what the author remembers.

The reader needs the opposite. The reader arrives with a specific gap. They do not care what you know. They care whether your documentation closes the gap between where they are and where they want to be.

This is a perspective shift that sounds simple but changes everything. When you write for the reader, you structure around questions, not topics. You anticipate confusion points before they happen. You provide working code before explaining edge cases. You prioritize the happy path and treat exceptions as secondary.

## Start with the task, not the concept

The most common mistake in engineering documentation is starting with background. Authors spend three paragraphs explaining what a system is before telling the reader how to use it.

Readers do not read linearly. They scan for action. If they cannot find what they need in thirty seconds, they leave or they ask a colleague. Either outcome means your documentation failed.

Lead with the task. State what the reader will accomplish. Show the concrete steps. Then provide context.

Example of the wrong order:

> "GraphQL is a query language for APIs. It was developed by Facebook in 2012 and open-sourced in 2015. Unlike REST, GraphQL allows clients to request exactly the data they need. This reduces over-fetching and gives frontend teams more autonomy. In this tutorial, we will cover how to set up a GraphQL server with Node.js."

Example of the right order:

> "Initialize a GraphQL server in Node.js:
>
> `npm install express-graphql graphql`
>
> Define your schema:
>
> `const schema = buildSchema('type Query { hello: String }');`
>
> GraphQL lets clients request exactly the fields they need, reducing the over-fetching that plagues REST endpoints. If this is your first time with GraphQL, read the official schema guide before continuing."

The second version respects the reader's time. It provides a working starting point immediately. The concept follows the action.

## Code that works beats code that explains

Every code example in documentation should be copy-paste-run. Not almost run. Run. This is a hard constraint.

If your code example has a missing import, a wrong variable name, or an API call that was changed three versions ago, you have actively wasted the reader's time. Engineers will forgive a poorly written explanation. They will not forgive code that does not work.

Write code examples as complete files when possible. Partial snippets force the reader to reconstruct the missing context. Complete examples let the reader verify the solution in under two minutes.

Test every code block. Run it yourself. Change the dependency versions to match your documentation's stated requirements and run it again. If you cannot run it successfully, either fix it or remove it.

The discipline here is brutal: if you are not willing to maintain it, do not write it.

## Name things precisely

Technical writing for engineers requires exact naming. Vague terminology creates cognitive overhead.

Avoid phrases like "the system," "it," "this module," "the component." Replace them with specific names. "The AuthService," "the background job queue," "the rate limiter." Specific names let readers build a precise mental model.

Avoid undefined acronyms in the introduction. If you use JWT, spell out what it means the first time: JSON Web Token (JWT). Engineers from different backgrounds may know the acronym but not its expansion, or vice versa.

Avoid vague verbs: "handle," "manage," "process." Instead, describe what actually happens. "The retry handler attempts the request up to three times with exponential backoff." That sentence contains no ambiguity. "The system handles retries" could mean anything.

## Structure for scanning

Engineers rarely read documentation from top to bottom. They scan. They look for keywords. They jump to the section most likely to contain their answer. Only when they are fully lost do they read linearly.

Write for this behavior. Use headings that function as answers, not topics. "Timeouts cause memory leaks in long-running workers" is a better heading than "Timeout handling." The former tells the reader what they will learn. The latter tells them what the section is about.

Use bullet points for lists of related things. Use numbered lists for sequential steps. Do not use bullet points for sequential steps — the ordering implied by a numbered list carries information.

Use code blocks for code. Use bold for UI labels and filenames. Avoid italics in technical writing — they are harder to read at speed and add no information in this context.

Keep paragraphs short. Two sentences maximum. This is not a style preference. It is functional. Short paragraphs break information into digestible chunks. When a paragraph exceeds three sentences, the reader has to work to identify which sentence carries the point.

## The four documentation types

Engineers need four types of documentation, and conflating them is a common failure.

**Tutorials** take a newcomer from zero to a working result. They are task-oriented and forgiving of complexity. Tutorials should say "here is how to build X" and hold the reader's hand through every step. The goal is success, not completeness.

**How-to guides** solve a specific problem for someone who already knows the basics. "How to configure OAuth with an existing Next.js app" is a how-to guide. It assumes the reader understands OAuth conceptually but needs help with the implementation details.

**Reference documentation** describes the API, CLI, or library as it exists. Reference docs are exhaustive, accurate, and boring. They answer "what does this parameter do?" not "why would I use this?" Examples and usage notes belong in reference docs, but they come after the parameter description.

**Explanation** explores a topic, discusses trade-offs, and provides context. "Why does eventual consistency make debugging harder?" is an explanation article. It does not give steps. It builds understanding.

Most teams produce only reference documentation and wonder why their docs feel cold. Reference material is necessary but insufficient. I have seen teams with great reference docs still have terrible developer experience because nobody wrote tutorials.

## Version control your documentation

Documentation belongs in version control. This is non-negotiable.

When docs live in Google Docs or Confluence, they rot. API versions change. Flags get renamed. Screenshots go stale. Nobody knows when the document was last updated. Diff history is nonexistent. Rollback is painful.

Markdown in a Git repository solves all of this. Changes have authors and timestamps. PRs enable review. Branches let you update docs for new API versions without breaking the current documentation. The diff view shows exactly what changed and why.

This also enables docs-as-code. Engineers can update documentation in the same PR as the code that changed. The documentation and the feature ship together. No more documentation sprints that never happen.

The tooling cost is near zero. Every static site generator — Hugo, MkDocs, Docusaurus, Astro — supports Markdown. GitHub Pages, Netlify, Cloudflare Pages, and Vercel all serve static sites for free. There is no reason to accept documentation rot.

## Measure whether docs work

You can improve what you measure. For documentation, the right metrics are behavioral, not vanity.

Bad metrics: pageviews, time on page, number of documents, doc coverage percentage. These measure activity, not outcomes.

Good metrics: task completion rate, support ticket deflection, time-to-answer for common questions, percentage of new engineers who rate onboarding docs as helpful. These measure whether the documentation actually works.

You can run a task completion survey at the bottom of every how-to guide. "Did this solve your problem? Yes / No." It takes five seconds for the reader. It gives you signal within days.

Read the search queries that return no results on your internal search. Those are documentation gaps. When engineers search for something and find nothing, they ask a colleague or open a support ticket. Both outcomes are documentation failures.

## The update discipline

Documentation has a half-life. The moment you publish a new feature, your documentation starts becoming outdated. Features get renamed. Flags get deprecated. Screenshots diverge from the current UI.

The only solution is treating documentation as code. When you change the behavior of a feature, you change the documentation in the same PR. If you cannot do this, at minimum add a "Last verified" timestamp to the top of the document. This sets expectations and creates accountability.

Automate staleness detection where possible. Run scripts that flag docs older than six months. Build a culture where updating docs is a normal part of feature work, not a separate project that never happens.

## What to cut

Documentation debt is not just about missing content. It is also about content that should not exist.

Delete onboarding documents that contradict the current codebase. Delete tutorials that reference deprecated API versions. Delete FAQ entries that are no longer questions anyone asks. Stale documentation is worse than no documentation because it sends engineers down wrong paths.

The test for keeping a document: does this help someone accomplish a task or understand a concept that exists in our current system? If not, cut it.

Every document you keep is a document you are committing to maintain. Be selective.

## The minimal viable documentation stack

You do not need a full documentation platform to start. You need three things.

A repository of Markdown files with a clear folder structure. Keep reference docs separate from tutorials. Keep internal docs separate from external docs.

A static site generator that produces a searchable site. Docusaurus, MkDocs Material, and Hugo with a documentation theme all satisfy this. Choose based on your team's existing tooling.

A convention: every feature PR includes a documentation update. This is the only process change required. Everything else follows from this.

You can add a documentation team, a content calendar, a style guide, and automated freshness checks. None of it matters if the documentation and the code ship independently. Start with the discipline. Add tooling later.

## The compounding return

Documentation compounds. Every accurate document you publish reduces the number of repetitive questions your team answers. Every tutorial that works shortens the time it takes a new engineer to contribute. Every reference doc that is kept current saves hours of debugging from engineers using outdated information.

The return on investment is not linear. The first document saves a few hours. The tenth document saves a full day per week. The fiftieth document makes your engineering team measurably faster.

The teams with excellent documentation did not start with excellent documentation. They started with the discipline to write it and the process to keep it current.

That discipline is what separates docs that gather dust from docs that engineers actually use.
