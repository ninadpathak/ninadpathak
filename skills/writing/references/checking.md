# Checking a draft

<!-- check_prose: word-mentions-allowed (quotes counts of banned words) -->

Mechanical checks first, then read it aloud. Ninad tests by reading, and "I can't even read the second sentence" is the standard no grep detects.

## The checker

```bash
python3 ~/.agents/skills/writing/scripts/check_prose.py draft.md --first-person-baseline <count from the pre-edit file>
```

Run it after every editing pass, not once at the end. The rules break each other:

- Collapsing a deferred-answer pair produced a new sentence starting with a number ("One schedule instead, on a workflow...").
- The economy pass deleted a first-person judgement ("The first thing I needed was normalisation" became "Normalisation comes first"), which the persona rule requires keeping.
- Fixing a subjectless fragment ("Finally, one command") swallowed the personal aside attached to it.
- The number rule adds words back, because supplying the elided subject costs words. Where it meets economy, the number rule wins.

What the script fails on: banned and slop words anywhere in the file (code included), sentences and headings that begin with a number, two headings back to back. What it only reports: em dashes (reduce in an article, since Ninad uses them himself; zero in a description or heading), framing openers and tells, sentences with three or more commas, a third consecutive prose paragraph, curly quotes, hard-wrapped paragraphs, and the first-person count against the baseline.

Not covered by the script, check by hand: integrity (diff claims, figures, links, code blocks, screenshots and frontmatter to prove they are unchanged; compare number multisets, not sets, so a dropped duplicate is visible), and every item in the pre-flight below that needs judgement.

## Checker traps

- **Number hits need context.** The script reflows paragraphs before splitting sentences, so wrapped continuation lines ("142 to 0 over an hour") are not flagged. Hits inside blockquotes are reported separately: a verbatim quotation of someone else's words is not yours to rewrite.
- **Banned words inside quotations and examples** show up in the whole-file count. Ninad's own rewrite of a passage contains "easily"; a quote stays, your prose does not.
- **"One" as a pronoun** ("One of them failed") is flagged. The rule still applies: supply the subject.
- **Strip fenced code before counting prose words,** or the count moves when nothing in the prose changed.
- A checker only finds what it was told to look for. The first pass over this skill never counted dashes and let thirty-one through, one in the frontmatter description. When someone names a new tell, add it to the script's lists the same day.

## Editing safely

**Reflowing is whitespace only, and prove it against the file you are about to change.** Snapshot each file immediately before reflowing it, then assert identical word count, identical word list, and a byte-identical hash of the concatenated fenced regions. A line ending in two trailing spaces is a deliberate markdown hard break; check for them before stripping line ends.

**Line-indexed edits on a hard-wrapped file silently drop the rest of the wrapped sentence.** Match and replace the full paragraph, assert the match count is exactly one, and write only after every replacement in the batch has matched.

## Working with a writer who is not landing a rule

- **Sweep the family, not the instance.** Correcting the one line someone pointed at leaves the rest of the family in place. This happened three times on the same defect class.
- **Show a rewrite instead of writing a fourth rule.** "No filler", "no runway" and "no buildup" each produced local compliance and recurrence elsewhere. Ninad's own rewritten passages moved the work further than any prohibition.
- **State what must survive the pass, not only what to remove.** A writer told to cut words will cut the voice. A writer pointed at a de-slopping tool will sand off "I chose" and "my number is" as hedging.
- **Give the counts.** "Most appears 46 times, ever 9, easy 3" produces better work than "remove the slop", and it lets you verify afterwards.
- **Describe a style reference's mechanics; never paste it.** A sample intro handed over verbatim comes back as a beat-for-beat structural copy. State the principles, forbid the skeleton, and ask what reframing insight this piece owns.
- **Keep the author alive until Ninad has read the work.** Closing the writer on completion forces a new owner to restructure without the author's context.

## Pre-flight

- [ ] `check_prose.py` passes; every reported note read in context and either fixed or deliberately kept
- [ ] Each prose paragraph is one line in the source; code, tables, list items, blockquotes, frontmatter and image lines keep their own line structure
- [ ] No negative parallelism ("isn't just X, it's Y"), no "Note that", no curly quotes
- [ ] Every sentence is a fact, a labelled example, or a conditional true by definition; every specific detail earns its place
- [ ] Intro follows [openings.md](openings.md) and is inside its word cap; no framing section after it
- [ ] Heading hierarchy exact; steps nested under one container H2; Step 1 creates the project; heading text names outcomes
- [ ] No step opens with three paragraphs before code
- [ ] Every section carries a command, a snippet, a verbatim prompt, a real table, or a check with a stated pass condition, and every check states its failure branch
- [ ] Persona: the builder, not the sufferer; first-person judgement intact
- [ ] Title parses for a stranger who has never used the tool
- [ ] Read aloud end to end; every hard-to-say line rewritten
