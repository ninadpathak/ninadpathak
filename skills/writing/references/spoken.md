# Spoken-narrative articles

<!-- check_prose: word-mentions-allowed (names banned sentence openers) -->

This skill writes articles that read the way a great talk sounds. The model for the voice is a technical lecture transcript: an engineer walks an audience through a complex system, and the whole thing holds together because every sentence hands the reader to the next one. No ums, no filler, no verbal tics. What stays is the connective tissue and the storytelling.

The style rests on two things, and both matter equally:

1. **Connectors.** Sentences are linked by small spoken bridges that tell the reader how the next thought relates to the last one.
2. **Story shape.** The piece moves through time and tension (how we got here, what broke, what changed, where it goes next) instead of dumping parallel facts.

If an article has only connectors, it feels chatty and empty. If it has only story shape, it feels like a case study with no voice. The skill is the combination.

## Why this style works

A listicle makes the reader do the connecting work. They get five facts and have to figure out why fact three follows fact two. A spoken narrative does that work for them. Each connector is a tiny promise: "this next thing explains the last thing," or "this next thing complicates it," or "this next thing is the payoff." Readers stay because the path is lit. Keep that in mind whenever you are tempted to cut a connector for brevity. If it carries a relationship between two ideas, it is doing real work.

## Process

1. **Find the arc before writing.** Ask what changed, what the old way was, what broke, what the new way is, and what is still unsolved. A topic about change has this shape. Write the arc in one sentence per stage before drafting.
2. **Open by orienting the reader.** Set the title and headings first, following [article.md](article.md). Say what the piece will cover and why it matters now, then preview the structure ("I'll go over six", "we'll get into that in a second"). For a web article, the intro's last sentence is the preview, in the author's voice: "in this article I'll walk you through ...". Speakers do this because listeners cannot skim ahead. Readers benefit too.
3. **Draft in flowing paragraphs.** One idea per paragraph, each paragraph ending in a handoff to the next. Reach for the connector bank in [spoken-connectors.md](spoken-connectors.md) as you go, but let each connector earn its place. Keep the word list in "Banned words and AI tells" open while you draft. The intro keeps its orienting warm-up. Spend setup and signposting sentences on the budget in "Setup sentences: use them, on a budget" below, and lead every other paragraph with its claim.
4. **Anchor every abstract claim with something concrete.** An analogy (a colleague, texting a friend, hovering over a link so the next page preloads), a worked example, a number, or a short scenario. The source voice never leaves an idea abstract for more than a few sentences. Pick the analogy that maps the mechanism accurately; when the article has a real concrete case, prefer it. See "Examples that earn their place" below.
5. **Close the loop.** Finish with takeaways and open problems, the way a talk ends. Name what is unsolved. It signals honesty and gives the reader somewhere to go next.
6. **Run the edit pass** (see below), including the banned-words sweep, before delivering.

## The voice, in practice

**Think out loud, but with a plan.** The prose can reason in real time ("Why is this important? Well, ...") because the writer already knows where it lands.

**Ask a question, then answer it.** A self-posed question followed by "Well," or a direct answer is the signature move for introducing a new component. It simulates the reader's own curiosity. It counts toward the setup budget below, so use it where the question is the reader's real one, not in every section.

**Narrate in eras and contrasts.** Set up the before ("you would prompt an agent, you would wait, you would approve a command"), then the after ("now you steer it mid-task"). The contrast is what makes the change feel real.

**Reason in ladders.** When there are several options, present them cheapest or simplest first and climb, ending with the fallback. Order carries meaning.

**Use plain, specific language.** Short, direct verbs. Real product names, real numbers, real failure modes. Say "the cache missed and every token got billed at full price" instead of "performance degraded."

**Let a little humor and honesty in.** One dry aside per section is plenty ("which feels like decades ago, but was only a few years"). Admit uncertainty directly ("I don't think we have it perfect yet").

**Address the reader directly.** "You close your laptop and the process stops." Second person keeps it a conversation.

## First person

Write the body as the author talking to the reader. The voice has two people in it: "I" is the author and "you" is the reader. A body with no "I" in it reads like documentation, however good the connectors are, so the first person is part of the style and not an optional extra.

**Where "I" goes.** Use it for the author's own deliberate choices, judgments, orderings and admissions, the places where the article makes a call the reader could have seen made differently:

- Which example or setup the author picked, and why: "I'll use a throwaway database called sample_app, so nothing here touches a real one."
- What the author would reach for first: "I'd reach for psql -l first, because it needs no open session."
- Which route or engine the article takes: "To show you how this works, I will use an example of ..." and "I'll run each query in SQLite and PostgreSQL, because they disagree in one place."
- What was checked, and what was not: "I ran this on PostgreSQL 18.6." "I could not find a published rule for this, so treat it as observed behavior."

**Where "you" and "we" go.** "You" is the reader, in their own hands-on moments ("you type", "you'll see"). "We" is for walking through something together, such as stepping through a query one clause at a time, and nowhere else. Use contractions (I'll, you'll, it's, don't, can't), because the voice is spoken, not written. Prefer the active voice, and avoid a passive or gerund opening on a sentence the reader is meant to hear.

**The intro.** Keep the intro's second sentence on the reader's snag, true for anyone who searched the topic. Close the intro with "in this article I'll walk you through ..." and name what the article covers. That closing sentence is the first "I" in the piece, and it is required.

**Where "I" never goes.** Never invent experience. No made-up personal history, habits, clients, projects, anecdotes, numbers or timelines for the author ("When I run Home Assistant ...", "I've fixed this a hundred times", "a client of mine ..."). First-person facts come only from what the author has stated or what the article itself did. The first person here belongs to choices, judgments and honest admissions that the article itself makes, and never to fake experience.

**Order and density.** The first sentence under each H2 still answers the heading in plain words. The first person comes after that answer, never in place of it. Aim for about one first-person sentence per 150 to 250 words of body, spread through the piece and never in every paragraph. A 1,500-word article carries roughly six to ten, each one attached to a real choice or admission. When a section has no choice or admission in it, leave it in plain "you" voice.

A before and after, from a PostgreSQL listing article:

- No first person (reads like a manual): "The examples use -X to prevent a local psql startup file from changing the output. Choose psql -l when you have not opened the client yet."
- First person (same facts): "I've added -X to every command so a startup file on your machine can't change the output. I'd reach for psql -l first, because it needs no open session. Once you're already at the psql prompt, `\l` does the same job."

The second version adds no new facts. It states which command the author picks and why, and it talks to the reader.

The budgets and rules elsewhere in this file stay as they are: the setup-sentence budget, answer-first headings, banned words, attribution frames, examples that earn their place and the SEO pass all apply to first-person sentences too.

## Where this form departs from the core

The core calls a sentence that announces a point a defect, and [editing.md](editing.md) cuts self-answered questions. This form is the stated exception: orienting connectors, the self-posed question and the setup-sentence budget below are part of the spoken voice, and inside a spoken-narrative article they win. The exception covers only those devices, inside their budget. Every other core rule still binds, and a setup sentence that orients nobody is still cut.

## Connectors: how to use them

The full bank, grouped by job, is in [spoken-connectors.md](spoken-connectors.md). Read it before drafting. The short version of the rules:

- Match the connector to the relationship: addition, contrast, cause, consequence, example, return, summary, shift. Using a contrast connector on a consequence misleads the reader.
- Start many sentences with a connector, but vary it. A run of three "So" openers reads like a tic. Rotate through the families.
- Let connectors open sentences and paragraphs, and use them to stitch short sentences together mid-paragraph ("which means", "and the reason is").
- Cut any connector that links nothing. A transition with no relationship behind it is filler, and filler is the one thing this style forbids.

## Setup sentences: use them, on a budget

Match the source speaker's rhythm. This skill was built from a real speech by a highly valuable developer, and setup and signposting sentences are a genuine part of how that speaker talks: "Here is the part that makes...", "Let's make that concrete with an example.", "Zooming out,", "So the takeaway is short.", "Now, how do you...?", "Going back to...", and ordinal walks like "The first one is...". These devices are what make the voice work, and none of them is removed or weakened here. Each does a job: announce a pivot, introduce a worked example, summarise, orient the reader after a dense stretch. The only goal of this section is spacing, so they land where the reader needs them and do not pile up.

**Frequency budget (soft guidance).** About one setup or signpost sentence per 250 to 350 words of body, so about four to six in a 1,500-word article. This is a range to aim for, not a hard cap. The numbers are provisional and can be calibrated against the source transcript by measuring its setup sentences per 1,000 words.

- Space them out: avoid two in the same paragraph or in consecutive paragraphs.
- Avoid repeating the same phrase in an article.
- Rotate the family: a pivot, a "let's make that concrete", a zoom-out, a callback to an earlier idea, a wrap-up, a self-posed question with the answer right after.
- Spend them where the reader needs orientation: the first mention of a new component, before a worked example, at the turn from problem to solution, and at the end.
- Everywhere else, lead with the claim itself, then the reason, then the consequence. The first words of a paragraph are the thing the reader came for.
- Ordinal and topic labels ("The first culprit is...", "Next is...") count toward the budget when they only label. A numbered preview with an ordinal walk ("I'll go over four. The first one is...") is a source-voice device and is welcome once per article where the structure pattern below calls for it.
- The self-posed question stays the signature move: about one per two sections, when it is the question the reader actually has, with the answer in the next words, rather than a fixed ritual in every section. The H2 often asks the question already, so open with the answer.
- **Attribution frames.** Attribute inside the sentence that carries the claim. Do not spend a throat-clearing frame plus a colon on it ("X's docs describe it directly:", "X is blunt:", "X says it plainly:", "X puts it this way:", "Here is what X says:"). Before: "OpenAI's docs describe it directly: the cache stores the model's key-value states for a reusable prefix, and a later request with a matching prefix skips reprocessing those tokens." After: "OpenAI's docs describe that cache as storing the model's key-value states for a reusable prefix; a later request with a matching prefix skips reprocessing those tokens." Another: "X lists base input at $2 per million tokens." Keep a colon only where it defines or scopes what follows. A direct quote with a real claim in it stays.
- Connectors are unaffected by the budget. They carry relationships between ideas ("Because tool definitions sit at the front of the prefix, changing one invalidates everything after it."), and the variety rule above still applies.
- The intro keeps its orienting preview and warm-up, and it is not counted against the body budget.

A before and after on frequency:

- Stacked (five setups in four paragraphs): "Here is the part that makes an agent's bill depend on any of this. Caching gives every token one of three prices. ... Let's make that concrete. Say you have an agent with a 50,000-token prefix. ... Zooming out, the failure modes say one thing. ... Going back to the three prices, the open problems live in the gaps."
- Spaced (one setup, before the worked example, and the rest straight claims): "Caching gives every token one of three prices, and which one you pay depends on the previous request. ... Let's make that concrete. At the Sonnet 5.5 rates above (illustrative arithmetic), a 50,000-token prefix reused across 20 calls costs $2.00 uncached and $0.22 with a clean cache. ... Any change near the top of the prompt costs you the discount."

Paragraphs without a setup sentence default to claim first:

- Setup-led: "Here is the part that makes an agent's bill depend on any of this. Caching creates three different prices for the same token, and which one you pay depends on what happened on the previous request."
- Claim-first: "Caching gives every token one of three prices, and which one you pay depends on the previous request."
- Label-led: "The first culprit is the timestamp. Manus calls out a timestamp precise to the second at the start of the system prompt as a common mistake."
- Claim-first: "A timestamp precise to the second at the start of the system prompt guarantees a miss on every request, and Manus names it as a common mistake."

The spoken voice lives in the logic and the rhythm (cause, consequence, contrast, a short sentence after a long one) as much as in the setup phrases, and spacing lets each setup phrase be heard.

## Examples that earn their place

An example is there to make a claim usable. If the reader cannot act on it or check it, it is decoration.

- **Use the reader's own likely situation.** Their real command, a real error message, real numbers from a named source, or a concrete case in the article's domain.
- **One example per claim, placed right after the claim.** Then state the pattern and stop.
- **Prefer a real concrete case when the article has one.** Real names, real values and runnable details: official-doc examples, real error output and real benchmarks.
- **Speaker-style analogies stay when they map the mechanism accurately.** A colleague resuming a report from the page where they stopped is a fair picture of prefix matching. Use one analogy per mechanism, and cut it if you would have to explain where it breaks.
- **A worked example uses numbers the reader can reproduce.** Show the arithmetic plainly and label derived numbers as illustrative.
- **No invented anecdotes.** No generic "say you have an agent that ..." scenario when a documented case or real numbers exist. When no real case exists, label the hypothetical and keep it checkable.
- **The deletion test.** If removing the example loses nothing the reader would use, cut it.

A before and after from the sample:

- Generic: "Say you have an agent whose tools, system prompt and reference material add up to 50,000 tokens, and it makes 20 model calls in a session. These are my own illustrative numbers, using the Sonnet 5.5 rates above."
- Concrete: "Let's make that concrete. At the Sonnet 5.5 rates above (illustrative arithmetic), a 50,000-token prefix reused across 20 calls costs $2.00 uncached and $0.22 with a clean cache: one write at $0.125 plus nineteen reads at $0.095."

The lead-in "Let's make that concrete." is a budgeted setup before a relevant, reproducible example. The generic version fails on the example itself: a generic "say you have..." scenario with no source and no arithmetic.

## Structure patterns

Use whichever fits the piece, and mix them:

- **Eras:** first this, then that, now this. Good for any "how we got here" section.
- **Numbered preview:** announce a count, then walk the items with ordinal connectors (The first one is..., Two, ..., And finally...). Write the ordinals in words inside the prose.
- **Problem, then fix:** show the pain concretely, then the mechanism that removes it, then the remaining tradeoff.
- **Zoom in, zoom out:** explain a component, then step back to show how it sits in the whole system ("So the idea is that, putting the pieces together, ...").
- **Callback:** reference an earlier point ("Going back to the queue versus workflow idea...") so the piece feels like one argument and not a pile of sections.

## Hard rules for the final text

These come from the author's editorial standards and apply to every article this skill produces.

- Zero fluff and zero em dashes. Use commas, periods or parentheses.
- Avoid contrastive parallelism, the "not X, but Y" or "it's not about A, it's about B" construction. State the positive claim directly. Contrast is fine when it describes a real before and after, such as old way versus new way.
- No clichés, no vague statements. Every claim should have a specific noun, number or example behind it.
- Do not begin any sentence with "In", "This", "By", "Finally", "Most" or "Ever", and do not begin a sentence with a number or numeral (write ordinals as words in the sentence body instead of leading with "1." or "6 reasons").
- No horizontal lines.
- Do not copy the verbal tics of the source speech: no "um", "uh", "like", "you know", "kind of", "sort of", "basically" used as padding, no false starts, no repeated words. Keep the bridges, drop the stammer.
- Prefer prose. Use headings to mark major turns. Use a list only if the content is a list, and even then introduce it with a spoken lead-in.

## Banned words and AI tells

The lists are in [core.md](../core.md) and the replacements in [rules.md](rules.md). A quoted source may keep a banned word inside quotation marks when the quote carries a real claim.

## Edit pass (do this before delivering)

Do a developmental edit, reading as the skeptical reader:

1. Does each paragraph hand off to the next with a real relationship?
2. Is there a place where three facts sit side by side with no connective reasoning? Add the reasoning.
3. Is any abstract claim running longer than a few sentences without a relevant example? Add one that passes "Examples that earn their place".
4. Search for banned openers, em dashes, "not X but Y" patterns and filler hedges, and fix them.
5. Does the ending name something unsolved, and does the opening preview match what the piece delivers?
6. **Setup budget sweep.** Count the setup and signpost sentences in the body (the intro is exempt). If the count is well above the range, thin the ones that merely label or repeat and keep the ones that orient. If it is below about three in a 1,500-word piece, add them back where orientation is needed. Check variety (no repeated phrase) and spacing (none stacked in the same or consecutive paragraphs). Run the example deletion test and the relevance test on every example. Re-run the connector variety check: no connector three times in a row.

7. **Heading-answer check.** List every H2 with the first sentence under it, and mark each pass or fail before delivering. A pass means the sentence answers that exact heading in plain words and names the actual items, behaviour, definition or number the heading asks for. A fail means it opens with background, a definition of terms, or a setup word ("So,", "Meanwhile,", "Now,", "Well,"), or it answers a different question. Fix each fail by rewriting the sentence, or by changing the heading, then list the pairs again.
8. **First-person check.** List every sentence that uses "I", "I'll" or "I'd". Confirm the intro's last sentence says "in this article I'll walk you through ...", the count is about one per 150 to 250 words and spread across the piece, and each one is a choice, a judgment, an ordering or an admission the article actually makes. Cut or rewrite any that invents history, habits, anecdotes or numbers for the author. Confirm no first-person sentence replaced an H2's answer: the first sentence under each heading stays the answer.
9. **Banned-words sweep.** Last item. Run `scripts/check_prose.py` on the whole draft, including title, headings, alt text, frontmatter and the meta description. Fix each hit by the replacements in [rules.md](rules.md), then re-read the sentence to confirm it gained no padding and lost no real claim. Check attribution frames in the same pass.

For a worked before-and-after, read [spoken-example.md](spoken-example.md).

## Titles, headings and the SEO finishing pass

Set the title and headings before drafting, and run the SEO finishing pass last. Both are in [article.md](article.md). The spoken voice lives in the body text and stays out of the headings.
