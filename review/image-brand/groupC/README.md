# Group C review

16 iframes replaced by plates across 12 articles (see `tools/image-brand/IFRAME-TRIAGE.md`, group C). Every target post was still published on `origin/main` and still embedded its iframe, so nothing was skipped. This branch stacks on group B (`image-brand-groupB`).

- `<slug>[@n].before-after.{light,dark}.png`: the live iframe on main next to the plate on this branch, at 1366 px. `@n` is the article's nth figure, counting from 0, when the article has more than one.
- `<slug>[@n].sweep.png` + `sweep.json`: each figure at 320, 375, 768, 1024, and 1366 px, in light and dark. 170/170 pass (the 16 group C figures plus group B's memory-operations, re-swept after the routing fix):
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

Review fixes (ship-with-fixes verdict), all re-rendered and re-swept:

- kv-cache-eviction: the heading is now "Attention decay: where importance concentrates", and the one pillar sentence describes a diagonal band and columns, matching the flat figure. No other prose changed. The TOC anchor follows the new heading, and nothing linked to the old one.
- The router now reads each chart's direction from its source. It had always assumed top-to-bottom, so left-to-right fan-outs routed through extra turns. They now share one bus: context-switching, output-mechanisms (wide and phone), the lost-in-the-middle phone variant, and group B's live memory-operations plate (`ai-memory-management.*`). No other plate's geometry changed.
- The lost-in-the-middle phone connectors now meet at Model's side port. Horizontal arrows end at a node's hit box in every left-to-right figure, about 18 px from a 74 px tile. Moving them to the tile edge would redraw 41 plates, so that change is left for its own batch.
- memory-compression alt: "low scorers are dropped".
- The latency caption reads "the cross-encoder is where the time goes".
