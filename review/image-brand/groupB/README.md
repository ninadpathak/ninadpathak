# Group B review

16 iframes replaced by plates (see `tools/image-brand/IFRAME-TRIAGE.md`, group B) across 12 articles. The four browser-vector-search figures follow the corrected article from `f8ccc619` and carry no benchmark results.

- `<slug>[@n].before-after.{light,dark}.png`: the live iframe on main vs the plate on this branch, at 1366 px. `@n` is the article's nth figure (0-based) when it has more than one.
- `<slug>[@n].sweep.png` + `sweep.json`: each figure at 320, 375, 768, 1024, and 1366 px in light and dark. Phones (≤712 px) get the narrow variant, capped at 1.25×; tablets and up get the wide plate. 160/160 pass: no page overflow, every image loads and fits, the smallest label shows at 12.1 px and the smallest mono text at 8.9 px, and the largest stretch is 1.14×.

Pipeline changes in this batch, all re-rendered and covered by `render.mjs --check`:

- `@tile n` draws one bar tile per n units (the DORA chart is one tile per 50 points), and `@unit %` follows its number.
- Chart callouts print the source's values, not widths measured back from pixels.
- A word label on a vertical span runs along the line, so it never crosses a tile on a phone. This re-renders the live agent-taxonomy plate too.
- The `experts` glyph takes a cell size (`s`) for small grids.
- `embed.mjs` syncs article embeds from each figure's JSON, and `tests/test_image_brand.py` fails on a stale embed. It fixed the harness embed's height (912 → 936).
- `sweep.mjs` takes `slug@n` and no longer waits on third-party network idle.
