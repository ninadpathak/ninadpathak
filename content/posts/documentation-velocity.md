---
category: developer-experience
primary_query: documentation roi
siblings:
- devtools-documentation
- technical-writing-for-engineers
bridges:
- slug: runbook-template
  reason: A runbook is the document that turns a one-person recovery into a team one.
- slug: claude-md
  reason: An instruction file is documentation whose return shows up as fewer review findings.
date: 2026-04-11
description: 'Documentation ROI and engineering velocity: what DORA''s 2022 table shows, how far it can be pushed, and how to measure one document on your own team.'
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. This post is for the person who has to argue for documentation with numbers, and once you've won that argument I can write the pages. [Let's work together](/services/)."
title: 'Documentation ROI and Engineering Velocity'
slug: documentation-velocity
updated: 2026-11-17
---

Documentation ROI is hard to state as one number, and the best published evidence treats documentation as a multiplier on other engineering practices. DORA's 2022 data shows a team with above-average documentation quality getting a 750% lift in organizational performance from continuous integration, and a team below average getting 34%.

A team's [bus factor](https://en.wikipedia.org/wiki/Bus_factor) counts people, and DORA's table counts performance. Neither is a return in money, and I think the case for investing in [developer content](/articles/developer-experience/) is stronger when it says so.

## What is engineering velocity?

Engineering velocity is how quickly a team moves a change from an idea to production, and DORA measures it as throughput. Its [metrics guide](https://dora.dev/guides/dora-metrics/) defines the term: "Throughput is a measure of how many changes can move through the system over a period of time."

The guide measures it by change lead time, deployment frequency and failed deployment recovery time. A claim that documentation raises velocity has to show up in one of those.

## What does DORA's research say about documentation?

It says documentation quality amplifies the payoff of every technical practice the 2022 study covered. DORA's [capability page on documentation quality](https://dora.dev/capabilities/documentation-quality/) prints the table, excerpted from an analysis by Michelle Irvine and Derek DeBellis.

| Technical capability | Lift with below-average documentation | Lift with above-average documentation |
| --- | --- | --- |
| Continuous delivery | 63% | 656% |
| Continuous integration | 34% | 750% |
| Loosely coupled teams | 46% | 313% |
| Site Reliability Engineering | 79% | 343% |
| Supply chain security | 37% | 451% |
| Trunk-based development | 36% | 1525% |
| Version control | 27% | 278% |

So the lift from every practice is far larger for teams with above-average documentation. DORA scored quality with eight metrics covering attributes such as clarity and findability.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/documentation-velocity/dora-multiplier.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/documentation-velocity/dora-multiplier.narrow.svg" width="288" height="416"><img class="np-has-narrow" src="/static/images/diagrams/documentation-velocity/dora-multiplier.svg" width="720" height="472" alt="The performance lift that continuous integration gives a team in DORA's 2022 data, by documentation quality: 34% for teams below average and 750% for teams above average. Each tile is 50 percentage points." loading="lazy" decoding="async"></picture></a>
  <figcaption>DORA's 2022 data for continuous integration: a 34% lift in organizational performance with below-average documentation quality and 750% with above-average. Each tile is 50 points.</figcaption>
</figure>

## How far can that table be pushed?

Less far than its largest number invites. The data is from 2022, and I read the table as a correlation between documentation quality and the payoff of other practices, whatever verbs the page uses.

A team with strong documentation is plausibly strong at other things the table doesn't show. The table can't separate those.

So what does it support? A narrower statement: a practice such as trunk-based development pays back far more where people can find out how it's meant to work, so documentation belongs in the plan for any practice a team is about to adopt.

And it gives no support to a sentence like "documentation makes a team seven times faster". No row measures a team before and after it wrote anything.

## Where does the time go without documentation?

Into work that looks like something else. Stripe's [Developer Coefficient report](https://stripe.com/files/reports/the-developer-coefficient.pdf) from September 2018 found that "the average developer spends more than 17 hours a week dealing with maintenance issues, such as debugging and refactoring."

The report doesn't say how much of that time is spent working out what code was meant to do, and I won't put a share on it. The places where missing documentation gets paid for can be named, though not measured from this report.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/documentation-velocity/documentation-debt.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/documentation-velocity/documentation-debt.narrow.svg" width="288" height="448"><img class="np-has-narrow" src="/static/images/diagrams/documentation-velocity/documentation-debt.svg" width="720" height="504" alt="Missing documentation never breaks the build, but it taxes three places: every pull request where a reviewer has to ask what a function does, every onboarding where a new hire reverse-engineers the deploy process, and every incident where the one person who understands the failing job is asleep." loading="lazy" decoding="async"></picture></a>
  <figcaption>Missing documentation never breaks the build, and its cost is paid in reviews, onboarding and incidents.</figcaption>
</figure>

A reviewer has to ask what a function is for. A new hire reconstructs the deploy process from old pull requests, and an incident waits for the one person who understands the failing job.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/documentation-velocity/knowledge-silos.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/documentation-velocity/knowledge-silos.narrow.svg" width="288" height="736"><img class="np-has-narrow" src="/static/images/diagrams/documentation-velocity/knowledge-silos.svg" width="720" height="256" alt="A delivery pipeline from code through build and deploy. A single stage depends on an architectural detail that lives only in one engineer's head, so every change waits on that person, and the whole pipeline moves only as fast as that silo, however quick the build and deploy are." loading="lazy" decoding="async"></picture></a>
  <figcaption>A delivery pipeline in which one stage depends on a detail only one engineer knows.</figcaption>
</figure>

That last case is the bus factor showing up in a recovery time. A [runbook](/articles/runbook-template/) is the document that takes it out of one person's head.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/documentation-velocity/context-switching.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/documentation-velocity/context-switching.narrow.svg" width="288" height="432"><img class="np-has-narrow" src="/static/images/diagrams/documentation-velocity/context-switching.svg" width="720" height="528" alt="An engineer working in the IDE needs an answer. Documentation kept in the same repository answers it a few keystrokes away, so the engineer stays in flow. A question sent to Slack or a stale wiki page pulls the engineer out of the IDE and drops the mental state they were holding." loading="lazy" decoding="async"></picture></a>
  <figcaption>Two places an engineer can look for an answer: documentation beside the code, or a question in chat or a wiki.</figcaption>
</figure>

## What changes when agents write the code?

The volume changes, and the reader does too. Anthropic's [account of its code review](https://claude.dev/blog/solving-code-review-at-anthropic/) from October 15 says the changes landing in its monorepo each day went from about 2,500 in May to more than 30,000 in September.

At that rate, the first reader of a team's conventions is a model. The post describes fixing repeated review findings at the source, in files such as the one where "CLAUDE.md tells Claude what the project is: the stack, the conventions, the goals and the non-goals."

I think of that as documentation with a visible return, since a line added to the file removes a class of review comment. My [CLAUDE.md guide](/articles/claude-md/) covers what belongs in it.

## How do you measure documentation ROI on your own team?

Pick one document, one metric and a period before and after. The measurements below are suggestions and I have no results of my own to report for them.

- **Onboarding.** Days from a new engineer's start to their first merged change, before and after a setup guide is written.
- **Repeat questions.** How often the same question appears in the team's chat in a month, before and after its answer has a page.
- **Recovery.** Time to recover from a recurring failure, with and without a runbook for it.

The last of these is close to DORA's recovery factor and the other two sit beside its factors, and each keeps the claim checkable. For a company whose buyers are developers, the same reasoning applies outside the team, and [devtools documentation](/articles/devtools-documentation/) makes that case.

And the writing doesn't need a specialist to start. My [guide to writing for engineers](/articles/technical-writing-for-engineers/) covers the rules an engineer can apply to the first page.

## FAQ

**Can documentation ROI be calculated?**

Not as a general figure. A team can measure one document against one metric, such as onboarding time, and the published research shows correlation at the level of whole organizations.

**What is the strongest evidence that documentation improves engineering performance?**

DORA's 2022 analysis, in which every technical capability studied produced a larger performance lift in teams with above-average documentation quality.

**Does AI-written code reduce the need for documentation?**

It moves it. Instruction files and written conventions become input to the tools that write and review the code.
