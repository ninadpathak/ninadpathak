---
category: ai-engineering
date: 2026-04-16
description: A systems-level guide to tracing latency across endpointing, transcription,
  model inference, speech synthesis, and transport.
status: published
tags:
- voice-ai
- real-time
- gemini
- latency
- webrtc
- engineering
title: How to Trace Latency in a Real-Time Voice Agent
updated: '2026-08-17'
---

Voice latency is the sum of endpointing, transcription, model inference, speech synthesis, buffering, and transport. The guide explains that chain without claiming a reproducible benchmark.

**Short answer:** The model's first-token latency is only one part of voice responsiveness. Endpointing, transcription, synthesis, buffering, and network handoffs also contribute.

## The architecture of the A2A latency chain

A real-time voice agent is not a single API call. It is a pipeline of four serial stages, each with its own latency profile, each adding buffer tax that compounds the total round-trip time.

```
Audio Input → VAD → STT → LLM → TTS → Audio Output
```

Voice Activity Detection (VAD) determines when the user has stopped speaking. STT converts the audio stream to text.

The LLM generates a response. TTS converts that response back to audio.

The user hears the result.

Each stage introduces at least one buffering decision: how much audio to accumulate before sending it, how many tokens to generate before starting TTS, how large each network packet should be. None of these decisions touch model quality.

A voice pipeline can still feel slow when each handoff adds buffering or network delay.



## The VAD tax: when does the user actually stop speaking?

Voice Activity Detection is the unsung hero (and villain) of voice agent latency. A VAD model must decide whether a pause in speech is a mid-sentence hesitation or a genuine turn boundary.

A caller may pause mid-sentence to check a figure, which makes endpointing a trade-off between interruption and delay.

The VAD model's compute time is only part of endpointing. Tune its patience threshold against labeled pauses and interruptions from the deployment environment.


## STT processing: the chunking bottleneck

STT can run in a cloud service or on local hardware. The choice changes network, compute, and buffering costs.

Smaller audio frames create more frequent handoffs, while utterance-level sends wait longer before transcription begins.

Sending the full utterance on VAD trigger means one larger payload but no state management overhead.

Cloud STT adds network work, while local STT consumes client resources. Trace both paths before choosing a chunking strategy.

When VAD fires too early, STT receives an incomplete sentence and produces a partial transcript, so the LLM ends up answering "what is the refund policy for" instead of "what is the refund policy for an annual plan I cancelled mid-cycle," which is a different question with a different answer.

## LLM time to first token

Longer prompts require more input processing before generation starts. The effect depends on the model and serving path, so trace first-token latency across representative conversation lengths.

The same context-management problem appears in [KV-cache eviction](/articles/kv-cache-eviction-accuracy/). Reduce prompt history only after testing what the model forgets.

## The TTS synthesis delay

Text-to-Speech is the final stage. Cloud and local TTS engines expose different streaming and buffering behavior.

Both operate on a streaming basis, beginning to emit audio bytes as soon as the first sentence is generated.

The critical metric here is *time to first audio byte* (TTFAB), which is not the time to synthesize the full response. It is the time from text receipt to the first playable audio sample.

A TTS engine may need enough text to form a playable unit before it emits audio. That creates a dependency between language-model output and speech synthesis even when both APIs stream.

A hidden coupling lives between LLM generation and TTS synthesis here. They are not truly parallel.

TTS is blocked on the LLM producing a complete linguistic unit, the way a typesetter cannot set a line until the writer has finished the sentence, not just the first few words.

## Latency budgets expose trade-offs

An end-to-end budget forces every stage to account for its wait time. Reducing endpointing patience may interrupt callers, and aggressive context pruning can remove details the model still needs.

The trade-off is architectural, not a universal latency table. Build the budget from traces collected in the target application.

## Speculative TTS: the risky shortcut

Speculative TTS is the voice agent equivalent of [speculative decoding](/articles/speculative-decoding-explained/). You start working before you have the full answer.

Instead of waiting for the LLM to produce a complete sentence, the TTS engine begins synthesizing audio as soon as the first few tokens arrive.

The risk is non-monotonic generation. LLMs do not always produce linear text.

They might generate "The best approach is to..." and then backtrack with "Actually, let me reconsider." If TTS has already synthesized audio for the first clause, you are now playing audio that contradicts the model's final answer.


## WebRTC vs. HTTP/2: the transport layer tax

Most voice agent tutorials use HTTP/2 streaming because it is the default in every SDK. HTTP/2 multiplexes streams over a single TCP connection, which is efficient for high-throughput data but suboptimal for low-latency audio.

The problem is TCP head-of-line blocking. If one audio chunk is lost and requires retransmission, all subsequent chunks are delayed until the retransmission completes.

TCP retransmission can turn packet loss into head-of-line blocking, while real-time media transports are designed to tolerate some loss without waiting for every packet.

WebRTC uses UDP with a custom reliability layer (SCTP over DTLS). Lost audio packets are simply skipped rather than retransmitted.

The audio stream continues with a minor glitch rather than a full stall.


It eliminates the catastrophic latency spikes that make a voice agent feel "unresponsive" even when the average is fine.

The downside is implementation complexity. WebRTC requires a signaling server, ICE candidate negotiation, and DTLS certificate management.

It also requires signaling, connection negotiation, and certificate management that a simple HTTP request does not.

## The silence filler problem: what plays while you wait?

Long silence after a caller stops speaking breaks the rhythm of ordinary turn-taking and can prompt the caller to speak again.

To bridge that silence, production voice agents use "filler utterances": "Hmm," "Let me think," "One second." These fillers serve two purposes.

They signal that the agent is still processing, and they buy time for the pipeline to complete.


A waiter who says "let me check on that" buys the kitchen time without the table feeling abandoned, and the filler does the same job for the pipeline.


## The context window memory tax

The [open-source AI memory review](/articles/state-of-open-source-memory-2026/) compares structured memory designs with raw context. Read it as an architecture survey, not as benchmark evidence for a voice pipeline.

Long conversation history increases prompt-processing work and can slow the first token. Summaries and selective recall can bound that cost, but both need tests for lost constraints.

No universal pruning threshold fits every conversation. Keep the details that affect the current task and measure the latency and recall trade-off on representative calls.

A customer support bot can tolerate these tradeoffs. A medical consultation assistant cannot.


## Practitioner's checklist: auditing your voice agent latency

1. **Profile every stage independently**: Instrument endpointing, STT, model first-token latency, TTS startup, buffering, and network handoffs.
2. **Tune endpointing against labeled audio**: Tune endpointing against a labeled interruption set, then choose the patience setting that fits the product's tolerance for false turn ends.
3. **Compare audio chunking strategies**: Test frame and utterance-level paths with the same audio fixture.
4. **Bound prompt history from traces**: Limit prompt history according to measured first-token latency and recall.
5. **Test speculative TTS before shipping it**: Record abandoned audio and audible corrections.
6. **Choose transport from loss and latency traces**: Compare behavior under the network conditions users actually have.
7. **Monitor connection health**: Detect stalled streams and reconnect before the session silently dies.

## The future of real-time voice AI

Voice responsiveness is a systems problem, not only a model-speed problem. Compare models inside the full audio pipeline rather than treating first-token latency as the answer.

It is the VAD configuration, the chunking strategy, the transport protocol, and the TTS pipeline.

The next frontier is **full-duplex voice**: the ability for the agent to listen while it speaks, detecting user interruptions and backing off mid-sentence. Pulling that off demands a fundamentally different architecture where STT, LLM, and TTS run in parallel rather than serially.

Full-duplex systems also need a measured interruption target because the agent must stop output promptly when the caller speaks.

I covered the broader [KV cache management problem](/articles/kv-cache-eviction-accuracy/) that affects all LLM-based systems. Voice agents are simply the most latency-sensitive application of these infrastructure constraints.

Every millisecond saved in the context window is a millisecond closer to a conversation that feels human.

Teams building voice-first products need clear architectural documentation and implementation guides. [My work page](/work) shows how I explain complex infrastructure for developer-tool companies.

## FAQ

**What is the single biggest latency contributor in a voice agent?** There is no universal answer. Instrument endpointing, transcription, inference, synthesis, buffering, and transport in the deployed pipeline.

**Is Gemini faster than GPT-4o Mini for voice?** This article does not contain a reproducible model comparison. Test both through the same audio pipeline, region, prompt set, and connection path.

**Can I run the entire voice agent pipeline locally?** Some VAD, STT, TTS, and language models can run locally. Whether the full pipeline is usable depends on the target hardware and measured quality.

**How does packet loss affect voice agent latency?** TCP retransmission can stall later packets behind a lost one. Real-time transports can prefer continuity over perfect delivery, which changes the failure mode.

**What is the "context quarantine" pattern?** It keeps a bounded active conversation plus a compressed summary of older turns. Test whether the summary preserves constraints that later answers need.

**Should I use filler utterances?** Test them with callers. A filler can signal that processing continues, but repetitive or misplaced fillers can make the interaction worse.
