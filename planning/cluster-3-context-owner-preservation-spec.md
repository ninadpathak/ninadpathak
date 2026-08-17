# Context-window owner preservation gate

Updated: 2026-08-18

This specification replaces the executable premise for
`beam-memory-benchmark` → `context-windows-vs-memory`. The consolidation audit calls the source a
measured benchmark, but the published source contains no local run or result artifact. It is a
literature-backed explanation of Lost in the Middle and RULER. Do not describe it as Ninad's
measurement.

## First-party constraint

The 2026-08-18 merge guard sees 15 source impressions at average position 12.9, but Search Console
withholds every source query. Merge-page query coverage is only 18.0%. Withheld demand is unknown,
not zero, so the target must preserve the source's complete reader job before any redirect.

`llm-context-windows-explained` is a separate hold. It owns the visible query `long context windows`
at position 5.0 on one named-human impression. Do not edit, merge, or redirect it in this batch.

## Target-only prose handoff

The writer may edit only `content/posts/context-windows-vs-memory.md` and must commit that one-file
change independently. It must:

1. Keep the owner's primary decision: context is a per-request reasoning budget; memory is
   persistent state retrieved into a later request.
2. Add an evidence-led explanation of why accepted context length is not reliable retrieval. Carry
   the Lost in the Middle positional result and RULER's configurable retrieval/reasoning tasks,
   sequence-length sweeps, and effective-context distinction. Link the primary paper and repository.
3. State that synthetic benchmark results select candidates; the deployed model, serving setup,
   document structure, and query set still require a target-corpus test.
4. Preserve the reader language behind the withheld source demand: long context windows can lose
   information in the middle, and advertised capacity is not a recall guarantee.
5. Remove unsupported first-person history and local measurements from the owner. In particular,
   delete the claimed 100-conversation/50-turn benchmark and its unattributed outcome. Do not claim
   that Ninad watched, shipped, benchmarked, or examined something without a repository revision,
   experiment artifact, issue, or other inspectable record.
6. Remove or qualify changing vendor window-size claims and universal production claims unless a
   primary source supports the exact statement. Do not invent replacement numbers, customers,
   systems, costs, latency, or experience.
7. Keep useful existing internal links. Do not add a link merely to satisfy a count; every link must
   be earned by the sentence's subject.

The writer must not edit either source, redirects, inbound links, navigation, publication status,
the queue, briefs, or campaign records. A target-only prose commit is not authorization to merge.

## Director execution gate

Only after the target-only commit passes review may the Director assemble an atomic execution that:

- marks `beam-memory-benchmark` merged without deleting it;
- repoints every active inbound body, pillar, and navigation reference to the owner;
- adds direct `/articles/` and legacy `/blog/` permanent redirects;
- leaves `llm-context-windows-explained` published and unchanged;
- passes `tools/gsc_merge_guard.py --dry-run`, claim/rule/heading checks, build, strict cluster,
  stylesheet, structure and inert-CSS gates, the full regression suite, deploy, redirect checks, and
  a human rendered-owner review.

Stop instead of redirecting if the owner loses the context-versus-memory distinction, the
lost-in-the-middle/RULER evidence, or the withheld source's full reader job.
