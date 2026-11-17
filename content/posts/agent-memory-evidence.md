---
category: agent-memory
primary_query: none
siblings:
- memory-serialization
- memory-versioning
date: 2026-11-17
description: A proposal for a shared agent memory format lists five questions a record must answer. This essay argues for a sixth, how the agent knew, as a required field.
slug: agent-memory-evidence
status: published
title: "I went looking for the citation field in a proposed agent memory format"
work_note: 'I ran Mem0''s team of 13 writers, and I write documentation where a claim needs a source a reader can check. This essay asks the same of an agent''s notes, and [my portfolio](/portfolio/) has the work.'
---

<div class="visual-wrapper">
  <div class="visual-title">xkcd 285, Wikipedian Protester</div>
  <div class="visual-container">
    <img src="/static/images/visuals/xkcd-285-wikipedian-protester.png" alt="xkcd comic 285. A politician speaks at a podium to a crowd, and a man in the crowd holds up a sign that reads: [CITATION NEEDED]." width="500" height="271">
  </div>
</div>
<p class="visual-caption"><a href="https://xkcd.com/285/">xkcd 285</a>, Randall Munroe, CC BY-NC 2.5.</p>

An agent's memory file is a page of uncited claims with one reader. Anthropic's post on [the components of agent memory](https://www.anthropic.com/research/components-of-agent-memory), published on November 6, says what that reader does with a wrong one: it "can be read, and trusted, by Claude in a later session."

So when Mads Thines argued on November 7 that [agent memory needs its OpenTelemetry moment](https://www.lorekit.io/blog/open-agent-memory-format), I read it looking for the citation field. He has it, and he leaves it optional, which is the one thing in his proposal for [AI agent memory](/articles/agent-memory/) I'd change.

## What the proposal asks for

Thines counts the places his coding tools keep what they remember and finds that "none of them can read the others". His remedy is the one observability reached in 2019, an agreed data model that vendors stop competing on.

His reduction of that model is five questions every format answers: "where a memory is true, what its identity is (does a second write update it or duplicate it?), what it says, when it stops being true, and which version is current."

The post is fair to its critics, and it prints the objection that traces and memories differ, since a trace is written once and a memory gets corrected.

And Thines gets close to my point more than once. He wants a record to say who wrote it, "so a reader knows how much to trust what it reads", and he praises GitHub's Copilot Memory because it "pairs citations you can check against the code with forgetting by default".

But he ends with it as an open question: "Should a record point at the code it depends on?"

## The sixth question

None of the five questions asks how the writer knew. A record can say where it applies, who wrote it and when it expires, and still be wrong, and the fields that would let a reader find out are the optional ones.

Is there evidence that this field does the work? Only a hint, from the Anthropic post.

On a benchmark where models built their own notes across sessions, the first model to close the loop was one whose entries "included a rule (and also how it knew the rule was true)".

That describes what a stronger model wrote, and the post doesn't test the clause in isolation, so I won't claim it does.

Anthropic also quotes a note written by a model playing Pokémon, a rule for what to do after several failed throws: "VARY the timing (insert extra 'wait' presses between menu steps) - the catch landed right after doing this."

The last clause of that note is a citation. A later session reading it knows the rule came from one success, and can weigh it as that.

The post's failure case is a wrong note that got trusted. A model recorded a landmark on the wrong side of a mountain and kept acting on it, and in a separate run, a pass that checked the note against the session log caught the error.

## Why format comes second

The commenters on [the Hacker News thread](https://news.ycombinator.com/item?id=50411467) made the case against a format better than I could. A commenter wrote that the need for a spec "is greatly reduced in the case of Agent memory because by definition it is read by agents", which can already read files in any shape.

Another had given up on the feature: "it remembers the wrong things, and then turns them into an inane focus for each task." That is a complaint about trust, and a shared envelope would deliver the same wrong things to more tools.

Thines half agrees, as I said. He calls a pointer to the code "the best protection against stale memory", and his draft record has room for a pull request number among its optional attributes.

A shipped product already goes further. His own table lists Copilot Memory's unit as "A fact with code citations", and its forgetting rule as "Deleted after 28 days unused".

So optional is the part I'd change. A record with no source should be readable as a guess, the way an untagged sentence on Wikipedia is readable as unchallenged, and a model should be told the difference.

## What a sourced note looks like

It needs little. A note says what was observed, where, and when: the command and its output, the file and line, or the turn of the session in which the user said it.

I hold a documentation page to that standard, and the reason is the same. A reader who can check a claim doesn't have to trust the writer, and for an agent the writer is an earlier session that can't be asked.

My page on [memory serialization](/articles/memory-serialization/) keeps the log beside the record for this reason, and [memory versioning](/articles/memory-versioning/) covers what to keep when a note is corrected. A shared format would be worth having once the notes inside it can be checked.
