---
title: "Technical Writing for Engineers: The 80/20 Guide"
date: 2026-04-18
description: Most engineering documentation fails for the same reasons. Here is what actually moves the needle.
tags: [technical-writing, developer-experience, engineering-culture]
status: published
---

Documentation debt accumulates silently. It starts when a project ships without a README, compounds when features get added but never explained, and becomes critical when a new engineer joins and spends three days reconstructing knowledge that lived in one person's head. I watched this play out at my last job. The senior engineer who built the entire auth system left, and the three people who inherited it spent two weeks rebuilding things like the token refresh flow and the permission model, none of which was written down anywhere.

Treated as a post-launch chore rather than a first-class engineering artifact, documentation defaults to the same place on most teams. The failure mode is consistent: technical writers who cannot keep up with the pace of development, and engineers who stop trusting the docs because they are perpetually out of date.

A version of the 80/20 rule applies here. Roughly twenty percent of documentation practices deliver most of the value. The rest is ceremony.

<div class="visual-wrapper">
  <div class="visual-title">The 80/20 of Doc Impact</div>
  <div class="visual-container">
    <iframe src="/static/visuals/docs-8020.html" title="Sorted impact bars showing the few documentation practices that move the needle versus the many that do not" loading="lazy"></iframe>
  </div>
</div>

## The core problem

Most technical writing fails because it is written for the wrong audience. The author writes to demonstrate understanding rather than transfer it, so every sentence comes from the author's perspective: what the author knows, what the author thinks is important, what the author happens to remember.

What the reader needs runs the other way. Someone arriving at your page has one specific missing piece, like the exact env variable that makes the local server boot. They do not care what you know. They care whether your documentation gets them from where they are stuck to the thing that works.

That perspective flip sounds small and changes everything downstream. Writing for the reader means you structure around questions instead of topics, anticipate the confusion points before they hit, hand over working code before you explain edge cases, and treat the happy path as the main event with exceptions kept secondary.

## Start with the task, not the concept

The most common mistake in engineering documentation is starting with background. Authors spend three paragraphs explaining what a system is before telling the reader how to use it.

Scanning for action is what readers actually do, not reading top to bottom. Someone who cannot find the relevant command in thirty seconds leaves or pings a colleague on Slack. Either outcome means your documentation failed at its one job.

Lead with the task. State what the reader will accomplish, show the concrete steps, then provide context.

Example of the wrong order:

> "GraphQL is a query language for APIs. It was developed by Facebook in 2012 and open-sourced in 2015. GraphQL lets clients request exactly the data they need, reducing over-fetching and giving frontend teams more autonomy. We will cover how to set up a GraphQL server with Node.js."

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

Respecting the reader's time is what the second version does. It hands over a working starting point immediately, and the concept follows the action instead of blocking it.

## Code that works beats code that explains

Every code example in documentation should be copy-paste-run. Not almost run. Run. I treat that as a non-negotiable constraint.

A missing import, a renamed variable, or an API call that changed three versions ago does not just confuse the reader, it actively wastes their time. Engineers will forgive a clumsy explanation. They will not forgive a snippet that throws on line one after they pasted it in good faith.

Write examples as complete files when you can. A partial snippet forces the reader to reconstruct the surrounding context, like a recipe that lists the spices but assumes you already know the base sauce. A complete example lets them verify the whole thing in under two minutes.

Test every code block by running it yourself. Bump the dependency versions to match whatever your docs claim as requirements, then run it again. Anything you cannot run successfully gets fixed or deleted.

The discipline is brutal and worth stating plainly: code you are not willing to maintain is code you should not publish.

## Name things precisely

Technical writing for engineers requires exact naming. Vague terminology creates cognitive overhead, because every fuzzy noun forces the reader to hold an open question in their head while they keep reading.

Phrases like "the system," "it," "this module," and "the component" should be replaced with specific names: "the AuthService," "the background job queue," "the rate limiter." A reader who sees the same precise name three times builds a stable mental model. A reader who sees "the component" three times has to guess whether you mean one component or three.

Spell out acronyms the first time they appear, even the ones you think everyone knows. Writing JSON Web Token (JWT) on first use costs you four words and saves a backend engineer who has only ever seen the abbreviation a moment of doubt. Someone from a different stack may recognize the expansion but not the three letters, or the reverse.

Avoid vague verbs: "handle," "manage," "process." Instead, describe what actually happens. "The retry handler attempts the request up to three times with exponential backoff." That sentence contains no ambiguity. "The system handles retries" could mean anything.

## Structure for scanning

Engineers rarely read documentation from top to bottom. They scan, hunt for keywords, and jump to the section most likely to hold their answer. Only when they are fully lost does anyone start reading linearly.

Write for that behavior. Headings should function as answers rather than topics. "Timeouts cause memory leaks in long-running workers" beats "Timeout handling," because the first tells the reader what they will learn and the second only labels the bin the information sits in.

Use bullet points for lists of related things. Use numbered lists for sequential steps. Do not use bullet points for sequential steps. The ordering implied by a numbered list carries information.

Use code blocks for code. Use bold for UI labels and filenames. Avoid italics in technical writing. They are harder to read at speed and add no information in this context.

Keep paragraphs short. Two sentences maximum. There is a real functional reason behind it, the same one that drives [the case for shorter technical documentation](/blog/the-case-for-shorter-technical-documentation/). Short paragraphs break information into chunks a scanning eye can absorb in one pass. Once a paragraph runs past three sentences, the reader has to hunt for which sentence actually carries the point.

## The four documentation types

Engineers need four types of documentation, and conflating them is a common failure.

**Tutorials** take a newcomer from zero to a working result. They are task-oriented and forgiving of complexity. Tutorials should say "here is how to build X" and hold the reader's hand through every step, which is the whole craft of [writing a technical tutorial that actually teaches](/blog/how-to-write-a-technical-tutorial-that-actually-teaches/). The goal is success, not completeness.

**How-to guides** solve a specific problem for someone who already knows the basics. "How to configure OAuth with an existing Next.js app" is a how-to guide. It assumes the reader understands OAuth conceptually but needs help with the implementation details.

**Reference documentation** describes the API, CLI, or library as it exists. Reference docs are exhaustive, accurate, and boring. They answer "what does this parameter do?" not "why would I use this?" Examples and usage notes belong in reference docs, but they come after the parameter description.

**Explanation** explores a topic, discusses trade-offs, and provides context. "Why does eventual consistency make debugging harder?" is an explanation article. It does not give steps. It builds understanding.

Plenty of teams produce only reference documentation and wonder why their docs feel cold. Reference material is necessary and nowhere near sufficient on its own. I have watched a team with an immaculate, fully generated API reference still bleed new hires, because nobody had ever written the one tutorial that walks you from a clean clone to a first passing request.

## Version control your documentation

Documentation belongs in version control, and I will not argue this one as a preference. It is the floor.

Docs that live in Google Docs or Confluence rot. API versions change, flags get renamed, screenshots drift from the actual UI, and nobody can tell you when the page was last touched. There is no diff history to read and no clean way to roll back a bad edit.

Markdown in a Git repository fixes the whole list. Every change carries an author and a timestamp, pull requests force a review before anything goes live, and a branch lets you stage docs for the v3 API without breaking the v2 page someone is reading right now. The diff view shows exactly what changed and, through the commit message, why.

Docs-as-code falls out of this for free. An engineer can update the documentation in the same PR that changes the code, so the feature and its explanation ship in the same merge. No more documentation sprints that get scheduled and quietly never happen.

The tooling cost is near zero. Every static site generator (Hugo, MkDocs, Docusaurus, Astro) supports Markdown. GitHub Pages, Netlify, Cloudflare Pages, and Vercel all serve static sites for free. There is no reason to accept documentation rot.

## Measure whether docs work

You can only improve what you measure, and for documentation the metrics worth tracking are behavioral rather than vanity.

Bad metrics include pageviews, time on page, raw document count, and coverage percentage. They measure activity, not outcomes, and a page can rack up views precisely because it keeps failing to answer the question.

Good metrics include task completion rate, support tickets deflected, time-to-answer for the common questions, and the share of new engineers who rate the onboarding docs as actually helpful. Those track whether the writing did its job.

Drop a one-tap survey at the bottom of every how-to guide: "Did this solve your problem? Yes / No." It costs the reader five seconds and gives you signal within days, often before you have shipped the next feature.

Read the search queries that return zero results on your internal search. Each empty result is a documented question your docs failed to answer. An engineer who searches and finds nothing pings a colleague or files a ticket, and both of those are the writing falling short.

## The update discipline

Documentation has a half-life. The moment a feature ships, its docs start decaying: the feature gets renamed, a flag gets deprecated, the screenshot stops matching the current UI.

Treating documentation as code is the only thing that keeps pace. Changing a feature's behavior means changing its docs in the same PR. Where that is genuinely impossible, the fallback is a "Last verified" date at the top of the page, which at least tells the reader how much to trust it and puts someone's name on the clock.

Automate staleness detection wherever you can. A scheduled script that flags every page untouched for six months turns a vague worry into a concrete list. The deeper fix is cultural: updating docs has to be a normal line in feature work, not a separate project that gets proposed every quarter and never staffed.

## What to cut

Documentation debt is not only about missing content. A large share of it is content that should never have survived this long.

Delete onboarding documents that contradict the current codebase, because stale guidance is one of the clearest signs of [developer onboarding docs that fail and the practices that actually work](/blog/developer-onboarding-docs-what-works-what-doesnt/). Delete tutorials that reference deprecated API versions. Delete FAQ entries that are no longer questions anyone asks. Stale documentation is worse than no documentation because it sends engineers down wrong paths.

The test for keeping a document comes down to one question: does this help someone accomplish a task or understand a concept that still exists in the current system? A no means you cut it.

Every document you keep is a document you have committed to maintaining forever. Be selective.

## The minimal viable documentation stack

You do not need a full documentation platform to start. Three things cover it.

A repository of Markdown files with a clear folder structure comes first. Keep reference docs separate from tutorials, and keep internal docs separate from anything customers will see.

A static site generator that produces a searchable site comes next. Docusaurus, MkDocs Material, and Hugo with a docs theme all clear this bar, so pick the one closest to what your team already runs.

One convention does the rest: every feature PR includes a documentation update. That is the only process change required, and everything else follows from it.

Later you can layer on a documentation team, a content calendar, a style guide, and automated freshness checks. None of it matters if the docs and the code still ship in separate PRs. Start with the discipline and add tooling once it is paying rent.

## The compounding return

Documentation compounds the way a paid-down mortgage does, with each entry quietly lowering what you owe later. Every accurate page cuts the count of repeat questions your team fields. Every tutorial that works shortens the runway before a new engineer ships their first real change. Every reference doc kept current spares someone the hours of debugging that come from trusting a stale flag.

The return is not linear. The first document saves a few hours. The tenth saves something closer to a day a week across the team. Around the fiftieth, the whole engineering org moves measurably faster and nobody can quite point to why.

Teams with excellent documentation did not start with excellent documentation. They started with the discipline to write it and the process to keep it current, and they let the compounding do the rest.

That discipline is what separates docs that gather dust from docs that engineers actually use.
