# Group D review

16 iframes replaced by plates across 12 articles (see `tools/image-brand/IFRAME-TRIAGE.md`, group D). Every target post was still published on `origin/main` and still embedded its iframe, so nothing was skipped. The two kept vector-embeddings visuals are aligned to the brand. After this batch, those two are the only iframes left on the built site.

- `<slug>[@n].before-after.{light,dark}.png`: the iframe on main next to the plate on this branch, at 1366 px. `@n` is the article's nth figure, counting from 0. The rag-reranking plates are @4–@7, after the article's four existing figures. vector-embeddings@1 is the chunking plate, compared against the chunking iframe rather than the kept visuals between them.
- `<slug>[@n].sweep.png` + `sweep.json`: each figure at 320, 375, 768, 1024, and 1366 px, in light and dark. 160/160 pass:
  - no page overflow, and every image loads and fits;
  - the smallest label shows at 12.1 px and the smallest mono text at 8.9 px;
  - the largest stretch is 1.14×.
- `kept-visuals.png` + `kept-live.json`: the two kept visuals live in the built article at 375 and 1366 px, in light, dark, reduced motion, with JavaScript off, and with the iframe request blocked (light and dark). Each iframe follows the article's theme (`data-theme` read from the parent) and fits its container (400 px desktop, 500 px phone and tall) with no overflow. With the frame blocked, the container shows the static fallback in the matching theme instead of an empty box.

Numbers the articles don't state stay out of the plates:

- the 0.89 / 0.02 vector and reranker scores (keyword-exactness);
- the 96/90/84… impact weights (docs-8020, marked "illustrative" in the old visual);
- the 0.40 / 0.50 / 0.10 load ratios (cognitive-load);
- the accuracy curve in the matryoshka slider, computed as 90 + 9.8 × ratio; the article says to measure quality on your own corpus.

Design notes:

- context-fill drops the model and archive-doors drops the final "Stripe" node in both variants. A four- or three-way fan-in plus a follow-on node can't be routed cleanly at 288 px. The alt text carries what the figures leave out.
- The release-notes phone plate links Summary → Impact → Resources at the cluster, rather than to each of the four entries.
- writing-changelogs and writing-release-notes had a `visual-caption` paragraph under the iframe. That text is now the figure's caption, and the paragraph is gone.
- The matryoshka wrapper title read "// // … Dimensionality vs. Precision". It is now "Matryoshka: keep the head of the vector".

Kept visuals (`static/visuals/cosine-similarity.html`, `static/visuals/matryoshka-truncation.html`), rebuilt as branded SVG pages with no Three.js or CDN scripts:

- the site fonts (Inter, JetBrains Mono) and the plate tokens from `brand.tokens.json`, in light and dark;
- token strokes (0.75 / 1 / 1.25 / 1.5 / 2) and the type floors; phones get a tighter crop and larger SVG text;
- cosine-similarity: drag the query arrow, or use the slider, and θ and cos θ update. The marks read 1, 0, and −1. A one-time opening sweep runs only without `prefers-reduced-motion`.
- matryoshka-truncation: the slider keeps the leading dimensions. Cells shade darker toward the front, and the RAM head is sized against the full vector on disk. Nothing moves on its own.
- Both draw completely without JavaScript (cosine at 45°, matryoshka at 256 of 1536 dimensions). That static drawing is the fallback.

No shared pipeline files changed in this batch.

Review fixes (ship-with-fixes verdict), all re-rendered and re-swept (rag-reranking@5, technical-writing-for-engineers, writing-release-notes, and both vector-embeddings figures: 50/50, and the batch stays at 160/160):

- cosine-similarity: the Query label stays inside the drawing at every angle and width. Near the axis (under 30° and over 150°) it sits above the tip on the inner side. Near 90° it sits beside the tip, clear of the "cos 0" tick. Then it is clamped into the current view. Checked at 0°, 45°, 90°, 135°, and 180° in iframes 270, 325, and 670 px wide, in light and dark: always inside, with no overlap with other text.
- Kept-visual fallback: `tools/image-brand/fallbacks.mjs` lifts each page's no-JS drawing into `static/visuals/<name>.fallback-{light,dark}.svg`, with subset Inter and JetBrains Mono embedded. `fallbacks.mjs --check` fails if either visual changes without regenerating them. The article layers the fallback under the iframe (`.visual-container--fallback`, `static/css/visuals.css`). `static/js/main.js` keeps the frame transparent until its page sets `window.npVisualReady`. A blocked or failed frame (a browser error page) therefore shows the drawing. With JavaScript off, the frame shows its own static drawing, as before. The normal case is unchanged: the frame is opaque and on top.
- writing-release-notes: the Impact group adds Known issues, the article's item 6, on both widths; the alt names it.
- rag-reranking models-providers caption: "…a local model costs a GPU but no hop and no fee."
- technical-writing-for-engineers: the Ceremony cluster sits level with the three practices on the wide plate.
