---
date: 2026-03-08
description: Users do not care about total throughput. They care about how fast the
  first word appears. Here is the engineering guide to measuring and optimizing Time
  to First Token (TTFT) in production.
status: published
tags:
- ai
- llm
- infrastructure
title: 'Time to First Token (TTFT): The Metric That Determines AI Snappiness'
---

Every interactive AI app I have shipped lives or dies by perceived latency. A model might churn out 100 tokens per second, and none of that speed matters when the user stares at a blank box for five seconds before the stream starts. Time to First Token (TTFT) is the metric I reach for when I want to know whether an application feels alive or feels broken, and I have watched the same chat UI go from delightful to abandoned on the strength of that one number alone.

What trips up most teams I work with is treating TTFT as a single dial they can turn. It is really the sum of a pipeline: the network hop from the user to your server and on to the inference host, time spent waiting in a queue behind other requests, and the model prefilling your prompt. Each one adds milliseconds, and any one of them can quietly dominate the others depending on the day. Chasing a slow chat endpoint for a full day, I assumed the model was the problem, when the culprit was requests piling up in a queue during the lunchtime traffic spike while the GPU sat near idle the rest of the afternoon.

Because the fix for each piece is completely different, breaking the number into those three parts is the first thing I do before I optimize anything. Network latency I attack with edge routing and keeping the inference host close to the user, say moving an endpoint from a single us-east region into a CDN that terminates closer to where the request originates. Queue time I attack with capacity and smarter scheduling. Caching and model choice are what I reach for against prefill. Spending a week shrinking the model when 80% of your TTFT is actually queue wait, the way one team I helped did before they measured anything, is the kind of wasted effort that good instrumentation prevents.



## What TTFT actually measures

When I talk about TTFT I mean the interval between a user sending a request and the first generated token landing back in their browser. That is a separate thing from tokens per second, which only describes how fast text flows once the stream has already opened. A model can post a gorgeous tokens-per-second figure and still feel sluggish to type at, because the user judges responsiveness almost entirely by that first word.

Prefilling the prompt is the part that dominates TTFT in my experience. Before the model can emit a single token it has to read every input token and build the [initial KV cache](/blog/kv-cache-eviction-accuracy/), and that work is a one-time tax paid at the start of every request. Because the cost scales with prompt length, a request carrying a 200-token question returns far faster than the same request after I have stuffed 40k tokens of retrieved documents in front of it. A support assistant I worked on went from snappy to painful purely because someone padded the system prompt with a second page of tone-of-voice instructions, doubling its size overnight and adding a beat of dead air before every reply.

<div class="visual-wrapper">
  <div class="visual-title">TTFT CHAIN</div>
  <div class="visual-container">
    <iframe src="/static/visuals/ttft-chain.html" title="The latency chain to the first token: network, queue, and prefill make up TTFT, then token generation continues as throughput" loading="lazy"></iframe>
  </div>
</div>

## TTFT is not the same as throughput

For batch jobs I happily optimize for throughput. Parsing ten thousand support tickets overnight to extract sentiment, nobody is watching the screen, so I want the GPU saturated and the total tokens-per-hour as high as I can push it. Interactive chat is the opposite job: a single human is waiting, and low TTFT is the only thing they feel. The two goals pull against each other, and I have to pick which one a given endpoint serves.

Batching is where the tension lives. Cramming more requests into one batch lets the GPU do more arithmetic per memory load, which is great for throughput, and it means your request now waits for the whole batch to assemble and run before its first token comes back. Think of it like a shuttle bus that only leaves once every seat is full: efficient per passenger, miserable if you are the one who boarded first and the bus refuses to move. To keep TTFT low I run smaller batches, or I carve off dedicated compute that processes interactive requests the moment they arrive instead of pooling them.

Continuous batching softens this on modern inference servers, where new requests can slot into a running batch instead of waiting for a fresh one to form. That helps a lot, and I still have to set the maximum batch size deliberately, because letting it grow without bound trades away the very TTFT I am trying to protect. My rule of thumb on interactive endpoints is to size the batch for the worst-case TTFT I am willing to ship, say 600ms at p95, then add hardware rather than batch size when I need more total capacity.

## Model size is the first real lever

Before any tuning, model size sets the floor on TTFT. A 7B parameter model will beat a 400B model to the first token on identical hardware every time, because the smaller one has fewer weights to pull through memory while it prefills your prompt. Picture prefill as reading a book aloud before you can answer a question about it: the thicker the model, the longer that silent read takes regardless of how clever the rest of your pipeline is. No amount of clever batching changes that baseline, which is why I treat model choice as the first knob I reach for, not the last.

Reaching for a smaller distilled model is the highest-impact move I know when my quality bar leaves room for it. On one assistant I built, I let a small fast model produce the immediate acknowledgement and opening sentence the user sees, then handed the actual heavy reasoning to a larger model running in the background and streamed its output in behind the first model's. The user gets a word on screen almost instantly, and the depth still arrives, so nobody feels the larger model's slower start.

## A practical order for optimization

When a team hands me a slow endpoint and asks me to make it feel fast, I work down the same hierarchy every time, cheapest wins first.

**Model Selection.** My first question is always whether a smaller model clears the quality bar, because swapping a 70B for a well-chosen 8B can halve TTFT before I touch the infrastructure. It is the cheapest experiment I can run and the one teams skip most often.

**Prompt Caching.** Static context like a long system prompt or a fixed set of few-shot examples gets paid for on every single request unless I cache it. Wiring up [prompt caching to eliminate the prefill tax for static context](/blog/prompt-caching-what-it-is-and-when-the-math-works/) has dropped TTFT by around 80% on the repeated-prefix portion of requests I have measured, since the model reuses the KV cache for the part of the prompt that never changes.

**Speculative Decoding.** Pulling in [a draft model to speed up LLM inference for free](/blog/speculative-decoding-explained/) lets a small model guess several tokens ahead while the big model verifies them in one pass. The snappiness comes from generating multiple tokens per step rather than one at a time, and the output stays identical to what the big model would have produced alone.

**Quantization.** Dropping the precision of the weights speeds up the memory loads that prefill is bottlenecked on. Moving from FP16 to INT8 or FP8 has given me a real TTFT improvement with accuracy loss small enough that my eval suite barely flinched. The reason it helps is mechanical: prefill spends most of its time hauling weights out of GPU memory, and halving the bytes per weight halves that traffic, so the first token arrives sooner even though the model is doing the same logical work.

## How to measure without fooling yourself

Averages are where I have fooled myself the most. A mean TTFT of 400ms looks healthy right up until I notice the tail, where one user in twenty is waiting two seconds and quietly churning. Latency lives in that tail, so I measure p95 and p99 and treat those as the real number, since they describe the experience of my unluckiest users rather than a comfortable fiction.

One dashboard mistake I see constantly is plotting TTFT as a flat line with no sense of input size. A p95 of 500ms is excellent for a 1k token prompt and physically impossible for a 100k token prompt without caching, so a single threshold tells me nothing. I normalize the metric by prompt length and look at TTFT per thousand input tokens, which finally makes a slow week distinguishable from a week where prompts simply got longer.

The other measurement habit I insist on is timing the real path, not a synthetic one. A benchmark that fires requests from a machine sitting next to the GPU will report a TTFT your actual users never see, because it skips the network hop and the queue contention that real traffic creates. I instrument the client side, capturing the moment the user's request leaves the browser and the moment the first token paints, and I sample it under genuine load rather than at three in the morning when the cluster is idle. The number that matters is the one a logged-in user produces during your busiest hour.

Perception is the whole game here. I have shipped features that win the moment the first token appears before the user has finished forming their thought, and lost ones that were technically fast yet felt dead because that first word lagged. Watch TTFT closely and the applications you build start to feel less like a request-response form and more like something that was already listening.