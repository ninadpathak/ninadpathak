---
category: developer-experience
primary_query: technical writing for engineers
siblings:
- stripe-technical-blog
- writing-for-ai-products
- devtools-documentation
bridges:
- slug: writing-technical-tutorials
  reason: A tutorial is the page built entirely on leading with the task.
- slug: code-documentation
  reason: That guide gives the reasoning for shipping samples that ran.
- slug: shorter-documentation
  reason: A page built around one task is short, which that essay argues for.
date: 2026-04-18
description: "Technical writing for engineers in four rules from aerospace's Simplified Technical English, a script that checks two of them, and the habits no script can check, such as leading with the task."
status: published
work_note: "Handed the docs along with everything else? You can hand them on again. I'm Ninad Pathak, a freelance technical writer, and I'll run your product before I write about it. [Let's work together](/services/)."
title: 'Technical Writing for Engineers'
slug: technical-writing-for-engineers
updated: 2026-11-17
---

Aircraft maintenance manuals are written in [Simplified Technical English](https://en.wikipedia.org/wiki/Simplified_Technical_English), a restricted English developed in the 1980s for the European airline industry. Its current edition has 53 writing rules and a dictionary of about 900 approved words.

Technical writing for engineers needs only a few of those rules, and a short program can check two of them.

Andrej Karpathy suggested a softer version on October 2, which is to ask a model for text "80% of the way to ASD-STE100", the standard's formal name. A project built on that tip, the [STE80 Humanizer](https://github.com/Dodaios/ste80-humanizer), reached Hacker News on November 9.

I think that proportion is right for [developer content](/articles/developer-experience/) as well, and this page is my version of it: four rules from the standard, a script that checks two of them, and the habits no script can check, such as leading with the task.

## What is technical writing for engineers?

Technical writing for engineers is writing that lets a reader carry out a task or make a decision without asking the author. An engineer already writes it in READMEs, pull request descriptions, design docs and runbooks, whether or not anyone calls it documentation.

The aerospace standard, in the STE80 README's words, "was made for mechanics whose first language is not English, because a misread step on an aircraft can kill."

A misread step in a deploy guide costs less. But your reader is mid-task and reading quickly, often in a second language.

## Which rules do the work?

Google's free course for engineers teaches the same four rules for sentences and paragraphs that the standard has, in its own words.

| The standard's rule, per Wikipedia's summary | What Google's course teaches |
| --- | --- |
| Keep sentences short: no more than 20 words in an instruction and 25 in a description | Give each sentence a single idea |
| Put one instruction in a sentence | Turn a long sentence into a list |
| Use the active voice | Write nearly every sentence in the active voice |
| Keep a paragraph to one topic | Focus each paragraph on a single topic |

So an aerospace committee in the 1980s and a [Google course](https://developers.google.com/tech-writing/one/short-sentences) written for software engineers arrived at the same list, which suggests the list comes from how people read instructions.

## Can a script check them?

A script of about fifty lines can check two of the four: sentence length and one instruction per sentence. The script below counts the words and the imperative verbs in each sentence, then applies the 20-word and 25-word limits and the one-instruction rule to a before-and-after passage I wrote for the purpose.

```python
"""Check a passage against two Simplified Technical English rules.

Rules, from the ASD-STE100 summary: sentence length (no more than 20 words in
an instruction and 25 in a description) and one instruction per sentence.
"""
import re

IMPERATIVES = {"run", "set", "open", "add", "install", "restart", "check", "copy",
               "delete", "create", "export", "use", "start", "stop", "wait", "confirm"}


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def instructions_in(sentence):
    """Count imperative verbs that open the sentence or follow 'and', 'then' or a comma."""
    words = re.findall(r"[a-z']+|,", sentence.lower())
    count = 0
    for i, word in enumerate(words):
        if word in IMPERATIVES and (i == 0 or words[i - 1] in {"and", "then", ","}):
            count += 1
    return count


def check(label, text):
    problems = 0
    print(label)
    for s in sentences(text):
        n = len(re.findall(r"[A-Za-z0-9'`_./-]+", s))
        steps = instructions_in(s)
        limit = 20 if steps else 25
        notes = []
        if n > limit:
            notes.append(f"{n} words, limit {limit}")
        if steps > 1:
            notes.append(f"{steps} instructions in one sentence")
        problems += len(notes)
        print(f"  {'FAIL' if notes else 'ok  '} {s[:48]:<48} {'; '.join(notes)}".rstrip())
    print(f"  problems: {problems}")


before = ("Before deploying you should make sure the environment variables that the "
          "service depends on have been exported in the shell that you are going to "
          "run the migration from. Run the migration, restart the worker and check "
          "the logs for errors.")

after = ("Export the service's environment variables in your shell. Run the migration. "
         "Restart the worker. Check the logs for errors.")

check("before", before)
check("after", after)
```

`python3 sentence_rules.py` marks each sentence.

```text
before
  FAIL Before deploying you should make sure the enviro 29 words, limit 25
  FAIL Run the migration, restart the worker and check  3 instructions in one sentence
  problems: 2
after
  ok   Export the service's environment variables in yo
  ok   Run the migration.
  ok   Restart the worker.
  ok   Check the logs for errors.
  problems: 0
```

The verb list is short and the detection is crude, so treat the script as a demonstration that the rules are mechanical. A real setup would use a prose linter such as the STE80 project's own `ste_check.py`, and the [technical writing linter](/linter/) on this site checks a draft in the browser.

And the rewrite is shorter too, 19 words against 41. Writing the first sentence as a direct instruction removed phrases such as "you should make sure" and "that you are going to".

## Why stop at 80%?

I'd stop at 80% because the rest of the standard controls vocabulary, and software has too many words of its own. The README describes full compliance as a state where "Normal prose sounds stiff", with common words restricted to one part of speech.

A dictionary of 900 words suits a fleet of aircraft maintained from one set of manuals. A codebase keeps naming new things, so the rule to carry over is the narrower one behind the dictionary: one name for one thing, used the same way every time.

## What can't a script check?

A script can't check whether the page helps. Sentence rules make text readable, and a readable page can still answer a question nobody asked.

A script can't check voice either. When I [reran the brief behind my essay skill's eleven logged drafts](/articles/eleven-rejected-essay-drafts/), a script could list one sentence pattern in a model's draft, and I had to read each run to find the narrator it had invented.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/technical-writing-for-engineers/docs-8020.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/technical-writing-for-engineers/docs-8020.narrow.svg" width="288" height="792"><img class="np-has-narrow" src="/static/images/diagrams/technical-writing-for-engineers/docs-8020.svg" width="720" height="464" alt="Practices that reach the reader are leading with the task, code that copies and runs, and a documentation update in every feature pull request. A style guide and a content calendar are drawn muted inside a cluster labelled ceremony and do not connect to the reader, because they matter only once the others are in place." loading="lazy" decoding="async"></picture></a>
  <figcaption>The practices that reach the reader are the task up front, code that runs and a docs change in the same pull request.</figcaption>
</figure>

The habits below come ahead of any style rule.

- **Lead with the task.** Open with what the reader is trying to do and the command that does it. The [guide to writing technical tutorials](/articles/writing-technical-tutorials/) builds a whole page that way.
- **Ship code that runs.** Every sample should be copied from something that executed, with its output. The reasoning is in my [code documentation guide](/articles/code-documentation/).
- **Change the docs in the same pull request.** A page updated with the code it describes is reviewed by the person who knows whether it is true.

A page that leads with one task is short, and [the case for shorter documentation](/articles/shorter-documentation/) argues for keeping it that way.

## Where does an engineer's writing get read?

An engineer's writing gets read well beyond the repository. The posts on [Stripe's engineering blog](/articles/stripe-technical-blog/) are engineer-written and are read as evidence of how the company builds.

Products built on models are harder to document, since their behaviour has to be described precisely enough to test, which is the problem [writing for AI products](/articles/writing-for-ai-products/) takes up. For a company selling to developers, [devtools documentation](/articles/devtools-documentation/) covers the pages a buyer checks before a trial.

Some engineers end up doing this work full time, the move described in [from engineer to technical writer](/articles/engineer-to-writer/).

## FAQ

**Which technical writing rules matter first?**

Start with four: short sentences, one instruction per sentence, the active voice and one topic per paragraph. The remaining rules in a full standard such as Simplified Technical English control vocabulary, which software teams can skip.

**How long should a sentence in documentation be?**

Simplified Technical English allows 20 words for an instruction and 25 for a description. Those limits are a sound default for developer docs.

**Do engineers need a style guide?**

A short style guide helps, once the team leads with the task and ships code that runs. A linter that enforces a few rules does more than a long guide nobody opens.
