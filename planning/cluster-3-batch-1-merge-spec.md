# Cluster 3, batch 1: memory core — merge specification

**Date:** 2026-08-17 · **Audit:** `planning/cluster-3-consolidation-audit.md`
**Status: prepared, not committed.** The prose is Codex's and the merge cannot ship without it.

Batch 1 first because it carries the most inbound links and the most impressions in the cluster.
That is where a mistake is most expensive and where the gates should be exercised earliest.

## Why this is not committed yet

A merge is four things: retire the source, redirect it, retrofit its inbound links, and **carry
the surviving ideas into the target.** The first three are mechanical and done below. The fourth is
prose.

Retiring a source before its ideas land in the target is precisely a deletion wearing a redirect,
which is the failure this audit exists to prevent. The retrofit cannot be split out either: it
orphans the source the moment it runs, and `--strict` is a gate. **So the batch commits as one
change, once Codex returns the carried-over text.** Queued rather than blocked on.

## Disposition change found while reading the sources

The audit assumed every source held an idea worth keeping. One does not.

**`agent-memory-for-customer-support` changes from MERGE to RETIRE, nothing carried over.**

Its "worked domain example", the thing the audit said should survive, is a fabricated case study:

> Average handle time for returning customers dropped from 18 minutes to 11 minutes, a 39%
> reduction. First-contact resolution rate went from 61% to 74%. Customer satisfaction scores for
> the agent channel improved from 3.8 to 4.3 on a 5-point scale.

Under a heading reading `Results After 90 Days`, describing "90 days of running this architecture".
That operation did not happen. It fails the 2c test at sentence level, and carrying it into
`state-of-ai-agent-memory-2026` would import invented metrics into a page that currently has none.

`tools/audit_claims.py` did **not** catch any of it. It flagged one link citation on line 19 and
none of the six fabricated figures. A scan of the whole cluster for the same pattern found this
page holds 6 of the 7 hits, so the problem is concentrated rather than systemic, but **the scanner
has a blind spot for first-person metrics** and that is worth closing separately.

Safe to retire: 0 impressions and 0 clicks lifetime, and it does not appear in
`tools/url_inventory.py` at all. It still gets a 301 as cheap insurance.

One related flag, not in this batch: `time-to-first-token-ttft` line 39 says "A support assistant I
worked on went from snappy to painful". An event claim with no measurement and no named client.
Weaker than the above, but it is a claim about something that happened. It is a KEEP page, so it
belongs in a voice-repair pass rather than here.

## The merges

All targets verified **terminal** (no target is itself a merge source) and present in the built
sitemap. One redirect chain was resolved before it reached this spec.

### 1. `state-of-open-source-memory-2026` → `state-of-ai-agent-memory-2026`

35 impressions, watch window 35, 0 clicks. 1 inbound.

**What survives:** the open-source and self-hosted vendor landscape. The target surveys the memory
stack but treats open-source options as a passing category, and the source works through named
projects with their design choices.

**Carry with care.** The source is a dated 2026 vendor survey naming Letta, Zep, Cognee and Open
Viking. Vendor surveys rot. Carry the **design distinctions** those projects illustrate, not the
project roundup, and verify any project still exists before naming it.

### 2. `memory-hierarchy-in-ai-systems` → `ai-memory-management-for-llms`

15 impressions, watch 15, alarm 5. **13 inbound, the largest retrofit in the batch.**

**What survives:** the layered model itself. The source maps Atkinson-Shiffrin onto five layers
(sensory, short-term, episodic, semantic, procedural) and argues why hierarchy beats flat memory.
The target is the largest page in the cluster at 3,182 words and manages memory without ever
laying out the layers.

### 3. `the-memory-hierarchy-why-rag-is-not-enough` → `ai-memory-management-for-llms`

13 impressions, watch 13, alarm 4. 2 inbound.

**What survives:** the argument for why RAG alone fails as memory, specifically episodic recall and
cross-session persistence. The hierarchy page states the layers; this one argues why retrieval does
not cover them.

**Note the resolved chain.** This originally pointed at `memory-hierarchy-in-ai-systems`, which is
itself merging. Both now land in `ai-memory-management-for-llms`, which means merges 2 and 3 write
into the same target and should be drafted together as one revision rather than two.

### 4. `memory-attribution-errors` → `ai-memory-management-for-llms`

4 impressions, watch 4, alarm 2. 1 inbound.

**What survives:** attribution as a named failure class, with its symptoms. Memory pointing at the
wrong user or the wrong session is a distinct failure the target does not name.

### 5. `agent-memory-for-customer-support` → `state-of-ai-agent-memory-2026`

0 impressions, 0 clicks. **RETIRE. Nothing carried over.** See above.

## The retrofit: 18 inbound links

Inside the merge commit, not after.

| Source being merged | Inbound | Notes |
|---|---:|---|
| `memory-hierarchy-in-ai-systems` | 13 | Includes one self-link from `ai-memory-management-for-llms`, which must be **unwrapped to plain text**, not repointed |
| `the-memory-hierarchy-why-rag-is-not-enough` | 2 | One is from `memory-hierarchy-in-ai-systems`, which is also merging, so it disappears with its page |
| `state-of-open-source-memory-2026` | 1 | From `voice-ai-latency-gemini-benchmark` |
| `memory-attribution-errors` | 1 | From `production-ai-agent-errors` |
| `agent-memory-for-customer-support` | 1 | Self-link from `state-of-ai-agent-memory-2026`, **unwrap** |
| **Total** | **18** | |

Two of the 18 become self-links after the merge and must be unwrapped rather than repointed. A
page linking to itself is not a link.

**One anchor-text defect to fix while there:** `the-taxonomy-of-ai-agents` links to
`memory-hierarchy-in-ai-systems` with the bare slug as anchor text. Bare-keyword anchors are
against the linking rule, so it needs real anchor text when it is repointed.

## Redirects

Four 301s, plus the legacy `/blog/` form for each, because retiring a post removes its generated
`/blog/` redirect and the legacy path still carries most post impressions. Direct to the final
target, never chained, never to a listing.

```
/articles/state-of-open-source-memory-2026/            -> /articles/state-of-ai-agent-memory-2026/
/articles/memory-hierarchy-in-ai-systems/              -> /articles/ai-memory-management-for-llms/
/articles/the-memory-hierarchy-why-rag-is-not-enough/  -> /articles/ai-memory-management-for-llms/
/articles/memory-attribution-errors/                   -> /articles/ai-memory-management-for-llms/
/articles/agent-memory-for-customer-support/           -> /articles/state-of-ai-agent-memory-2026/
```

## The prose request for Codex

Two revisions, not five, because three sources land in one target:

1. **`ai-memory-management-for-llms`** absorbs the layered model, the RAG-is-not-enough argument,
   and attribution as a failure class. Drafted as one revision.
2. **`state-of-ai-agent-memory-2026`** absorbs the open-source design distinctions only, with the
   vendor roundup left behind and any named project re-verified.

House rules apply. Nothing from `agent-memory-for-customer-support` is carried.

## Gate order for the commit

1. `.venv/bin/python build.py`
2. `.venv/bin/python tools/audit_clusters.py --strict`
3. `.venv/bin/python tools/daily_cycle.py --dry-run`
4. `.venv/bin/python -m unittest discover -s tests`

Build before audit. The audit reads `output/` and refuses to report without it.
