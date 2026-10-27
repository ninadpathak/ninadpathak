# ninadpathak.com image brand guideline

Version 3.1 · October 2026 · covers every image an article ships: diagrams, charts, share cards, screenshots, terminal receipts, and interactive visuals.

The site's stylesheet opens with *Technical Precision. No gradients. No decoration.* Images follow it. Version 3 adds a second rule: **visuals are visual.** A figure gets its intricacy from drawing: glyphs that depict the concept, layered depth, repetition, fill levels, hatching, and connectors with ports and flow marks. Words and data don't count as detail. The article carries the explanation; the figure shows the shape of the idea. A reader should get it at a glance and find more on a closer look.

Pele still lays out every diagram. The brand layer in this folder (`lib/glyphs.js`, `lib/plate.js`, `theme/brand.css`) draws the rest. If this document and `brand.tokens.json` disagree, the tokens file wins and the document gets fixed.

---

## 1. Visual over text: the rules

1. **Word budget, enforced.** A diagram carries at most **15 words**, and a share-card diagram at most **6**. The head band (figure title and number) is exempt, and so are the share card's title and byline. A word is any token with two or more letters; digits, `$`, `×`, and single letters don't count. Wrapped label lines are joined with spaces before counting, so the count doesn't depend on where a platform wraps. `render.mjs` and `--check` both fail a figure over budget.
2. **Labels are names, one to three words.** "Perceive", "KV cache", "Outside reader?". Never a sentence, a description, a payload, or a parenthetical.
3. **Draw the concept, don't write it.** Before adding a word, look for a glyph (§7) that shows it: a lock instead of "private", a globe instead of "public", a check or cross instead of "yes" or "no", filling cells instead of "context grows".
4. **Numbers only when the number is the point.** In a benchmark or price chart, encode values as length, count, or fill (tile bars, §8 M12), and label at most two key values plus one ratio. Everywhere else, numbers stay in the article.
5. **Text moves to three places:** the article prose, the HTML `<figcaption>` (one or two sentences), and `@alt` (a full description of what the figure shows). None of them count against the budget, and all of them stay readable by search engines and screen readers.
6. **One accent idea.** Accent marks the path, node, or part the figure is about, and nothing else.
7. **Glanceable first, rewarding second.** At thumbnail size the silhouette should tell the story: a ring for a loop, a stack of slabs for a stack, a fork for a decision. Up close, the glyphs, hatching, ticks, ports, and particles reward a second look. If the thumbnail doesn't read, simplify the structure. Don't add words.

## 2. Image types and archetypes

| Archetype | Mermaid | Visual kit | Sample |
|---|---|---|---|
| Decision tree | `flowchart TB` | Glyph tiles with short questions; ✓/✕ marks on the branches; symmetric buses; hot path with particles; badge-labelled span brackets under outcome groups | `internal-vs-external-docs/documentation-placement` |
| Anatomy | `flowchart TB` | Muted "before" tile → focal heading; coloured brackets under each phrase; bare glyphs for the parts | `documentation-headings/task-heading-anatomy` |
| Loop | `flowchart` + `@ring` | Circular track with tick rail, accent arcs, chevrons, particles, and numbered stations; a centre glyph for the state that accumulates; entry and exit tiles radially outside | `agent-loop-anatomy/agent-loop` |
| Architecture | `flowchart TB` + cluster | Glyph tiles per component; hatched `external` tiles; stacked `stack` tiles; one-word cluster label; hot path with steps and particles | `agent-harnesses/harness-layers` |
| Stack | `block-beta` | Layer slabs, each carrying a wide strip glyph that pictures its mechanism; numbered squares for order | `llm-inference-optimization/inference-stack` |
| Benchmark | `xychart-beta horizontal` | Tile bars (one tile per unit), solid versus hatched series, two value callouts, one ratio bracket | `llm-token-budgets/token-pricing` |
| Share card | `@kind og` | Title column plus a word-free glyph chain at 1.5× or larger | `agent-harnesses/og` |

Evidence screenshots and terminal receipts follow §12. Interactive visuals follow §13.

## 3. Palette

The colors are the site tokens from `static/css/main.css`, and `--check` reports zero drift.

| Token | Light | Dark | Visual role |
|---|---|---|---|
| `canvas` | `#f8f8f6` | `#090909` | Plate, masks, empty memory cells |
| `surface` | `#ffffff` | `#111111` | Tiles, glyph bodies, slabs |
| `surface-2` | `#efefed` | `#1a1a1a` | Shaded faces (isometric sides), causal cells, outcomes |
| `hairline` | `#e0e0dc` | `#1e1e1e` | Band separators, chart grid |
| `rule` | `#c8c8c4` | `#2c2c2c` | Tile borders, hatching, tick rails, text lines inside pages, grid dots |
| `line` | `#7d7d79` | `#6f6f6f` | Glyph outlines, connectors, filled cells and tiles (≥3:1) |
| `ink` / `ink-2` | `#0e0e0e` / `#3a3a3a` | `#f0f0f0` / `#c2c2c2` | Labels / glyph detail strokes, dimension lines |
| `muted` | `#6b6b6b` | `#8a8a8a` | Decorative digits, chart ticks, series key |
| `accent` | `#c23b00` | `#ff5f1f` | The one idea: hot path, particles, step squares, the newest cell, the focal glyph part |
| `accent-wash` | `#fdf1ec` | `#1a0d07` | The focal tile |
| `on-accent` | `#ffffff` | `#090909` | Digits on step squares |

All 46 contrast pairs pass in both schemes: ink ≥15.27, ink-2 ≥9.77, muted ≥4.63, accent text ≥4.84, on-accent ≥5.36, and connectors ≥3.76 against 3.0. Hatching, dots, rails, and ticks are texture; they carry no contrast requirement and can carry no meaning on their own.

## 4. Typography

There is less text, but the same faces: **Inter** for labels, **JetBrains Mono** for the head band, chart ticks, step digits, and the series key.

| Role | Family | Size / weight | Color |
|---|---|---|---|
| Head kicker `// TITLE` (exempt) | Mono caps | 11 / 500, tracking 0.12em | accent |
| Glyph label | Inter | 13 / 500 | ink |
| Slab label | Inter | 13 / 600 | ink |
| Plain node label | Inter | 14 / 500 | ink |
| Cluster label (one word) | Mono caps | 9.5 / 600, tracking 0.12em | muted |
| Chart category | Inter | 12.5 / 500 | ink |
| Chart tick, decorative digit | Mono | 9.5 / 500, 8.5 / 500 | muted |
| Value callout, ratio | Mono | 10 / 600 | ink / accent |
| Step digit | Mono | 9 / 600 | on-accent |
| OG title (exempt) | Inter | 54 / 600, −0.025em | ink |

Floors: Inter 12 px and mono 8.5 px **at display size**, measured on the page by `sweep.mjs` at 320, 375, and 1366 px. Article plates are drawn 1:1 (`minScale` 1), because a scaled plate puts its strokes off-token. A figure that doesn't fit changes layout, or gets a narrow variant (§14a). Share-card diagrams render at **1.5× or larger**, with non-scaling strokes, and carry no words.

## 5. Canvas

```
┌──────────────────────────────────────────────────────────────────────┐ frame: rule 1px, r4
│ // FIGURE TITLE                                              FIG. 01 │ head band 44 (exempt)
├──┬───────────┬───────────┬───────────┬───────────┬───────────┬───────┤ ruled strip 12, 80 px cells
│  │┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┤ ruler 8/40
│  │ ⌜ · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·  ⌝  │ field: 16 px dots, crops
│  │   · · ┌──────┐ ●──1──•••──▶□ ┌──────┐ · · · · · · · · · ·       │ diagram centred, pad 32
│  │   · · │ ▣▣▣  │               │ ◇◇◇  │ · · · · · · · · · ·       │
│  │   · · └──────┘               └──────┘                            │
│  │     ·  Label                  Label  · · · · · · · · · · ·    ⌟  │
├──┴───────────────────────────────────────────────────────────────────┤
│ ▬▭▬▭▬▭▬▭                                                         ⊕  │ foot 26: scale bar, registration mark
└──────────────────────────────────────────────────────────────────────┘
```

There are no text bands. v2's notes band, panels band, and title block are gone. Article plates are 720 wide, share cards 1200 × 630. Flowchart spacing is `nodeSpacing 28`, `rankSpacing 64`; override it per figure with `@spacing node,rank`.

## 6. Strokes, radii, depth

| Element | Rule |
|---|---|
| Glyph outline | 1.25 px `line`, round joins; detail strokes 1.25 px `ink-2`; emphasis 1.75 px |
| Tile | 1 px `rule`, radius 4, 9 px padding around the glyph |
| Connector / hot connector | 1.25 px `line` / 1.75 px accent, 4 px corner radius |
| Ring rails / arcs | 1 px `rule` ±9 px from the radius / 2 px accent |
| Hatching | 1 px `rule` at 45°, 5 px pitch |
| Depth | Isometric slabs (top face surface, left face surface-2, right face hatched), stacked offset outlines (3 and 6 px), and hatch for "outside". No shadows, gradients, blur, or opacity stacks |

## 6a. Token audit (enforced)

After composing a figure, `npAudit` (in `lib/plate.js`) measures every drawn mark after all transforms. A figure fails `render.mjs` and `--check` if any of these is off-token:

| Measured | Allowed |
|---|---|
| Stroke width | 0.75, 1, 1.25, 1.5, 1.75, 2 px |
| Rect corner radius | 0, 1, 2, 4 px (glyph corners snap: ≤1.5 → 1, ≤3 → 2) |
| Text size | Inter ≥12 px, JetBrains Mono ≥8.5 px |

One border width per element type: every tile, slab, frame, and panel is 1 px, including accent and focal tiles, which change color but not weight. The share card's diagram scales 1.5× or more, so its strokes use `vector-effect: non-scaling-stroke` and stay on token. A deviation is a bug in the pipeline, not a per-figure choice.

## 7. Glyph library

Each glyph lives in `lib/glyphs.js`, draws on a 56 × 48 box (strips: 360 × 46), and uses at most one accent part. The accent part switches on when the node is `accent` or `focal`, or when the glyph gets the `accent` option. **Use when** is a rule: a glyph means one thing everywhere.

| Glyph | Drawing | Use when the node is… | Options |
|---|---|---|---|
| `doc` | Page with folded corner, heading bar, text lines | A document, page, or artifact | badge: `lock` private, `globe` public, `question` undecided, `check`, `cross`, `flag` |
| `pair` | Private page behind a public page | Two documents with one contract | — |
| `reader` | Head and shoulders | A person or audience | badge as above |
| `window` | App window with title rule, sidebar, content lines | An application or caller | — |
| `loop` | 300° track with chevron, particles, hub | A control loop or scheduler | — |
| `tokens` | Rows of tiles: solid, hatched, outline, newest in accent | A prompt or token stream | `rows=a,b,c` |
| `context` | Token rows inside a bracketed window; the newest tokens spill past the right bracket | A context window filling up (92 px wide tile) | `rows=a,b,c`, `inside=n` (window width in tokens, default 7; set `w` to match) |
| `vectors` | Axes with three embeddings; the nearest pair in accent | Embeddings, vector search, similarity | — |
| `wave` | Waveform bars, newest syllable in accent | Voice input or audio | — |
| `cells` | Memory grid filled to a level, newest cell accent | State, memory, or cache, where the fill level means fullness | `fill=0–1`, `flag` (checkpoint) |
| `eye` | Eye over a log trace | Observation, monitoring, logging | — |
| `core` | Three isometric slabs with weight lines | A model | — |
| `tools` | Four tiles: search, terminal, braces, database | A set of tools or integrations | — |
| `rack` | Three server units with vents and status lights | A serving engine, service, or host | — |
| `chip` | Package, pins, hatched die | A processor or accelerator | — |
| `inbox` | Tray with work dropping in | An incoming task or request | — |
| `stop` | Octagon with bar | Termination or a stop condition | — |
| `action`, `object`, `key` | Play head / isometric cube / key | Parts of a phrase: verb, noun, condition | — |
| `outline` | Page of heading bars | A heading outline or table of contents | — |
| `queue` *(strip)* | Request lanes; a finished slot refilled in accent | Batching or scheduling | — |
| `sram` *(strip)* | Causal score matrix, one tile in flight to an on-chip block | Tiled computation or streaming through fast memory | — |
| `paged` *(strip)* | Logical sequences wired to scattered physical blocks | Paging, allocation, or fragmentation | — |
| `quant` *(strip)* | One weight at 16, 8, and 4 bits, with the freed width bracketed | Precision or compression | — |
| `gpu` *(strip)* | Chip, memory stacks, interconnect to a second chip | Hardware and memory bandwidth | — |
| `plug` | Plug meeting a socket | A connector, client, router, or merge point | — |
| `ranked` | Rows shortening with rank, one in accent | A ranked result list | `rows=n`, `hi=i` |
| `globe` | Meridians and parallels | The network or the public web | — |
| `store` | Three stacked cylinder discs | Durable storage | — |
| `experts` | Grid of cells with a few lit | Sparse selection (`on` of `n`) | `n`, `on`, `cols`, `s` (cell size, default 3.6) |
| `attention` | Causal score grid: sink column, local diagonal band, heavy-hitter columns | Attention scores or KV-cache retention | `part=sink`, `local`, `heavy` |
| `ledger` | Rows newest-first, superseded rows hatched | Versioned, append-only records | `rows=n` |
| `sliding` *(strip)* | Turns in a row under a window bracket; old turns fall away, the newest is accent | A sliding context window | — |
| `budget` *(strip)* | Per-turn bars of system, replayed history, message, answer | Cost that compounds per turn | — |

A new glyph is added to `glyphs.js` and to this table in the same change. Never improvise a one-off drawing inside a figure.

## 8. Motifs

| # | Motif | Use when |
|---|---|---|
| M1 | Glyph tile: surface tile, glyph, label below | The default node |
| M2 | Bare glyph: no tile | Parts of something drawn elsewhere (anatomy parts) |
| M3 | Layer slab: full-width slab, label column, strip glyph | Each layer of a stack |
| M4 | Cluster: dashed boundary, 35% wash, accent tick, one-word label | A real boundary (process, runtime, trust zone) |
| M5 | Orthogonal router: side ports, symmetric shared buses | Always, for flowcharts |
| M6 | Ports and handles: ring out, square in | Always |
| M7 | Flow particles: three shrinking accent dots trailing toward the head | The hot path only |
| M8 | Edge marks: ✓ / ✕ in a ring for yes/no; otherwise one to three words | Decisions; avoid edge words elsewhere |
| M9 | Step squares: numbered accent squares | When order matters (`@path`, `@step`) |
| M10 | Ring: tick rail, accent arcs, chevrons, particles, stations, centre glyph | Any cycle (`@ring a>b>c>d`, `@center glyph`) |
| M11 | Parts brackets: coloured brackets under phrases, edges start from them | Taking apart a label (`@parts`) |
| M12 | Tile bars: one tile per unit, solid versus hatched series, ≤2 callouts, one ratio | Benchmarks and prices (`@callout s:i`, `@ratio i`) |
| M13 | Span bracket: dimension line labelled by a badge glyph (`:lock`, `:globe`); a word label on a vertical span runs along the line, reading upward | Grouping outcomes or layers without words |
| M14 | Drafting field: dot grid, ruled strips, ruler, crop marks, foot scale bar, registration mark | Always; texture only |
| M15 | Corner badge (`corner=person`, `cross`, `flag`, …): a badge pinned to any tile's top-right | Ownership (person = a human's stage) or status (cross = failure point) |
| M16 | Glyph key (`@key solid=…; hatch=…; outline=…; accent=…`): swatches naming fill encodings, wrapping on narrow plates | Any figure whose fills encode categories |

Budget per figure: one hot path, at most two span brackets, at most two value callouts and one ratio, and one centre glyph.

## 9. Removed in v3

`@note`, `@detail`, `@table`, `@row`, `@bar`, `@timeline`, and `@index` are gone, along with the title block, grid-coordinate letters, payload chips, kicker grammar, and the notes and panel bands. The parser rejects them with a message pointing here. Their content belongs in the article.

## 10. Composition

- Pick the archetype (§2) first, then glyphs (§7), then motifs (§8).
- Every visual encoding must be readable without a legend, except chart series, which get a two-word key.
- If the figure needs more than 15 words, it's two figures, or the extra words belong in the prose.
- Check both PNGs at 100% for crossings, collisions, and connectors that stop short of their glyph.

## 11. Share cards

1200 × 630, light, with a 4 px accent rule along the top. Left: the category kicker, the published title, a hairline, the byline, and the URL; all of it is exempt. The title steps down 54 → 48 → 42 → 38 px until it fits in four lines. Right: a drafting panel with a **word-free** chain of two or three glyph tiles at 1.5× or larger. Never shrink the article's full diagram into the card.

Chains live in `og-cards.json`, one entry per slug, read top to bottom, with `*` marking the focal glyph. Pick glyphs by the article's subject using §7, and always the same glyph for the same concept. `node og.mjs` writes `content/diagrams/<slug>/og.mmd` from the map. The source holds only the glyph chain; `render.mjs` reads the title, category, and URL from the post when it renders, so publishing or retitling a post never edits a hashed file. Posts on unmerged branches go under `$pending` with their title and category, so their cards are rendered and committed before they land. A published post without a card is a **warning**, never a failure; it keeps the site's default image until a card is added. A hand-written `og.mmd` (without the GENERATED marker) is left alone. Frontmatter `og_image` overrides the card; a relative path is prefixed with the site URL, an absolute URL is used as-is, and only the generated card declares 1200 × 630. The build points `og:image` and `twitter:image` at `static/images/diagrams/<slug>/og.png` (`summary_large_image`) unless the post's frontmatter sets `og_image`. Review every card on `review/image-brand/batch1/og-contact-sheet.png` (`node contact.mjs`).

## 12. Screenshots and receipts

**Evidence screenshots.** Capture at 1440 wide in the light scheme and crop to the proving element. Mark it with one accent rectangle (2 px, r4, 8 px outside the element) and redact with a solid surface-2 block. Never use device frames, shadows, or blur. The source and capture date go in the caption, not in the image.

**Terminal receipts** (template in the rollout). Real output only, on a dark canvas in both schemes, in JetBrains Mono 13/1.6, with the cited line in accent. Trim to the lines the article cites; the receipt counts against the word budget like any figure.

## 13. Interactive visuals

Keep one only when interaction teaches something a drawing can't, such as dragging a vector or scrubbing a slider. Those that stay use the same glyphs, strokes, palette, and word budget, load the site fonts, respect `prefers-reduced-motion`, and get a static plate fallback. Everything else becomes a plate. Plates may later move inline into the page with CSS-only motion (pending decision; see `INVENTORY.md`).

## 14. Accessibility

- `@alt` is required and full. It states every path, part, and value the figure shows, because the image no longer spells them out.
- `@caption` carries the takeaway.
- Never encode with color alone: hot paths are also thicker and carry particles and steps; badges differ by shape (lock versus globe); series differ by fill versus hatch.
- Contrast is checked on every render.

## 14a. Embedding and narrow variants

```html
<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/<slug>/<id>.svg"><picture>
    <source media="(max-width: 712px)" srcset="…/<id>.narrow.svg" width="288" height="…">
    <img src="…/<id>.svg" width="720" height="…" alt="…" loading="lazy" decoding="async">
  </picture></a>
  <figcaption>…</figcaption>
</figure>
```

Copy the markup from the figure's `.json`; the `<picture>` appears only when a narrow variant exists. `static/css/figures.css` loads only on pages with an `.np-figure` (the build sets `has_figure`). The link opens the full-size SVG.

**Derived phone variants.** Every article figure gets a phone variant. A hand-written `<id>.narrow.mmd` wins. Otherwise `render.mjs` derives one: 288 px wide, left-to-right flows turned top-to-bottom, block diagrams collapsed to one column with strips under their labels, and rings laid out as a column. A derived variant that doesn't fit at 1:1 is skipped with a warning, and the figure then needs a hand-written one.

**Narrow variant.** Phones and small tablets (≤712 px, where the wide plate's labels would drop below 12 px) get the variant, capped at 360 px (1.25×) and centred, so a tablet never stretches it. A 720 px plate shown at a phone's ~272 px column renders 13 px labels at about 5 px. So any figure whose labels would fall below the §4 floor on a phone needs `<id>.narrow.mmd` beside it, with `@width 288`. Narrow plates drop the ruled coordinate strips and keep 8 px field padding, which leaves 272 px for the diagram at 1:1. That shows labels at ≥12 px on a 320 px screen. Re-flow the figure, don't shrink it: stack subtrees, wrap headings onto two lines, and use the same glyphs and the same word budget. When a straight connector would cross another node, the router detours it past the obstacle.

## 15. Files

```
content/diagrams/<article-slug>/<figure-id>.mmd
static/images/diagrams/<article-slug>/<figure-id>.svg | .light.png | .dark.png | .json
static/images/diagrams/<article-slug>/og.svg | og.png
```

The SVG header holds a hash of the source and the whole pipeline: `render.mjs`, every `lib/` module, the theme, the tokens, and `package-lock.json`, which pins Pele, the fonts, subset-font, and playwright-core (and so the Chromium build). `--check` re-renders every figure and fails when:

- the hash is stale;
- a sibling output is missing (`.light.png`, `.dark.png`, `.json`, `og.png`);
- the committed SVG or JSON differs from the fresh render (numbers may differ by up to 0.5 px, so a different Chromium build's text metrics don't fail CI);
- a contrast pair, a stroke, radius, or text token, or the word budget fails.

A share card whose post was retitled or recategorized only warns: the card keeps the old title and kicker until someone re-renders. Output is byte-identical across re-renders on one machine.

## 16. Directive reference

| Directive | Meaning |
|---|---|
| `@alt`, `@caption`, `@kicker`, `@fig` | Description, takeaway, head title, figure number |
| `@glyph id \| name [options]` | Draw node `id` as a glyph (`bare` for M2; strips become slabs) |
| `@path a>b>c` | Hot path with particles and steps |
| `@ring a>b>c>d \| radius` | Lay those nodes on a ring (M10) |
| `@center glyph [options] label=Word` | Glyph at the ring's hub, with an optional one-word label |
| `@parts id \| phrase>node; …` | Parts brackets (M11) |
| `@step id \| n` | Pin a numbered square to a node or slab |
| `@dim a \| b \| :badge` | Span bracket (M13); text labels allowed but counted |
| `@series A; B`, `@unit $`, `@callout s:i`, `@ratio i` | Tile-bar charts (M12). `@unit %` follows the number; other units lead it |
| `@tile n` | One bar tile per `n` axis units, for values in the hundreds (default 1) |
| `@spacing node,rank` | Flowchart spacing override |
| `@kind og`, `@og-title`, `@og-kicker`, `@og-url` | Share card |

## 17. Do and don't

| Do | Don't |
|---|---|
| A lock badge on a page | The word "Private" in a box |
| ✓ / ✕ marks on branches | `YES` / `NO` labels |
| Memory cells filling up | "Context exhaustion: untrimmed tool outputs" |
| A ring with arcs and stations | A timeline panel listing the steps again |
| Tile bars with two callouts and a ratio | A chart plus a table of every value |
| One-word cluster label ("Harness") | Cluster label plus meta ("Agent harness · Runtime") |
| A word-free glyph chain on the share card | A shrunken copy of the article diagram |
| Specifics in the article and alt text | Detail panels, notes bands, title blocks |
| A new glyph added to the library and this table | A one-off doodle inside one figure |
| Fewer, larger, better-drawn elements | More boxes to look "intricate" |

## 18. Checklist

- [ ] `node tools/image-brand/render.mjs` is clean, and the words count is within budget.
- [ ] `--check` passes.
- [ ] The thumbnail silhouette reads; a close look rewards with detail.
- [ ] Every glyph is used for the meaning in §7.
- [ ] Alt text covers everything the figure shows; the caption carries the takeaway.
- [ ] Both PNGs checked at 100%.
