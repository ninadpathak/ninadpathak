---
title: "Writing with AI Before You Know What You Think"
date: 2026-09-07
description: "A polished draft can make an unsettled idea feel finished. Use AI to expose the assumptions that deserve another test."
category: technical-documentation
tags: [technical-writing, documentation, ai-writing]
status: published
slug: writing-with-ai-before-you-know-what-you-think
---

Deleting a good paragraph can improve an essay. The paragraph may explain its point clearly and still be defending an idea the rest of the draft has stopped supporting.

That becomes a practical problem when you ask AI to expand an outline before you have worked out its central claim. You can end up reviewing complete sentences while the decision that produced them escapes review.

I want AI involved in writing at that earlier stage. But I want the question to remain open long enough for an answer to earn its place.

## Letting a draft change its premise

Suppose you want to write that shorter documentation helps developers finish their work faster. You ask an assistant for an essay, and the draft explains that developers have limited time and prefer direct instructions.

Those reasons sound plausible. They also leave out the case where a short page sends a reader elsewhere to find a prerequisite that a longer page would have supplied.

Your claim now needs a condition. Cutting a page helps when the removed material does not have to be rediscovered before the reader can complete the task.

That change should affect the essay's recommendations. A paragraph arguing for a fixed length limit may have to disappear even if its sentences still read well.

An assistant can help examine the claim before it grows into a draft. I would start with a prompt like this:

```text
Claim: shorter documentation helps a developer finish a task sooner.
Describe a case where shortening the page increases total completion time.
Name the condition responsible for the reversal.
Keep the case hypothetical; do not invent research or customer results.
```

The response passes a useful first check if it describes a believable route from the edit to extra work for the reader. If it merely says “some readers prefer detail,” ask for the missing step or investigate the example yourself.

The assistant's answer supplies a possibility to examine. Whether that possibility occurs in your product still depends on evidence from the product and its readers.

“Removing the authentication step forces a new user to find it elsewhere” is an argument you can inspect.

“Readers perform better with longer tutorials” needs observations that the example does not provide.

## Keeping an explanation attached to its evidence

The same mistake can happen with a technical example. Consider an imaginary draft claiming that a database constraint prevents duplicate webhook processing.

The example below establishes something narrower. It uses an in-memory SQLite database to show how a primary key handles repeated inserts, following Python's [documented SQLite interface](https://docs.python.org/3/library/sqlite3.html).

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE received (event_id TEXT PRIMARY KEY)")
inserted = []

for event_id in ("event-a", "event-a"):
    cursor = db.execute(
        "INSERT OR IGNORE INTO received VALUES (?)", (event_id,)
    )
    inserted.append(cursor.rowcount)

assert inserted == [1, 0], inserted
assert db.execute("SELECT COUNT(*) FROM received").fetchone()[0] == 1
print("The repeated ID was inserted once.")
db.close()
```

The assertions should pass and the script should print its final sentence. If an assertion fails, inspect the local result before treating this example as evidence for the draft.

Even a passing result leaves the original claim unresolved. The script inserts IDs into a table without sending an email or establishing what happens if a process crashes between those actions.

An implementation that sends the email before recording the ID can send it again after a crash. Recording the ID first introduces a different failure: a crash before sending could leave a record that causes the retry to skip an unsent email.

The constraint remains useful. Its guarantee applies to the stored ID, and the relationship between that record and an external action needs its own design.

A writer who follows this example has to revise “prevents duplicate processing.” That phrase described a larger guarantee than the evidence supported.

I would ask the assistant to locate that mismatch: “List what the assertions establish, then identify which words in my claim go beyond them.” If the answer treats the printed result as proof about email delivery, the review has failed even though the code ran.

The writing problem comes back to [deciding what the reader can assume](/articles/technical-writing-is-deciding-what-the-reader-can-assume/). A technical sentence is consequential because another person may use it as a premise in their own implementation.

## Knowing when fluency helps

There are writing jobs where the central claim is already settled. If an engineer supplies a verified behavior change, an assistant can help turn it into a clear release note without first conducting a philosophical inquiry.

The distinction depends on what remains undecided. Rephrasing a checked statement and discovering what a statement ought to claim require different kinds of review.

AI can help try several explanations of the same verified result. Seeing how an explanation changes for a new user can expose an assumption that a specialist would fill in without noticing.

But the new explanation must stay within the original result. Calling a bug fix “reliable delivery” because it sounds more helpful can turn a wording task into an unsupported promise.

The [documentation review checklist](/articles/documentation-review-checklist-before-you-publish/) separates checking behavior from checking presentation. That separation gives a fluent draft somewhere useful to go: it can improve the presentation after the behavioral claim survives review.

An exploratory essay needs a fresh look at its claim after a substantial revision. If the strongest example has changed, the introduction may now be promising an argument the body no longer makes.

## Preserving the freedom to throw work away

The attraction of a complete draft is that it gives you something to edit. It also gives the original premise a great deal of supporting prose, which takes effort to reconsider as a whole.

A small exploratory request leaves less work to abandon when its answer fails. A counterexample can be more useful than another section when it changes what the existing sections should say.

That does not require writing alone or refusing help with sentences. It requires retaining responsibility for the connection between a sentence and the reason to believe it.

The final read should include a paragraph you like. Remove its supporting evidence in your head and ask whether you would still keep it because it sounds good.

If so, the next useful request to the assistant may be to help replace the claim, even if that means losing the paragraph. The finished essay should carry the idea that survived the work.
