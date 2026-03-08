# ninadpathak.com

Personal portfolio and blog. Built with a custom Python static site generator — no frameworks, no CMS, ~4 dependencies.

## Stack

- **Generator**: `build.py` — single Python script
- **Templates**: Jinja2
- **Markdown**: python-markdown + pygments for syntax highlighting
- **CSS**: Vanilla, no build step
- **JS**: Vanilla, no frameworks
- **Hosting**: Cloudflare Pages

## Setup

```bash
pip install -r requirements.txt
python3 build.py
```

Output goes to `output/`. That's the folder to deploy.

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

content/
  about.md
  portfolio.yaml
  work/              # Case study markdown files
  posts/             # Blog posts (fallback if no Obsidian path)

output/              # Generated site (gitignored)
```

## Deploying to Cloudflare Pages

Set the build command to `python3 build.py` and the output directory to `output`.

Or push manually:

```bash
python3 build.py
# deploy output/ to Cloudflare
```
