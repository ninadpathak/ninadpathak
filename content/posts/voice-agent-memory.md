---
category: agent-memory
primary_query: voice agent memory
siblings:
- short-term-agent-memory
- ai-memory-management
bridges:
- slug: voice-agent-latency
  reason: A memory lookup in the middle of a turn is silence on the line, which the latency page measures.
date: 2026-04-19
description: 'Memory for voice AI agents has one rule text chatbots skip: store what the caller heard. How OpenAI, LiveKit and Pipecat differ, with a simulated example.'
status: published
work_note: 'I wrote Firecrawl''s comparison of AI voice agent platforms and ran the writing team at Mem0. Voice and memory meet on this page, and [the Firecrawl comparison](/portfolio/) is in my portfolio.'
title: 'Memory for Voice AI Agents: What Text Chatbots Cannot Do'
slug: voice-agent-memory
updated: 2026-11-17
---

Phone agents got a shorter path to production this month. OpenAI's [SIP guide](https://developers.openai.com/api/docs/guides/voice-sip) now says "Outbound SIP calling is available to all organizations through the Live API", a change that reached Hacker News on November 6, and every agent placed on a call inherits a problem text chatbots never had.

A caller can interrupt, and a voice agent can have generated a full sentence when it is cut off after the seventh word. Memory for voice AI agents has the layers a text agent has, plus one rule: the record of the agent's side has to match what was played, because a reader sees every word the model wrote and a caller hears only part.

Everything else follows the general design of [AI agent memory](/articles/agent-memory/).

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/voice-agent-memory/voice-pipeline.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/voice-agent-memory/voice-pipeline.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/voice-agent-memory/voice-pipeline.svg" width="720" height="392" alt="A caller's speech goes through speech-to-text, then the language model, then text-to-speech back to the caller. Stored memory is drawn as a dashed input to the model." loading="lazy" decoding="async"></picture></a>
  <figcaption>A voice pipeline. What the model generates and what the caller hears part ways at the last stage, text-to-speech.</figcaption>
</figure>

## What can a text chatbot ignore that a voice agent can't?

A text chatbot can treat what the model generated as what the user received. A voice agent sees those two drift apart every time the caller interrupts, because generation runs ahead of playback.

OpenAI's [Realtime conversations guide](https://developers.openai.com/api/docs/guides/realtime-conversations) names the fix. "We call this truncating the model's last response, that is, removing the unplayed portion of the model's last response from the conversation."

The guide gives the reason in the caller's words: the model should know where it stopped in case "the user says "what was that last thing?"". An agent that remembers its whole sentence will answer that question with words the caller never heard.

## How do voice frameworks record what the caller heard?

They differ, and the difference decides what ends up in memory. The stacks I read fall into two groups.

| Stack | What is kept after an interruption |
| --- | --- |
| OpenAI Realtime API | Played audio only. Truncation "will cut the audio at a given place and remove the text transcript for the unplayed portion", and the guide adds that this "doesn't provide a truncated transcript." |
| [LiveKit Agents](https://docs.livekit.io/agents/build/turns/) | Text of the heard part. The agent "automatically truncates its conversation history to include only the portion of the speech that the user heard before interruption." |
| [Pipecat](https://docs.pipecat.ai/guides/learn/context-management) | Text of the heard part, word by word. Its documentation says "Your context stays updated at the word level in case an interruption occurs". |

On the Realtime API the transport also matters. Over WebRTC or SIP "The server will automatically truncate unplayed audio when there's a user interruption.", and over WebSocket the client must "Record how many milliseconds of that item's audio the user actually heard."

OpenAI's guide explains the missing transcript: the model "doesn't have enough information to precisely align transcript and audio". So an application on that API that wants the heard words as text has to produce them itself.

## What does the difference look like in the history?

The simulation below gives each word of one reply a playback time, interrupts at 1.7 seconds, and compares two versions of the stored turn. It models the bookkeeping only, with made-up word timings and no audio.

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

```text
generated : I have you booked for Tuesday the fourteenth at three in the afternoon with Dr Rao
heard     : I have you booked for Tuesday the
unplayed  : fourteenth at three in the afternoon with Dr Rao
stores generated text  -> history claims the caller was told the time: True
stores heard text      -> history claims the caller was told the time: False
```

A history that stores the generated text says the caller was told an appointment time. The caller heard seven words that stop before the date.

When the caller then says "no, Wednesday", a model given the first history has no way to know the time was never spoken. Given the second, the missing half of the sentence is visible in the record.

## Can a voice agent remember context from earlier in the same call?

Yes. Everything said earlier in the call sits in the conversation history sent to the model on each turn, the same [short-term memory](/articles/short-term-agent-memory/) a text agent has, with the same limit on length.

The voice-specific risk is a wrong entry more than a missing one. A turn recorded as spoken when it was cut off stays in the history for the rest of the call.

## What should a voice agent remember across calls?

Facts the caller would expect a person to remember, written after the call from a history that matches what was played. On LiveKit or Pipecat that history is the framework's own.

On the Realtime API it isn't available as text, so the choice is between transcribing the played audio and accepting that long-term notes are built from a transcript with holes. My choice is the first for anything a caller will be held to, such as a booking.

Retrieval has a constraint text doesn't share, since a lookup in the middle of a turn is silence on the line. [Tracing voice agent latency](/articles/voice-agent-latency/) follows where that time goes, and [AI memory management for LLMs](/articles/ai-memory-management/) covers what to store.

## FAQ

**Does the Realtime API handle interruptions for me?**

It handles the audio, depending on the connection. OpenAI's guide says the server truncates unplayed audio on WebRTC and SIP, and that with a WebSocket connection the client "must stop playback and handle truncation".

**What is the unplayed portion of a response?**

It is the part of a generated reply that was produced and never reached the caller's speaker because they started talking. Voice stacks remove it from the conversation so the model's record matches the call.

**Why does this matter for memory across sessions?**

Long-term memory is written from the conversation history. If the history contains sentences the caller never heard, the stored facts can include things nobody said aloud.
