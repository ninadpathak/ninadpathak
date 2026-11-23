# The deferral family

<!-- check_prose: word-mentions-allowed (quoted defects and Ninad's own rewrites) -->

Ninad rejected the same defect six times in six costumes. Treating it as one family works.

A sentence that points at content instead of delivering it.

| Costume | The defect | The fix |
|---|---|---|
| Restates the structure | "That is the whole list." after a list | Delete. The list ending says it ended. |
| Denies what was never claimed | "No database to provision, no queue, no tunnel." | Delete. Nobody was worried. |
| Announces a turn | "The half I wanted to understand was the other one." | Delete and let the next sentence turn: "The hard half is knowing which requests to leave alone." |
| Locates the answer | "The useful part of Granola is the end: a rambling call becomes a short list." | "Granola turns a rambling call into a short list someone can act on." |
| Defers across a pair | "Writing at that level starts further back than writing. It starts with understanding the product." | "Writing at that level starts with understanding the product well enough that..." |
| Ranks two things already said | "That is the more interesting half." | Delete. |

**Test per pair of sentences, not per sentence.** Every row above passes a per-sentence check in isolation, which is how they survived four cleanup passes. Where two consecutive sentences can be one with no loss, make them one.

**Delete the frame, assert the thing.** Kill on sight:

- "The useful part of X is..." · "The interesting thing about X is..." · "The thing to understand about X is..."
- "What matters here is..." · "The key insight is..." · "Where this gets hard is..."
- "But here is the thing" · "That is where it gets interesting" · "There is a second reason to do this"
- "Two rules keep it usable" · "One more thing cost me an afternoon" · "I should be straight about how often this fires"

Know the line between locating and asserting. "The colour rule is the other decision I would repeat" carries a judgement and stays. "The boundary I care about is between the extractor and the verifier" only locates, and becomes "I put the boundary between the extractor and the verifier."

**Informative colons and scoping lines stay.** A colon lead-in, a framing question or a "we're not doing X" line that defines a term, states the exact question or marks what is out of scope is content, not deferral. Ninad kept: "Here, we'll judge policy faithfulness: did a refund-support agent answer from the supplied policy without inventing a rule? We're not comparing two candidate answers or grading tone." Cut only zero-information announcements ("Let's build one", "Two studies help explain why").

## Worked rewrite 1: the deferred pair

Before:

> Writing at that level starts further back than writing. It starts with understanding the product well enough that you can look at a change someone shipped and say what it costs the person using it.

After, Ninad's own:

> Writing at that level starts with understanding the product so well, you can easily identify when a feature has been added or changed and how it affects the outcomes users want.

His note: *"'Writing at that level starts further back than writing' is redundant… see how we stopped wasting the reader's time? A technical writer never writes BS."*

The pair became one sentence and nothing was lost. The first sentence's only content was a direction, *further back*, which the second then had to supply anyway.

(His rewrite contains "easily", which the banned-word rule now forbids. The published line names the cost instead: "you can identify when a feature has been added or changed".)

## Worked rewrite 2: the framing opener

The "Locates the answer" row in the table above was the first attempt at a cookbook intro. Ninad: *"unnecessary buildup."* The frame announces where the answer lives before giving it, so the fix deletes the frame and asserts the claim.

## Worked rewrite 3: the announcement sentence

The Fin article carried this line:

> The half I wanted to understand was the other one. A support agent earns its place by being trusted with a queue...

The sentence's only job is to signal that a pivot is coming, and the sentence after it already makes the pivot. Published version:

> The hard half is knowing which requests to leave alone. A support agent earns its place by being trusted with a queue...

## Shapes to catch, so the pattern is findable

- Names a direction or category, then a second sentence fills it in: "It starts further back than X. It starts with Y." → "It starts with Y."
- A pronoun-subject continuation that merges upward: "It starts with...", "That means...", "This is where...", "The answer is..."
- Denies then asserts: "This is not about A. It is about B." → "This is about B."
- Announces that a point is coming: "There is one thing that matters here. It is Z." → "Z decides it here."
- Restates the structure: a count of the bullets above the bullets; "First, we set up the project" under a heading reading `Step 1: Create the project`.

## Announcement sentences caught in finished drafts

Each of these was removed from prose that had already passed three cleanup passes:

- "There is a second reason to do this"
- "But here is the thing"
- "That is where it gets interesting"
- "The interesting part turned out to be"
- "Two rules keep it usable"
- "Two things in there are deliberate"
- "One more thing cost me an afternoon"
- "One product decision belongs here too"
- "One case needs its own flag"
- "I should be straight about how often this fires"

## Framing openers, extended list

- "The useful part of X is..."
- "The interesting thing about X is..."
- "What matters here is..."
- "The key insight is..."
- "Where this gets hard is..."
- "The thing to understand about X is..."
- "The load-bearing decision is that..."
- "The step that matters is..."

If the sentence after the colon or the full stop is the real content, that sentence is the sentence. Start there.

## The line between locating and asserting

Not every sentence of this shape is a defect. "The colour rule is the other decision I would repeat" carries a judgement about which decisions were good, so it stays. "The boundary I care about is between the extractor and the verifier" carries no judgement past the location, so it becomes "I put the boundary between the extractor and the verifier."

Ask what the clause before the verb contributes. Where it only tells the reader where to look, delete it.

## The test

Read each sentence alone. If its only content is "something is coming" or "that was one thing, here is another", it carries no information by itself. Cut it and check the paragraph still reads. It will.

Then read every pair of consecutive sentences. If the pair can be one sentence with no loss of meaning, make it one. A clever-sounding construction that defers the answer is still deferring the answer.
