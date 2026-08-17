---
category: ai-engineering
date: 2026-04-16
description: A practical guide to RAGAs, recall, precision, and the metrics that separate
  production RAG systems from prototypes.
status: published
tags:
- rag
- evaluation
- llm
- metrics
title: 'RAG Evaluation Metrics: What Actually Matters'
updated: '2026-08-17'
---

Building a RAG system is the part every tutorial covers. Measuring whether it works is the part almost none of them touch.


RAG evaluation is genuinely hard because you're scoring a pipeline that chains retrieval, passage selection, and generation. A failure at any stage compounds into the next.


The useful metrics separate retrieval, context selection, and answer quality so a failure can be traced to the stage that produced it. The guide does not report article-specific benchmark results.

## The RAG Evaluation Stack

Three distinct failure modes live inside a RAG system, and an evaluation strategy worth running has to catch all three.

### Stage 1: Retrieval Quality

Everything downstream is capped by retrieval quality. When the retrieved passages don't contain the answer, no amount of clever prompting will conjure it.

A generator can be blamed for hallucination when the supporting passage never reached the top results.

**Recall@K** measures what fraction of all relevant passages appear in the top-K results. For a question with multiple supporting facts spread across documents, recall tells you whether the system even has access to the information it needs.

```
recall@k = (number of relevant documents in top-k) / (total number of relevant documents)
```

Treat recall@K as a lower bound and nothing more. A system can score perfect recall and still hand the generator passages packed with noise, so recall alone never tells the whole story.

**Precision@K** measures how many of the top-K results are actually relevant. High precision means the model wastes less of its context budget on irrelevant material, and low precision dilutes the signal the generator has to work with.

A larger context window can tolerate more retrieved passages, while a tight latency or token budget puts more pressure on precision.

When you're squeezing ten passages into a tight budget for a latency-sensitive chatbot, precision earns its keep.

**NDCG@K** (Normalized Discounted Cumulative Gain) weights ranked results by relevance. A relevant document at rank 1 scores higher than the same document at rank 5.

Use NDCG when rank order matters for your pipeline, which is exactly the case once you add [a reranking stage to fix wrong top-k ordering](/articles/reranking-in-rag-why-your-top-k-results-are-probably-wrong/).

### Stage 2: Passage Selection

Retrieval finds candidate passages. Selection decides which of them actually reach the context.

**Context Precision** measures whether relevant content ranks higher within a passage. A retrieved passage might be 80% relevant and 20% noise, and context precision penalizes the ones where the useful sentence sits buried under boilerplate the generator has to wade through first.

Comparing the retrieved context against a ground-truth answer is what **Context Recall** does. It checks whether every fact needed to answer is present in the context you actually assembled, not merely sitting somewhere in the raw document store.

Cutting corners here is where many tutorials go wrong. They test retrieval against a document store rather than against the context fed to the generator, and those two things diverge constantly.

Retrieval and assembled-context scores can disagree when chunking splits supporting facts across passages that never reach the generator together.

### Stage 3: Response Quality

Whatever the generator produces is the only thing the user ever sees, so the final answer needs its own evaluation.

**RAGAs** (Retrieval-Augmented Generation Assessment) is a framework built specifically for this. It breaks response evaluation into three scores:

Faithfulness measures whether the generated answer stays consistent with the retrieved context. A faithful answer doesn't invent a date or a figure that appears nowhere in the passages it was given.

Answer Relevancy measures whether the response actually addresses the question. A relevant answer provides information the user was asking for, not a plausible-sounding tangent.

Context Relevancy measures whether the retrieved context is useful for answering the question. High context relevancy means the passages selected actually contain information needed to construct the answer.

RAGAs metrics use bounded scores, but a deployment threshold must come from labeled examples and the cost of each failure type. Do not copy a universal cutoff.

### The Hallucination Problem

Hallucination lives in generation, not retrieval. Retrieval metrics can be flawless and the model will still confidently fabricate, which is exactly why answer-level evaluation has to go beyond context faithfulness.

**Self-RAG** and similar approaches attack this by having the model critique its own responses against the retrieved context. The model learns to raise a flag when it's pulling an answer from parametric knowledge rather than the passages in front of it, like a writer pausing to check whether a claim came from the source on their desk or from memory.

Latency and cost are the price of these approaches, since each critique is another model call. For factual Q&A where retrieval is already strong, that extra round trip rarely pays for itself.

It earns its place in open-ended generation, where the model is far more tempted to extrapolate past what the passages support.

## Metrics That Look Good But Mislead

**BLEU** and **ROUGE** score surface-level overlap between generated and reference answers. They're popular because they're automated and easy.

They're also nearly useless for RAG evaluation.

Two answers can mean the exact same thing and score 0.3 on BLEU, and two answers can say flatly opposite things and score 0.7 on ROUGE. These metrics measure text similarity, not whether the answer is correct.

Optimizing BLEU or ROUGE can improve surface overlap without improving factual correctness. Treat that divergence as a metric-design failure.

**Perplexity** on the generated text misleads in the same way. Low perplexity means the model is confident in its phrasing, and a confidently wrong answer sails right past a perplexity-based check.

## Building a Practical Evaluation Pipeline

A practical pipeline combines automated metrics with human evaluation, each covering what the other misses.

### Automated Metrics You Can Run in CI

Set up automated scoring on every commit:

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

def evaluate_rag_response(question, answer, contexts, ground_truth):
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
    ]
    
    result = evaluate(
        question=question,
        answer=answer,
        contexts=contexts,
        ground_truth=ground_truth,
        metrics=metrics
    )
    
    return {
        "faithfulness": result["faithfulness"],
        "answer_relevancy": result["answer_relevancy"],
        "context_precision": result["context_precision"],
    }
```

The code above is an implementation sketch, not a runnable evaluation artifact. A real pipeline still needs a versioned dataset, current RAGAs API integration, judge configuration, and stored outputs.

LLM-based grading also adds cost. Route or sample evaluations according to risk, and send borderline cases to a stronger judge or a human reviewer.

### Human Evaluation Traps

Human evaluation is necessary and expensive, and the way it usually goes wrong is asking humans the wrong question.

Bad question: "Rate this answer from 1-5 on quality."

Open-ended ratings like that produce inconsistent, subjective scores that don't generalize. A 4 from a careful annotator and a 4 from a generous one mean nothing in common, so the average is noise dressed up as a number.

Good question: "Does this answer contain any factual errors compared to the retrieved context? (Yes/No)"

Binary factual checks are fast, consistent, and actionable. When an annotator marks yes, that single row becomes a concrete bug I can pull up and trace back through retrieval and generation.

### Evaluating Retrieval in Isolation

Test retrieval separately before touching generation:

```python
def evaluate_retrieval(test_dataset, k_values=[1, 3, 5, 10]):
    """Measure retrieval quality independent of generation."""
    
    results = []
    for item in test_dataset:
        query = item["query"]
        relevant_docs = set(item["relevant_doc_ids"])
        
        retrieved = retrieval_model.query(query, k=max(k_values))
        retrieved_ids = set(retrieved["doc_ids"])
        
        for k in k_values:
            retrieved_k = set(retrieved_ids[:k])
            
            precision = len(retrieved_k & relevant_docs) / k
            recall = len(retrieved_k & relevant_docs) / len(relevant_docs)
            
            results.append({
                "k": k,
                "precision": precision,
                "recall": recall,
                "query": query,
            })
    
    return pd.DataFrame(results)
```

Retrieval scoring can run without generation, which makes it useful for isolating index and ranking failures before tuning the answer model.

## The Most Common Failure Mode

One failure mode shows up more than any other: evaluation looks great in testing and collapses in production.

Distribution shift is the culprit. Test datasets sit frozen while production queries drift, as users discover new ways to phrase questions, as documents go stale, as the corpus grows and changes shape underneath you.

A FAQ bot tuned on last quarter's questions starts fielding queries about a feature that shipped two weeks ago and has no good passage to retrieve.

Monitor retrieval and answer quality on a recurring sample of production queries so distribution shift appears in the evaluation record before it becomes a support pattern.

## What to Actually Optimize

If you're starting from scratch, optimize in this order:

1. **Retrieval recall first.** No generation improvement fixes missing context. Measure what percentage of your knowledge base the system can actually surface for any given query, and remember that techniques like [Anthropic's contextual retrieval can cut top-20 retrieval failures by 49%](/articles/how-anthropics-contextual-retrieval-changes-rag-architecture/).

2. **Context precision second.** Once recall is solid, reduce noise. High precision means the generator spends its context budget on signal, not noise.

3. **Faithfulness third.** Faithful generation keeps users trusting the system. Measure it, set a threshold, reject generations that fall below it.

4. **Answer relevancy fourth.** Everything above this point measures parts of the system. Answer relevancy measures the whole thing working together.

Starting with answer relevancy alone hides upstream failures. The [embedding models guide](/articles/embedding-models-compared/) explains one possible failure in the retrieval layer, but it does not provide benchmark evidence for a particular model.

<div class="visual-wrapper">
  <div class="visual-title">RAG EVALUATION FUNNEL</div>
  <div class="visual-container">
    <iframe src="/static/visuals/rag-eval-metrics.html" title="A RAG evaluation funnel scoring context recall, context precision, faithfulness, and answer relevance against their thresholds" loading="lazy"></iframe>
  </div>
</div>

## Setting thresholds

Set thresholds from labeled queries, reviewer agreement, and the cost of false positives and false negatives in the target domain. A medical or legal system will need different operating points from a brainstorming assistant.

A legal RAG tool that misses one controlling statute can sink a brief, so it demands higher recall than a product FAQ bot where a near-miss answer still helps.

## The Human Feedback Loop

Metrics don't capture everything. A system that scores well on RAGAs can still hand back answers that read as cold, evasive, or technically-correct-but-useless, the kind that satisfies faithfulness yet makes a user rephrase the same question three times.

Capturing user feedback at scale is what closes that loop. Thumbs up and down on answers, a "this was helpful" button, and the follow-up questions themselves, which tell you whether the first answer actually resolved the need or just stalled it.

User feedback can become a human-labeled evaluation set when it is sampled, reviewed, and versioned. Refresh that set as the product and query distribution change.

## The Real Takeaway

No single metric solves RAG evaluation. The cheap automated ones (BLEU, ROUGE, perplexity) are exactly the metrics that fail to measure correctness, and the ones that do measure it (faithfulness, answer relevancy) lean on LLM-based judges that cost real money and still get things wrong sometimes.

A multi-layered strategy is the answer. Automated metrics catch regressions, human evaluation catches misalignment, and production monitoring catches the distribution shift the other two will never see.

Score retrieval, generation, and end-to-end quality as separate things, because a failure in retrieval compounds through generation and the end-to-end number alone won't tell you where it started. Fix the foundation before polishing the surface.

A RAG system worth trusting treats evaluation as a first-class concern. Version the dataset, store the outputs, and keep monitoring production drift so failures turn into traceable fixes.
