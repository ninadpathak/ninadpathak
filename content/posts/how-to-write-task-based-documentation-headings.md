---
title: "How to Write Task-Based Documentation Headings"
date: 2026-08-10
updated: 2026-08-10
description: "Turn vague documentation labels into headings that reveal the reader’s next task, decision, or recovery path."
tags: ["technical-writing", "documentation", "developer-experience"]
takeaways:
  - "A heading should name the action, decision, concept, or recovery path in its section."
  - "Heading levels describe content structure, not visual styling."
  - "Read the outline without body copy to test whether a skimming reader can find the next move."
status: published
slug: "how-to-write-task-based-documentation-headings"
---

A heading called “Setup” asks the reader to open the section before it reveals what setup means. That small delay gets expensive in a long guide, especially when the reader has returned to fix a failed request or complete one unfinished step.

Task-based headings make the route visible before the body copy begins. They name the work, the thing being changed, or the condition the reader needs to recover from.

<div class="visual-wrapper">
  <div class="visual-title">A vague label versus a reader task</div>
  <picture>
    <img src="/static/images/articles/how-to-write-task-based-documentation-headings/task-heading-anatomy.svg" width="1344" height="640" alt="A diagram changes the vague heading Setup into Configure the client with an API key, then labels the reader task with action, object, and context." loading="lazy" decoding="async">
  </picture>
</div>
<p class="visual-caption">The better heading gives a skimming reader an action, the thing it applies to, and enough context to decide whether the section is relevant.</p>

## Give each section one reader job

A heading is a navigation label, a link target, and a promise about the content below it. [Google’s documentation style guide](https://developers.google.com/style/headings) recommends descriptive, unique headings and says that a tutorial title should be task-based when the document’s primary purpose is to guide work.

Start by naming the job the section performs. A procedure moves the reader through work, an explanation resolves a concept, reference identifies a specific object, and recovery helps the reader respond to a condition.

| Section job | Weak label | Heading that exposes the job |
| --- | --- | --- |
| Procedure | Setup | Create the project and install the CLI |
| Configuration | Configuration | Configure the client with an API key |
| Verification | Testing | Verify the endpoint accepts a signed test event |
| Recovery | Errors | Recover when signature verification fails |
| Explanation | Authentication | Understand how token scopes limit an integration |
| Reference | Options | Choose a retry policy for background jobs |

The rewrites do not need to be longer for their own sake. They need to remove the question that forces a reader to inspect the paragraph before deciding whether the section helps.

## Name action, object, and context when the section guides work

A procedure heading often needs a verb because it represents work that changes state. “Configure the client with an API key” tells the reader what to do, what they will touch, and the constraint that makes the step specific.

The context can be a prerequisite, a target environment, a decision boundary, or a failure condition. Add it only when it changes what the reader should do next.

Use the reader’s goal before naming the product control. [Diátaxis describes how-to guides as goal-oriented directions](https://diataxis.fr/how-to-guides/) that should be framed around a person’s task or problem, not a system walking through its own controls.

That distinction keeps headings from becoming a menu transcription. “Set the `retry_after` field” may be accurate, yet “Delay retries after a rate-limit response” explains why a reader would open the section.

## Use noun phrases for concepts and references

A task verb is useful when a section changes something. It becomes awkward when the page needs to define a concept or identify a field, so use a noun phrase that names the subject and its boundary instead.

“Token scopes and integration access” gives a reader more help than “Overview.” “Webhook signature headers” gives them a better anchor than “Details.”

The test is simple: can a reader predict the section’s content from its label alone? If the only answer is “some information about this topic,” the heading still depends on surrounding prose to do its job.

## Keep hierarchy separate from wording

<!-- evidence-three: W3C is the named source institution in the linked tutorial. -->
A precise sentence is not automatically a good heading if it appears at the wrong level. [The WAI headings tutorial](https://www.w3.org/WAI/tutorials/page-structure/headings/) explains that heading ranks communicate the organization of a page and create in-page navigation for browsers and assistive technologies.

Use one page title for the page’s primary job. Use major section headings for its main tasks or concepts, then use nested subheadings to break a complex stage into smaller work that belongs beneath it.

Do not choose a heading level for its size. Styling can change the visual presentation, but a skipped level changes the document structure a screen reader and a table of contents need to interpret.

## Test the outline before polishing paragraphs

Hide the body copy and read the Markdown headings from top to bottom. A useful outline exposes where the reader begins, which work follows, where a choice appears, and how they can verify or recover.

I used the tiny audit below on a webhook outline during this article’s preparation. It catches a deliberately narrow group of labels, so use it as a prompt for review rather than proof that every heading is good.

```python
import re
from pathlib import Path

VAGUE = {"overview", "setup", "configuration", "usage", "examples", "errors", "conclusion"}
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

for line in Path("webhook-guide-outline.md").read_text().splitlines():
    match = HEADING.match(line)
    if match:
        text = match.group(2)
        status = "REWRITE" if text.lower() in VAGUE else "OK"
        print(f"{status:7} {text}")
```

The first fixture contained `Setup` and `Errors`, and the audit flagged both labels. Replacing them with “Create the endpoint that receives events” and “Recover when signature verification fails” produced an outline where every heading named a subject or a reader task.

```text
OK      Configure webhooks
OK      Create the endpoint that receives events
OK      Verify the endpoint accepts a signed test event
OK      Recover when signature verification fails

Outline names a subject or reader task at every level.
```

The script cannot judge whether “Configure the client” is the right task for your reader. That call still needs product knowledge, a clear starting state, and the same rendered-page review you would apply to any [documentation release checklist](/articles/documentation-review-checklist-before-you-publish/).

## Rewrite headings where readers lose their place

Start with the points where a reader has the strongest reason to scan: the first action, a prerequisite, a verification step, a risky decision, and a likely recovery path. Those labels determine whether the rest of the guide feels like a route or a pile of topics.

A full tutorial needs the broader path from starting state to checked result. The [technical tutorial guide](/articles/how-to-write-a-technical-tutorial-that-actually-teaches/) covers that structure, including runnable examples and visible checkpoints.

For an existing page, change one outline before rewriting its prose. The section label should tell the reader why the paragraph exists, and the paragraph should then deliver exactly that work.
