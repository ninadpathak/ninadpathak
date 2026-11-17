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

OpenAI's notice takes its hosted fine-tuning service out of the RAG vs fine-tuning decision for any team that isn't already a customer, so the decision is worth making again. RAG puts knowledge into the prompt at request time by retrieving it from an index, and fine-tuning puts knowledge into the model's weights by training the model on examples.

Developers already have a rule for deciding what gets built in and what gets looked up. [The Twelve-Factor App](https://12factor.net/config) says anything likely to vary between deploys, such as a database URL, is config and has to live outside the code.

I think knowledge splits the same way. A fact that changes often, such as a price, belongs in the RAG index, and a behavior that stays the same, such as always answering in JSON, can be trained into the weights.

My position on this page is that RAG is the default and fine-tuning needs a specific reason. The page is filed under [RAG](/articles/rag/) for that reason.

## What is the difference between RAG and fine-tuning?

RAG changes what the model can see for one request, and fine-tuning changes how the model behaves on every request. The other differences between RAG and fine-tuning come from where each one keeps the knowledge:

| | RAG | Fine-tuning |
|---|---|---|
| Where the knowledge lives | In an index outside the model | In the model's weights |
| How you update it | Re-index the document | Train again |
| Can the answer cite a source | Yes, the passage is in the prompt | No |
| What it's good at changing | Facts | Format and behavior |
| What you pay | Longer prompts on every request | A training run up front |

The researchers who named RAG described the weaknesses of weights-only models in 2020, which are the citation and update rows of that table. Their [paper](https://arxiv.org/abs/2005.11401) says that for a model with knowledge only in its weights, "providing provenance for their decisions and updating their world knowledge remain open research problems".

## When should you use RAG?

Use RAG when the facts change or when an answer has to show where it came from. Say a product's price changed this morning: once the pricing page is re-indexed, the next request retrieves the new price, and the answer can link to the pricing page as its source.

Research has also compared RAG and fine-tuning directly on factual knowledge. A 2023 study, [Fine-Tuning or Retrieval?](https://arxiv.org/abs/2312.05934), compared RAG and fine-tuning on knowledge-heavy tasks and found that RAG "consistently outperforms" unsupervised fine-tuning, for facts the model had seen in training and for new ones.

The same authors report that models struggle to learn a new fact from fine-tuning unless they see it in many variations. That finding is a warning for anyone who plans to fine-tune a model on product docs, where a fact may be stated only once.

RAG moves the hard part to retrieval, because the answer is only as good as the passages that reach the prompt. [RAG evaluation](/articles/rag-evaluation/) measures whether the right passage was retrieved, and techniques such as [contextual retrieval](/articles/contextual-retrieval/) exist because retrieval can return the wrong one.

## When should you use fine-tuning?

Use fine-tuning when the model has the right facts and behaves the wrong way, for example by ignoring your output format. OpenAI's guide names two cases: getting a model to format responses the same way every time, and giving it more examples than fit in one context window.

OpenAI's guide also makes a cost argument for fine-tuning. A fine-tuned model needs shorter prompts with fewer examples, which cuts token cost at scale, while RAG makes every prompt longer by adding retrieved passages to it.

Fine-tuning has also become cheaper to run since 2021. [LoRA](https://arxiv.org/abs/2106.09685), from 2021, trains small added matrices and leaves the original weights frozen, and its authors report 10,000 times fewer trainable parameters than full fine-tuning of GPT-3.

What changed in 2026 is where you can fine-tune. OpenAI's [deprecations page](https://developers.openai.com/api/docs/deprecations) ends job creation on its self-serve platform on January 6, 2027, so I read fine-tuning as something you now plan around open-weight models, or around a provider whose docs still offer it on the day you check.

## Can you use RAG and fine-tuning together?

Yes, and a study that measured RAG and fine-tuning together found that their gains add up. A [2024 case study on agriculture data](https://arxiv.org/abs/2401.08406) reports an accuracy gain of over 6 percentage points from fine-tuning, and a further 5 points when RAG was added on top.

The study covers one domain, agriculture, and one set of models, so I wouldn't expect 6 points and 5 points on your data. The part I'd expect to hold elsewhere is that the gains added up, because fine-tuning and RAG were fixing different problems.

When a RAG pipeline already retrieves the right passage along with too many wrong ones, I'd fix the retrieval before training the model. [Reranking](/articles/rag-reranking/) is cheaper than a training run and you can undo it in a deploy.

## How do you decide between RAG and fine-tuning?

Decide by asking two questions in order: do the facts change, and is the model's behavior the problem? The figure and the list below show which answer leads to RAG and which leads to fine-tuning.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/fine-tuning-vs-rag/memory-finetuning-decision.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/fine-tuning-vs-rag/memory-finetuning-decision.narrow.svg" width="288" height="520"><img class="np-has-narrow" src="/static/images/diagrams/fine-tuning-vs-rag/memory-finetuning-decision.svg" width="720" height="640" alt="A decision tree. If the knowledge changes frequently, use RAG. If it doesn't, ask whether the problem is behavioral, meaning the model's format or conduct is wrong: a behavioral problem means fine-tuning, and a factual problem means RAG." loading="lazy" decoding="async"></picture></a>
  <figcaption>Facts that change go to RAG. Fine-tuning is for behavior that has to hold on every request.</figcaption>
</figure>

- **The facts change:** use RAG, even if you also fine-tune for behavior.
- **The facts are stable and the model behaves wrongly:** use fine-tuning, after you've tried to fix the behavior in the prompt.
- **The facts are stable and the model behaves well:** use RAG, or put the facts directly in a longer prompt.

What one user told the system last week is knowledge that neither RAG over documents nor fine-tuning covers. A user's stated preference is per-user state, which makes storing it a memory problem, and [RAG vs memory](/articles/rag-vs-memory/) and the page on [types of agent memory](/articles/agent-memory-types/) cover memory.

## FAQ

**Is RAG cheaper than fine-tuning?**

Which one is cheaper depends on request volume. RAG costs extra tokens on every request, and fine-tuning costs a training run up front and then allows shorter prompts.

**Can fine-tuning teach a model new facts?**

Fine-tuning teaches new facts poorly, according to the 2023 study cited above. That study found that models struggle to learn new facts through unsupervised fine-tuning unless each fact appears in many variations.

**Can I still fine-tune OpenAI models?**

Not as a new user, according to OpenAI's guide. Eligible existing customers can create training jobs until January 6, 2027, and fine-tuned models stay available for inference until their base models are deprecated.

**Does RAG change the model?**

No. The model's weights stay as they are, and only the prompt changes from one request to the next.

**Should I start with RAG or fine-tuning?**

I'd start with RAG and a good prompt. Add fine-tuning when you can point to one behavior, such as a broken output format, that neither RAG nor the prompt fixed.
