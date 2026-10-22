# ninadpathak.com image brand guideline

Version 2 · October 2026 · covers every image an article ships: diagrams, charts, share cards, screenshots, terminal receipts, and interactive visuals.

The site's stylesheet opens with *Technical Precision. No gradients. No decoration.* Images follow it. A figure earns its intricacy the way an engineering drawing does. It has a coordinate grid, a title block, numbered steps, dimensioned spans, lettered detail callouts, and tables of real values. Each layer answers a question a reader would otherwise have to dig out of the prose. Glow, gradients, and illustration don't count as detail.

Version 2 adds a **component library** (§8). Each component has a fixed look, a "use when" rule, and a per-figure budget that the pipeline enforces (§9). Density comes from choosing components, so a figure stays precise as it gets richer.

The pipeline in this folder implements everything below. If this document and `brand.tokens.json` disagree, the tokens file wins and the document gets fixed.

---

## 1. Image types and archetypes

| Type | Use it for | Made with | Output |
|---|---|---|---|
| **Diagram plate** | Flows, decisions, loops, architectures, stacks, anatomies, sequences, states | Mermaid → Pele → brand layer | SVG (light and dark), PNG 2x, JSON sidecar |
| **Chart plate** | Measured numbers: prices, latencies, benchmark scores | Pele `xychart` in a plate, plus a table panel | Same as above |
| **Share card** | `og:image` and `twitter:image`, one per article | `@kind og` source with its own small diagram | PNG 1200×630 |
| **Evidence screenshot** | Proof that a third-party page says what the article claims | Browser capture under §15 | PNG, 1440 wide |
| **Terminal receipt** | Output of a command the article ran | Receipt plate (§15; template is in the rollout) | PNG 2x or SVG |
| **Interactive visual** | Only when interaction teaches something a static plate can't | `static/visuals/*.html` | HTML |

Diagram plates come in five archetypes. Each one has a default component kit, so two figures of the same archetype look like siblings:

| Archetype | Mermaid | Default kit | Sample |
|---|---|---|---|
| Decision tree | `flowchart TB` | Kicker meta `Q1…`, hot path + steps, span dims under outcome groups, detail panels on two outcomes | `internal-vs-external-docs/documentation-placement` |
| Loop or pipeline | `flowchart TB` with `ghost` rows | Hot path + steps, payload edge labels, timeline panel, detail panels on failure-prone steps | `agent-loop-anatomy/agent-loop` |
| Architecture | `flowchart TB` with a cluster | Cluster with meta, layer kickers with meta, `external` and `stack` nodes, payload label on the main call, dim spanning the system boundary, one detail | `agent-harnesses/harness-layers` |
| Stack | `block-beta` | Ordered kicker meta (`1st`, `2nd`), a dim spanning the software layers, order-of-application table, details on quantities | `llm-inference-optimization/inference-stack` |
| Comparison or benchmark | `xychart-beta horizontal` | Two series (solid and hatched), value labels, a table with the derived ratio and inline bars | `llm-token-budgets/token-pricing` |
| Anatomy | `flowchart TB` | Muted "before", focal "after", parts as outcomes, dim across the parts, a mapping table | `documentation-headings/task-heading-anatomy` |

## 2. Palette

The colors are the site tokens from `static/css/main.css`. The target palette from site-fixes (`#c23b00`, `#6b6b6b` / `#8a8a8a`) is now live, and `render.mjs --check` reports zero drift.

| Token | Light | Dark | Site token | Role |
|---|---|---|---|---|
| `canvas` | `#f8f8f6` | `#090909` | `--bg` | Plate, label masks, title block |
| `surface` | `#ffffff` | `#111111` | `--bg-1` | Nodes, panels, coordinate strips, payload chips |
| `surface-2` | `#efefed` | `#1a1a1a` | `--bg-2` | Outcome nodes, panel headers, cluster wash (35%), bar tracks |
| `hairline` | `#e0e0dc` | `#1e1e1e` | `--border` | Band and cell separators, row rules, grid lines |
| `rule` | `#c8c8c4` | `#2c2c2c` | `--border-2` | Node and panel borders, frame, cluster dashes, ruler, crop marks, hatching, grid dots |
| `line` | `#7d7d79` | `#6f6f6f` | image-only | Connectors, arrowheads, ports, handles, inline bars |
| `ink` | `#0e0e0e` | `#f0f0f0` | `--text-1` | Labels, table cells, panel titles, detail tags |
| `ink-2` | `#3a3a3a` | `#c2c2c2` | `--text-2` | Detail lines, notes, edge labels, payloads, dimension lines and labels |
| `muted` | `#6b6b6b` | `#8a8a8a` | `--text-3` | Neutral kickers and meta, coordinates, table headers, keys, title-block labels |
| `accent` | `#c23b00` | `#ff5f1f` | `--accent` | One idea: the hot path, step markers, top rules, callout rings, timeline track |
| `accent-wash` | `#fdf1ec` | `#1a0d07` | `--accent-lo` | Fill behind the single focal node |
| `on-accent` | `#ffffff` | `#090909` | `--on-accent` | Step numbers on accent (dark text in dark mode) |
| `danger` / `success` | `#b42318` / `#18794e` | `#ff8a80` / `#6ee7a7` | `--status-*` | `fail` and `pass` nodes only |

**Contrast,** checked on every run across all 46 pairs. The table shows the worst ratio for each pair across its backgrounds:

| Pair | Light | Dark | Needs |
|---|---|---|---|
| ink on canvas, surface, surface-2, accent-wash | 16.77 | 15.27 | 4.5 |
| ink-2 on canvas, surface, surface-2 | 9.88 | 9.77 | 4.5 |
| muted on canvas, surface | 5.01 | 5.47 | 4.5 |
| muted on surface-2 (outcome kickers, panel-header meta) | 4.63 | 5.04 | 4.5 |
| accent on canvas, surface, accent-wash | 4.84 | 6.21 | 4.5 |
| on-accent on accent (step numbers) | 5.36 | 6.55 | 4.5 |
| canvas on ink (detail-tag letters) | 18.15 | 17.47 | 4.5 |
| danger, success on canvas and surface | 6.18 / 5.08 | 8.27 / 12.28 | 4.5 |
| line on canvas, surface (connectors) | 3.89 | 3.76 | 3.0 |

`muted` never sits on `accent-wash`. Hatching, grid dots, the ruler, and crop marks are texture, so they carry no contrast requirement and can carry no meaning.

**Accent budget.** One hue, one idea per figure. Accent marks the hot path and its step markers, top rules on at most half the nodes, at most one focal node, and callout rings. Never type hex values into Mermaid `style` or `classDef`; that hard-codes color and breaks dark mode.

## 3. Light and dark

- Plate SVGs carry both palettes. Inside `<img>` they follow `prefers-color-scheme`. Inline, they also follow the site's `data-theme` toggle.
- Each figure also exports `<id>.light.png` and `<id>.dark.png` at 2x for feeds and email.
- Share cards are always light.

## 4. Typography

Two families: **Inter** (400, 500, 600, 700) and **JetBrains Mono** (400, 500, 600). The pipeline embeds a per-figure WOFF2 subset. Mono labels things *about* the diagram (kickers, coordinates, keys, metadata, values). Inter carries the diagram's content.

All sizes are px at the 720 px article width.

| Role | Family | Size | Weight | Tracking | Color |
|---|---|---|---|---|---|
| Head kicker `// TITLE` | Mono, caps | 11 | 500 | 0.12em | accent (the `//` at 50%) |
| Head meta `FIG. 01` | Mono, caps | 10 | 400 | 0.08em | muted |
| Node label | Inter | 14 | 500 | 0 | ink |
| Node title `**bold**` | Inter | 14 | 700 | 0 | ink |
| Node kicker `§`, kicker meta | Mono, caps | 9.5 | 600 / 500 | 0.10em | muted; accent on `accent` and `focal` |
| Node detail `~` | Inter | 12.5 | 400 | 0 | ink-2 |
| Edge label | Mono, caps | 9.5 | 600 | 0.08em | ink-2; accent when hot |
| Payload chip | Mono | 10 | 400 | 0 | ink-2 |
| Cluster label, cluster meta | Mono, caps | 9.5 / 9 | 600 / 500 | 0.12em / 0.08em | muted |
| Step and badge numbers | Mono | 9 | 600 | 0 | on-accent / accent |
| Detail-tag letter | Mono | 9 | 600 | 0 | canvas on ink |
| Dimension label | Mono, caps | 9 | 600 | 0.08em | ink-2 |
| Grid coordinates, index tags | Mono | 8.5 | 500 | 0.06em | muted |
| Panel title / panel meta | Mono, caps | 9.5 / 9 | 600 / 500 | 0.12em / 0.08em | ink / muted |
| Table header, key-value key | Mono, caps | 9 | 600 / 500 | 0.10em / 0.08em | muted |
| Table text cell, key-value value | Inter | 12.5 | 400 | 0 | ink |
| Table numeric cell, chart value | Mono, tabular | 11.5 / 9.5 | 500 | 0 | ink / ink-2 |
| Chart category | Inter | 12.5 | 500 | 0 | ink |
| Note text | Inter | 12.5 | 400 | 0 | ink-2 |
| Title-block label / value | Mono, caps | 8.5 / 10 | 500 | 0.10em / 0.04em | muted / ink-2 |
| OG title | Inter | 54 / 1.12 | 600 | −0.025em | ink |

**Floors:** Inter at 12 px and mono at 8.5 px, both at final display size. A plate may scale down to 87.5% and no further (`minScale`), so a 14 px label never drops below 12.25 px. The share-card diagram must render at **1.75× or larger**, which puts labels at 24.5 px on the 1200 px card and about 10 px when a feed shows the card 500 px wide. The pipeline fails any figure that breaks either floor. Uppercase is written into the text itself, never applied with CSS.

## 5. Canvas and plate anatomy

Everything snaps to a 4 px grid.

```
┌──────────────────────────────────────────────────────────────────────┐ frame: rule 1px, r4
│ // KICKER                                                    FIG. 01 │ head band 44
├───┬────────A────────┬────────B────────┬────────C────────┬──── … ─────┤ C3 coordinate strip 16
│ 1 │┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬ │ C2 ruler 8/40
│   │ ⌜ · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ·  ⌝ │ C1 field: 16px dots, crops
│ 2 │   · · ┌────────┐ ●─1─┐      · · · · · · · · · · · · · · ·   ┐   │ diagram centred, pad 32
│   │   · · │  node  │     └──▶□┌────────┐      · · · · · · · · ·  │   │ C11 dim gutter
│ 3 │ ⌞ · · └────────┘          │ node  A│· · · · · · · · · · ·    ┘ ⌟ │
├───┴──────────────────────────────────────────────────────────────────┤
│ ①  C3  One-line note                                                 │ C9 notes band (optional)
├──────────────────────────────────────────────────────────────────────┤
│ ┌ TIMELINE / TABLE / DETAIL A · DETAIL B ───────────────────────────┐ │ panels band (optional)
│ └──────────────────────────────────────────────────────────────────┘ │
├──────┬───────────────────────────────────────────────────────────────┤
│ KEY  │ ●─▶ PATH   ─▶ FLOW   ▭ CLASS …                                 │ C16 title block 66
├──────┴──────────────────────────────┬─────┬───────┬─────────┬────────┤
│ SOURCE slug/id.mmd                  │ FIG │ SCALE │ REV     │ DRAWN  │
└─────────────────────────────────────┴─────┴───────┴─────────┴────────┘
```

| Type | Canvas | Notes |
|---|---|---|
| Article plate | 720 × content height | 1440 px PNG. Field pad 32, coordinate strips 16, grid pitch 80 |
| Share card | 1200 × 630 | Title column x 64–584, drafting panel x 624–1160 |
| Evidence screenshot | 1440 × 900 or 1440 × 810 | Cropped to the claim |

Flowchart spacing: `nodeSpacing 28`, `rankSpacing 64`. Override per figure with Mermaid frontmatter, never with colors.

## 6. Strokes and radii

| Element | Stroke |
|---|---|
| Frame, node border, panel border | 1 px rule |
| Band, cell, and row separators | 1 px hairline (table rows dotted 1/2) |
| Top rule (accent, fail, pass) | 3 px fill, clipped to the node's top corners |
| Connector / hot connector | 1.25 px line / 1.75 px accent |
| Dashed connector (`-.->`) | 1.25 px, 3/3, meaning async or observe-only |
| Cluster boundary | 1 px rule, 4/3 dash |
| Dimension line / extension line | 1 px ink-2 / 1 px rule 2/2 |
| Detail ring | 1 px ink-2, 2/3 dash, offset 5 from the node |
| Hatching | 1 px rule at 45°, 6 px pitch |
| Ruler ticks / crop marks | 0.75 px / 1 px rule |

Radii: 4 px on the plate, nodes, panels, and corner turns of routed edges. 2 px on chips, masks, step markers, and tags.

## 7. Nodes

**Label grammar**, written in plain Mermaid:

```
id["§Kicker | Meta
Label
~Detail line"]:::class
id["`§Outcome
**Title**
~Detail line
continues as detail`"]
```

- `§Kicker | Meta`: the kicker on the left and an optional meta on the right (`Q1`, `1st`, `Durable`, `Before`), both in mono caps. A kicker never wraps. Any node with a kicker becomes a left-aligned card with 10–16 px padding.
- Label: seven words or fewer.
- `**Title**`: needs a backtick string. Use it for destinations and named parts.
- `~Detail`: every line after the first `~` is a detail line. Break long details by hand. In `block-beta`, keep each cell to three lines, because detail lines collapse the column widths.

**Classes** (names only; no `classDef`):

| Class | Look | Meaning |
|---|---|---|
| *(none)* | surface, rule border | A step or component |
| `accent` | 3 px accent top rule, accent kicker | A primary step |
| `focal` | accent-wash fill, accent border | The one node the figure is about |
| `outcome` | surface-2 fill | End state, destination, engine, part |
| `external` | canvas fill under 45° hatching | Outside the system boundary |
| `stack` | two offset outlines behind the shape | Many interchangeable instances (tools, workers, replicas) |
| `muted` | dashed border, muted label | Before, deprecated, optional |
| `fail` / `pass` | danger / success top rule and kicker | Failure or success state |
| `ghost` (clusters) | nothing drawn | Layout-only grouping, such as the two rows of a 2×2 loop |
| `hatch` (clusters) | hatched boundary zone | A trust or network boundary |

## 8. Component library

Every component is drawn by `lib/plate.js` and styled by `theme/brand.css`. The **Use when** column is a rule, not a suggestion.

| # | Component | Look | Use when | Directive |
|---|---|---|---|---|
| C1 | Drafting field | 16 px dot grid, crop marks | Always | — |
| C2 | Ruler | Ticks every 8 px, majors every 40 px, inside the coordinate strips | Always | — |
| C3 | Grid coordinates | Columns A… and rows 1…, 80 px pitch, mono 8.5 | Always. Notes, details, and the timeline cite them (`C4`) so the prose can point into the figure | — |
| C4 | Card node | Kicker, meta, label, title, detail; class treatments | Any node that needs a category or more than one line | Label grammar |
| C5 | Cluster | Dashed boundary, 35% wash, accent tick, label and meta lifted above edges on a mask | A real boundary: a process, service, trust zone, or loop | `subgraph id ["Name \| Meta"]` |
| C6 | Orthogonal router | Edges leave and enter at side centres with 4 px corner radii. Siblings leaving one side share one port and one bus (vertical buses split at 50%, horizontal at 40%), so trees come out symmetric | Always, for flowcharts | — |
| C7 | Ports and handles | 2.5 px ring where an edge leaves, 5 px square where it lands; filled accent on the hot path | Always | — |
| C8 | Edge label + payload chip | Mono caps label; `label :: payload` adds a mono chip with an example value | A label: one to three words. A payload: only when the article names the data that crosses that edge | `-->\|"call :: tool(name, args)"\|` |
| C9 | Callout | Numbered ring on the node's top-right corner; a notes band with grid ref and one sentence | A trap or consequence that fits in one line | `@note id \| text` |
| C10 | Step markers | Numbered accent squares on each hot edge in `@path` order; skipped on edges shorter than 36 px | Any figure with an order the reader must follow | `@path a>b>c` |
| C11 | Dimension line | Extension lines, a span with 45° ticks, and a caps label, in a gutter right of or below the diagram; spans that don't overlap share a row | To name what a group of nodes amounts to ("Private readers", "Four software levers") or a measured span | `@dim a \| b \| label` (`a = b` spans one node or cluster) |
| C12 | Detail tag + panel | Dashed ring and lettered ink tag on the node; a panel with the letter, title, `DETAIL A · F6`, and key/value rows | When a node hides specifics the article states: quantities, failure modes, ownership | `@detail id \| Title \| key: value; …` |
| C13 | Table panel | Mono caps header, dotted row rules, numeric columns right-aligned in tabular mono | When the article has a table or a set of comparable values the figure organizes | `@table Title \| cols…` + `@row …` |
| C14 | Mini-chart and chart | Inline bars in one table column; branded `xychart` with solid series 1, hatched series 2, value labels at bar ends | A numeric column whose shape matters; any chart plate | `@bar n`, `@series`, `@unit` |
| C15 | Timeline panel | The hot path laid flat: numbered steps, grid refs, and a dashed return hook for loops | Loops and pipelines where the order is the point | `@timeline a>b>c \| loop \| label` |
| C16 | Title block | Key row generated from the classes and edge kinds in use, then cells for source, figure number, scale, revision hash, and drawn-by | Always | `@legend k=v; …` |

## 9. Composition rules

1. **Budget per figure** (enforced): at most 2 notes, 2 dims, 2 details, 1 table (8 rows or fewer), 1 timeline, and 1 hot path. The key must fit on one row.
2. **Pick by question, not by appetite.** Use a table when the reader asks "how much?". Use a detail when they ask "what's inside that box?". Use a dim when they ask "what do these add up to?". Use a timeline when they ask "in what order?", and a note when they ask "where does this break?". If you can't name the question, don't add the component.
3. **Don't say anything twice.** If a detail panel covers a failure mode, drop the matching note (the loop sample does exactly this). Table cells must not repeat node labels word for word unless the table adds a column the nodes don't have.
4. **Every number is sourced from the article.** Payloads, quantities, and ratios must appear in the article or follow directly from its table, as with output ÷ input. Mark illustrative payloads as such in the caption.
5. **Order of the panels band:** timeline, table, details. Panels are always full width or split in exactly two.
6. **Readability gates** (enforced): scale of at least 87.5%, every note on one line, every detail value inside its panel, and every table inside its panel width.

## 10. Edges

- Arrowheads are open chevrons, 8 px long and 6.8 px wide, with the shaft running to the tip. The tip stops 3 px short of the node so the input handle stays visible.
- Bidirectional edges (`<-->`) get chevrons at both ends and no port.
- Only one hot path per figure, and the key must name it.
- Labels on a vertical drop sit centred on a canvas mask. On a short horizontal branch they sit above the line, flush with the arrow, so neither the trunk nor the head is hidden.
- No crossings. If two edges would cross, reorder the source, change direction, or add `ghost` rows. The router doesn't detect crossings, so check both PNGs.

## 11. Charts

- Horizontal bars by default; category labels in Inter 12.5 ink.
- Series 1 is solid accent; series 2 is surface with a line border and hatching. Never use a third series; split the chart instead.
- Value labels at bar ends, formatted like the article's table: two decimals below 10 unless the value is whole.
- A dashed hairline grid; the axis title in mono caps.
- Pair every chart with a table panel only when the table adds a derived column, such as output ÷ input. A chart that just repeats the table adds noise.

## 12. Callouts, details, and notes, compared

| Need | Component |
|---|---|
| One sentence about a trap at one node | C9 note |
| Three or four facts about one node | C12 detail |
| Facts across several nodes or options | C13 table |
| What a group or span adds up to | C11 dim |

## 13. Texture and depth

Layers bottom to top: canvas → drafting field (C1–C3) → clusters and hatching → edges → nodes (stack outlines, fill, top rule, text) → ports and handles → edge labels → steps → cluster labels → dims and detail rings → callout badges → bands (notes, panels, title block).

Depth comes only from hairlines, hatching, stacked outlines, and band backgrounds. Shadows, blur, gradients, and opacity stacks beyond the 35% cluster wash are not allowed.

## 14. Share cards

- 1200 × 630, light, with a 4 px accent rule along the top and a rule frame.
- Left column: kicker (`// CATEGORY`), the published title in Inter 600 54/1.12 (four lines at most, enforced), and a card title block with AUTHOR, READ (canonical URL), and REV cells.
- Right: a drafting panel with coordinates and the card's **own** three-node diagram, written in the `og.mmd` body at 1.75× or larger. The article's full diagram is never reused here, because it can't be read at feed size.
- An article without a diagram gets the text column centred on the left two-thirds (layout planned for the rollout; today a card without a body renders an empty drafting panel). Never use stock imagery.

## 15. Screenshots and receipts

**Evidence screenshots.** Capture at 1440 wide in the light scheme and crop to the proving element, keeping enough chrome to identify the source. Mark the claim with one accent rectangle: 2 px stroke, 4 px radius, 8 px outside the element. Redact with a solid surface-2 block. No device frames, shadows, or blur. The caption names the source and the capture date.

**Terminal receipts** (template planned for the rollout). Real output only. A plate with a dark canvas in both schemes, a head band showing `// COMMAND` and the run date, JetBrains Mono 13/1.6, commands in ink with a `$` prefix, output in ink-2, and the cited line in accent. A title block gives the command source and REV. No traffic-light window dots.

## 16. Interactive visuals

Keep one only when the interaction itself teaches. Rules for those that stay:

- Load the site fonts. Every visual today falls back to Courier.
- Use only `visual-embed.css` variables. 14 visuals still hard-code the old palette.
- Use the same type roles, strokes, chevrons, ports, and coordinate and title-block treatments as plates.
- No Three.js glow, fog, bloom, or auto-orbit, and respect `prefers-reduced-motion`.
- Give each one a static plate fallback rendered from Mermaid.

Everything else becomes a plate (see the rollout plan in `INVENTORY.md`).

## 17. Accessibility

- `@alt` is required. In one to three sentences, state what the figure shows, including where each path ends and any numbers it presents. It is written into `<desc>` and the `<img alt>`.
- `@caption` carries the takeaway and the sourcing note.
- Text inside a figure is limited to labels, kickers, values, and one-sentence notes. Article titles appear only on share cards.
- Never carry meaning by color alone. The hot path is thicker and numbered, classes are named in the key, and hatching means "outside" only together with the key entry.

## 18. Files

```
content/diagrams/<article-slug>/<figure-id>.mmd
static/images/diagrams/<article-slug>/<figure-id>.svg | .light.png | .dark.png | .json
static/images/diagrams/<article-slug>/og.svg | og.png
```

- The SVG header comment and the title block's REV hold a 16-character hash of the source, tokens, CSS, brand layer, and Pele version. `render.mjs --check` fails on a mismatch, so it catches stale output and AA breaks alike.
- Output is byte-identical across re-renders on the same machine.
- Size budget: SVG under 120 KB (the v2 samples are 71–104 KB, mostly embedded font subsets) and PNG under 300 KB.

## 19. Directive reference

| Directive | Meaning |
|---|---|
| `@alt`, `@kicker`, `@fig`, `@caption` | Alt text, head kicker, figure number, HTML caption |
| `@path a>b>c` | Hot path with step markers (C10) |
| `@note id \| text` | Callout (C9) |
| `@dim a \| b \| label` | Dimension line (C11) |
| `@detail id \| Title \| k: v; k: v` | Detail tag and panel (C12) |
| `@table Title \| col \| …` + `@row v \| …` + `@bar n` | Table panel and inline bars (C13, C14) |
| `@timeline a>b>c \| loop \| label` | Timeline panel (C15) |
| `@series A; B`, `@unit $` | Chart series names and value prefix (C14) |
| `@legend class=Label; …` or `off` | Key labels (C16) |
| `@index on` | Index tags above nodes |
| `@kind og`, `@og-title`, `@og-kicker`, `@og-url` | Share card |

## 20. Do and don't

| Do | Don't |
|---|---|
| Symmetric orthogonal buses with shared ports | Curved, uneven branches from one node (v1's START node) |
| Add the component that answers a reader's question | Add a component because the figure "looks empty" |
| Cite grid coordinates in notes, details, and prose | Write "the box on the right" |
| Give the OG card its own large three-node diagram | Shrink the article diagram into the card |
| Stay within the budget, or split the figure | A third note, a second table, or a second hot path |
| Source every number in the article | Invent latencies or payloads for texture |
| Draw a plate with its own frame, without `.visual-wrapper` | Double borders and doubled titles |

## 21. Checklist

- [ ] `node tools/image-brand/render.mjs` is clean and `--check` passes.
- [ ] The archetype kit (§1) is applied, and each extra component answers a named question (§9).
- [ ] Scale is 1:1, or at least 0.875 with a reason. The OG diagram is at 1.75× or more.
- [ ] No crossings, collisions, or masked arrowheads in either PNG.
- [ ] Every number traces to the article. Illustrative payloads are labelled in the caption.
- [ ] Alt text states each path's end. The caption carries the takeaway.
