---
title: "Code Documentation: Comments, Generated Reference, and External Guides"
date: 2026-08-18
updated: 2026-08-18
description: "Decide what belongs in code comments, generated reference, and written guides so each reader can find the right kind of answer."
tags: ["documentation", "technical-writing", "developer-experience"]
takeaways:
  - "Put local rationale beside the code that needs it to be read correctly."
  - "Generate reference from stable contracts that source can expose."
  - "Use guides for decisions, sequences, and operating context that no symbol can contain."
status: published
slug: "code-documentation"
---

A codebase starts to become hard to change when the reason for a line lives in a handbook, while the handbook repeats signatures the source already knows. I use a simpler boundary in this site's Python code: comments explain local reasoning, generated reference records stable contracts, and guides carry the decisions that connect several parts of the system.

That division keeps each form honest about what it can maintain. A comment can travel with a branch, a reference page can follow a public interface, and a guide can explain a reader's task without pretending that every answer belongs beside one function.

## Put local reasoning beside the code that needs it

A comment belongs near code when removing it would make a careful reader misread the implementation. It should explain a constraint, an invariant, a surprising choice, or a boundary that the names and control flow cannot make obvious.

### Comments explain intent that syntax cannot carry

In this site's [build script](https://github.com/ninadpathak/ninadpathak/blob/main/build.py), I keep comments next to decisions such as stable ordering and class-based stylesheet detection because those rules protect output that a later edit could quietly break. The comment earns its place because a reader changing that code needs the reason before changing the condition.

A line-by-line translation of the code adds maintenance work without adding meaning. Google's [API reference guidance](https://developers.google.com/style/api-reference-comments) makes the same distinction in another form: documentation comments should describe behavior and required details instead of repeating a name that already says what the symbol does.

### Docstrings define the unit a caller can depend on

A docstring belongs on a module, class, function, or method when it states the unit's contract in language a caller can use. Python's [pydoc documentation](https://docs.python.org/3/library/pydoc.html) explains that its displayed documentation for modules, classes, functions, and methods is derived from each object's docstring.

That makes a docstring more than an internal note. When the contract is stable enough for a caller or contributor to rely on, the same source-adjacent text can feed generated reference without copying it into another file.

## Generate reference from contracts that source can expose

Generated reference is the home for facts that need exact names, types, defaults, return values, and error behavior. It is strongest when the source, annotations, or structured comments can provide those facts directly.

### Generated reference keeps exact facts close to change

A reference page can show the interface without asking a reader to infer details from prose. [Python's documentation tooling](https://docs.python.org/3/library/pydoc.html) can present documentation in text or HTML, which is useful because the generated surface stays attached to the object it describes.

The same rule applies to APIs and configuration. Google asks API reference authors to document methods, parameters, return values, and exceptions because those details are part of the contract a developer implements.

### A generated page cannot explain a multi-step decision

Generated output can tell a reader what a parameter accepts. It cannot reliably decide which operation proves an integration is working, which prerequisite changes the order of setup, or what a team should do when an otherwise valid request fails in production.

That limit matters because a reference page can be complete and still leave a new reader stranded. The distinction between reference and explanation is useful in the site's [guide to technical documentation types](/articles/types-of-technical-documentation/), where each document earns its place through a different reader task.

## Write guides for decisions that cross symbols

A written guide belongs where the reader needs a path through several symbols, files, systems, or roles. Guides explain sequence, context, tradeoffs, and recovery, all of which exceed the scope of one callable interface.

### Guides connect a task to the contract it needs

A setup guide can show a reader where to begin, what must already exist, how to recognize success, and where to look when the result differs. The guide should link into reference at the exact point where a stable name or constraint becomes necessary.

That relationship keeps the guide readable and keeps the reference dependable. The site's [technical documentation template](/articles/technical-documentation-template/) uses the same split by giving task pages and reference pages separate jobs within one documentation system.

### Guides preserve context that source cannot reveal

Source code can show that a build copies deployment controls into an output directory. It cannot tell a new contributor which release responsibility owns those controls, why that handoff matters to a hosted platform, or what to inspect after a deployment changes.

Put that knowledge in a guide, README, architecture note, or runbook according to the reader's task. IBM's [code documentation overview](https://www.ibm.com/think/topics/code-documentation) also separates in-code material from broader documentation that explains how people use, maintain, and collaborate around software.

## Use one placement test before you document code

Ask what kind of answer the reader needs at the moment they discover the information. The answer determines the document's home more reliably than the format you happen to be editing.

| If the reader needs to know | Put it in | Why it belongs there |
| --- | --- | --- |
| Why this branch, guard, or ordering rule exists | A nearby comment | The explanation changes how that local code should be read or edited. |
| What a public callable unit accepts or returns | A docstring and generated reference | The contract needs exact, searchable facts that can remain close to source. |
| How to complete work across several units or recover from failure | A written guide | The reader needs sequence, context, and a decision that no single symbol owns. |

There is a practical objection to this boundary: maintaining several documentation forms can sound like duplicated work. It becomes duplication only when each form repeats the same answer, because the local rationale, contract facts, and reader path have different update triggers.

Keep the source of truth close to the change that can invalidate it. Then let the comment, reference, and guide send the reader to the next question instead of trying to answer every question in one place.
