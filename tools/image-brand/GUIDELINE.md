# ninadpathak.com image brand guideline

Version 3 · October 2026 · covers every image an article ships: diagrams, charts, share cards, screenshots, terminal receipts, and interactive visuals.

The site's stylesheet opens with *Technical Precision. No gradients. No decoration.* Images follow it. Version 3 adds a second rule: **visuals are visual.** A figure gets its intricacy from drawing: glyphs that depict the concept, layered depth, repetition, fill levels, hatching, and connectors with ports and flow marks. Words and data don't count as detail. The article carries the explanation; the figure shows the shape of the idea. A reader should get it at a glance and find more on a closer look.

Pele still lays out every diagram. The brand layer in this folder (`lib/glyphs.js`, `lib/plate.js`, `theme/brand.css`) draws the rest. If this document and `brand.tokens.json` disagree, the tokens file wins and the document gets fixed.

---

## 1. Visual over text: the rules

1. **Word budget, enforced.** A diagram carries at most **15 words**, and a share-card diagram at most **6**. The head band (figure title and number) is exempt, and so are the share card's title and byline. A word is any token with two or more letters; digits, `$`, `×`, and single letters don't count. `render.mjs` and `--check` both fail a figure over budget.
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

Floors: Inter 12 px and mono 8.5 px at display size. Plates scale down to 87.5% at most. Share-card diagrams render at **1.5× or larger** and carry no words.

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

## 7. Glyph library

Each glyph lives in `lib/glyphs.js`, draws on a 56 × 48 box (strips: 360 × 46), and uses at most one accent part. The accent part switches on when the node is `accent` or `focal`, or when the glyph gets the `accent` option. **Use when** is a rule: a glyph means one thing everywhere.

| Glyph | Drawing | Use when the node is… | Options |
|---|---|---|---|
| `doc` | Page with folded corner, heading bar, text lines | A document, page, or artifact | badge: `lock` private, `globe` public, `question` undecided, `check`, `cross`, `flag` |
| `pair` | Private page behind a public page | Two documents with one contract | — |
| `reader` | Head and shoulders | A person or audience | badge as above |
| `window` | App window with title rule, sidebar, content lines | An application or caller | — |
| `loop` | 300° track with chevron, particles, hub | A control loop or scheduler | — |
| `tokens` | Rows of tiles: solid, hatched, outline, newest in accent | A prompt, context, or token stream | `rows=a,b,c` |
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
| M13 | Span bracket: dimension line labelled by a badge glyph (`:lock`, `:globe`) | Grouping outcomes or layers without words |
| M14 | Drafting field: dot grid, ruled strips, ruler, crop marks, foot scale bar, registration mark | Always; texture only |

Budget per figure: one hot path, at most two span brackets, at most two value callouts and one ratio, and one centre glyph.

## 9. Removed in v3

`@note`, `@detail`, `@table`, `@row`, `@bar`, `@timeline`, and `@index` are gone, along with the title block, grid-coordinate letters, payload chips, kicker grammar, and the notes and panel bands. The parser rejects them with a message pointing here. Their content belongs in the article.

## 10. Composition

- Pick the archetype (§2) first, then glyphs (§7), then motifs (§8).
- Every visual encoding must be readable without a legend, except chart series, which get a two-word key.
- If the figure needs more than 15 words, it's two figures, or the extra words belong in the prose.
- Check both PNGs at 100% for crossings, collisions, and connectors that stop short of their glyph.

## 11. Share cards

1200 × 630, light, with a 4 px accent rule along the top. Left: the category kicker, the published title (four lines at most), a hairline, the byline, and the URL; all of it is exempt. Right: a drafting panel with a **word-free** chain of two or three glyph tiles at 1.5× or larger. Never shrink the article's full diagram into the card.

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

## 15. Files

```
content/diagrams/<article-slug>/<figure-id>.mmd
static/images/diagrams/<article-slug>/<figure-id>.svg | .light.png | .dark.png | .json
static/images/diagrams/<article-slug>/og.svg | og.png
```

The SVG header holds a hash of the source, tokens, CSS, glyphs, brand layer, and Pele version. `--check` fails on stale output, broken contrast, or a figure over its word budget. Output is byte-identical across re-renders.

## 16. Directive reference

| Directive | Meaning |
|---|---|
| `@alt`, `@caption`, `@kicker`, `@fig` | Description, takeaway, head title, figure number |
| `@glyph id \| name [options]` | Draw node `id` as a glyph (`bare` for M2; strips become slabs) |
| `@path a>b>c` | Hot path with particles and steps |
| `@ring a>b>c>d \| radius` | Lay those nodes on a ring (M10) |
| `@center glyph [options] scale=k` | Glyph at the ring's hub |
| `@parts id \| phrase>node; …` | Parts brackets (M11) |
| `@step id \| n` | Pin a numbered square to a node or slab |
| `@dim a \| b \| :badge` | Span bracket (M13); text labels allowed but counted |
| `@series A; B`, `@unit $`, `@callout s:i`, `@ratio i` | Tile-bar charts (M12) |
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
