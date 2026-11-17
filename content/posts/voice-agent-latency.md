---
category: ai-engineering
primary_query: voice ai latency
siblings:
- time-to-first-token
- kv-cache-eviction
- speculative-decoding
bridges:
- slug: voice-agent-memory
  reason: A memory lookup in the middle of a turn is added silence on the line.
date: 2026-04-16
description: Voice AI latency is the time from the caller's last word to the agent's first
  sound. Where that time goes, why endpointing is the largest fixed cost, and a stage-by-stage
  budget you can rerun with your own numbers.
status: published
work_note: "I'm Ninad Pathak, a freelance technical writer. If your AI product's tutorials have fallen behind the product, I write them, and I run the product first. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
title: Voice AI Latency and Where a Voice Agent's Time Goes
updated: '2026-08-17'
slug: voice-agent-latency
---

Radio operators solved the hardest part of voice AI latency with one word. On a channel where only one side can talk at a time, you end your turn by saying "over", which the [list of procedure words](https://en.wikipedia.org/wiki/Procedure_word) defines as the end of a transmission that needs a reply.

A voice agent doesn't get that word. It has to guess when the caller has finished, and voice AI latency is the time from the caller's last word to the first sound the agent makes, with that guess included.

People are quick at the same guess. A [2015 review of turn-taking research](https://pmc.ncbi.nlm.nih.gov/articles/PMC4464110/) puts the usual pause between speakers at around 200 ms, while planning a spoken reply takes over 600 ms, so listeners must be predicting the end of a turn before it arrives.

That's the bar, and it explains where the time goes in a voice pipeline. I've laid the stages out below with a budget you can rerun, and the model-side pieces link to the rest of [AI engineering](/articles/ai-engineering/).

## What is voice AI latency?

Voice AI latency is the delay a caller hears between finishing a sentence and the agent starting to answer. It's the sum of a chain of stages, and the language model is one link in it:

1. **Endpointing:** deciding that the caller has stopped.
2. **Transcription:** turning the audio into text.
3. **Inference:** the model producing the first words of a reply.
4. **Synthesis:** turning those words into audio.

A speech-to-speech model folds the middle stages into one, and the first and last remain. Somebody still has to decide the turn is over, and the caller still waits for sound.

## Where does the time go in a voice agent turn?

More of it goes to waiting for silence than people expect. The script below adds up one turn under stage times I've assumed, so the numbers show the structure and aren't measurements of any service:

```python
"""Add up one voice-agent turn stage by stage. The stage times are assumed, not measured."""
STT_MS, LLM_FIRST_TOKEN_MS, LLM_PER_TOKEN_MS, TTS_FIRST_AUDIO_MS = 150, 300, 20, 120
REPLY = "Your refund was issued on Monday. It should reach your card within five business days.".split()
FIRST_SENTENCE = REPLY.index("Monday.") + 1


def turn(silence_ms, stream_to_tts):
    """Return when each stage finishes, in ms after the caller stops speaking."""
    tokens_before_tts = FIRST_SENTENCE if stream_to_tts else len(REPLY)
    stages = [
        ("turn end detected", silence_ms),                       # endpointing waits out the silence
        ("transcript ready", STT_MS),
        ("first LLM token", LLM_FIRST_TOKEN_MS),
        ("text handed to TTS", tokens_before_tts * LLM_PER_TOKEN_MS),
        ("first audio", TTS_FIRST_AUDIO_MS),
    ]
    clock, marks = 0, []
    for name, cost in stages:
        clock += cost
        marks.append((clock, name))
    return marks


RUNS = [
    ("500 ms silence, TTS waits for the full reply", 500, False),
    ("500 ms silence, TTS starts on the first sentence", 500, True),
    ("200 ms silence, TTS starts on the first sentence", 200, True),
]
for label, silence_ms, stream in RUNS:
    print(label)
    for at, name in turn(silence_ms, stream):
        print(f"  {at:>5} ms  {name}")
```

Running `python voice_trace.py` printed:

```text
500 ms silence, TTS waits for the full reply
    500 ms  turn end detected
    650 ms  transcript ready
    950 ms  first LLM token
   1250 ms  text handed to TTS
   1370 ms  first audio
500 ms silence, TTS starts on the first sentence
    500 ms  turn end detected
    650 ms  transcript ready
    950 ms  first LLM token
   1070 ms  text handed to TTS
   1190 ms  first audio
200 ms silence, TTS starts on the first sentence
    200 ms  turn end detected
    350 ms  transcript ready
    650 ms  first LLM token
    770 ms  text handed to TTS
    890 ms  first audio
```

In the first run the caller waits 1,370 ms, and the model's first token accounts for 300 ms of it. The 500 ms spent confirming silence is the largest single line, and it's spent before any model has done anything.

The second run changes one thing: speech synthesis starts when the first sentence is complete, without waiting for the rest of the reply. That saves 180 ms here, and the saving grows with the length of the answer.

The third run cuts the silence wait to 200 ms and brings first audio under a second. It also makes the agent likelier to talk over someone who paused to think.

## Why is endpointing the hard part?

Because a pause doesn't tell you whether a person is finished. Wait a short time and you interrupt people mid-thought, and wait a long time and every reply starts late.

The 500 ms in my script is OpenAI's default. Its [Realtime API guide](https://developers.openai.com/api/docs/guides/realtime-vad) shows `silence_duration_ms` set to 500 for the default mode, which chunks audio on periods of silence, and that one setting is more than twice the pause people leave each other.

The way out is to predict the end of the turn the way a listener does. OpenAI's second mode, `semantic_vad`, scores how likely it is that the speaker is done from the words so far, and waits longer on a sentence that trails off than on a definite statement.

LiveKit has landed in the same place. Its [turn detection docs](https://docs.livekit.io/agents/logic/turns/) make a turn detector model the default, one that "Predicts end of turn from both the meaning of speech and its acoustic properties", and keep silence-only detection for when you need minimal latency.

I think that's the right default, and I'd go further. If I had one week to make a voice agent feel faster, I'd spend it on endpointing before touching the model.

## How do you cut the model's share?

You shorten the wait for the first token and you hand text to the speech engine early. The first of those is ordinary [time to first token](/articles/time-to-first-token/) work, and a voice agent is the case where it's felt directly.

Prompt length is the lever you control. A long history has to be processed before the first token comes out, and a cached prefix skips that work, which is the reuse the [KV cache](/articles/kv-cache-eviction/) page describes.

Handing over text early has a catch. Start speaking before the sentence is settled and you're betting the model won't change course, which is the bargain [speculative decoding](/articles/speculative-decoding/) makes inside the model, except that here a wrong guess has already been said aloud.

Tool calls are the other place a turn stretches. A lookup in the middle of a reply is silence on the line, and [voice agent memory](/articles/voice-agent-memory/) covers how to keep those lookups off the critical path.

## How should you measure voice AI latency?

Timestamp each stage boundary and report them separately, the way the script prints them. A single end-to-end number can't tell you whether to tune the silence wait or the model.

Both vendors' APIs give you the boundaries. OpenAI's Realtime API emits `input_audio_buffer.speech_stopped` when it decides a turn has ended, and that event is where I'd start the clock for everything after endpointing.

And measure with real pauses. A test caller who speaks in clean, complete sentences will make a 200 ms silence setting look free, and it isn't.

## FAQ

**What is a good latency for a voice agent?**

Human conversation is the reference, and people leave around 200 ms between turns. No pipeline in my script gets near that, so the practical target is the lowest delay that doesn't cut callers off.

**What is the biggest contributor to voice AI latency?**

It depends on the pipeline, so measure each stage. With a silence-based endpointer at its 500 ms default, the wait for silence can exceed the model's time to first token.

**What is endpointing?**

Endpointing is deciding that a speaker has finished their turn. It's done by detecting silence, by a model that reads the meaning of the words, or by both.

**Does a speech-to-speech model remove the latency problem?**

It removes the handoffs between transcription, inference and synthesis. It doesn't remove turn detection, which is why OpenAI's speech-to-speech sessions still have a turn-detection setting.

**Is time to first token the same as voice latency?**

No. Time to first token covers one stage, and the caller also waits for endpointing before it and for synthesis after it.
