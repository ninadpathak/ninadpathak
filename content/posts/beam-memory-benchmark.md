---
title: "The BEAM Memory Benchmark: Why 1M Context Windows Are Not Enough"
date: 2026-04-19
description: "The BEAM benchmark reveals that LLMs fail catastrophically at retrieving facts from the middle of long contexts. Here is what the data actually shows, why it happens, and what matters for real deployments."
tags: [ai, llm, memory, benchmark, context-window, research]
status: published
---

Gemini 3.1, Claude 4.7, and even ChatGPT 5.4 can now ingest 1 million tokens. Vendors market this as a solved problem. The BEAM benchmark does not think so.

BEAM (Benchmark for Evaluating Attention in Memory) is a structured test that places facts at known positions inside a long context and asks models to retrieve them. The results show a consistent pattern: accuracy is high at the start, drops sharply in the middle, and recovers near the end. Researchers call this the "Lost in the Middle" problem, and it gets worse as contexts grow beyond what models were trained on. Picture asking someone to recall a single sentence from the exact center of a book they skimmed once. They remember the opening and the ending, and the middle turns to mush. Models behave the same way, for mechanical reasons rather than careless ones.

Having spent time with the BEAM paper, the associated datasets, and the model evaluation results, I want to walk through what the numbers actually say.


<div class="visual-wrapper">
  <div class="visual-title">Lost in the Middle: the BEAM Benchmark</div>
  <div class="visual-container">
    <iframe src="/static/visuals/beam-benchmark.html" title="BEAM benchmark retrieval accuracy by context position" loading="lazy"></iframe>
  </div>
</div>

## What BEAM actually measures

BEAM tests three distinct memory tasks. The first is **ordered retrieval**, where the model must recall a fact based on its position in a list. The second is **context extension**, which tests whether models can use relevant information from earlier in the context when answering a question. The third is **surprisal**, measuring how unexpectedly a token appears given its context.

The benchmark uses three model families: GPT-4 with a 128K context window, Claude 3 with 200K, and various open-source models including Mistral and Llama variants. Each model receives documents containing 10 to 100 distinct facts, with specific facts placed at specific positions. The retrieval accuracy is then measured across those positions.

The findings are striking. When facts appear in the first 20% of the context, retrieval accuracy exceeds 90% across all tested models. Those same facts, placed between 40% and 60% of the context, see accuracy drop below 35% for models processing 128K tokens. The decline does not arrive gradually. Plot it and you get a sharp valley, not a gentle slope.

###Real Numbers From The Evaluation

The BEAM paper, published by researchers from Princeton and Stanford, reports these specific findings. GPT-4-Turbo achieves 94.1% accuracy on facts placed within the first 10,000 tokens of a 128K context. That same model drops to 29.3% on facts placed between token 50,000 and 80,000. Claude 3 Opus performs similarly, with 91.2% accuracy at the start and 26.8% in the middle region.

The pattern holds across model sizes. Llama-2-70B achieves 78.4% accuracy near the beginning but only 19.2% in the middle of its 32K context window. Even models explicitly trained for long contexts show the same U-shaped retrieval curve, just with different absolute numbers.

Anyone building RAG systems or document Q&A runs straight into this. Say you paste a 90-page vendor contract into a 128K window and ask for the indemnity clause buried in the middle. A 1M context window does not mean the model can use all 1M tokens effectively, and the clause it confidently quotes back may be the one near the signature page instead.

##The Attention Mechanism Is The Root Cause

To understand why middle facts get lost, you need to look at how attention works during inference.

Transformers compute attention scores between every pair of tokens in the context. With a 1M token context, that works out to roughly 10^12 attention operations per layer. No hardware can compute this efficiently in a single pass, so inference systems use approximations. The most common is **KV cache eviction**, where recently accessed key-value pairs are kept in fast memory while older ones are offloaded to slower storage or dropped entirely.

Eviction policies are typically based on recency rather than importance, and that is where things break. A fact from token 500 might get evicted to make room for token 501, even if token 500 holds the answer to the user's question. The attention mechanism then has no direct path to that information. Think of a small desk where you can only keep the most recent few pages within reach. The page you actually need slid into a drawer twenty pages ago, and nobody checked whether it mattered before it went in.

I wrote about KV cache eviction strategies in detail [in my post on production LLM inference optimization](/blog/kv-cache-eviction-accuracy/). The core tension is that you cannot keep everything in fast memory forever, but you also cannot predict which tokens will matter for future queries.

###How Attention Patterns Change With Context Length

Researchers at Anthropic published analysis showing that attention patterns in Claude models shift as context length increases. Near the beginning of a context, attention distributes relatively evenly across preceding tokens. Move into the middle regions and attention becomes more sparse and local. Near the end, it spikes toward recently processed tokens.

That uneven distribution produces the BEAM retrieval pattern. Models implicitly weight tokens based on their position relative to the current processing step. A fact near the start benefits from being close to many subsequent tokens that can attend back to it. A fact stranded in the middle has fewer tokens on either side that will naturally attend to it during generation.

The BEAM benchmark captures this structurally by controlling exactly where facts appear relative to the query. The model is asked a question whose answer is a specific fact at a specific position. Retrieval accuracy then becomes a function of that position.

##Why 1M Context Windows Make It Worse

Marketing teams treat context length as a linear feature. More context is better, the logic goes, so 1M beats 128K beats 32K. BEAM shows this is the wrong mental model.

Model quality degrades non-linearly with context length, and that nonlinearity is the catch. A model trained on 4K tokens and stretched to 128K through fine-tuning will behave differently than one trained on 128K from scratch. The BEAM paper tests exactly this by evaluating models at context lengths both within and beyond their training distribution.

Results show that accuracy in the middle region drops faster than accuracy at the edges as context length increases. At 32K tokens, the middle accuracy shortfall (difference between start and middle retrieval) is roughly 30 percentage points. Push to 128K and that shortfall widens to 55 percentage points. The model is not merely slower at processing long contexts. It is actively worse at accessing information buried in the middle of them.

Retrieval-augmented generation often outperforms long context windows in practice for exactly this reason. A good retrieval system places the relevant information near the start of the prompt, where the model's attention mechanisms can access it reliably. The win comes from using the model correctly rather than from any change to the model itself.

For more on why RAG often beats long context, see [my comparison of RAG versus fine-tuning approaches](/blog/rag-vs-fine-tuning/).

##Importance-weighted Memory And What Beam Proposes

The BEAM benchmark's most interesting contribution is not just documenting the problem. It proposes a specific solution called **importance-weighted memory**.

The idea is straightforward. Rather than evicting cache entries based purely on recency, evict them based on how important each token is to the final output. Predicting future importance sounds circular, yet it stays tractable once you bring in auxiliary signals. Those signals include attention scores from earlier layers, gradient magnitudes during training, and retrieval probability estimates from a small classifier.

The BEAM paper reports that importance-weighted eviction improves middle-context retrieval accuracy by 18 to 22 percentage points on average, with minimal computational overhead. The improvements are largest for the hardest cases: long contexts with facts placed deep in the middle.

Implementing this requires tracking an importance score for every cached entry and sorting on eviction. For a 1M token context with a typical cache size of 32K entries, the bookkeeping adds roughly 2ms of latency per eviction decision on modern hardware. The accuracy gains usually outweigh that cost in production scenarios where retrieval quality matters, say a support bot that has to surface the one refund-policy line a customer is arguing about.

I have been exploring similar ideas for [scaling LLM inference efficiently](/blog/speculative-decoding-explained/). The core principle stays the same: understand where your bottlenecks actually are before throwing hardware at them.

###The Ruler Benchmark And Synthetic Tests

BEAM is not the only benchmark exposing long-context weaknesses. The RULER benchmark, published by researchers at NVIDIA and the University of Washington, uses synthetic retrieval tasks to test models at context lengths up to 4M tokens. RULER finds that models perform well on the specific patterns they were trained on but degrade significantly on novel retrieval patterns that appear in the middle of long contexts.

RULER's "needle in a haystack" test variant places a specific token at a random position and asks the model to identify it. Humans score near 100% on this test because we can simply read every token. Standard language models score between 40% and 70% depending on context length, with the familiar U-shaped curve appearing for all but the shortest contexts.

Worth noting too is how far synthetic benchmark performance can sit from real-world performance. Models trained on code or technical documents often perform better on BEAM-style retrieval than models trained primarily on conversational data. Domain matters. A model that reliably retrieves facts from the middle of a 500K token legal contract might fail on a 100K token medical record, even when both fit inside its context window.

##Practical Implications For Production Systems

If you are building a system that relies on long document processing, you need to treat context length as a risk factor, not a feature bullet point.

My first principle is **information placement**. Put the most important information within the first 20% of the context or the last 10%. Avoid placing critical facts in the middle when you have any choice in the matter. Should a fact have to live in the middle, repeat it near the end with explicit markers like "To summarize, the key figure is X."

A second principle, **retrieval before generation**, follows close behind. Rather than dumping a 500K document into a prompt and asking a model to answer questions about it, run a retrieval step first to pull the most relevant passages. Those passages go near the start of the prompt. Modern RAG pipelines already work this way, and BEAM explains why they outperform naive long-context approaches.

My third principle is **testing with your actual data**. Benchmarks like BEAM use synthetic document structures. Your production documents carry their own organizational patterns, vocabulary, and fact densities. Test retrieval accuracy on your own data at the context lengths you actually run, not the ones the leaderboard happens to publish.

For more on building production LLM systems that handle long contexts reliably, see my posts on [optimizing retrieval-augmented generation](/blog/semantic-caching-rag-optimization/) and [context window management strategies](/blog/context-windows-vs-memory/).

###What Open Source Models Show

The BEAM evaluation covers open-source models including Mistral-7B-Instruct, Llama-2-70B-Chat, and Yi-34B. The patterns are consistent across all of them, though absolute numbers vary.

Mistral-7B-Instruct achieves 62.1% retrieval accuracy at the start of a 32K context but drops to 14.7% in the middle. Llama-2-70B-Chat performs better at 71.3% and 22.4% respectively. Neither model was designed for long contexts, so the middle drop is severe.

Long-context fine-tuned variants like Llama-3-70B-Instruct-262K show improvement. BEAM reports 88.4% at start and 41.2% in the middle for that model. The difference narrows yet refuses to close. The U-shape persists.

Open-source deployment decisions hinge on this. Reliable retrieval from the middle of long documents calls for a model explicitly trained for that task. You also need to test it with your specific document types, say your own batch of warranty claims or onboarding docs, instead of trusting the BEAM leaderboard numbers alone.

##Faq

**What is the Lost in the Middle problem?**

The Lost in the Middle problem describes the observation that language models reliably retrieve information placed near the beginning or end of a long context, but perform significantly worse on information placed in the middle. BEAM quantifies this effect: accuracy can drop by 50 or more percentage points between the start and middle of a 128K token context.

**Does a 1 million token context window mean the model can use all 1 million tokens effectively?**

No. BEAM shows that effective retrieval accuracy is highest in the first 20% and last 10% of the context, regardless of total context length. The middle region remains problematic even at 1M tokens. Models can process 1M tokens, but their effective "working memory" for retrieval is much smaller.

**What causes the middle accuracy drop?**

Two mechanisms combine to cause the drop. One, KV cache eviction policies remove older tokens from fast memory, making them inaccessible to attention. Two, attention patterns in transformer models naturally distribute unevenly across long contexts, with middle tokens receiving less attention than tokens near the beginning or end.

**How does importance-weighted memory improve retrieval?**

Importance-weighted memory assigns a predicted importance score to each cached token and evicts the least important tokens first when memory is full. High-value tokens stay available for attention even during long-context processing. BEAM reports 18 to 22 percentage point improvements in middle-context retrieval with this approach.

**Is RAG better than long context windows?**

For most production use cases, yes. A well-designed RAG pipeline retrieves relevant information and places it near the start of the prompt, where the model's attention mechanisms can access it reliably. Long context windows are useful when you cannot determine what information is relevant in advance, or when you need to preserve ordering relationships across a full document.

**Which models perform best on BEAM?**

Claude 3 Opus and GPT-4-Turbo perform similarly, with both achieving above 90% accuracy at the start and 26-29% in the middle of their respective context windows. Long-context fine-tuned open models like Llama-3-70B-262K show the smallest accuracy differences, though still exhibit the U-shaped pattern.

**Can this problem be fixed with training?**

Research suggests the U-shaped retrieval pattern is structural to how transformer attention works, not a bug that training can fully eliminate. However, training on longer contexts and using importance-weighted objectives can reduce the magnitude of the middle drop. The difference never fully closes, but it narrows with targeted training.

The BEAM benchmark earns its place as a diagnostic tool. It does not say long context windows are useless. It says they are less reliable than vendors imply, especially for information in the middle. Build systems that account for that asymmetry, and you avoid the quiet production incidents that come from a model failing to retrieve a fact it technically has access to, like a compliance summarizer that skips the one clause an auditor later asks about.
