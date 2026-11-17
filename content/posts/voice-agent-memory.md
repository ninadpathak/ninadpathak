---
category: ai-engineering
date: 2026-04-19
description: 'Memory for voice AI agents has one rule text chatbots skip: store what the caller heard. How OpenAI, LiveKit and Pipecat handle it, with a run example.'
status: published
work_note: 'I wrote Firecrawl''s comparison of AI voice agent platforms and ran the writing team at Mem0. Voice and memory meet on this page, and [the Firecrawl comparison](/portfolio/) is in my portfolio.'
title: 'Memory for Voice AI Agents: What Text Chatbots Cannot Do'
slug: voice-agent-memory
updated: 2026-11-17
---

A voice agent can generate a full sentence and be cut off after the fifth word. What it stores as its side of the conversation decides whether the rest of the call makes sense, and the documentation for the voice stacks compared below agrees on what that should be: the words the caller heard.

Memory for voice AI agents has the layers a text agent has, plus that one rule a text chatbot never needs. A reader sees every word the model wrote, and a caller hears only what was played before they spoke.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/voice-agent-memory/voice-pipeline.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/voice-agent-memory/voice-pipeline.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/voice-agent-memory/voice-pipeline.svg" width="720" height="392" alt="A caller's speech goes through speech-to-text, then the language model, then text-to-speech back to the caller. Working memory lives inside the pipeline stages and updates on every audio frame. Retrieved memory is fetched in parallel with generation, drawn as a dashed input to the model, so it arrives before the first token is spoken instead of blocking the turn." loading="lazy" decoding="async"></picture></a>
  <figcaption>The caller hears every pause, so retrieved memory runs alongside generation, never in front of it.</figcaption>
</figure>

## What can a text chatbot ignore that a voice agent can't?

A text chatbot can treat what the model generated as what the user received. A voice agent sees those two drift apart every time the caller interrupts, because generation runs ahead of playback.

OpenAI's [Realtime conversations guide](https://developers.openai.com/api/docs/guides/realtime-conversations) names the fix. "We call this truncating the model's last response, that is, removing the unplayed portion of the model's last response from the conversation."

The guide gives the reason in the caller's words: the model should know where it stopped in case "the user says "what was that last thing?"". An agent that remembers its whole sentence will answer that question with words the caller never heard.

## How do voice frameworks record what the caller heard?

They track playback and cut the stored reply at the point of interruption. Who does the tracking depends on the transport.

| Stack | What its documentation says |
| --- | --- |
| OpenAI Realtime API over WebRTC or SIP | "The server will automatically truncate unplayed audio when there's a user interruption." |
| OpenAI Realtime API over WebSocket | The client must "Record how many milliseconds of that item's audio the user actually heard." |
| [LiveKit Agents](https://docs.livekit.io/agents/build/turns/) | The agent "automatically truncates its conversation history to include only the portion of the speech that the user heard before interruption." |
| [Pipecat](https://docs.pipecat.ai/guides/learn/context-management) | Context is built from the text the speech service reports as spoken: "This ensures context matches what users actually hear." |

The WebSocket row is the one that fails without anyone noticing. Nothing breaks if the client skips the truncation event, and the conversation history fills with sentences that were never played.

## What does the difference look like in the history?

A short simulation makes it concrete. It gives each word of one reply a playback time, interrupts at 1.7 seconds, and compares the two versions of the stored turn.

```python
"""What a voice agent should remember after an interruption: the words the caller heard."""

# One generated reply, with the time each word finishes playing (milliseconds).
reply = "I have you booked for Tuesday the fourteenth at three in the afternoon with Dr Rao"
words = reply.split()
ends_ms = [220 * (i + 1) for i in range(len(words))]

interrupted_at_ms = 1700  # the caller starts speaking: "no, Wednesday"


def heard(words, ends_ms, cutoff_ms):
    return " ".join(w for w, end in zip(words, ends_ms) if end <= cutoff_ms)


generated = {"role": "assistant", "text": reply}
truncated = {"role": "assistant", "text": heard(words, ends_ms, interrupted_at_ms), "interrupted": True}

print("generated :", generated["text"])
print("heard     :", truncated["text"])
print("unplayed  :", reply[len(truncated["text"]):].strip())

for label, history in (("stores generated text", generated), ("stores heard text", truncated)):
    knows_time = "three in the afternoon" in history["text"]
    print(f"{label:<22} -> history claims the caller was told the time: {knows_time}")
```

The two versions of the turn, as `python3 heard_demo.py` reports them:

```text
generated : I have you booked for Tuesday the fourteenth at three in the afternoon with Dr Rao
heard     : I have you booked for Tuesday the
unplayed  : fourteenth at three in the afternoon with Dr Rao
stores generated text  -> history claims the caller was told the time: True
stores heard text      -> history claims the caller was told the time: False
```

The script models the bookkeeping only, with made-up word timings and no audio. The outcome is the point: the first history says the caller was told an appointment time, and the caller heard seven words that stop before the date.

When the caller then says "no, Wednesday", a model reading the first history believes the time is settled and only the day is in dispute. A model reading the second knows it has to give the day and the time again.

## Can a voice agent remember context from earlier in the same call?

Yes. Everything said earlier in the call sits in the conversation history that is sent to the model on each turn, the same [short-term memory](/articles/short-term-agent-memory/) a text agent has.

A long call brings the same limit a long chat does. The history has to be shortened at some point, and [context windows vs memory](/articles/context-windows-vs-memory/) covers what that costs.

The voice-specific risk is a wrong entry, more than a missing one. A turn recorded as spoken when it was cut off stays in the history for the rest of the call.

## What should a voice agent remember across calls?

Facts the caller would expect a person to remember, written after the call from the corrected history. That ordering matters, because a summary of a transcript that contains unplayed sentences will store things the caller was never told.

Retrieval of those facts has a constraint text doesn't share. A lookup in the middle of a turn is silence on the line, and [tracing voice agent latency](/articles/voice-agent-latency/) covers where that time goes.

The write side works as it does for any agent. [AI memory management for LLMs](/articles/ai-memory-management/) covers what to store and when to replace it, and the [state of agent memory](/articles/agent-memory-2026/) surveys the products that do it.

## FAQ

**Does the Realtime API handle interruptions for me?**

It depends on the connection. OpenAI's guide says the server truncates unplayed audio on WebRTC and SIP, and that with a WebSocket connection the client "must stop playback and handle truncation".

**What is the unplayed portion of a response?**

It is the part of a generated reply that was produced and never reached the caller's speaker because they started talking. Voice stacks remove it from the conversation so the model's record matches the call.

**Why does this matter for memory across sessions?**

Long-term memory is written from the conversation history. If the history contains sentences the caller never heard, the stored facts can include things nobody said aloud.
