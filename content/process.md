---
title: "My technical writing process, from keyword strategy to a measured result"
nav_title: "Process"
seo_title: "My Technical Writing Process, From Strategy to Measured Result"
description: "My technical writing process in eight stages, from keyword strategy to a measured result. I run the product, trace every claim and track what moved."
lead: "My technical writing process takes a page from keyword strategy to a measured result in eight stages. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies, and where a stage describes how this site is run, it says so."
primary_query: technical writing process
status: published
stages:
  - id: strategy
    label: Strategy
    title: "Strategy: what buyers ask, then what they search"
    figure: Topic map
    alt: "Twelve buyer topics of three kinds sort into three clusters. The narrow middle cluster is picked first and feeds one page."
    beats:
      - "I start by listening. I listen to calls and ask for sales call transcripts, then use Claude and other AI tools to summarize the topics buyers keep raising."
      - "Semrush then shows which of those topics people search for. I group the queries into clusters and begin with the narrow ones a new site can win."
      - "Each page gets one primary query and one job. For [DelightChat](/work/delightchat/) the queries were support problems, such as missed WhatsApp messages, and never software categories."
    evidence: "How I run strategy with clients, and the [DelightChat](/work/delightchat/) and [LinuxForDevices](/work/linuxfordevices/) case studies."
  - id: brief
    label: Brief
    title: "Brief: written within 24 hours of the call"
    figure: Call to brief
    alt: "Four answers from a discovery call fill a page, and within 24 hours they become a written brief with an outline."
    beats:
      - "We talk for 30 minutes about the reader and the decision the page has to support."
      - "I require a demo account and API keys, plus any account that already holds data. I also ask what evidence and engineering review exist."
      - "Within 24 hours of that call you get a written brief and a specific timeline. Once the brief is agreed, we start with a paid trial piece."
    evidence: "Steps 1 to 4 of [how we'd work together](/services/#how-wed-work-together) on the services page."
  - id: research
    label: Research
    title: "Research: I run the product before I write"
    figure: Tested example
    alt: "A terminal runs the happy path, hits a failing edge case, and the fix passes. Each edge case lands in a notes page."
    beats:
      - "I build or test a working example locally before there's a draft."
      - "Then I go past the happy path and note the edge cases that show up after it."
      - "On the [Centus](/work/centus/) guides, when the docs said one thing and the framework did another, I kept what worked in the code. For [LinuxForDevices](/work/linuxfordevices/) a command that hadn't been run wasn't ready to publish."
    evidence: "Step 3 of [how we'd work together](/services/#how-wed-work-together), and the [Centus](/work/centus/) and [LinuxForDevices](/work/linuxfordevices/) case studies."
  - id: draft
    label: Draft
    title: "Draft: in the order a developer follows"
    figure: Outline to draft
    alt: "A draft holds three numbered steps of tested code. A model helps from one side and the writer owns the page from the other."
    beats:
      - "I write the draft in the order a developer follows it, built around the example I already ran. It takes about 5 days from brief to draft."
      - "AI helps me prepare research and attack a draft. I won't ask a model to manufacture product understanding or personal judgment."
      - "The draft arrives as a Google Doc or a Markdown pull request, or in whatever your team already uses. It says what I'd do, and it has an owner who knows why each claim is there."
    evidence: "Steps 5 and 7 of [how we'd work together](/services/#how-wed-work-together), and [what I believe](/about/#what-i-believe) on the about page."
  - id: checks
    label: Checks
    title: "Checks: every claim traced to a source"
    figure: Claim check
    alt: "Three claims in a draft each connect to a source. Four checks pass in turn, and a review reports 95 quotes re-fetched and 3 blockers sent back."
    beats:
      - "Before anyone else reads it, each number and each quote gets traced to a page a reader can open. I won't publish code I can't run or a result I can't trace."
      - "On this site scripts take the first pass: a rule checker for the prose and a claims audit for first-person claims and bare measurements. Quote verifiers then re-fetch each quoted page, and the build stops on a leftover TODO."
      - "Then a reviewer with no hand in the draft checks it against the sources. The review of 17 November 2026 re-fetched 95 recorded quotes and still sent back three blockers."
    evidence: "The checkers in this site's repository and its review of 17 November 2026. The [technical writing linter](/linter/) is the public one."
  - id: review
    label: Review
    title: "Review: never more than two rounds"
    figure: Engineer review
    alt: "A draft passes an engineer's review and goes live. Fifty tiles stand for the Centus guides, and thirteen dots for the writers at Mem0."
    beats:
      - "Your engineers review the draft for accuracy, and they get working code to review. Review never goes past two rounds."
      - "For [Centus](/work/centus/) that meant 50+ localization guides across 10+ frameworks, approved without a round of engineering revisions."
      - "When one writer isn't enough, the review scales to a team. At [Mem0](/work/mem0/) I wrote 11 guides and ran a team of 13 writers, with the hiring and the technical reviews."
    quote: "Our devs called it awesome and just sent it ahead for publishing."
    quote_by: "Roman Hresko, Head of Content at Centus"
    evidence: "Step 6 of [how we'd work together](/services/#how-wed-work-together), and the [Centus](/work/centus/) and [Mem0](/work/mem0/) case studies."
  - id: publish
    label: Publish
    title: "Publish: findable by search engines and by agents"
    figure: Findability
    alt: "A published page takes one link in and sends two out. A search crawler and an agent reach it, nine answer checks pass, and it ships as Markdown."
    beats:
      - "If you want the page uploaded into your CMS, I do that, and otherwise I hand it over. On this site each new page also gets at least one link in from an existing page and at least two links out."
      - "Then I check what an answer engine gets. The [AI Overviews checker](/ai-overviews-checker/) runs nine structural checks, and the [AI crawler access checker](/ai-crawler-checker/) reads which AI crawlers robots.txt lets in."
      - "Each article and services page here also ships as plain Markdown, listed in [llms.txt](/llms.txt). llms.txt is good to have, but there's no evidence that LLMs fetch it."
    evidence: "The [AI-ready documentation audit](/services/ai-ready-documentation-audit/) and the four checkers under [tools](/tools/)."
  - id: measure
    label: Measure
    title: "Measurement: what moved, and how sure I am"
    figure: Reading a change
    alt: "Search Console feeds a 28-day baseline. One change ships, 14 days pass with no verdict, and each number is labelled measured or estimate."
    beats:
      - "Publishing isn't a result. A page counts when Google Search Console shows impressions and a position for it."
      - "I report from Search Console. On this site a script pulls it every day, with windows that end three days back because the data lags."
      - "The loop allows one change to a page at a time. It freezes the 28 days before the change as the baseline and refuses a verdict for 14 days."
    evidence: "This site's daily Search Console pull and its weekly loop, where each number is labelled as measured or as an estimate."
start:
  - step: "A 30-minute call"
    line: "We settle the reader, the decision and the access I need."
  - step: "The brief, in 24 hours"
    line: "A written brief and a specific timeline, within a day of the call."
  - step: "A paid trial piece"
    line: "One piece, start to finish. We continue only if you're happy with it."
  - step: "A working week"
    line: "About 5 days from brief to draft and 2 for revision. Later pieces take 4 days end to end."
results:
  - client: LinuxForDevices
    url: /work/linuxfordevices/
    before: "487"
    after: "203,400"
    period: "2019 to 2022"
    line: "A cluster map and tested commands took monthly visits from 487 to 203,400."
  - client: DelightChat
    url: /work/delightchat/
    before: "0"
    after: "50,000"
    period: "2021"
    line: "Problem queries in narrow clusters took monthly organic visits from zero to 50,000."
  - client: Kiwi Sizing
    url: /work/kiwisizing/
    before: "7,000"
    after: "450,000"
    period: "2022"
    line: "Clean sizing data behind each page template took monthly visits from 7,000 to 450,000."
results_note: "Monthly visits before and after. Source: Semrush, for LinuxForDevices from 2019 to 2022, DelightChat in 2021 and Kiwi Sizing in 2022. Documentation can't repair a weak product or create demand where none exists."
---

## What I need from you to start

I ask for three things:

- who the reader is
- a demo account and API keys, plus any account that already holds data
- who on your side reviews for accuracy

Bring the page that is making people guess. My [technical writing services](/services/) page lists what I write, and the [case studies](/work/) show the results in full.

## FAQ

**What is your technical writing process?**

My technical writing process runs from keyword strategy to a measured result in eight stages. I run the product before I write, and each claim is traced to a source before an engineer reviews the draft.

**How long does one page take?**

It takes about 5 days from brief to draft and 2 days for revision, so one working week before you can publish. Once we've worked together for a while, that drops to 4 days end to end.

**How many review rounds are there?**

Review never goes past two rounds. A third round is never required.

**How does an engagement start?**

It starts with a 30-minute call, and you get a written brief and a specific timeline within 24 hours. Then we do a paid trial piece, and we continue only if you're happy with it.

**Do you use AI to write?**

I use AI to prepare research, check a corpus and attack a draft. I check the product myself before I sign off on the claims.

**How do you measure whether a page worked?**

By Google Search Console impressions and position for the page, read against the 28 days before the change. Publishing a page doesn't count as a result.
