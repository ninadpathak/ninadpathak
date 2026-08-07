# AI Memory editorial program

## Position

**AI memory is not a feature. It is a data system with quality, privacy, and operational failure modes.**

NinadPathak.com will own the vendor-neutral operating layer of agent memory. The content should help a team decide how to design, evaluate, govern, and operate memory across Mem0, Supermemory, self-built stacks, and future providers.

## What we will not chase

- Generic “what is AI memory?” pages without a real decision or artifact.
- Thin vendor-alternative pages.
- Product-declared performance claims without a reproducible workload, versions, configuration, and limitations.
- Branded vendor concepts as category-defining language.
- Demos that call retrieval “memory” without a retention, update, provenance, or failure policy.

## Site architecture

- `/articles/ai-memory/` is the category archive.
- Article URLs remain flat at `/articles/<slug>/` to protect existing URL equity and avoid taxonomy-driven migrations.
- The first pillar is **AI Memory Systems: Architecture, Evaluation, and Operations**.
- Durable hubs: **Design**, **Evaluate**, and **Operate**.

## Coverage map

### Design

- Memory data models, identity resolution, fact confidence, provenance, temporal truth, and contradiction representation.
- Memory versus RAG versus agent state, with routing rules and context budgets.
- Write policies, retrieval policies, consolidation, expiry, deletion, replay, and migration.

### Evaluate

- Acceptance-test fixtures for recall, precision, stale facts, contradictory facts, sensitive data, and wrong-but-plausible personalization.
- Benchmark protocol, latency and cost measurement, regression testing, and human-review rubrics.
- Reproducible comparisons that use the same task, dataset, configurations, versions, and boundaries.

### Operate

- Observability, audit logs, tenant isolation, PII minimization, consent, deletion, exports, poisoning, incident response, and rollback.
- Build-versus-buy, data portability, migration, and exit planning.
- Domain patterns only when each has its own data policy, acceptance set, and operational risk.

## First reusable assets

1. Memory-system acceptance-test repository.
2. Vendor-neutral memory schema template.
3. Production-readiness checklist.
4. Scenario-based cost model with disclosed assumptions.
5. Migration and exit-plan template.

## House writing system

This is a synthesis of Paul Graham’s intellectual economy and Simon Willison’s inspectable technical practice. It is not an imitation of either writer.

1. Open with a technical tension, verified result, or usable artifact.
2. Make one central claim and earn it through mechanism, evidence, trade-off, and application.
3. Use ordinary verbs and concrete nouns. Cut buzzwords, decorative metaphors, and fake contrast.
4. Keep evidence beside the claim: a source, command, test, screenshot, API response, benchmark, or clear limit.
5. Use first person only as receipt-backed provenance.
6. Explain the mechanism before prescribing an action.
7. State the competent objection when it changes the decision, then narrow the recommendation.
8. Publish narrow findings when they carry an honest scope and inspectable proof.
9. Make headings retrieval-friendly without turning the article into a keyword-shaped section dump.
10. End with a next move, a test, or an artifact. Never recap by habit.

## Default article forms

- Tested technical note
- Decision memo
- Build receipt
- Deep mechanism explainer
- Annotated field guide

## Research sources

- Paul Graham, [Good Writing](https://paulgraham.com/goodwriting.html)
- Paul Graham, [Writing, Briefly](https://paulgraham.com/writing44.html)
- Simon Willison, [What to Blog About](https://simonwillison.net/2022/Nov/6/what-to-blog-about)
- Simon Willison, [One Year of TILs](https://simonwillison.net/2021/May/2/one-year-of-tils)
- [Mem0 documentation index](https://docs.mem0.ai/llms.txt)
- [Mem0 blog](https://mem0.ai/blog)
- [Supermemory documentation index](https://supermemory.ai/docs/llms.txt)
- [Supermemory blog](https://supermemory.ai/blog)
