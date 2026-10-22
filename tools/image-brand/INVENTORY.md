# Article image inventory and rollout plan

Taken on `origin/main` at `2e40c460` (2026-10-22); branch since rebased onto `0759ad64`. There are 67 posts in `content/posts/`.

## Inventory

| Type | Live (referenced by content) | Unreferenced files | How it is made today | Problems found |
|---|---|---|---|---|
| Interactive iframe visuals (`static/visuals/*.html`) | **68** in 51 posts (46 posts have 1, one has 2, three have 4, one has 8) | 52 | Hand-written HTML per visual. Of the live ones, **23** use Three.js r128 from two different CDNs (cdnjs and jsDelivr, plus OrbitControls), **13** use inline SVG plus JS, and **32** use HTML/CSS. Embedded with `.visual-wrapper > .visual-title + .visual-container > iframe` at a fixed 400 px height. | No visual loads Inter or JetBrains Mono, so mono text falls back to Courier. 14 hard-code `#d44000` / `#ff5f1f` instead of `visual-embed.css` (106 of 120 do load it). `rag-vs-memory.html` draws a dark scene in light mode, with glow and orbit. `cosine-similarity.html` clips its vectors at the top edge. No static fallback for RSS or no-JS readers. |
| Static SVG diagrams | **2** figures in 2 posts (3 files: the placement flowchart has desktop and mobile variants) | 0 | Hand-drawn SVG | The placement flowchart overflows its card ("task?" crosses the border) and puts an accent rule on all 7 cards. `task-heading-anatomy.svg` hard-codes light colors (a white slab in dark mode), clips its `CONTEXT` pill, and writes a sentence into the image. |
| Evidence screenshots (third-party pages) | **18** in 10 posts (16 at 1280×720 or 1280×1000 in `static/images/visuals/`, plus a 3840×2160 Cloudflare docs page and a 2560×1664 checker capture) | 36 image files under `static/images/{articles,posts,visuals}` are referenced by nothing | Browser captures | Inconsistent sizes. Several are full-page captures that aren't cropped to the claim (the DORA capture is mostly hero illustration). Some have vague alt text (`alt="DORA Metrics"`). |
| Terminal receipts | **1** (`seo-for-technical-documentation/cloudflare-docs-seo-audit.png`, 1920×1118) | 9 more receipt or checker PNGs among the 36 unreferenced files (judging by filename, in `static/images/articles/`) | Screenshot of a terminal window | macOS traffic-light dots, unbranded gray, no head band or date |
| Mermaid diagrams | **0** | — | — | — |
| `flowcharts.css` | `.flowchart-image` wrapper: 1 post. `.flowchart` HTML card component: 1 use, in `content/data/glossary.yaml` | — | CSS-drawn cards | A second diagram system parallel to the iframes |
| Featured / OG images | **0** per article. Every page's `og:image` and `twitter:image` is `/static/favicon.png` at 512×512 (`templates/base.html:32,42`) | — | — | A square favicon in 1.91:1 link previews |
| Other | `static/images/mem0-growth.png` (1 case study), `static/images/clients/` logos (home page) | — | — | Out of scope (not article images) |

**`hermes-featured-images` (sibling repo, inspected read-only).** It is a Python renderer that makes 1920×1080 featured images for LinuxForDevices, CodeForGeek, and AskPython, deterministic and byte-identical. Nothing in it targets ninadpathak.com, and this site doesn't consume its output. This pipeline borrows its deterministic-output and validate-before-render ideas but doesn't depend on it.

## Samples (phase 1, v3 visual library)

| # | Archetype | Article | Source | Replaces |
|---|---|---|---|---|
| 1 | Decision tree | internal-vs-external-docs | `content/diagrams/internal-vs-external-docs/documentation-placement.mmd` | hand-drawn desktop and mobile SVGs |
| 2 | Anatomy | documentation-headings | `content/diagrams/documentation-headings/task-heading-anatomy.mmd` | light-only SVG |
| 3 | Loop | agent-loop-anatomy | `content/diagrams/agent-loop-anatomy/agent-loop.mmd` | `agent-loop-cycle.html` iframe |
| 4 | Share card | agent-harnesses | `content/diagrams/agent-harnesses/og.mmd` | the 512×512 favicon as og:image |
| 4b | Architecture | agent-harnesses | `content/diagrams/agent-harnesses/harness-layers.mmd` | `agent-harness-layers.html` iframe (Three.js-era rings) |
| 5 | Stack | llm-inference-optimization | `content/diagrams/llm-inference-optimization/inference-stack.mmd` | `inference-optimization-stack.html` iframe |
| 6 | Comparison / benchmark | llm-token-budgets | `content/diagrams/llm-token-budgets/token-pricing.mmd` | `token-budget.html` iframe |

Content findings while sourcing the samples:

- `llm-token-budgets.md` once priced a 1,000-in / 500-out GPT-5.4 Nano request at $0.00026; at the article's own table it is $0.000825. Fixed on main in 937d5742. The sample uses only the pricing table.
- The current `inference-optimization-stack.html` iframe shows a combined "20–80x" figure and puts speculative decoding at step 5. The article states neither: its fifth step is INT8 or 4-bit, and it adds speculative decoding only after the basics. The v2 stack follows the article.

## Proposed rollout (after the look is approved)

Efforts are estimates for one owner working with this pipeline.

1. **Wire-up (about half a day, after site-fixes merges `static/css` / `templates` / `build.py`).** Add `np-figure` CSS (about 10 lines). Add an `og_image` front-matter field to the post template, defaulting to `/static/images/diagrams/<slug>/og.png`. Run `render.mjs --check` in CI or the build. Re-run `--check` drift once the new accent and muted values are in `main.css` (it should then report nothing).
2. **Static diagrams (about 1 hour).** Swap in samples 1 and 2 and delete the three old SVGs.
3. **Share cards for all 67 posts (about half a day).** Generate `og.mmd` from front matter (title, category, slug). Posts with a lead plate get the diagram card. The rest get the text-only card (§14, to build). Review a contact sheet of all 67 before shipping.
4. **Iframes (about 3 days total), triaged first.**
   - *Triage (about 2 hours):* screenshot all 68 live visuals and sort each into **replace with a plate** (motion is decoration: loops, pipelines, layers, flows, and most Three.js orbit scenes; likely 40 to 50) or **keep and align** (interaction teaches: vector angles, embedding spaces, sliding windows, heatmaps you scrub; likely 15 to 25). The list goes to Ninad for approval.
   - *Replace:* write the Mermaid source and render, at 20 to 30 minutes per figure. Fix the embed to `<figure class="np-figure">`.
   - *Keep and align:* add a shared `visual-fonts.css` (fixes Courier everywhere at once), replace the 14 hard-coded hex palettes with `visual-embed.css` variables, apply the stroke and type rules, add `prefers-reduced-motion`, and pin one Three.js CDN and version. Each kept visual also gets a plate PNG fallback.
5. **Receipts and screenshots (about 1 day, lowest priority).** Build the receipt plate template and re-render the one live receipt. Re-capture the 18 evidence screenshots at 1440 wide, cropped to the claim with one accent highlight and a dated caption, and rewrite vague alt text.
6. **Cleanup (needs Ninad's approval; deletions).** 52 unreferenced visuals and 36 unreferenced image files. List them, confirm none are linked externally or kept on purpose, then delete them.

## Rollout status

- **Batch 1** (branch `image-brand-batch1`): token audit and consistency fixes, stack numbering, loop context glyph, wiring (figures.css, og_image, CI check, tests), the two static diagrams swapped, and share cards for all 67 posts. Review evidence is in `review/image-brand/batch1/`.
- **Batch 2+**: iframe triage (replace with a plate, or keep and align) and conversions in groups of 15–20.
- Old assets (the 52 unused visuals, the 36 unused images, and the two replaced static SVGs) stay in place until Ninad approves deletion.
