---
category: technical-documentation
title: 'Code Documentation: Comments, Generated Reference, and External Guides'
date: 2026-08-18
updated: 2026-11-16
description: 'Code documentation has three homes: comments, generated reference and guides. Real examples, where each fact belongs, and whether agents should write comments.'
takeaways:
- Put local rationale beside the code that needs it to be read correctly.
- Generate reference from stable contracts that source can expose.
- Use guides for decisions, sequences, and operating context that no symbol can contain.
status: published
work_note: 'The comment and docstring examples on this page come from this site''s own build script. I write developer documentation for a living, and [my portfolio](/portfolio/) links to the published work.'
slug: code-documentation
video: code-documentation
---

Claude Fable 5.1 was told not to add code comments and added a comment or docstring anyway in 33 of 100 tasks. The count comes from [Shut up and SWE-bench](https://bayes.net/shut-up-and-swe-bench/), a small benchmark Tom Adamczewski published on September 24 out of one frustration: "AIs have such poor judgement for when to write a code comment that I prefer to have them write none at all."

Code documentation is the written material that explains source code, and it has three homes: comments for local reasoning, docstrings and generated reference for contracts, and guides for decisions that cross several parts of a system. The benchmark is an argument about the first home, and the post weakens its own no-comments rule when it says of the comments GPT-6 Astra added that "all 6 comments seem legitimate to me".

I believe the measurement and would throw out the rule. Models fill that first home with narration, which human teams have always done too, and the fix is the same for both.

## What is code documentation?

Code documentation is any text whose job is to help someone read, call or change source code. The forms differ in who reads them and in what makes them wrong.

| Form | Answers | Reader | Goes stale when |
| --- | --- | --- | --- |
| Comment | Why this branch, guard or ordering rule exists | Whoever edits these lines next | The lines change |
| Docstring and generated reference | What a callable unit accepts and returns | A caller | The public contract changes |
| Guide, README or runbook | How to finish work that spans several units | Someone with a task | The workflow changes |

The [types of technical documentation](/articles/documentation-types/) covers the wider set that sits outside the code.

## Code documentation examples from a real build script

A useful comment states a reason the code can't show, and a useful docstring states a contract a caller can rely on. Both examples below come from [this site's build script](https://github.com/ninadpathak/ninadpathak/blob/main/build.py).

```python
# Detect by CLASS, not by embed type. Gating visuals.css on "<iframe"
# missed five published pages that wrap an <img> or <picture> in a
# .visual-container, and they shipped unstyled. The class is what needs
# the stylesheet; the element inside it is irrelevant.
"has_visuals": ('class="visual-' in html) or ("<iframe" in html),
```

Delete that comment and the next editor will tidy the condition back into the bug it fixed. The opposite kind is the one ryandrake [quoted on Hacker News](https://news.ycombinator.com/item?id=49613881) on September 8, "This code returns true if the user clicked on a button -- not on the list view.", with the verdict "I don't care what the code doesn't do."

A docstring is the comment a caller reads, so it describes the unit from outside.

```python
def render_work_note(note) -> str:
    """Render plain text and one internal link, separate from the article body."""
```

Python's [pydoc](https://docs.python.org/3/library/pydoc.html) builds reference from that string, so one sentence serves the source reader and the generated page. Running it from the repository root prints the entry.

```bash
python -c "import build, pydoc; print(pydoc.render_doc(build.render_work_note, renderer=pydoc.plaintext))"
```

```text
Python Library Documentation: function render_work_note in module build

render_work_note(note) -> str
    Render plain text and one internal link, separate from the article body.
```

Google's [API reference guidance](https://developers.google.com/style/api-reference-comments) asks for the same thing at scale: describe behavior, parameters, return values and exceptions, and skip text that repeats what the name already says. The [API documentation guide](/articles/api-documentation/) writes one reference entry out in full and checks it against a running service.

## Should coding agents write code comments?

Yes, when the comment records a reason, and a ban is the wrong fix for the ones that don't. The rule in Adamczewski's own AGENTS.md, "Don't add any comments or documentation unless I explicitly ask for them.", would also have blocked the stylesheet comment above.

I think model comments read wrong because they narrate the change. A sentence about what the diff did is addressed to whoever reviews this session, and the reader of a comment is whoever opens the file next year.

Machine-written comments are regular enough to detect, whatever the tell turns out to be. The [classifier](https://entropicthoughts.com/better-ai-comment-classifier) kqr published on September 9 separates them from human ones, and "the headline number is the balanced accuracy of 77 %."

A better instruction turned up in Nathan Broadbent's November 13 [review of the Ponytail plugin](https://docspring.com/blog/posts/ponytail-vs-agents-md/). Broadbent summarises one Ponytail rule as telling an agent to "leave a shortcut: comment naming any limit you accepted and when to revisit it.", which is a rationale comment with a required shape.

DocSpring's repository, which Broadbent describes in the same post, applies the placement idea to whole directories. It has a root AGENTS.md and "a nested file next to each part of the code that has its own pitfalls (migrations, background jobs, the public API, CI)."

## Why the code alone isn't enough documentation

Code records what the program does and has no place to record what was rejected. The strongest version of the opposite view came from kaydub, in the [thread on Kevin Liao's documentation post](https://news.ycombinator.com/item?id=49955753) on October 4: "The code IS the documentation."

The reason given was experience with the alternative: "I kept tons of markdown docs and decision docs. Now those things are just causing problems because they got stale."

That evidence supports a narrower claim than the conclusion. Documents kept far from the code went stale, and that argues for moving each fact next to the change that can invalidate it.

Generated reference has the matching limit from the other side. It can list what a parameter accepts, and it can't say which call proves an integration works or what to do when a valid request fails in production.

## Where should each piece of code documentation go?

Put each fact next to the change that would make it wrong.

| If the reader needs to know | Put it in | Because |
| --- | --- | --- |
| Why this branch, guard or ordering rule exists | A comment beside it | The explanation changes how those lines should be edited |
| What a public unit accepts or returns | A docstring and generated reference | The contract needs exact, searchable facts that stay close to source |
| How to finish work across several units, or recover from a failure | A written guide | The reader needs sequence, context and a decision no single symbol owns |
| Which pitfalls apply to everything in a directory | A README or AGENTS.md in that directory | Agents and people both load it when they start work there |

Guides are where a [quick start](/articles/quickstart-guide/) or a page from the [technical documentation template](/articles/documentation-template/) lives, and each should link into reference at the point where an exact name becomes necessary. A change that breaks a public contract also owes its callers an entry in the [release notes](/articles/release-notes-template/).

Maintaining several forms sounds like duplicated work, and it becomes duplication only when each form repeats the same answer. A comment, a contract and a reader's route have different update triggers, so keep each beside its own trigger and let it hand the reader to the next one.
