---
category: rag
primary_query: rag vs fine tuning
siblings:
- rag-evaluation
- contextual-retrieval
- rag-reranking
bridges:
- slug: agent-memory-types
  reason: What one user said is per-user state, which neither retrieval over documents nor training covers.
- slug: rag-vs-memory
  reason: What one user said is per-user state, which neither retrieval over documents nor training covers.
date: '2026-05-12'
description: RAG vs fine-tuning comes down to where knowledge lives. RAG puts changing
  facts in the prompt, fine-tuning trains fixed behavior into the weights, and the
  papers that compared them say when each one works.
slug: fine-tuning-vs-rag
status: published
work_note: "I'm Ninad Pathak. I work with AI companies as a freelance technical writer on setup tutorials, concept explainers and comparisons, and I run each product before I write about it. [See the work and get in touch](/services/freelance-technical-writer-for-ai-companies/)."
title: 'RAG vs Fine-Tuning and When to Use Each'
updated: '2026-08-17'
---

OpenAI's [model optimization guide](https://developers.openai.com/api/docs/guides/model-optimization) now carries a notice above its fine-tuning section: "OpenAI is winding down the fine-tuning platform." New users have been shut out of the self-serve platform since May, and eligible existing customers can create training jobs only until January 6, 2027.

So the RAG vs fine-tuning question has a different shape than it had a year ago. RAG puts knowledge into the prompt at request time by retrieving it from an index, and fine-tuning puts it into the model's weights by training on examples.

Developers already have a rule for this kind of choice. [The Twelve-Factor App](https://12factor.net/config) says anything likely to vary between deploys is config and has to live outside the code, and I think knowledge splits the same way: what changes often belongs in the index, and what holds still can be trained in.

That's the answer I'll defend below, and it's why the page sits under [RAG](/articles/rag/). Retrieval is the default, and fine-tuning has to earn its place.

## What is the difference between RAG and fine-tuning?

RAG changes what the model can see for one request, and fine-tuning changes how the model behaves on every request. The rest follows from where each one keeps the knowledge:

| | RAG | Fine-tuning |
|---|---|---|
| Where the knowledge lives | In an index outside the model | In the model's weights |
| How you update it | Re-index the document | Train again |
| Can the answer cite a source | Yes, the passage is in the prompt | No |
| What it's good at changing | Facts | Format and behavior |
| What you pay | Longer prompts on every request | A training run up front |

The people who named RAG saw both columns coming. The [2020 paper](https://arxiv.org/abs/2005.11401) lists what a model with knowledge only in its weights can't do well, saying that "providing provenance for their decisions and updating their world knowledge remain open research problems".

## When should you use RAG?

Use RAG when the facts change or when an answer has to show where it came from. A price that moved this morning is in the index by the next request, and the passage that states it can be linked from the answer.

There's a measured case for RAG on knowledge as well. A 2023 study, [Fine-Tuning or Retrieval?](https://arxiv.org/abs/2312.05934), compared the two on knowledge-heavy tasks and found that RAG "consistently outperforms" unsupervised fine-tuning, for facts the model had seen in training and for new ones.

The same authors report that models struggle to learn a new fact from fine-tuning unless they see it in many variations. I'd keep that in mind whenever someone proposes training the product docs into a model.

RAG has its own work, and it's the retrieval. Whether the right passage made it into the prompt is something you measure with [RAG evaluation](/articles/rag-evaluation/), and techniques like [contextual retrieval](/articles/contextual-retrieval/) exist because that step fails.

## When should you use fine-tuning?

Use fine-tuning when the model's behavior is wrong and the facts are fine. OpenAI's guide names the cases: getting a model to format responses the same way every time, and giving it more examples than fit in one context window.

The guide adds a cost argument I think gets overlooked. A fine-tuned model needs shorter prompts with fewer examples, which cuts token cost at scale, and that's the opposite of what RAG does to a prompt.

Training has become cheaper as well. [LoRA](https://arxiv.org/abs/2106.09685), from 2021, trains small added matrices and leaves the original weights frozen, and its authors report 10,000 times fewer trainable parameters than full fine-tuning of GPT-3.

What's changed is where you can do it. OpenAI's [deprecations page](https://developers.openai.com/api/docs/deprecations) ends job creation on its self-serve platform on January 6, 2027, so I read fine-tuning as something you now plan around open-weight models, or around a provider whose docs still offer it on the day you check.

## Can you use RAG and fine-tuning together?

Yes, and a study that measured both found the gains stack. A [2024 case study on agriculture data](https://arxiv.org/abs/2401.08406) reports an accuracy gain of over 6 percentage points from fine-tuning, and a further 5 points when RAG was added on top.

That's one domain and one set of models, so I wouldn't carry the numbers anywhere else. What carries is the shape: the two fix different things, so the gains didn't cancel.

When a RAG pipeline is already retrieving more than it needs, I'd tune the retrieval before the model. [Reranking](/articles/rag-reranking/) is cheaper than a training run and you can undo it in a deploy.

## How do you decide between RAG and fine-tuning?

Ask whether the facts change, and then whether the problem is behavior. Those two questions settle nearly every case I can think of.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/fine-tuning-vs-rag/memory-finetuning-decision.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/fine-tuning-vs-rag/memory-finetuning-decision.narrow.svg" width="288" height="520"><img class="np-has-narrow" src="/static/images/diagrams/fine-tuning-vs-rag/memory-finetuning-decision.svg" width="720" height="640" alt="A decision tree. If the knowledge changes frequently, use RAG. If it doesn't, ask whether the problem is behavioral, meaning the model's format or conduct is wrong: a behavioral problem means fine-tuning, and a factual problem means RAG." loading="lazy" decoding="async"></picture></a>
  <figcaption>Facts that change go to RAG. Fine-tuning is for behavior that has to hold on every request.</figcaption>
</figure>

- **The facts change:** RAG, whatever else is true.
- **The facts are stable and the model behaves wrongly:** fine-tuning, after you've tried fixing it in the prompt.
- **The facts are stable and the model behaves well:** RAG again, or just a longer prompt.

A last kind of knowledge fits neither branch, and that's what a single user told the system last week. It's per-user state, which makes it a memory problem, and [RAG vs memory](/articles/rag-vs-memory/) and the page on [types of agent memory](/articles/agent-memory-types/) pick it up from there.

## FAQ

**Is RAG cheaper than fine-tuning?**

It depends on volume. RAG costs extra tokens on every request, and fine-tuning costs a training run up front and then allows shorter prompts.

**Can fine-tuning teach a model new facts?**

Poorly, on the evidence above. The 2023 comparison found that models struggle to learn new facts through unsupervised fine-tuning unless each fact appears in many variations.

**Can I still fine-tune OpenAI models?**

Not as a new user, according to OpenAI's guide. Eligible existing customers can create training jobs until January 6, 2027, and fine-tuned models stay available for inference until their base models are deprecated.

**Does RAG change the model?**

No. The model's weights stay as they are, and only the prompt changes from one request to the next.

**Should I start with RAG or fine-tuning?**

I'd start with RAG and a good prompt. Add fine-tuning when you can point to a behavior that neither of those fixed.
