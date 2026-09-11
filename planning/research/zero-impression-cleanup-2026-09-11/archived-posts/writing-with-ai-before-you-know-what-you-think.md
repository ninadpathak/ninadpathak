---
title: "Before You Ask an Expert"
date: 2026-09-07
description: "AI can help me prepare for an expert conversation: question an idea, find what I don't understand, and arrive with something worth discussing."
category: technical-documentation
tags: [technical-writing, documentation, ai-writing]
status: published
slug: writing-ai-first-content
---

If I had to write a good draft seven years ago, I'd sit down with someone who knew the subject and have a conversation, maybe a bit of a debate. I'd want to get past the answers I could find through SEO research and hear what they'd learned by doing the work.

Search research helps me understand what people ask and which answers are already available. An expert can add the reasoning behind a decision, including what happened when a sensible recommendation met a condition the published advice hadn't considered.

But getting to that discussion takes preparation, and AI gives me somewhere to work through the questions that come before it. I can follow an explanation until I understand it, then argue against it without asking an expert to sit through each attempt.

## Use AI to find the question beneath the topic

AI is useful before the conversation because a topic is not yet a question an expert can do much with. "How do you write shorter documentation?" invites familiar advice.

I need to arrive at the decision inside the topic. What would a writer remove, who might need it, and what would tell us whether the edit worked?

### Start with the claim you would otherwise take to the interview

Take a hypothetical assignment: an article about making documentation shorter, with a quickstart as the example. The starting position is reasonable enough: developers are busy, so cutting unnecessary text should help them finish sooner.

The question is what a new reader must do before they can use what remains after we remove half the quickstart. I am no longer asking the assistant to explain concise writing; I am giving it a tentative claim and looking for the condition that makes it fail.

### Challenge the assumption until it becomes specific

A missing prerequisite is a possibility to explore with the assistant. Say it's the account setup instructions: an experienced user already has an account, so why make them scroll past instructions they don't need?

I could put the claim to the assistant this way:

> I want to remove account setup from a quickstart and link to it instead. Argue against that choice from the perspective of a new reader. Name the assumption in my reasoning and the evidence I would need before making the edit.

A link to those instructions seems like a reasonable compromise. But does a new reader know they need to follow it before starting, or do they discover that only when the example fails?

I can keep pressing in both directions: what does the account step cost the returning reader if it stays, and what signal guides the new reader back if it moves? I stop when I have a choice with a consequence I cannot settle from general advice.

## Bring the expert an open question

That unresolved choice changes the expert conversation. I can ask about a decision the expert made and the evidence that shaped it, so they do not have to spend the opening minutes turning my broad topic into something concrete for us to discuss.

### Prepare questions from what you still do not know

Working through the hypothetical gives me something specific to ask the documentation lead: how do you decide what a quickstart assumes about its reader? Can you walk me through an edit where you moved a prerequisite elsewhere, and what happened afterward?

I am ready to speak with the expert when I can name the uncertainty behind each question: I do not know whether moving setup instructions reduces friction or merely hides it, and I do not know what evidence the team had when it made the edit. Those unknowns are more useful than a page of generated talking points because the expert can answer them from experience.

### Leave room for the expert to reject your premise

A model can produce a convincing explanation for why a reader gets stuck, but asking it to challenge that explanation doesn't tell me whether the problem occurred. The answer needs evidence from the expert's work, so the question stays open: is a missing prerequisite a problem you've observed, and how did you identify it?

The expert needs room to disagree with the explanation I've been exploring. Having a polished draft about the dangers of shortening quickstarts at this point would give me something to defend, when I want enough understanding to follow a correction without fishing for agreement.

## Follow the expert into the evidence

Understanding the initial argument and its weak point lets me recognize a detail that changes the problem and ask why. I can follow that detail instead of defending the route I prepared, which moves the interview toward experience I could not simulate beforehand with AI.

### Let one concrete detail change the problem

Suppose the documentation lead points out that the setup instructions were adequate; the code example had fallen behind the product. Now I want to know how they found that mismatch and whether the initial complaints suggested something else, including whether readers asked for more explanation when the code itself needed fixing.

The expert's correction turns the tentative article into a better question: when readers appear to need more explanation, how do you tell whether the prose is unclear or the example is wrong? I could not have prepared that exact question because I did not know about the stale code, but I could prepare well enough to notice why the detail matters.

### Ask what the record can show

The relevant versions of the docs give us something to examine together: what the instructions said and how the example changed. Reader reports might show the failure they saw, while a product release or commit could establish when the code stopped matching the product; I still need to connect those records before treating stale code as the cause.

The expert's memory tells me where to look and why the team made a decision; the record helps us test the sequence. If the available evidence does not connect the stale example to the reported problem, the article should preserve that uncertainty instead of converting a plausible explanation into a result.

## Write from what survived the conversation

The AI exchange helps me form questions, while the expert discussion tells me where experience complicates them and the evidence tests which explanation belongs in the article. Treating them as one source can make a possibility raised during preparation sound like something that happened.

### Separate the stale-code claim from what the record proves

For the stale-code example, the missing prerequisite remains a possibility I explored with AI. The documentation lead's correction is a claim from the hypothetical interview until the relevant work supports it.

The documentation history can show what changed, and reader reports can show what someone encountered if those reports are available. Neither alone proves that the stale example caused the reported problem; if I cannot say what supports a sentence, that sentence is not ready for the article.

### Rebuild the article around the evidence

In this hypothetical, the final piece may no longer be about making quickstarts shorter. It might examine how teams distinguish a writing problem from a broken example, using the changed code and the documentation decision as its centre while keeping the original premise as the reasonable explanation the evidence forced us to reconsider.

That takes some restraint when an AI conversation feels productive, because a long exchange can leave me confident in an explanation I've only discussed; someone who has done the work can interrupt that confidence with a detail I didn't know to ask about. I still want the conversation I described at the start: preparing with AI means we can spend less of it establishing what I already could have worked out, leaving more time to discuss the decision that surprised me and the experience behind it.
