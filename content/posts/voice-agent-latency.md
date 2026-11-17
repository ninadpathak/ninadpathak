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

Radio operators solved the hardest part of voice AI latency, knowing when the other person has finished talking, with one word. On a channel where only one side can talk at a time, you end your turn by saying "over", which the [list of procedure words](https://en.wikipedia.org/wiki/Procedure_word) defines as the end of a transmission that needs a reply.

A caller on the phone with a voice agent never says "over". The agent has to guess when the caller has finished, and voice AI latency is the time from the caller's last word to the first sound the agent makes, including the time spent on that guess.

People make the same guess in conversation and make it fast. A [2015 review of turn-taking research](https://pmc.ncbi.nlm.nih.gov/articles/PMC4464110/) puts the usual pause between speakers at around 200 ms, while planning a spoken reply takes over 600 ms, so a listener must be predicting the end of the speaker's turn before the speaker reaches it.

A reply after about 200 ms is what callers are used to from other people, and a voice agent that waits for silence can't reach it. Below I've laid out the four stages of a voice agent's turn with a time budget you can rerun, as part of [AI engineering](/articles/ai-engineering/).

## What is voice AI latency?

Voice AI latency is the delay a caller hears between finishing a sentence and the agent starting to answer. The delay is the sum of four stages, and the language model accounts for one of the four:

1. **Endpointing:** deciding that the caller has stopped.
2. **Transcription:** turning the audio into text.
3. **Inference:** the model producing the first words of a reply.
4. **Synthesis:** turning those words into audio.

A speech-to-speech model, such as the one behind OpenAI's Realtime API, merges transcription, inference and synthesis into one model. Endpointing stays a separate step, because some part of the system still has to decide that the caller's turn is over.

## Where does the time go in a voice agent turn?

The largest share of a turn in the budget below goes to waiting for silence, and the model's first token takes less. The script adds up one turn under stage times I've assumed, so the numbers show the structure and aren't measurements of any service:

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

The caller in the first run waits 1,370 ms for the first audio, and the model's first token accounts for 300 ms of that wait. The 500 ms spent confirming that the caller has gone silent is the largest of the five stage costs, and the agent spends it before transcription or the model has started.

The second run changes one thing: speech synthesis starts when the first sentence of the reply is complete, without waiting for the second sentence. Starting synthesis early saves 180 ms on this two-sentence reply, and it saves more on a longer reply.

The third run cuts the silence wait from 500 ms to 200 ms, which brings the first audio down to 890 ms. A 200 ms wait also means the agent starts talking whenever a caller pauses for a fifth of a second to think.

## Why is endpointing the hard part?

Endpointing is hard because a pause doesn't tell the agent whether the caller is finished or only thinking. An agent that waits 200 ms interrupts callers in the middle of a thought, and an agent that waits 800 ms starts every reply late.

The 500 ms silence wait in my script is OpenAI's default. OpenAI's [Realtime API guide](https://developers.openai.com/api/docs/guides/realtime-vad) shows `silence_duration_ms` set to 500 for the default mode, which chunks audio on periods of silence, and that 500 ms is more than twice the 200 ms pause that people leave each other.

The alternative to waiting for silence is to predict the end of the turn from the words, the way a human listener does. OpenAI's second mode, `semantic_vad`, scores how likely it is that the speaker is done from the words so far, and waits longer on a sentence that trails off than on a definite statement.

LiveKit made the same choice for its voice agent framework. LiveKit's [turn detection docs](https://docs.livekit.io/agents/logic/turns/) make a turn detector model the default, one that "Predicts end of turn from both the meaning of speech and its acoustic properties", and keep silence-only detection for when you need minimal latency.

I think predicting the end of the turn from meaning is the right default, and I'd rank it above model speed. If I had one week to make a voice agent feel faster, I'd spend it on endpointing before touching the model.

## How do you cut the model's share?

You cut the model's share in two ways: shorten the wait for the model's first token, and hand text to the speech engine before the reply is finished. Shortening the first-token wait is ordinary [time to first token](/articles/time-to-first-token/) work, and on a phone call every 100 ms of it is silence the caller hears.

Prompt length is the part of first-token time that you control. The model has to process the whole conversation history before it produces a first token, and a cached prompt prefix lets it skip the part it has already processed, as the [KV cache](/articles/kv-cache-eviction/) page describes.

Handing text to the speech engine early carries a risk. If the agent starts speaking the first half of a sentence and the model then finishes the sentence differently, the caller has already heard the wrong half.

[Speculative decoding](/articles/speculative-decoding/) makes a similar bet inside the model, where a wrong guess can be thrown away before anyone sees it.

Tool calls also lengthen a turn. When the agent looks up an order status in the middle of a reply, the caller hears silence for as long as the lookup takes, and [voice agent memory](/articles/voice-agent-memory/) covers ways to do such lookups before the caller is waiting.

## How should you measure voice AI latency?

Measure voice AI latency by recording a timestamp at the end of each stage and reporting the stages separately, the way the script prints them. A single end-to-end number such as 1,370 ms can't tell you whether to shorten the silence wait or speed up the model.

OpenAI's and LiveKit's APIs both emit events at those stage boundaries. OpenAI's Realtime API emits `input_audio_buffer.speech_stopped` when it decides a turn has ended, and I'd start the clock for transcription, inference and synthesis at that event.

Test with recordings of real callers, who pause in the middle of sentences. A scripted test caller who speaks in complete sentences without pausing will never be interrupted by a 200 ms silence setting, and a real caller will be.

## FAQ

**What is a good latency for a voice agent?**

Human conversation sets the reference, and people leave around 200 ms between turns. The fastest run in my script takes 890 ms, so the practical target is the lowest delay at which the agent doesn't cut callers off.

**What is the biggest contributor to voice AI latency?**

The biggest contributor depends on the pipeline, so measure each stage. With a silence-based endpointer at its 500 ms default, the wait for silence can exceed the model's time to first token.

**What is endpointing?**

Endpointing is deciding that a speaker has finished their turn. An agent does it by detecting silence, by running a model that reads the meaning of the words, or by both.

**Does a speech-to-speech model remove the latency problem?**

A speech-to-speech model removes the handoffs between transcription, inference and synthesis. It doesn't remove turn detection, which is why OpenAI's speech-to-speech sessions still have a turn-detection setting.

**Is time to first token the same as voice latency?**

No. Time to first token covers the inference stage only, and the caller also waits for endpointing before inference and for synthesis after it.
