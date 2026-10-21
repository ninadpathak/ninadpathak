# ninadpathak.com image brand guideline

Version 1 · October 2026 · applies to every image an article ships: diagrams, share cards, screenshots, terminal receipts, charts, and interactive visuals.

The site's stylesheet opens with one line: *Technical Precision. No gradients. No decoration.* Images follow that rule. A figure looks intricate because it holds precise detail: numbered references, typographic hierarchy inside nodes, an annotated route, drafting marks. Glow, gradients and illustration don't count as detail. Every mark has to justify itself to a reader who is trying to understand a system, and anything that doesn't gets cut.

The pipeline in this folder implements everything below. If the document and `brand.tokens.json` disagree, the tokens file wins, and the document gets fixed.

---

## 1. Image types

| Type | Use it for | Made with | Format |
|---|---|---|---|
| **Diagram plate** | Flows, decisions, architectures, loops, sequences, states, anatomies | Mermaid source → Pele → brand layer (`render.mjs`) | SVG (light/dark), PNG 2x fallbacks |
| **Share card** | `og:image` / `twitter:image` per article | `@kind og` source that reuses the article's lead diagram | PNG 1200×630 |
| **Data chart** | Measured numbers: benchmarks, costs, latencies | Pele `xychart` / `pie` / `quadrantChart` in a plate; hand-built SVG only when Pele lacks the form | SVG |
| **Evidence screenshot** | Proof that a third-party page says what the article claims | Browser capture, then the screenshot rules (§13) | PNG, 1440 px wide |
| **Terminal receipt** | Output from a command the article ran | Real output in the receipt plate (§13; template is in the rollout plan) | PNG 2x or SVG |
| **Interactive visual** | Only when interaction teaches something a static plate can't (dragging a vector, scrubbing time) | `static/visuals/*.html` iframe | HTML + `visual-embed.css` |

The default is the diagram plate. An interactive visual has to earn its iframe: if the interaction is just "it animates" or "you can orbit it", ship a plate.

## 2. Palette

Colors are the site tokens. Accent `#c23b00` and the muted text values are the target palette from the pending site-fixes change, chosen to pass WCAG AA. `node render.mjs --check` warns whenever `main.css` differs.

| Token | Light | Dark | Site token | Role |
|---|---|---|---|---|
| `canvas` | `#f8f8f6` | `#090909` | `--bg` | Plate background; sits flush with the page |
| `surface` | `#ffffff` | `#111111` | `--bg-1` | Node fill, callout fill, OG diagram panel |
| `surface-2` | `#efefed` | `#1a1a1a` | `--bg-2` | Outcome nodes, cluster wash (35%), swatches |
| `hairline` | `#e0e0dc` | `#1e1e1e` | `--border` | Plate frame, band separators |
| `rule` | `#c8c8c4` | `#2c2c2c` | `--border-2` | Node borders, cluster dashes, ruler ticks, crop marks, grid dots |
| `line` | `#7d7d79` | `#6f6f6f` | image-only | Connectors and arrowheads (≥3:1, WCAG 1.4.11) |
| `ink` | `#0e0e0e` | `#f0f0f0` | `--text-1` | Node labels, OG title |
| `ink-2` | `#3a3a3a` | `#c2c2c2` | `--text-2` | Detail lines, note text, neutral edge labels |
| `muted` | `#6b6b6b` | `#8a8a8a` | `--text-3` | Neutral kickers, index tags, legend, footer meta |
| `accent` | `#c23b00` | `#ff5f1f` | `--accent` | Header kicker, primary route, top rules, callout badges |
| `accent-wash` | `#fdf1ec` | `#1a0d07` | `--accent-lo` | Fill behind the one focal node |
| `on-accent` | `#ffffff` | `#090909` | `--on-accent` | Text on solid accent (dark mode uses dark text) |
| `danger` | `#b42318` | `#ff8a80` | `--status-error` | Failure nodes and edges |
| `success` | `#18794e` | `#6ee7a7` | `--status-success` | Pass nodes and edges |

**Why `line` is its own token.** Connectors carry meaning, so WCAG 1.4.11 asks for 3:1 against their background. The site's `--border-2` reaches 1.6:1, which suits card edges but not arrows. `line` sits between `rule` and `muted`.

**Contrast, as checked by `render.mjs` on every run** (minimum ratio across the backgrounds each pair is used on):

| Pair | Light | Dark | Needs |
|---|---|---|---|
| ink on canvas / surface / surface-2 / accent-wash | 16.77 | 15.27 | 4.5 |
| ink-2 on canvas / surface / surface-2 | 9.88 | 9.77 | 4.5 |
| muted on canvas / surface / surface-2 | 4.63 | 5.04 | 4.5 |
| accent on canvas / surface / accent-wash | 4.84 | 6.21 | 4.5 |
| on-accent on accent | 5.36 | 6.55 | 4.5 |
| danger on canvas / surface | 6.18 | 8.27 | 4.5 |
| success on canvas / surface | 5.08 | 12.28 | 4.5 |
| line on canvas / surface | 3.89 | 3.76 | 3.0 |

A run fails if any pair drops below its minimum. Muted text stays off `surface-2` in light mode apart from kickers (4.63:1, a narrow pass), and it never goes on `accent-wash`.

**Accent budget.** One accent hue per image. Accent marks exactly one idea: the route the article is about, or the node it is about. In practice that means at most one focal node, at most one hot path, and top rules on at most half the nodes. If everything is orange, nothing is. `danger` and `success` appear only when the figure is about failing or passing.

**Never:** gradients, drop shadows, glows, blurs, transparency stacks beyond the 35% cluster wash, brand colors from other companies (except inside evidence screenshots), or hex values typed into Mermaid `style` / `classDef` lines. Inline Mermaid styles are fixed colors and break dark mode.

## 3. Light and dark

- A plate SVG carries both palettes. `<img>` embeds follow the reader's OS through `prefers-color-scheme`, the same convention as the iframes (`build.py: build_visual_embed_css`). Inline SVG also honors the site toggle: `[data-theme="dark"] .np-plate` and `[data-theme="light"] .np-plate` override the media query.
- The pipeline exports `<id>.light.png` and `<id>.dark.png` at 2x for RSS, email, and anywhere SVG is stripped.
- Share cards always use light. Social feeds pick their own chrome, and one fixed card is easier to recognize.
- Never bake a scheme into a diagram. The old `task-heading-anatomy.svg` hard-codes light colors and renders as a white slab in dark mode (see `review/image-brand/2-anatomy.dark.png`).

## 4. Typography

Two families, both already loaded by the site: **Inter** (400, 500, 600, 700) and **JetBrains Mono** (400, 500, 600). The pipeline embeds a per-figure subset of each face as WOFF2, so an SVG renders identically inside `<img>`, where page fonts can't reach it. Mono is for labels about the diagram. Sans is for the content of the diagram.

Sizes are display pixels at the 720 px article width.

| Role | Family | Size | Weight | Tracking | Case | Color |
|---|---|---|---|---|---|---|
| Header kicker (`// TITLE`) | Mono | 11 | 500 (`//` at 400, 50% opacity) | 0.12em | Upper | accent |
| Header / footer meta (`FIG. 01`, `NINADPATHAK.COM`) | Mono | 10 | 400 | 0.08em | Upper | muted |
| Node label | Inter | 14 | 500 | 0 | Sentence | ink |
| Node title (`**bold**`) | Inter | 14 | 700 | 0 | Sentence | ink |
| Decision (diamond) label | Inter | 13 | 600 | 0 | Sentence | ink |
| Node kicker (`§`) | Mono | 9.5 | 600 | 0.10em | Upper | muted; accent on `accent`/`focal` |
| Node detail (`~`) | Inter | 12.5 | 400 | 0 | Sentence | ink-2 |
| Index tag (`01`) | Mono | 8.5 | 500 | 0.06em | — | muted |
| Edge label | Mono | 9.5 | 600 | 0.08em | Upper | ink-2; accent on hot edges |
| Cluster label | Mono | 9.5 | 600 | 0.12em | Upper | muted |
| Callout number | Mono | 9 | 600 | 0 | — | accent |
| Note text | Inter | 12.5 | 400 | 0 | Sentence | ink-2 |
| Legend label | Mono | 9 | 500 | 0.10em | Upper | muted |
| OG kicker | Mono | 15 | 500 | 0.12em | Upper | accent |
| OG title | Inter | 54 / 1.12 | 600 | −0.025em | Title case as published | ink |
| OG byline | Mono | 14 | 600 | 0.12em | Upper | ink |
| OG URL | Mono | 14 | 400 | 0.02em | Lower | muted |

Rules:

- **Minimum rendered size: 12 px for sans and 8.5 px for mono at final display size.** That is why a diagram can scale down to 87.5% (`minScale 0.875`) and no further. The pipeline refuses anything smaller. Split the diagram or change its direction instead.
- Uppercase is applied to the text itself, never through CSS `text-transform`, so every renderer shows the same characters.
- Line height inside nodes is Pele's 21 px rhythm. Keep it.
- No italics, underlines, or more than two weights inside one node.

## 5. Canvas, grid, and composition

Everything snaps to a **4 px grid**. Plate heights round up to a multiple of 4 and field heights to a multiple of 8.

| Type | Canvas | Aspect | Notes |
|---|---|---|---|
| Article plate | 720 wide × content height (464–936 so far) | Free; target ≤ 4:3 tall, ≥ 16:9 wide | Matches `--prose-w: 720px`; PNG at 1440 wide |
| Share card | 1200 × 630 | 1.91:1 | Diagram panel at x 676–1152, y 64–566 |
| Evidence screenshot | 1440 × 900 (16:10) or 1440 × 810 (16:9) | Fixed | Crop to the claim (§13) |
| Terminal receipt | 1440 wide, height from content | Free | 2x of 720 |

**Plate anatomy, top to bottom:**

```
┌──────────────────────────────────────────────────────────────┐  frame: hairline 1px, radius 4
│ // KICKER TEXT                                       FIG. 01 │  head band: 44 px
├┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┤  ruler: 8 px minor, 40 px major ticks
│ ⌜  · · · · · · · · · · · · · · · · · · · · · · · · · · ·  ⌝ │  field: 16 px dot grid, crop marks inset 14
│    · · · ┌───────────┐ · · · · · · · · · · · · · · · · ·    │  diagram centered, 32 px padding
│    · · · │ diagram   │──────▶ · · · · · · · · · · · · ·      │
│ ⌞  · · · └───────────┘ · · · · · · · · · · · · · · · · ·  ⌟ │
├──────────────────────────────────────────────────────────────┤
│ ①  Note text, one line each                                  │  notes band: 24 px per note (optional)
├──────────────────────────────────────────────────────────────┤
│ ●─ HOT PATH   ▭ OUTCOME   ▭ DECISION           NINADPATHAK.COM│  foot band: 36 px, legend + site mark
└──────────────────────────────────────────────────────────────┘
```

- Side and vertical field padding: **32 px**. Head-band text sits at x 20 and baseline 27.
- The diagram is centered horizontally and never stretched. Scale is `min(1, 656 / natural width)`.
- Flowchart node spacing is **28 px** (`layout.nodeSpacing`). Rank spacing stays at Pele's default.
- The `FIG. NN` number counts figures within the article, not across the site.

## 6. Strokes and radii

| Element | Stroke | Notes |
|---|---|---|
| Plate frame, band separators | 1 px hairline | |
| Node border | 1 px rule | Outcome nodes keep the rule border on a surface-2 fill |
| Accent / fail / pass top rule | 3 px solid fill | The site's `--rule-accent`, clipped to the node's top corners |
| Connector | 1.25 px line | Butt caps, miter joins |
| Hot connector | 1.75 px accent | |
| Dashed connector | 1.25 px, 3 px dash / 3 px gap | Async, optional, or observe-only flows (`-.->`) |
| Cluster boundary | 1 px rule, 4 / 3 dash | |
| Muted node | 1 px rule, 3 / 3 dash | |
| Ruler ticks | 0.75 px rule | |
| Crop marks | 1 px rule, 8 px arms | |

| Element | Radius |
|---|---|
| Plate frame, nodes, clusters, OG panel | 4 px (`--radius-sm`) |
| Edge-label and cluster-label masks | 2 px |
| Stadium (`([ ])`) nodes | Full pill; reserve for entry and exit points |

## 7. Nodes

**Label grammar**, written in plain Mermaid:

```mermaid
step["§Layer 1
Execution loop
~Steps, stop rules, retries"]:::accent

outcome["`§Outcome
**Split**
~Public task +
private record`"]:::outcome
```

- `§` line: the **kicker**, a short category such as *Start*, *Layer 2*, or *01 Perceive*. It never wraps. Any node with a kicker becomes a left-aligned card with 16 px inner padding.
- Plain line: the **label**. Keep it under 7 words; Pele wraps it.
- `**bold**`: the **title**. Use it when the node's name matters more than its sentence (outcomes, destinations). It needs Mermaid's backtick string: `` ["`…`"] ``.
- `~` line: the **detail**. Every line after it is detail too, so break long details by hand. Keep each line under about 30 characters so the node doesn't widen the figure.

**Classes.** These are names only. Mermaid needs no `classDef`, and the colors come from the brand CSS.

| Class | Treatment | Meaning |
|---|---|---|
| *(none)* | surface fill, rule border | A step or component |
| `accent` | 3 px accent top rule, accent kicker | Primary steps: the ones the article is about |
| `focal` | accent-wash fill, accent border, accent kicker | The single most important node. One per figure. |
| `outcome` | surface-2 fill | An end state, destination, or something outside the system |
| `muted` | dashed border, canvas fill, muted label | A "before", a deprecated option, or an optional step |
| `fail` / `pass` | danger or success top rule and kicker | A failure path or a success state |

**Shapes.** Rectangles for steps and cards. Diamonds only for yes/no decisions that have a single question line. Cylinders for stores (databases, vector indexes, tool registries). Stadiums for entry and exit. Circles and hexagons need a reason in the caption.

**Index tags** (`@index on`): 8.5 px mono numbers placed 5 px above each node's top-left corner, in source order. Use them when the prose refers to steps by number. Otherwise number the steps in the kicker (`§01 Perceive`).

## 8. Edges

- **Arrowheads are open chevrons**, drawn from Pele's marker geometry: about 8 px long, 6.7 px wide, stroked rather than filled, with the shaft running to the tip. This is the open-arrow style of the site's `→` glyph. Filled triangles are not allowed.
- **Ports.** Each edge starts at a 2.25 px ring (canvas fill, line stroke). On the hot path the ring is filled with accent. Ports show where a flow leaves a node and make bundled edges readable.
- **Hot path** (`@path a>b>c`): every consecutive pair turns accent at 1.75 px, including its label. Use one path per figure, and name it in the legend (`@legend hot=Request path`).
- **Dashed** (`-.->`): asynchronous, optional, or observe-only.
- **Bidirectional** (`<-->`): chevrons at both ends and no port.
- **Edge labels:** one to three words in mono caps, on a canvas mask that is 6 px wider than the text on each side and 16 px tall. Never repeat a word that is already in a node.
- Don't let edges cross. If they would, reorder the nodes in the source or switch the direction. The pipeline doesn't detect crossings, so review the PNG.

## 9. Clusters

- A dashed rule boundary with a 35% surface-2 wash. The label goes top-left in mono caps, with a 4 × 4 accent tick before it. It sits on a mask drawn above the edges, so a line that passes behind the label never cuts through the text.
- `ghost` (`class upper,lower ghost`): an invisible cluster that only steers layout, for example the two rows of the 2×2 agent loop (one `direction LR`, the other `direction RL`).
- Nest at most two levels deep.

## 10. Callouts and notes

- `@note nodeId | One sentence.` A numbered badge sits on the target node's top-right corner: an 8.5 px radius circle with a surface fill, a 1 px accent ring, and the number in mono 9/600 accent. The same number and the sentence then appear in the notes band.
- **Two notes per figure at most.** Each note is a single line (the pipeline fails anything longer than the plate allows). A note states a consequence or a trap, such as "Infinite loops start here", never a restatement of the node.
- Leader lines aren't used. Pinned badges stay legible at any scale, while leader lines tangle.

## 11. Legend and bands

- The legend is generated from the classes the figure actually uses, plus the hot path. Every entry gets a figure-specific label: `@legend accent=Decision; outcome=Destination; hot=Both readers`. Use `class=off` to drop an entry, or `@legend off` to drop the whole legend.
- Footer right: `NINADPATHAK.COM`. Header right: `FIG. NN`.
- The header kicker is a short noun phrase, not a sentence, and no longer than 40 characters. It reads like the site's `.visual-title`: `// THE FOUR-PHASE AGENT LOOP`.

## 12. Texture and intricacy

Five layers, drawn bottom to top. Each one has a single job:

1. **Canvas:** the page color, inside a hairline frame.
2. **Drafting field:** a 16 px dot grid (0.75 px dots in rule color at 55% opacity), a tick ruler along the top and left edges, and crop marks at the four inner corners. This is the engineering-drawing layer. It's barely visible, contains no information, and tells the reader that the figure was measured.
3. **Structure:** clusters, then edges, then nodes, then ports, then cluster labels.
4. **Emphasis:** the hot path, top rules, the focal fill, and callout badges.
5. **Reference:** the head band, notes band, and legend.

Intricacy comes from layers 3 to 5: typographic hierarchy inside nodes, numbered references, ports, and a named route. Don't add a sixth layer. Don't add texture to nodes. Don't make the grid darker to "add detail".

## 13. Screenshots and receipts

**Evidence screenshots**

- Capture at 1440 px wide in the site's light scheme unless the claim is about dark mode. Crop to the element that proves the claim, and keep enough page chrome (logo, URL, or breadcrumb) to identify the source.
- No device frames, no fake browser chrome, no drop shadows, and no browser extensions in view.
- Highlight with one accent rectangle: 2 px accent stroke, 4 px radius, 8 px outside the element. Never use arrows, blur, or circles.
- Redact with a solid `surface-2` block, never blur.
- Embed as a `figure` with a caption naming the source and capture date: *Stripe quickstart, captured 2026-08-17.*

**Terminal receipts**

- Real output only. Render it in the brand receipt plate (spec below; the pipeline template is part of the rollout, not built yet): canvas `#090909` in both schemes (a terminal is dark on purpose), JetBrains Mono 13/1.6, text-2 for output, ink for commands prefixed `$`, and accent only for the line the article cites. Add a head band with `// COMMAND NAME` and the run date.
- No traffic-light window dots. The current `cloudflare-docs-seo-audit.png` uses macOS chrome dots and an unbranded gray; it's on the rollout list.

## 14. Share cards

- 1200 × 630, light scheme, a 4 px accent rule along the top edge, and a hairline frame.
- Left column (x 64 to 628): the kicker is the article category (`// AI ENGINEERING`). The title is set exactly as published, in 54/1.12 Inter 600, up to four lines; the pipeline fails a fifth. Below a hairline separator sit the byline `NINAD PATHAK` and the canonical URL.
- Right panel: the article's lead diagram on a surface panel with the drafting field, scaled to fit, up to 135%.
- An article without a diagram gets a card with the kicker, title, and byline only, centered on the left 2/3. Never use stock imagery.
- This is the only image type that may carry its title as text, because social platforms show no caption.

## 15. Interactive visuals

The 68 iframes on live articles follow these rules from now on, and the rollout plan aligns the existing ones:

- Load `visual-embed.css` and use only its variables. 14 visuals still hard-code `#d44000` / `#ff5f1f`, and at least one (`rag-vs-memory.html`) renders a dark scene in light mode.
- **Load the fonts.** None of the 120 visual files load Inter or JetBrains Mono, so every mono label inside an iframe falls back to Courier. The fix is one `<link>` to the same Google Fonts URL `base.html` uses, or a shared `visual-fonts.css`.
- Same type roles as plates (§4): mono caps for labels about the visual, Inter for content. Minimum 12 px sans and 9 px mono.
- Same stroke language: 1.25 px lines, open chevrons, 4 px radii, one accent idea.
- 3D (Three.js) only when depth is the subject, as with embedding spaces or vector angles. No bloom, glow, fog, particles, or auto-orbit. Use flat-shaded materials in palette colors on the canvas color.
- Motion respects `prefers-reduced-motion` and settles in a meaningful resting state. That still frame is what the static PNG fallback captures.
- Every iframe gets a plate PNG fallback rendered from a Mermaid source. It covers RSS, no-JS readers, and the `og:image` diagram.

## 16. Accessibility

- **Alt text** (`@alt`, required): one to three sentences that state what the figure *shows*, including the outcome of each path, not "diagram of X". Write it so a reader who can't see the image gets the same answer. It goes into `<desc>` and the `<img alt>`.
- **The caption** (`@caption`) carries the takeaway in HTML, where it can be read, searched, translated, and linked.
- **Text that stays out of the image:** article titles, takeaways, paragraphs, citations, numbers the prose depends on, and links. Images hold labels of three to seven words, kickers, and notes of one sentence. The share card is the only exception (§14).
- Contrast is checked on every render (§2).
- No meaning carried by color alone: hot paths are also thicker, accent nodes also carry a top rule, and failure nodes are also labeled.
- Motion: none in plates. Iframes follow §15.

## 17. Files

```
content/diagrams/<article-slug>/<figure-id>.mmd      source (Mermaid + %% @directives)
static/images/diagrams/<article-slug>/<figure-id>.svg          theme-adaptive, fonts embedded
static/images/diagrams/<article-slug>/<figure-id>.light.png    2x
static/images/diagrams/<article-slug>/<figure-id>.dark.png     2x
static/images/diagrams/<article-slug>/<figure-id>.json         alt, caption, size, hash, embed markup
static/images/diagrams/<article-slug>/og.png                   share card, 1200x630
```

- The slug is the article's `slug`, and the figure id is a lowercase noun phrase such as `documentation-placement` or `agent-loop`. Never use `fig1`, `image`, or `final`.
- Every SVG starts with a comment naming its source file, the Pele version, and a 16-character content hash of the source, tokens, CSS, brand layer, and Pele version. `--check` uses the hash to catch stale output.
- Output is deterministic: re-rendering on the same machine is byte-identical (verified on the samples).
- Size budget: SVG under 100 KB (the samples are 57 to 71 KB, mostly embedded font subsets). PNG under 250 KB.

**Embed markup**, copied from the `.json`:

```html
<figure class="np-figure">
  <img src="/static/images/diagrams/agent-loop-anatomy/agent-loop.svg" width="720" height="864"
       alt="…" loading="lazy" decoding="async">
  <figcaption>Each phase has its own failure modes, so debug the loop one phase at a time.</figcaption>
</figure>
```

`np-figure` needs about ten lines of CSS (no border; the plate draws its own frame), which can go in once the site-fixes work on `static/css` lands.

## 18. Directives

| Directive | Required | Meaning |
|---|---|---|
| `@alt` | yes (diagrams) | Alt text (§16) |
| `@kicker` | yes | Head-band title |
| `@fig` | recommended | Figure number within the article |
| `@caption` | recommended | HTML caption written into the embed |
| `@path a>b>c` | no | Hot path; may repeat |
| `@note id \| text` | no | Callout, at most two |
| `@legend k=v; …` / `off` | no | Legend labels |
| `@index on` | no | Index tags above nodes |
| `@kind og`, `@og-title`, `@og-kicker`, `@og-url`, `@diagram file.mmd` | share cards | Share-card fields |

Mermaid frontmatter (`config: flowchart: nodeSpacing: 20`) still works for one-off layout tweaks. Never set colors there.

## 19. Do and don't

| Do | Don't |
|---|---|
| One accent idea per figure, named in the legend | Accent top rules on every card (the old decision tree has seven) |
| Let the plate draw its own frame | Wrap a plate in `.visual-wrapper` (that gives a double border and a doubled title) |
| Put the takeaway in `figcaption` | Write the takeaway sentence inside the image ("A heading should expose the next useful move.") |
| Fix a dense diagram by changing direction, using `ghost` rows, or splitting it | Let it shrink below 87.5%, or keep a second hand-drawn mobile SVG in sync (the old tree ships two) |
| Open chevrons, ports, 1.25 px lines | Filled triangles, 2 px+ arrows, curved decorative arrows |
| Short mono caps edge labels on a mask | Edge labels floating in gaps, as in the old tree's `NO` / `YES` |
| Embed font subsets; check in both schemes | Rely on page fonts inside `<img>` or an iframe (Courier fallback) |
| Badge plus one-line note for a trap | Paragraph callouts, leader lines, arrows into empty space |
| Evidence screenshot cropped to the claim, with source and date | Full-page captures, device mockups, blurred redactions |
| A static plate when motion only decorates | Three.js orbit scenes with glow (`rag-vs-memory.html`) |

The samples in `review/image-brand/` show each rule on real articles.

## 20. Checklist before shipping a figure

- [ ] The source is in `content/diagrams/<slug>/`, and `node tools/image-brand/render.mjs` ran clean.
- [ ] `node tools/image-brand/render.mjs --check` passes (fresh output, AA contrast).
- [ ] Scale is 1.0, or at least 0.875 with a reason.
- [ ] One accent idea; legend labels are specific to this figure.
- [ ] No edge crossings and no label collisions in either PNG.
- [ ] Alt text states what each path concludes; the caption carries the takeaway.
- [ ] Read the dark PNG once at 100%.
