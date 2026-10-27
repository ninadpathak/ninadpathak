# Group C review

16 iframes replaced by plates across 12 articles (see `tools/image-brand/IFRAME-TRIAGE.md`, group C). Every target post was still published on `origin/main` and still embedded its iframe, so nothing was skipped. This branch stacks on group B (`image-brand-groupB`).

- `<slug>[@n].before-after.{light,dark}.png`: the live iframe on main next to the plate on this branch, at 1366 px. `@n` is the article's nth figure, counting from 0, when the article has more than one.
- `<slug>[@n].sweep.png` + `sweep.json`: each figure at 320, 375, 768, 1024, and 1366 px, in light and dark. 160/160 pass:
  - no page overflow, and every image loads and fits;
  - the smallest label shows at 12.1 px and the smallest mono text at 8.9 px;
  - the largest stretch is 1.14×.

Numbers the articles don't state stay out of the plates:

- the 8,400 → 2,100 token animation (memory-compression);
- the 90% and 59% reliability readout (multi-agent-vs-single-agent);
- the fixed eval thresholds (rag-evaluation);
- the ~50/250/300 ms bars (rag-reranking).

The latency plate uses only the prose's "milliseconds" and "hundreds of ms".

The kv-cache-eviction article embedded a uv package-cache animation under its attention-sink heading. Its plate shows what that section says instead: StreamingLLM keeps the sinks and recent tokens, and H2O keeps the heavy hitters.

rag-reranking's existing two-stage figure is renumbered FIG. 03, because the new bi-encoder and cross-encoder figures come before it in the article.

Pipeline changes in this batch, all re-rendered and covered by `render.mjs --check`:

- A new `attention` glyph: a causal score grid with a sink column, a local diagonal band, and heavy-hitter columns. `part=sink|local|heavy` lights one part. It is listed in GUIDELINE.md §7.
- A span over a single node (`@dim a | a`) now runs across the flow: under the node in a left-to-right figure, beside it in a top-to-bottom one. No earlier figure used a single-node span.
