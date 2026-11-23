# Openings

An opening holds on real material from the first clause. Each model below is here for what it does. Copy the judgement behind a model and never its wording or its order.

## The narrative intro

Ninad's example, written on 2026-11-11 for a piece titled "How to build a software factory":

> People like us, who are builders at our cores, always want to break the limits of tech. When ChatGPT was released, I remember moving from chatting with it about trivial ideas to quickly testing coding skills. Then asking it for commands and trying to add more ways to simplify my day to day workflows. Now with CLI agents capable of handling tasks end to end, we simply need to hand LLMs a solid structure to use our instruction and past context and create an output that is precisely what we needed, modified for the new requirements. That's the "software factory" setup we did at Mastra and I'm going to walk you through how you can do it for your organization too.

The jobs it does. The first move is fixed: the intro starts on the author (here "People like us, who are builders" and his own path from chatting to testing code), and the claim about the technology comes after, never first. Ninad, 2026-11-11: "Writing about CLI agents right away sounds robotic." The rest of the order below is his paragraph and no template; a new intro picks its own from its own material.

- **It puts author and reader on the same side.** "People like us, who are builders" makes one group before any claim is made.
- **It gives the backstory through a real memory.** His own path from chatting, to testing code, to asking for commands is the field's path over the same years, and it shows he was there for it.
- **It says what is true now.** Agents finish tasks end to end, so what the reader lacks is structure.
- **It says what the piece covers.** It names the setup, says where it was done and promises the walk-through.

The intro never explains what a software factory is or argues that the reader should want one. The reader searched for it. The definition comes next, under its own heading, in one or two short paragraphs.

## Other entries that work

Pick the one this piece's strongest material supports.

| Entry | What it needs | Source of the rule |
|---|---|---|
| A sourced fact or historical note about the topic | A checkable event that explains why the topic exists. A comparison opens on the original pivot: MariaDB forked from MySQL after Oracle bought Sun. | Ninad, 2026-10-07 |
| A real surprising behaviour | Something the tool does that a newcomer would not predict, stated plainly | Ninad, 2026-10-07 |
| The reader's own snag, as a conditional | True for anyone who searched the topic: "If you're coming from SQL you probably expect to see tables using the SHOW TABLES command." | Ninad's approved SQLite intro |
| Named exemplars | Real products the reader can go and look at, with what is observably good about them | The playbook model below |
| The end of the story, told first | The striking terminal moment shown plainly, then the body earns it. Nothing is withheld, so it is never bait. | Ninad's cold-open rule |

## What every opening obeys

- **It differs from every other opening in the series.** A writer once cloned an approved "When I ..." opener onto thirty pages, and Ninad rejected the batch.
- **First person carries only real things.** The author's stated facts and the article's own choices qualify. Invented habits ("When I run Home Assistant") do not.
- **Nothing assumes the reader's situation.** "You've written the same three-table join for the fourth report this month" is a made-up scene stated as fact, and it is false for the reader in line one.
- **Value sits in the line.** "By the end of this you'll have..." reads as a template the moment someone sees the second one.
- **No framing section follows.** "Why this matters" and "The system" go. After the intro comes the quick definition or the first action.
- **Personal experience is evidence.** The piece teaches one outcome the reader can use, and the author's story is how it is proved.

## The playbook opening

Ninad's passage, written after eleven drafts opened with the same manufactured promise:

> There are a few companies that seem to have cracked documentation writing: Stripe, Laravel, Mozilla docs, and so on. Their docs are to the point, extremely well structured, tight and don't add yet another learning curve to your already worked up schedules.
>
> To become an excellent technical writer, you need to aspire to create documentation at that level. And that requires you to build a thought process starting right from the ground up — understanding the product deeply.
>
> In this little playbook, I want to show you the process I follow when I first start working on a new documentation project. It will help you see my workflow and processes that I follow to understand the product, find the obstacles new users face, and much more.

It names real exemplars, says what is observably good about them, turns that into the requirement and then frames the piece personally. The register is a peer being written to: "assuming you use markdown like the rest of us docs folks".

## The build-article opening

A build article gets two paragraphs of roughly 120 words. It says what the thing is and why the hard part is hard.

> [Granola](https://www.granola.ai/) turns a rambling call into a short list someone can act on. Pulling the decisions and action items out of a transcript takes one model call. Verifying them is the part that needs engineering, because an action item with the wrong owner is worse than no action item at all.
>
> So I built Recap, and put the engineering in the check: a note is not allowed to exist unless it names the line it came from and quotes it, and ordinary TypeScript verifies that claim before the note reaches the page.

The named product arrives in the first three words and the sharp claim leads. The author is the one who identified the hard half.

The same shape without a product to name, from the Fin article:

> Answering from your docs is the solved half of a support agent. Chunk the help centre, embed it, retrieve, generate, cite. You can have that working in an afternoon and it will look great on the questions your documentation actually answers.
>
> The hard half is knowing which requests to leave alone.

## Length

| Piece | Intro length |
|---|---|
| How-to or explainer with a narrative intro | One paragraph, up to about 120 words |
| Playbook | Three short paragraphs, 120 to 180 words |
| Build article or cookbook | Two paragraphs, roughly 120 words |
| Reference-style search page | Two or three spoken sentences, closing on "in this article I'll walk you through ..." |
