# ninadpathak.com

Personal portfolio and blog. Built with a custom Python static site generator — no frameworks, no CMS, ~4 dependencies.

## Stack

- **Generator**: `build.py` — single Python script
- **Templates**: Jinja2
- **Markdown**: python-markdown + pygments for syntax highlighting
- **CSS**: Vanilla, no build step
- **JS**: Vanilla, no frameworks
- **Hosting**: Cloudflare Pages
- **Serverless tools**: Cloudflare Pages Functions

## Setup

```bash
pip install -r requirements.txt
python3 build.py
```

Output goes to `output/`. That's the folder to deploy.

Every build runs `seo_audit.py` before it exits. Deployment stops if a generated page
has a broken internal link, missing metadata, duplicate canonical, invalid JSON-LD,
missing sitemap entry, missing `llms.txt` target, or malformed Cloudflare redirect. It also
fails on internal links that would take a redirect hop (a slashless page path or a
redirected URL), redirect chains, redirects to missing or live pages, and a redirect
source without its bare or trailing-slash twin, since Cloudflare matches sources exactly.

To preview locally:

```bash
python3 build.py --serve
# → http://localhost:8000
```

## Writing blog posts

Write in Obsidian (or any editor). Add frontmatter:

```yaml
---
title: "Your Post Title"
date: 2026-03-08
description: "One sentence summary."
tags: [ai, devtools]
status: published
---

Post content here...
```

Set `obsidian_path` in `config.toml` to your Obsidian folder. Posts with `status: published` are included on the next build.

If `obsidian_path` is empty, posts are read from `content/posts/`.

Every prose paragraph is limited to two sentences. The build stops when a published
post exceeds that limit; headings, lists, tables, blockquotes, and code are excluded.

Articles are written as a personal blog, not anonymous SEO copy. Use first person when
it adds a real opinion, decision, or experience, but never to satisfy a numeric rule or
repeat what the section heading already says.

The voice should feel relaxed and spoken, while the technical claims stay exact. Use
natural connectors such as "if you look at," "so," "which means," and "the thing is"
when they help one thought lead into the next. Context can carry the subject; do not
rewrite every sentence as a standalone claim or force specificity where a pronoun would
sound more natural.

Open with tension, not background. Challenge a decision the reader has already made,
show the cost of getting it wrong, or give them a test they may be uncomfortable running.
Avoid generic scene-setting that could introduce any article in the category.

Keep the opening short: one concrete moment from the reader’s work, then one paragraph
that names the problem and hands them the article’s promise. The detail belongs in the
body once the reader has decided to continue.

Use only details the reader can reasonably recognize across teams. Do not invent page
counts, dates, folder names, navigation labels, release cadences, or other specifics to
make an opening feel vivid.

Do not build paragraphs around a contrast formula such as "not X, but Y" or "rather
than X, do Y." Stay with the situation, name what happens next, and let the reader
follow the reasoning without a rhetorical reversal.

## Project structure

```
build.py              # The generator
config.toml           # Site config + Obsidian path
requirements.txt

templates/            # Jinja2 templates
  base.html
  index.html
  blog_list.html
  post.html
  work.html
  work_single.html
  portfolio.html
  about.html
  contact.html

static/
  css/main.css
  js/main.js

functions/
  api/discover-site.js # Sitemap and page metadata scanner

content/
  about.md
  portfolio.yaml
  work/              # Case study markdown files
  posts/             # Blog posts (fallback if no Obsidian path)

output/              # Generated site (gitignored)
```

## Design system

The shared design primitives live in `:root` at the top of `static/css/main.css`.
Use the existing color, typography, spacing, radius, shadow, and focus tokens instead
of adding raw values to a component. Reuse base classes such as `.container`,
`.prose-container`, `.label`, `.btn`, `.section-row`, and `.arrow-link` before creating
a new structural class.

Keep page-specific CSS out of the global bundle. The linter owns `linter.css`, while
article syntax highlighting and visual-embed styles are included only when the rendered
article needs them. Static decision trees use the reusable classes in `flowcharts.css`;
the build includes that stylesheet only for articles containing a `.flowchart`.

Tokens cover color, font size, weight (`--weight-*`), line height (`--leading-*`),
tracking (`--tracking-*`), spacing (`--space-*`), rules (`--rule`, `--rule-strong`,
`--rule-accent`, `--rule-accent-thin`), durations (`--t-*`), and page stacking layers (`--z-*`). A handful of
single-use values stay raw because snapping them would visibly move a component;
`tests/test_design_tokens.py` names each one, so a new one-off fails the build.

Templates, articles, and site scripts never set `style=`. Use a class, or a state class
toggled from JavaScript such as `.scroll-locked`, `.is-active`, or `.copy-failed`. There
are three exceptions. The critical `<style>` in `base.html` paints the themed background
before `main.css` loads. The reading-progress bar sets its per-scroll width inline, and
`post.html` sets an embedded visual's height from the height the visual reports.

The iframe visuals in `static/visuals/` are standalone documents that cannot inherit
`main.css`. They link `/static/css/visual-embed.css`, which `build.py` generates from the
`main.css` palette, so a color is edited in one place. Visuals follow the reader's OS
color scheme through `prefers-color-scheme`. Each visual keeps only its own geometry,
chart colors, and any token it deliberately overrides. The Three.js scenes with fixed
artwork colors do not link the shared palette.

Visual markup has no `style=` either. A utility used by two or more visuals lives once in
`static/css/visual-utilities.css`. That file loads before each visual's own `<style>`, so
a utility repeats its class until it outranks every rule that matches the same element.
A utility used by one visual stays in that visual. Script state changes toggle classes
that sit last in the visual's sheet. The listed visuals in `tests/test_design_tokens.py`
still write computed geometry at runtime, such as a data-driven bar width or a tooltip
position.

## Deploying to Cloudflare Pages

Set the build command to `python3 build.py` and the output directory to `output`.

Or push manually:

```bash
python3 build.py
# deploy output/ to Cloudflare
```
