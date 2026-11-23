# Technical docs, cookbooks, tutorials and playbooks

The sentence rules live in [core.md](../core.md), and their worked cases in [rules.md](rules.md) and [deferral.md](deferral.md). Openings are in [openings.md](openings.md). This file holds what is specific to developer-facing prose.

## Economy

Delete outright: prose that restates a code block, a closing summary that repeats the section above it, and any claim already made upstream. Then phrase by phrase: "in order to" to "to", "is able to" to "can", "the reason for this is that" to "because". Delete a filler lead-in such as "what this means is that", then state the thing.

Cut words that carry no information. Keep words that carry judgement, including informal ones, because that judgement is why someone reads a practitioner instead of a manual. De-slopped prose that comes out flat and careful has traded one problem for a worse one. Where a sentence loses its voice while being tightened, put the voice back in plainer words.

## Headings

Nesting is what makes position knowable. Ninad on drafts where every step was a top-level sibling: *"I can't understand the headings at all. It seems completely like a mess. Even if the content is right, I just cannot follow through with it."*

```
# <Title>
(intro prose, no heading)
## What you will build
## What are the prerequisites
## Building <the thing>
    (short lead-in paragraph, before the first step)
    ### Step 1: Create the project
    ### Step 2: <outcome>
## Demo
## Wrap-up
## Try it
```

- **Steps are H3 under one container H2**, so the reader sees four or five top-level sections instead of twelve.
- **Step 1 creates the project.** A reader going top to bottom has something runnable before any domain work starts.
- **Heading text names the outcome, not the mechanism.** "Step 4: Make the diagnosis point at the evidence" works. "Step 4: Schema validation" does not.
- **Reading only the headings shows the whole path and where you are on it.** In a playbook they are gerund action phrases, series-wide, with no bare numbered H2s.
- **Never two headings back to back.** Every heading gets a lede paragraph before the next one.
- Nest further only where a long step has distinct parts. Never nest for decoration.

Paragraph shape, which fails alongside headings: a step opens with a sentence or two on what it accomplishes, then code, then what to notice. Break any run of three consecutive prose paragraphs: either it has structure that should be visible, or it is longer than it needs to be. A reader must be able to skim headings and code blocks and still execute the build.

## Every section carries something runnable or checkable

At least one of these, with real content rather than a description of it:

- a command written out
- a file or snippet with its actual contents
- a verbatim prompt you would paste
- a table with real values
- an observable check with a stated pass condition

**Every check states its failure branch.** A check without one is a wish. Ninad flagged "Pick any recent pull request, grep the map for the paths it touches, and say in one sentence what it changes for a user" as impractical and vague: no command, and no way to know whether the answer was adequate. The rewrite:

```bash
git log -20 --oneline
git show --stat <sha>
grep -n "src/deploy" docs-context/feature-map.md
```

If the map returns an entry and you can say in one sentence what that change costs the person using the product, playbook 2 will run. If it returns nothing, the map is missing a capability and step 6 is not finished.

A section holding only advice or a category of thing gets rewritten into one of the five, or deleted. Where it teaches judgement, anchor the judgement to a specific case with real content in it. Do not pad to satisfy this: a short section with one runnable command beats a long one with none.

## Lists and prose

Lists for enumerable things: artifacts, rules, checks and options. Prose for judgement and argument. Neither by default. Tables, code blocks and bullets wherever they simplify an explanation, because paragraph-heavy content breaks the flow.

## Choosing the subject

Write into demand that already exists: replicate an app people search for, or collapse a workflow a team hand-assembles across three tools. **The title test:** if the title only parses for someone who already uses the tool, the piece is dead. "Harness orchestration using Mastra" fails. "Build your own Granola: meeting notes with decisions and owners attached" passes. The framework is the lens, not the subject.

## Working method

- **Sweep the family, not the instance.** Fixing the one line someone pointed at leaves the rest in place. When an instance surfaces, name the pattern and search every file for its surface forms.
- **The rules break each other, so re-run every check after every pass.** Collapsing a deferred pair produces a sentence starting with a numeral. The economy pass deletes a first-person judgement the persona rule requires. Where economy and the number rule meet, the number rule wins.
- **Diff first-person token counts against the pre-edit baseline** (`--first-person-baseline N`). De-voicing is invisible to every other checker.
- **Verify a hit in context before fixing it.** Hard-wrapped lines and quotations produce false positives.
- **Verify mechanically, then read it aloud.** The real standard is "I can't even read the second sentence", and no grep detects that.

Checker traps, safe-editing rules for wrapped files, how to steer a writer who is not landing a rule, and the pre-flight checklist: [checking.md](checking.md).
