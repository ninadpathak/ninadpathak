---
title: "My technical writing process"
nav_title: "Process"
seo_title: "My Technical Writing Process: a Docs Page, From Issue to Production"
description: "My technical writing process follows the path a code change takes, from issue to production. I run the product before I write, and your engineers review a draft that already works."
tagline: "I ship a docs page the way you ship a change."
lead: "This is one docs page going from a question on a sales call to production. I'll show it as a pull request, though some teams get it as a Google Doc."
primary_query: technical writing process
status: published
example_label: "example: from a guide I wrote for Centus"
example_url: "https://centus.com/blog/react-i18next-localization"
stages:
  - id: issue
    label: Issue
    title: "The issue"
    alt: "An issue thread titled How do plurals work in react-i18next, labelled question and docs, with later comments marked duplicate and a linked page, docs/plurals.md."
    object:
      - "How do plurals work in react-i18next?"
      - "question"
      - "docs"
      - "duplicate"
      - "source: sales calls, call transcripts"
      - "docs/plurals.md"
    beats:
      - "Every page starts as a question that keeps coming up. I get those from your sales calls and the call transcripts."
      - "Claude and other AI tools summarize the transcripts into topics. Semrush tells me which of them people search for."
      - "Each question gets its own page and its own search query. I take the narrow ones first, because a new site can win those."
  - id: spec
    label: Spec
    title: "The spec"
    alt: "A file named SPEC.md with four fields, reader, decision, access and timeline, stamped within 24 hours of the call."
    object:
      - "SPEC.md"
      - "reader:    who opens this page"
      - "decision:  what they need to get done"
      - "access:    demo account, API keys, an account with real data"
      - "timeline:  dated"
      - "within 24h of the call"
    beats:
      - "We talk for 30 minutes. I need to know who reads the page and what they're trying to get done."
      - "I need a demo account, API keys and an account with real data in it, because I run the product before I write about it."
      - "You get the spec and a timeline within 24 hours of the call. The first piece is a paid trial, and we carry on only if you're happy with it."
  - id: repro
    label: Repro
    title: "The repro"
    alt: "A terminal. The English run passes. The Arabic run exits 1 because count 3 wants items_few and got items_other. After the missing forms are added it passes."
    object:
      - "works on a clean machine"
      - "$ npm install react react-dom i18next react-i18next"
      - "$ node plurals.mjs en"
      - "ok    count 3: items_other -> \"3 items\""
      - "exit 0"
      - "$ node plurals.mjs ar"
      - "wrong count 3: wants items_few, got items_other"
      - "exit 1"
      - "$ node plurals.mjs ar locales-fixed"
      - "ok    count 3: items_few"
    beats:
      - "I build the example on a clean machine before there's a draft. A command that hasn't been run doesn't go on the page."
      - "Then I leave the happy path. The edge cases are what developers trip over in production, so they get written down."
      - "When the docs and the framework disagree, I keep what ran. That happened on the [Centus](/work/centus/) guides."
  - id: diff
    label: Diff
    title: "The diff"
    alt: "A diff of one Markdown file, docs/plurals.md, on the branch docs/plurals, adding four sections: Install, First run, Plurals, When it fails."
    object:
      - "docs/plurals"
      - "docs/plurals.md"
      - "+ ## Install"
      - "+ ## First run"
      - "+ ## Plurals"
      - "+ ## When it fails"
    beats:
      - "The draft follows the order a developer works in, built around the example that already ran. It takes about 5 days from the spec."
      - "It lands as a Markdown pull request or a Google Doc, whichever your team reviews in."
      - "I use AI to prepare research and to attack the draft. I won't ask a model to supply product understanding or judgment."
  - id: checks
    label: Checks
    title: "Checks"
    alt: "A pull request's checks list, tagged this site's checks: commands run, numbers have a source, quotes match their source, links resolve, no TODO left. All checks have passed."
    object:
      - "this site's checks"
      - "✓ commands run"
      - "✓ numbers have a source"
      - "✓ quotes match their source"
      - "✓ links resolve"
      - "✓ no TODO left"
      - "All checks have passed"
    beats:
      - "Nothing goes to review red. Every command has been run, and every number and quote points at its source."
      - "On this site those are scripts: a prose linter, a claims audit, a quote verifier that re-fetches each page, and a build that fails on a leftover TODO."
      - "Checks miss things, so a second reviewer reads it cold. On this site, the review of 17 November 2026 re-fetched 95 quotes and still sent back 3 blockers."
  - id: review
    label: Review
    title: "Review"
    alt: "A pull request's review panel. The reviewer is your engineer. Round 1 says Changes requested and round 2 says Approved, with a comment from Roman Hresko at Centus."
    object:
      - "your engineer"
      - "Round 1"
      - "Changes requested"
      - "Round 2"
      - "Approved"
    quote: "Our devs called it awesome and just sent it ahead for publishing."
    quote_by: "Roman Hresko, Head of Content at Centus"
    beats:
      - "Your engineers review for accuracy. They're reading a draft that already runs."
      - "It never takes a third round. Revisions take about 2 days."
      - "[Centus](/work/centus/)'s engineers approved 50+ guides across 10+ frameworks without requesting changes."
  - id: deploy
    label: Deploy
    title: "Merge and deploy"
    alt: "A merged pull request, then a curl request to the page returning HTTP 200, with robots.txt allowing AI crawlers and nine of nine answer checks."
    object:
      - "Merged"
      - "$ curl -I https://<your docs>/plurals"
      - "HTTP/2 200"
      - "robots.txt     AI crawlers allowed"
      - "answer checks  9 of 9"
    beats:
      - "I can load it into your CMS, or hand over the file."
      - "Then I check it can be reached. That's which AI crawlers your robots.txt lets in, and [nine structural checks](/ai-overviews-checker/) for whether an answer engine can quote it."
      - "On this site every article also ships as Markdown at its own index.md. [llms.txt](/llms.txt) is good to have, but there's no evidence that LLMs fetch it."
  - id: metrics
    label: Metrics
    title: "After the deploy"
    alt: "A graph from Google Search Console with a deploy marker. The 28 days before it are the baseline and the 14 days after it are marked too early. It carries no numbers."
    object:
      - "Google Search Console"
      - "deploy"
      - "28 days: baseline"
      - "14 days: too early"
    beats:
      - "A page counts once Search Console shows impressions and a position for it. Until then it's only deployed."
      - "I report from Search Console. On this site a script pulls it daily, and every window ends three days back because the data lags."
      - "On this site one change ships at a time. The 28 days before it are the baseline, and the script refuses a verdict for 14 days."
results:
  - client: LinuxForDevices
    url: /work/linuxfordevices/
    before: "487"
    after: "203,400"
    period: "2019 to 2022"
  - client: DelightChat
    url: /work/delightchat/
    before: "0"
    after: "50,000"
    period: "2021"
  - client: Kiwi Sizing
    url: /work/kiwisizing/
    before: "7,000"
    after: "450,000"
    period: "2022"
results_note: "Monthly visits before and after, on one scale across the three charts, so a starting figure too small to draw at that scale shows as a hairline. Source: Semrush."
results_limit: "Docs can't fix a weak product, and they can't create demand that isn't there."
results_team: "When one writer isn't enough I run the team: 13 writers at [Mem0](/work/mem0/), with the hiring and the technical reviews."
start:
  - step: "call"
    line: "30 minutes"
  - step: "spec"
    line: "within 24 hours"
  - step: "trial"
    line: "one paid piece; we carry on only if you're happy with it"
  - step: "draft, review"
    line: "about 5 days, then about 2"
start_note: "After we've done a few, the cycle comes down to 4 days."
---

## FAQ

**What is your technical writing process?**

My technical writing process follows the path a code change takes, from issue to production. I run the product before I write, and your engineers review a draft that already works.

**How long does one page take?**

A draft takes about 5 days from the spec and revisions take about 2, so one working week before you can publish. After we've done a few, the cycle comes down to 4 days.

**How many review rounds are there?**

Review never goes past two rounds. A third round is never required.

**How does an engagement start?**

It starts with a 30-minute call, and you get a written spec and a timeline within 24 hours. Then we do one paid trial piece, and we carry on only if you're happy with it.

**Do you use AI to write?**

I use AI to prepare research, check a corpus and attack a draft. I check the product myself before I sign off on the claims.

**How do you measure whether a page worked?**

On this site, by Google Search Console impressions and position for the page, read against the 28 days before the change. A page counts once Search Console shows both.
