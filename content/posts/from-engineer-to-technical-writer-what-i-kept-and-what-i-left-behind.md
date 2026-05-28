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

Moving from engineering to technical writing did not feel like abandoning a technical career. I simply changed the artifact I delivered. Code used to be the primary output of my work. Clarity became the primary output later. Plenty of my old instincts as a programmer still help me navigate complex documentation projects, yet others became immediate liabilities that I had to unlearn.

**Short answer:** I kept the engineering habits that prioritize verification, systems thinking, and operational rigor. I left behind the habits that rewarded local optimization and the assumption of shared context. Technical writing requires a transition from a mindset of "it works on my machine" to a mindset where a stranger can succeed using only the text I provide.

## I kept the habit of empirical verification

Engineering taught me to distrust any explanation that has not survived contact with a real environment. I transfer this skepticism directly to my writing. If a tutorial claims that a command produces a specific JSON output, I run that command on my own machine before I commit the sentence.

Some of the strongest technical teams bake this mindset into their formal workflows. GitLab treats documentation as a mandatory part of the "definition of done" for any user-facing change. Their [documentation workflow](https://docs.gitlab.com/development/documentation/workflow/) requires that developers draft the initial docs and that these undergo a technical review before merging. I agree with their stance that generative AI cannot replace the subject matter expertise required for these verification passes.

My entire production cycle is shaped by this habit. If I am writing about [Structured Outputs With LLMs](/blog/structured-outputs-llms-json-mode-function-calling/), I am not just summarizing a press release. I am testing the API to see what it really guarantees when the schema is deeply nested. Writers without a background in code can build this discipline, but engineers arrive with the scars from "untested" code already installed.

## I kept systems thinking and documentation architecture

Technical writing is often mistaken for simple wordsmithing. Day to day, the job is closer to information architecture and systems design. A single page does not exist in isolation. It lives within a network of headers, search indices, versioned artifacts, and internal links.

Engineering trained me to think about coupling and cohesion. I ask the same questions when structuring a documentation site.

1. Is this section too tightly coupled to a specific version of the UI?
2. Does this tutorial have high cohesion, or is it trying to teach three unrelated concepts?
3. What is the upstream dependency for this configuration step?
4. Where should this logic live so that I don't have to duplicate it in five places?

GitHub's [best practices for docs](https://docs.github.com/en/contributing/writing-for-github-docs/best-practices-for-github-docs) emphasize this structural approach. They push writers to define the core purpose of a document and choose the right content type before writing a single word. I use the **Diataxis framework** to maintain this separation of concerns. By categorizing content into tutorials, how-to guides, technical references, and conceptual explanations, I ensure that the architecture of the information remains stable as the product grows. You can find the framework at [diataxis.fr](https://diataxis.fr/).

## I left behind the assumption of shared context

Engineers survive on a massive amount of unstated context. Team communication often relies on acronyms, service names, and implicit deployment quirks that everyone "just knows." Technical writing punishes this habit immediately because your reader is often a stranger who is missing the exact piece of context that makes the rest of the page work.

Google's technical writing course identifies this as the "curse of knowledge." Their [audience guidance](https://developers.google.com/tech-writing/one/audience) states that writers must account for the reader's role and their proximity to the subject matter. I had to learn to be explicit about prerequisites that I once thought were too basic to mention.

I also had to unlearn the "idempotency" of my engineering explanations. In code, an idempotent operation can be run multiple times without changing the result. In writing, repeating the same explanation in different ways on the same page just creates noise. I had to learn the value of a single, precise definition that I could link back to whenever the concept reappeared.

## I kept the instinct to debug the "unhappy path"

Technical writing rewards the engineer's habit of looking for failure modes. Most documentation describes the "happy path," which is the sequence where everything works perfectly on the first try. Real software rarely behaves this way.

A debugger's mindset persists in my writing for this reason. One recurring problem in AI content is the neglect of control flow and observability. My post on [Agent harnesses](/blog/agent-harnesses/) grew out of that frustration. Plenty of material explained how to prompt an agent, but almost nobody explained how to handle the failure when the agent entered an infinite loop. Great documentation comes from someone who has already anticipated the crash.

## I left behind local optimization of prose

Engineering often rewards local optimization, speeding up one specific function or cleaning up one specific module. Writing has similar local moves, such as perfecting a single sentence or adding a clever analogy. I found that local optimization in writing can easily damage the utility of the whole page.

<div class="visual-wrapper">
  <div class="visual-title">The Context Bridge</div>
  <div class="visual-container">
    <iframe src="/static/visuals/context-bridge.html" title="The Context Bridge" loading="lazy"></iframe>
  </div>
</div>

A sentence can be grammatically perfect and still wrong for the audience. A section can be technically brilliant and still ruin the flow of a tutorial. I had to learn to cut sections that I was personally proud of because they added unnecessary weight to the reader's journey.

Microsoft's [style and voice quick start](https://learn.microsoft.com/en-us/contribute/content/style-quick-start) emphasizes empathy and conciseness. They advise writers to focus on the customer's intent and use everyday words. I learned that an engineer's desire for "completeness" is often the enemy of a reader's need for "utility." Ruthless omission is a professional requirement in technical writing.

## I kept the respect for Docs-as-Code tooling

Writers who treat documentation as a sidecar artifact usually end up with a library of stale truths. Engineers understand that the artifact only remains valid if the process around it is rigorous. I embrace the operational side of the job because the shape of the work is familiar to me.

I use the same tools for documentation that I use for code.

- **Version Control:** Storing Markdown files in Git repositories alongside the source code.
- **Linting:** Automated style and link checks to catch errors before they reach the reader.
- **CI/CD Pipelines:** Automated builds that generate previews of the documentation on every pull request.
- **Review Gates:** Ensuring that a technical expert has signed off on every change.

The **Write the Docs 2024 salary survey** shows that this "DocOps" side of the field is expanding. The survey collected data from 55 countries and identified 217 unique job titles, many of which focus on information architecture and tooling rather than just drafting prose. Technical writing is a production function that scales through process, not through individual charisma. You can read the full survey results at [writethedocs.org](https://www.writethedocs.org/surveys/salary-survey/2024/).

## I left behind the idea of "shipping and forgetting"

Code enters a maintenance phase once it is shipped. Documentation follows the same lifecycle, yet many teams behave as if clicking "publish" is the end of the project. I learned to think in terms of maintenance costs for every page I create.

Search queries change over time. Product defaults drift. Screenshots become outdated as the UI evolves. I view a published tutorial as a living system that requires recurring validation. I also look for opportunities to link older posts to newer ones, turning the site into a network of information rather than a pile of isolated blog posts.

One example from this site is [How to Write a Changelog That Developers Actually Read](/blog/how-to-write-a-changelog-developers-actually-read/). That post creates a stable reference point that I can link to in every subsequent piece about developer communication. Maintenance is not a chore. It is how you preserve the value of the technical assets you have already built.

## I left behind a narrow definition of what is "technical"

Some people assume that moving into writing is a step away from technical substance. My experience is that writing for a technical audience is one of the most intellectually demanding forms of engineering work.

Serious technical writing requires six specific skills.

1. Accurate reading of source code and internal specs.
2. Judgment of the product's underlying mental model.
3. Rigorous verification of every code example.
4. Strategic information architecture for the entire site.
5. Empathy-driven calibration for different audiences.
6. Ruthless editorial compression under technical constraints.

Google’s materials on [becoming a technical writer](https://developers.google.com/tech-writing/becoming/meet) show that many writers arrive from roles in software engineering, support, and testing. This framing matches my own belief. Technical writing is not a decorative layer added to engineering. It is a separate production function with its own success metrics.

If you are looking for this kind of depth for your own team, [my work page](/work) shows how I apply these engineering habits to client projects.

## What changed in my day-to-day workflow

Three major shifts stand out from my time in this role.

First, feedback loops became more legible. A confusing page fails in visible ways that are often easier to observe than a latent bug in a distributed system. Readers drop off at specific steps. Support questions repeat the same patterns. When you are willing to look at the data, documentation failure is highly observable.

Second, audience empathy moved from a "soft skill" to a core production requirement. An engineer can occasionally succeed while being impatient with a user's lack of context. A technical writer cannot. My job is to bridge that difference by becoming the "first user" of every feature.

Third, the reach of my work shifted. A feature helps the users who find it. A well-written page can change the understanding of thousands of developers before they ever interact with your product. I focus on durable technical assets (changelogs, migration guides, and deep-dive tutorials) because they provide the highest return on investment for the team over the long term.

## FAQ

**Do engineers have an advantage when they switch to technical writing?**

Yes, but only if they are willing to unlearn their communication habits. The advantage comes from their ability to read source code, verify examples, and understand system architecture. The risk is that they will write from their own private context and leave the reader behind.

**Which engineering skill was the most useful for me?**

Empirical verification. Refusing to publish anything that I haven't tested on my own machine prevents the most common trust-killing errors in documentation.

**What was the hardest habit to break?**

I had to stop compressing my explanations too early. I used to write for the person who already understood 90% of the system. I had to learn to write for the person who is missing the exact 10% that makes the whole system fail.

**Does technical writing involve less technical work than engineering?**

No. It involves a different type of technical work. You are still reading code, testing APIs, and designing systems. You are simply producing a technical document as the final artifact instead of a pull request.

**Should I move into technical writing if I enjoy explaining things?**

Enjoying the explanation is only half of the job. You also need to enjoy the research, the verification, the editing, and the architectural design of information systems. If you find those tasks as rewarding as writing code, the transition is likely a good fit.