# Image brand pipeline

Renders article figures from Mermaid source into the ninadpathak.com image brand. [Pele](https://pele.run) lays out the diagram. `lib/plate.js` restyles Pele's SVG and composes the plate around it in headless Chromium, so text is measured with the real fonts. The rules live in [GUIDELINE.md](GUIDELINE.md).

```bash
cd tools/image-brand
npm ci                                   # pele 1.8.0, playwright-core, @fontsource fonts, subset-font
node render.mjs                          # every content/diagrams/<slug>/<id>.mmd -> static/images/diagrams/<slug>/
node render.mjs ../../content/diagrams/agent-loop-anatomy/agent-loop.mmd   # one figure
node render.mjs --check                  # exit 1 if output is stale, contrast fails AA, or a source is invalid
node render.mjs --out /tmp/preview       # render somewhere else
V1_DIR=/path/to/v1 node review.mjs http://127.0.0.1:8791   # before/after (+ v1-vs-v2) sheets against a served build
```

Chromium comes from Playwright's browser cache (`npx playwright-core install chromium` if it is missing).

| File | Job |
|---|---|
| `brand.tokens.json` | Palette (light/dark, site token mapping), contrast pairs, type roles, strokes, radii, canvas sizes |
| `lib/tokens.mjs` | Loads tokens, checks WCAG contrast, reports drift from `static/css/main.css`, emits the Pele theme CSS |
| `theme/brand.css` | Element styles for plates and Pele classes, using only `--np-*` variables |
| `lib/source.mjs` | Parses `%% @directive` metadata, enforces the component budget, prepares the `§` kicker / `~` detail grammar |
| `lib/plate.js` | In-browser brand layer: orthogonal router, components C1–C16 (GUIDELINE.md §8), plate and share-card composition |
| `render.mjs` | CLI: render, embed WOFF2 font subsets, write SVG, PNG 2x light/dark, JSON sidecar with embed markup |
| `review.mjs` | Before/after sheets in live article pages |

A source file is valid Mermaid. Directives sit in `%%` comments, which Mermaid ignores:

```mermaid
%% @fig 01
%% @kicker The four-phase agent loop
%% @alt The agent loop runs perceive, think, act, and remember ...
%% @path perceive>think>act>remember>perceive
%% @note act | Infinite loops start here. Set an explicit iteration budget and test it.
flowchart TB
  perceive["§01 Perceive
Read context
~Form the task state"]:::accent
```

Determinism: the same sources, tokens, CSS, brand layer, Pele version, fonts, and Chromium build give byte-identical files. Each SVG records a hash of those inputs, and `--check` compares it.

Build integration (proposed, not wired in yet, since `build.py` belongs to the site-fixes branch): have `build.py` or CI run `node tools/image-brand/render.mjs --check`, and keep rendered files committed so Cloudflare Pages needs no Node or Chromium.
