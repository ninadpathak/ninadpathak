# Framework memory owner correction

**Date:** 2026-08-18  
**Decision:** keep and independently repair both published URLs; never redirect either one to the
other.

## Why the merge is cancelled

The planned `how-memory-works-in-hyperagents` → `how-memory-works-in-deerflow` redirect joins two
different branded reader jobs. Search Console cannot validate overlap: HyperAgents has 11 complete
page impressions at position 11.2 and DeerFlow has 46 at position 22.1, while every query for both
pages is withheld. Those impressions are demand floors with unknown query text, not evidence that
the intents are interchangeable.

The primary sources contradict the consolidation premise:

- Meta's March 2026 [Hyperagents paper](https://arxiv.org/abs/2603.19461) defines self-referential
  agents that combine a task agent and a meta agent in one editable program. It reports persistent
  memory as an improvement DGM-H developed during its self-improvement process. The official
  `facebookresearch/HyperAgents` implementation was inspected at
  `59a68f672dfb92c74aeb7e61535d776fb36e172d`.
- ByteDance's [DeerFlow repository](https://github.com/bytedance/deer-flow) defines DeerFlow 2.0 as
  a super-agent harness and explicitly says it is a ground-up rewrite sharing no code with v1. Its
  current memory documentation and implementation were inspected at
  `0debff98c1caf4a7d3047e8ef162d85a841b5c6d`.

## HyperAgents owner contract

Edit only `content/posts/how-memory-works-in-hyperagents.md` and, if the existing illustration
cannot be made accurate with current reusable assets, remove its embed. Keep the URL, published
status and branded title intent.

The rewrite must:

- identify Hyperagents as the DGM-H research system, not a generic multi-agent framework;
- explain the editable task/meta program, evaluation loop and archive only to the level supported
  by the paper and official repository;
- frame persistent memory and performance tracking as capabilities that emerged in the reported
  self-improvement runs, not a universal three-tier storage API;
- distinguish paper evidence, implementation structure and editorial interpretation;
- link the paper and official repository in useful body sentences.

Remove the invented three-layer architecture, SQLite/vector-store code, context thresholds,
500-turn claim, personal-agent anecdotes, multi-agent coordination protocol, unsupported model
recommendations and every result not traceable to the primary sources.

## DeerFlow owner contract

Edit only `content/posts/how-memory-works-in-deerflow.md` and, if the existing illustration cannot
be made accurate with current reusable assets, remove its embed. Keep the URL, published status and
branded title intent.

The rewrite must:

- state that the page covers DeerFlow 2.0 and distinguish it from the separately maintained 1.x
  deep-research framework;
- explain the current runtime memory categories, controlled prompt injection, default middleware
  update path, experimental tool mode, per-user/per-agent isolation and pluggable backend boundary;
- describe file layout, retrieval or lifecycle behavior only where the pinned documentation or
  code supports it;
- link the official repository and current memory documentation in useful body sentences.

Remove the invented stage JSON/YAML, checkpoint/resume test, pgvector adapter claim, sequential
stage protocol, production incidents, latency numbers, framework scorecard and unsupported FAQ
answers. Do not turn code-shaped illustrations into claimed DeerFlow APIs.

## Shared release gates

- No redirects, source-page edits, queue/status changes or calendar rows.
- No first-person event, benchmark, customer, deployment or product-use claim without an
  inspectable repository artifact.
- No cross-link between the two pages unless a sentence has a genuine comparison need.
- Each page keeps earned body links and receives any necessary inbound retrofit in the atomic
  release commit; never link from a merged or retiring source.
- Run the changed-page claim and rule checks, heading audit, build, strict cluster/stylesheet/
  structure/inert-CSS checks, link checks, full suite and rendered-page review.
- Before release, rerun the first-party page totals. Withheld queries remain unknown and block any
  renewed cross-brand consolidation.
