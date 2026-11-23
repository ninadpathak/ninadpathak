---
name: writing
description: "Ninad's writing standard for long-form work: articles, how-tos, explainers, docs, tutorials, READMEs, founder (Paul Graham-style) essays, personal and narrative nonfiction, spoken-narrative articles, video scripts and social posts. Also edits a draft to strip AI slop, or audits one without rewriting. Use for any of these; short messages need only the always-loaded core."
---

# Writing

[core.md](core.md) holds the sentence rules and the banned-word lists, and every harness loads it at session start. Read it now if it is not already in your context. Nothing below repeats it.

## Pick the job

| Job | When | Go to |
|---|---|---|
| Write | A new piece, or a rewrite from notes | The four steps below, then the form's reference |
| Edit | A draft exists and should sound sharper and less generated | [references/editing.md](references/editing.md) |
| Detect | "Is this AI slop?", audit, scan or flag without a rewrite | [references/editing.md](references/editing.md), detect mode |

## Step 1: Place the reader

Answer four questions in a few private lines before drafting.

1. Who reads this, and what did they do just before arriving? A search, a link from a colleague and a subscription each say something different about them.
2. What do they already know? List the concepts you can use without defining them.
3. What did they come for? Name the one thing they should be able to do or decide afterwards.
4. Where does that put the first sentence? It starts at the last thing they already hold, and it moves forward from there.

A reader who typed "how to build a software factory" is already curious and already knows the term. Explaining why software factories matter spends their attention on something they brought with them. Give them the build.

## Step 2: Choose the shape

A how-to or explainer runs in this order.

1. **Intro.** One of the entries in Step 3.
2. **Quick definition.** A heading such as "What is a software factory?", then one or two short paragraphs. It aligns vocabulary for the reader who half-knows the term and gives an answer engine something to quote. It is never a history lesson.
3. **The substance.** The steps or the mechanism, which is what the reader came for.
4. **Edge cases and next actions.** Stop on the last useful one.

Other forms have their own shape. Read the one reference that matches before drafting.

| Form | Reference |
|---|---|
| How-to, explainer or search article | [references/article.md](references/article.md) |
| Developer docs, cookbook, tutorial, README, playbook, release notes | [references/technical.md](references/technical.md) |
| Founder essay or reflective technical prose in Paul Graham's register | [references/essay.md](references/essay.md) |
| Researched narrative nonfiction, or a personal account of real experience | [references/narrative.md](references/narrative.md) |
| Article in a spoken, talk-like voice | [references/spoken.md](references/spoken.md) |
| Video script or narration | [references/video-script.md](references/video-script.md) |
| LinkedIn or X post | [references/social.md](references/social.md) |

## Step 3: Open on something the reader already holds

The intro's whole job is to meet the reader where they stand and tell them what they will leave with. A narrative intro does up to four jobs. They have no fixed order, an intro may skip one, and a single sentence may do two.

- **Put the author and the reader on the same side**, in terms the reader would use about themselves.
- **Give the backstory through something real.** The author's own path through the technology can stand in for the field's path, which also shows the author was there.
- **Say what is true now** and what that leaves the reader needing.
- **Say what the piece walks through** and whose experience backs it.

**Open on the author, never on the technology.** The first sentences carry the author's experience: why they wrote the piece, or how they found or built the thing. A first line about the field ("CLI agents can now handle tasks end to end...") reads as robotic, because anyone could have written it. The present state and what the reader lacks come after the author's part. Order the remaining jobs from this piece's strongest material.

Ninad's own example of these jobs is quoted in [references/openings.md](references/openings.md), with the other entries that work: a sourced fact, a historical note, or a real surprising behaviour. Every entry obeys three rules.

- **Use the mechanics and never the skeleton.** No two intros share an opening pattern. If two pieces could swap openings unnoticed, both are wrong.
- **The memory must be real.** It comes from what the author supplied or published. When there is none, open on a sourced fact or the reader's literal question, and leave a `[TODO: author]` slot if only their story would do.
- **Every sentence passes the nod test.** It is true for anyone who arrived at this topic, so the reader keeps agreeing. An assumption about their past or their tools loses them in the first line.

## Step 4: Check, then read it aloud

```bash
python3 ~/.agents/skills/writing/scripts/check_prose.py draft.md
```

The script fails on banned words, a sentence that starts with a number and two headings back to back. It reports the rest for judgement. Run it after every pass, because the rules break each other: merging a deferred pair often produces a sentence that starts with a numeral. If it reports a failure, fix the line in context and run it again. If it passes, read the piece aloud as the reader from Step 1. Ninad's standard is "I can't even read the second sentence", and no script detects that. Checker traps and the pre-flight list are in [references/checking.md](references/checking.md).

## Shared references

- [references/deferral.md](references/deferral.md): the deferral family in full, with worked rewrites.
- [references/rules.md](references/rules.md): each core rule with its replacements and rejected examples.
- [references/checking.md](references/checking.md): the checker, safe editing and how to steer a writer who is not landing a rule.
