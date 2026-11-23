# The core rules in detail

<!-- check_prose: word-mentions-allowed (this file names banned words in order to replace them) -->

[core.md](../core.md) states each rule in a line and carries the word lists. This file holds the replacements and the rejected examples behind them. Open it when a rule needs a worked case.

## Banned words: what to write instead

**easy / easier / easily.** Name the actual cost. The reader can judge easy for themselves.

| Before | After |
|---|---|
| Pulling decisions out of a transcript is the easy half | Pulling decisions out of a transcript takes one model call |
| an easier path | a path with no container to run |
| you can easily identify | you can identify · one grep tells you |

**most / mostly.** Give the real proportion, name the specific case, or restructure until no quantifier is needed. Never substitute *many*, *usually*, *typically* or *often*, which are the same unprovable claim in softer clothes.

| Before | After |
|---|---|
| Most new pages should edit an existing page | Check whether an existing page serves the same goal. If it does, edit that page. |
| most of the audience already has it | the audience the quickstart targets already has it |
| Documentation work is mostly responding | Documentation work is responding: something shipped, a page is now wrong |
| what matters most | what decides it |

In a decision tree, turn the frequency claim into a check the reader runs rather than a proportion they have to trust.

**ever.** Deletable with no replacement, or replaced by a real time bound.

| Before | After |
|---|---|
| the most valuable observation you will ever make | an observation you get once |
| before the model ever sees the text | before the model sees the text |

**leverage.** Use.

**quietly.** Delete, or say the fact: "quietly drops the discount" becomes "drops the discount without any error". The same goes for "quiet" and "silently" as drama ("the quiet cost"); a technical "silently fails" that describes real error handling is fine.

**Adverb tells.** genuinely, truly, honestly, frankly, literally (as intensifiers), simply (as a softener): delete. The sentence should carry its own weight.

`harness` stays where it names a real product concept. The ban is on the metaphor ("harness the power of").

**Shape-nouns.** A noun that names the outline of a thing instead of the thing reads as precise while carrying no information, and the reader has to translate it. Say what changes.

**Absolutes.** Wrong unless proven: every, all, any, always, never, nobody, everyone. Strip them or prove them.

**Where to check.** Body prose, headings, alt text, table cells, code comments, prompt strings and frontmatter descriptions. `scripts/check_prose.py` reads its lists from `core.md`, so a new tell is added there once, the day someone names it.

**Two failure modes.** Do not pad to route around a banned word. "There are a number of pages that will need editing" is worse than the original. Restructure until the claim is specific. Do not delete a real claim to satisfy the list. If a proportion genuinely matters, state the actual number and where it came from.

**A banned word inside a shipped prompt string** is a real conflict: changing it in the article desynchronizes the article from the repo. Change it in both, or flag it and let the owner decide.

## No sentence begins with a number

The rule also covers a quantity word standing in for a number (`Dozens of`, `Hundreds of`). It applies to captions, list-item bodies, table cells that read as sentences and alt text.

| Before | After |
|---|---|
| Three pieces make that work. | The design rests on three pieces. |
| Two minutes is a budget I hold myself to. | I hold myself to a two-minute budget. |
| One entry per user-facing capability. | Write one entry per user-facing capability. |
| 142 to 0 over an hour, database latency flat. | Requests fell from 142 to 0 over an hour, and database latency stayed flat. |

The number-first construction is a fragment with the actor removed, so the fix is to supply the subject it elided. Do not fix it by padding: "There are three pieces that make that work" trades this rule for the economy rule and loses. Keep the judgement when the sentence carries one ("Two days is my number" becomes "My number is two days"). Never alter the figure itself.

**The one exemption:** ordered-list markers are markdown structure. `1. Set the payload URL` stays exactly as it is. Do not rewrite ordered lists to dodge the rule and do not convert them to bullets. The rule governs the sentence after the marker.

## Grounded, and only as specific as the argument needs

A conditional that passes: "if your index was built in May, it cites May's policy". An invented vignette narrated as fact was rejected: "The RAG-backed support agent cites a refund policy replaced three months ago". Prefer the piece's own tested artifacts and documented facts as raw material.

A detail that fails the weaker-without-it test: "a 404 fixture returned 314 Markdown characters" in an intro is true, checkable and useless there. Details that survive go where they pay off, which for a test artifact's internals is the methodology section.

## Give one example, then the pattern

Ninad's words: *"They don't need to be fed the food in their mouth. If they just are presented with the food in the right order, they know how to eat it."*

Fix a comma-stuffed sentence by splitting it, by making a list or a table, or by dropping detail the reader does not need. Swapping the commas for semicolons or slashes fixes nothing.

## Plain and spoken

Compressed abstract phrasing fails even when it is short. Ninad rejected "Traditional automation fixes every route before the first run; an agentic workflow keeps the route open during the run" as "complicated shit" and rewrote it: "Traditional automation means defining each route beforehand. An agentic workflow, on the other hand, allows a language model to decide the next step based on the result from the previous step." Write it the way a person would say it aloud. Tight metaphors read as clever compression, not clarity, and the pressure is highest in TL;DR bullets and summaries.

- The first-read test: could a smart person who is new to the topic follow every sentence on first read? A sentence that needs a second read fails.
- Reference writers for the register: Paul Graham, Naval Ravikant and Simon Willison.
- Use real examples and analogies the reader recognises from their own work. Industry context connects ideas; it is never name-dropping.
- Contractions and a human register are fine. Stiff, passive or academic phrasing is not.
- Prefer the plain word: "uses" over "utilizes", "before" over "prior to", "decides" over "determines the disposition of".
- Prefer a concrete verb to a noun built from a verb. "That experiment split freshness from training" hides something the reader could have seen directly.
- Connect sentences with "so", "but" and "for example" where the logic calls for it. Prose with no connective tissue reads robotic.
- A concept is taught and never sold. Ninad: "Anyone who's smart should be able to convey their message in extremely simple words."

## The author is the builder

First person stays. What the first person is *doing* decides whether the piece reads as authority or as a struggling user.

Ninad, on a cookbook intro that described the author pasting transcripts into a chat window and re-reading them by hand: *"These cookbooks are going from the founder's account. And right now it feels like a dumbass guy."*

**Cut** these:

- narration of your own manual workarounds as clumsy: "I had been doing that half by hand", "I would paste it into a chat window"
- hedged competence: "I'm not sure this is the right way", "this is just a toy"
- any framing of the work as a hobby or an accident. No weekend project, no "for fun".
- positioning yourself as a confused user of the product you are rebuilding.

**Keep** what you chose and rejected, the threshold you set and why, and the hard part named as an engineering problem rather than a personal inconvenience. Keep limits as scope decisions. "There is no feedback loop from what the human did after a handoff, which is the signal that would tell you whether the policy is calibrated" reads as authority; "this is only a toy, don't rely on it" does not.

Lead with the sharp observation. The build-article opening in [openings.md](openings.md) shows it: the claim about a wrong owner comes first, where an earlier draft buried it under two sentences of the author being inefficient.

Never fix this defect by removing first person. That undoes the voice the piece needs.
