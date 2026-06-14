---
date: 2026-04-05
description: I explain which engineering habits still make me better at technical
  writing, which ones I had to drop, and how the day-to-day work changed.
status: published
tags:
- technical-writing
- career
- developer-experience
title: 'From Engineer to Technical Writer: What I Kept and What I Left Behind'
---

Moving from engineering to technical writing did not feel like abandoning a technical career. I simply swapped the artifact I shipped. For years my output was code, and then it became clarity. Plenty of my old instincts as a programmer still help me navigate a tangled documentation project, yet a few of them turned into liabilities the moment I started writing for readers I would never meet.

**Short answer:** I kept the engineering habits built around verification, systems thinking, and operational rigor. I dropped the ones that rewarded local optimization and the assumption of shared context. The job moved me from "it works on my machine" to "a stranger I will never meet can succeed using only the words on this page."

## I kept the habit of empirical verification

Engineering taught me to distrust any explanation that has not survived contact with a real environment. That skepticism carries straight into my writing. When a draft says `npm run build` emits a dist folder with three files, I run it and count the files before the sentence stays. The command that "obviously" works is often the one that prints a deprecation warning the author never saw.

Some of the strongest technical teams bake this mindset into their formal workflows. GitLab treats documentation as a mandatory part of the "definition of done" for any user-facing change. Their [documentation workflow](https://docs.gitlab.com/development/documentation/workflow/) requires that developers draft the initial docs and that these undergo a technical review before merging. I agree with their stance that generative AI cannot replace the subject matter expertise required for these verification passes.

My whole production cycle bends around this habit. Writing about [Structured Outputs With LLMs](/blog/structured-outputs-llms-json-mode-function-calling/) meant more than paraphrasing a release note. I fed the API a schema nested four levels deep with an optional enum buried at the bottom, just to watch where the guarantee actually held and where it quietly degraded to "best effort." Writers without a coding background can build this discipline over time, though engineers arrive with the scars from untested code already installed.

## I kept systems thinking and documentation architecture

People mistake technical writing for simple wordsmithing. Day to day, the work sits closer to information architecture and systems design. No single page lives in isolation. Each one sits inside a web of headers, search indices, versioned artifacts, and internal links, and pulling one thread tugs on the rest.

Coupling and cohesion were drilled into me as an engineer, and I now ask the same questions when I lay out a documentation site.

1. Is this section too tightly coupled to a specific version of the UI?
2. Does this tutorial have high cohesion, or is it trying to teach three unrelated concepts?
3. What is the upstream dependency for this configuration step?
4. Where should this logic live so that I don't have to duplicate it in five places?

GitHub's [best practices for docs](https://docs.github.com/en/contributing/writing-for-github-docs/best-practices-for-github-docs) emphasize this structural approach. They push writers to define the core purpose of a document and choose the right content type before writing a single word. To hold that separation of concerns, I lean on the **Diataxis framework**. Sorting every page into a tutorial, a how-to guide, a technical reference, or a conceptual explanation keeps the architecture stable as the product grows. The same way a router table refuses to mix concerns, a reference page that starts narrating a tutorial is a sign the structure has rotted. You can find the framework at [diataxis.fr](https://diataxis.fr/).

## I left behind the assumption of shared context

Engineers survive on a mountain of unstated context. Standups run on acronyms, service names, and deployment quirks that everyone "just knows," like the fact that `auth-gateway` always needs a manual restart after a config change. Writing punishes that reflex on contact, because the reader is usually a stranger who is missing the one piece of context that makes the rest of the page work.

Google's technical writing course names this the "curse of knowledge." Their [audience guidance](https://developers.google.com/tech-writing/one/audience) tells writers to account for the reader's role and their proximity to the subject. So I learned to spell out prerequisites I once judged too obvious to mention, like which Node version the install steps assume.

The "idempotency" of my engineering explanations also had to go. An idempotent operation runs many times and lands on the same result, which is a virtue in code. Repeating the same idea three different ways on one page only adds noise for a reader. What I needed was a single precise definition I could link back to every time the concept resurfaced, the way a function gets defined once and called everywhere else.

## I kept the instinct to debug the "unhappy path"

Looking for failure modes is an engineer's reflex, and technical writing rewards it. Documentation tends to describe the "happy path," the run where every step succeeds on the first try, and real software almost never behaves that politely.

A debugger's mindset persists in my writing for that reason. AI content keeps neglecting control flow and observability, which is exactly the frustration that produced my post on [Agent harnesses](/blog/agent-harnesses/). Plenty of material covered how to prompt an agent, and almost none of it covered what to do when the agent caught itself in a retry loop, burning tokens on the same failing call forever. The best documentation comes from someone who already watched the thing crash and wrote down the recovery.

## I left behind local optimization of prose

Engineering often rewards local optimization, shaving milliseconds off one function or tidying one module. Writing offers the same little wins, polishing a single sentence or slipping in a clever analogy. I found that those local wins can quietly wreck the usefulness of the whole page.

<div class="visual-wrapper">
  <div class="visual-title">The Context Bridge</div>
  <div class="visual-container">
    <iframe src="/static/visuals/context-bridge.html" title="The Context Bridge" loading="lazy"></iframe>
  </div>
</div>

A sentence can be grammatically perfect and still wrong for its audience. A section can be technically brilliant and still derail the flow of a tutorial. Some of the cleanest paragraphs I have written ended up deleted, because a sharp three-page aside on rate-limit internals was weight the reader had to carry without ever needing it to finish the task.

Microsoft's [style and voice quick start](https://learn.microsoft.com/en-us/contribute/content/style-quick-start) emphasizes empathy and conciseness. They advise writers to focus on the customer's intent and reach for everyday words. An engineer's hunger for "completeness" turned out to be the enemy of a reader's need for "utility." Cutting hard, even the good stuff, is a professional requirement in this job, not a stylistic preference.

## I kept the respect for Docs-as-Code tooling

Treating documentation as a sidecar artifact tends to produce a library of stale truths, a page that confidently tells you to click a button removed two releases ago. Engineers know an artifact stays valid only when the process around it stays rigorous. I take to the operational side of the job because the shape of the work already feels familiar.

I use the same tools for documentation that I use for code.

- **Version Control:** Storing Markdown files in Git repositories alongside the source code.
- **Linting:** Automated style and link checks to catch errors before they reach the reader.
- **CI/CD Pipelines:** Automated builds that generate previews of the documentation on every pull request.
- **Review Gates:** Ensuring that a technical expert has signed off on every change.

The **Write the Docs 2024 salary survey** shows this "DocOps" side of the field expanding. The survey collected data from 55 countries and identified 217 unique job titles, many of them centered on information architecture and tooling rather than drafting prose alone. Technical writing scales through process, the same way a service scales through automation rather than through one heroic on-call engineer. You can read the full survey results at [writethedocs.org](https://www.writethedocs.org/surveys/salary-survey/2024/).

## I left behind the idea of "shipping and forgetting"

Code enters a maintenance phase the moment it ships. Documentation runs the same lifecycle, yet plenty of teams act as if clicking "publish" closes the ticket. Every page I create now carries a maintenance cost in my head before I write the first line.

Search queries drift, product defaults change, and screenshots rot the instant a designer moves a button. A published tutorial is a living system that needs recurring validation, no different from a cron job you have to check still runs. I also hunt for chances to link older posts into newer ones, knitting the site into a network instead of a pile of isolated blog posts.

[How to Write a Changelog That Developers Actually Read](/blog/how-to-write-a-changelog-developers-actually-read/) is one example from this site. That post gives me a stable reference point to link from every later piece about developer communication. Maintenance is not a chore tacked on at the end. Maintenance is how the technical assets you already built hold their value.

## I left behind a narrow definition of what is "technical"

People assume that moving into writing is a step away from technical substance. My experience runs the other direction: writing for a technical audience is one of the most intellectually demanding forms of engineering work I have done.

Serious technical writing requires six specific skills.

1. Accurate reading of source code and internal specs.
2. Judgment of the product's underlying mental model.
3. Rigorous verification of every code example.
4. Strategic information architecture for the entire site.
5. Empathy-driven calibration for different audiences.
6. Ruthless editorial compression under technical constraints.

Google’s materials on [becoming a technical writer](https://developers.google.com/tech-writing/becoming/meet) note that many writers arrive from software engineering, support, and testing roles. That framing matches my own belief. Technical writing is not a decorative layer painted over engineering. The work is a separate production function with its own success metrics.

If you are looking for this kind of depth for your own team, [my work page](/work) shows how I apply these engineering habits to client projects.

## What changed in my day-to-day workflow

Three major shifts stand out from my time in this role.

Feedback loops got more legible, for one. A confusing page fails in visible ways that beat chasing a latent bug in a distributed system: readers drop off at step four, and the same support ticket arrives a dozen times asking why the API key field is empty. Documentation failure is highly observable once you are willing to read the analytics.

Audience empathy was the second shift, moving from a "soft skill" to a core production requirement. An engineer can occasionally ship and stay impatient with a user's missing context. A technical writer never gets that pass. My job is to bridge that divide by becoming the first user of every feature, clicking through the onboarding with the fresh confusion of someone who has read nothing.

The reach of my work changed too. A feature helps the users who manage to find it, and one well-built page can reshape how thousands of developers understand a product before they ever sign up. I pour my time into durable assets, the changelogs, migration guides, and deep-dive tutorials, because their return compounds for the team over years rather than a single release.

## FAQ

**Do engineers have an advantage when they switch to technical writing?**

Yes, as long as they are willing to unlearn their communication habits. The edge comes from reading source code fluently, verifying examples, and understanding system architecture. The trap is writing from their own private context and leaving the reader stranded at the one step they assumed was obvious.

**Which engineering skill was the most useful for me?**

Empirical verification. Refusing to publish a command, flag, or output I haven't run on my own machine prevents the most common trust-killing errors, like a copied snippet that fails because the API renamed a parameter last quarter.

**What was the hardest habit to break?**

I had to stop compressing my explanations too early. I used to write for the person who already understood 90% of the system. I had to learn to write for the person who is missing the exact 10% that makes the whole system fail.

**Does technical writing involve less technical work than engineering?**

No. It involves a different type of technical work. You are still reading code, testing APIs, and designing systems. You are simply producing a technical document as the final artifact instead of a pull request.

**Should I move into technical writing if I enjoy explaining things?**

Enjoying the explanation is only half of the job. You also need to enjoy the research, the verification, the editing, and the architectural design of information systems. If you find those tasks as rewarding as writing code, the transition is likely a good fit.