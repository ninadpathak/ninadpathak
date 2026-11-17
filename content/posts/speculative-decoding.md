---
category: ai-engineering
primary_query: speculative decoding
siblings:
- kv-cache-eviction
- time-to-first-token
- llm-token-budgets
date: 2026-03-07
description: 'Speculative decoding has a fast predictor draft tokens and the large model verify them in one pass. How it works, what it gains and when it stops helping.'
status: published
work_note: "Your engineers shouldn't have to fix a tutorial's code in review. I'm Ninad Pathak, a freelance technical writer for AI companies, and I build and run every example before I draft. [Work with me on yours](/services/freelance-technical-writer-for-ai-companies/)."
title: 'Speculative Decoding: Speeding Up LLM Inference'
slug: speculative-decoding
updated: 2026-11-17
---

Speculative decoding has a cheap predictor draft the next few tokens of a model's output, and the large model check all of them in one pass. Every accepted draft is a token the large model didn't have to generate one at a time.

[Wikipedia's entry](https://en.wikipedia.org/wiki/Speculative_execution) on speculative execution in processors says "work is done before it is known whether it is actually needed", and the idea reached a wider audience in 2018, when the Spectre attack [took its name](https://spectreattack.com/) from "the root cause, speculative execution".

That entry also gives the condition under which the bet pays, which is "if extra resources are available". A processor usually has them, and a GPU server under load doesn't, so among [LLM inference](/articles/ai-engineering/) techniques this one helps some workloads and slows others.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/speculative-decoding/draft-verify.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/speculative-decoding/draft-verify.narrow.svg" width="288" height="736"><img class="np-has-narrow" src="/static/images/diagrams/speculative-decoding/draft-verify.svg" width="720" height="392" alt="A small draft model guesses the next few tokens in quick succession, and the large target model verifies all of the guesses in one parallel step. Tokens the target agrees with are kept; the first one it rejects, and everything after it, is discarded." loading="lazy" decoding="async"></picture></a>
  <figcaption>The draft model is fast and often wrong, and the target model has the final say on every token.</figcaption>
</figure>

## How does speculative decoding work?

It runs a draft-and-verify loop: a fast predictor proposes several tokens, and the target model scores those positions together and keeps the proposals up to the first one it rejects. The target then supplies its own token at that position, so each loop yields at least one token.

The method comes from [a paper submitted on November 30, 2022](https://arxiv.org/abs/2211.17192) by Yaniv Leviathan and colleagues, which borrows the hardware term in its abstract. It describes "an algorithm to sample from autoregressive models faster without any changes to the outputs, by computing several tokens in parallel."

The last clause is the reason the trick is safe to turn on. The paper's sampling rule accepts and corrects drafts "without changing the distribution", so the text is what the large model would have produced alone.

## How much faster does it make inference?

It depends on how often drafts are accepted. The paper reports "a 2X-3X acceleration" for one model, T5-XXL, and gives a formula for the expected number of tokens per verification step.

```python
"""Expected tokens per verification step in speculative decoding (Leviathan et al., Equation 1)."""


def expected_tokens(alpha, gamma):
    """alpha: chance a drafted token is accepted. gamma: tokens drafted per step."""
    return (1 - alpha ** (gamma + 1)) / (1 - alpha)


print("acceptance   2 drafted   4 drafted   8 drafted")
for alpha in (0.5, 0.7, 0.8, 0.9):
    row = "   ".join(f"{expected_tokens(alpha, gamma):9.2f}" for gamma in (2, 4, 8))
    print(f"{alpha:>10.1f}   {row}")
```

Running `python3 spec_tokens.py` gives the table.

```text
acceptance   2 drafted   4 drafted   8 drafted
       0.5        1.75        1.94        2.00
       0.7        2.19        2.77        3.20
       0.8        2.44        3.36        4.33
       0.9        2.71        4.10        6.13
```

At an acceptance rate of 0.5 the loop never averages more than two tokens a step however many are drafted. At 0.9 with four drafted it averages about four, so the quality of the guesses matters far more than their number.

The table is the paper's formula evaluated as written, with no model run behind it.

Those are tokens per step, and a step costs more than a plain decoding step because the predictor has to run too. The paper explains why the trade can still pay: inference "is often not bottlenecked on arithmetic operations, but rather on memory bandwidth and communication".

## Do you need a separate draft model?

No. The draft can come from a second, smaller model or from a prediction head built into the large one.

NVIDIA's [GLM-5.3 tutorial](https://developer.nvidia.com/blog/when-one-gpu-isnt-enough-serving-glm-5-3-across-two-nvidia-dgx-stations-with-vllm/) from November 13 uses the second kind, turned on in vLLM with one setting, `{"method":"mtp","num_speculative_tokens":4}`. It explains that "the model's MTP layer drafts four tokens per step, and vLLM verifies them with the full model before accepting them, so each step can produce several tokens."

The tutorial adds the caveat every deployment shares: "The gain depends on how often drafts are accepted, which varies with the prompt."

## When does speculative decoding stop helping?

It stops helping when the server is busy or the drafts are bad.

Modelplane's [inference field guide](https://docs.modelplane.ai/guides/inference-guide), which gives its figures as of October 2026, lists its cost as "Wasted compute when guesses are rejected. Its value shrinks as load rises and spare compute runs out."

That makes it a tool for the case the guide names, "Individual responses stream too slowly, even at low load". On a server already batching many requests there is little spare compute to spend on guesses.

The guide also says what to monitor.

"Watch speculative decoding acceptance. Acceptance depends on temperature, subject matter and the draft model."

A falling acceptance rate is hard to spot from the outside, because requests still succeed and only get slower. The related metric is tokens per second for each stream, and [time to first token](/articles/time-to-first-token/) doesn't move, since the first token still waits on the same queue and prefill.

## Where does it sit among other optimizations?

It is a decode-side technique, next to quantization and KV cache settings, and constrained decoding for [structured outputs](/articles/llm-structured-outputs/) acts at the same step. The memory those settings manage is the subject of [KV-cache eviction](/articles/kv-cache-eviction/), and the glossary entry on [speculative decoding](/glossary/speculative-decoding/) has the short definition.

The method changes speed and leaves the token count alone, since the large model has the final say on every token. What sets the bill is covered in [LLM token budgets](/articles/llm-token-budgets/).
