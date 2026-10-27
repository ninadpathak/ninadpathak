# Code blocks: review sheets

Each block now sits on the text column inside a brand frame: a head strip with the language as a mono kicker (with the plates' 4px accent tick) and a copy button, a site-palette syntax theme for light and dark, and an accent edge fade wherever code runs past the edge.

## What was wrong

- **Inset.** `build.py` wrote `.highlight { padding: 1rem }` into `highlight.css`, so Pygments' wrapper (which also had its own background) sat around the bordered `<pre>`. The box edge was 16px right of the paragraphs, and the code text 41px right. The frame now replaces that wrapper's padding and background, so the frame's left edge equals the paragraph's.
- **Clipping.** The `<pre>` did scroll, but macOS overlay scrollbars hide until you scroll, so a long line just looked cut off.
- **Bland.** It was Pygments' default and monokai styles on a plain white box.
- **Split tokens.** Inline code inherited `overflow-wrap: break-word`, and browsers may break after a hyphen, so `-e` became "-" and "e".

## Rules

- **Scroll or wrap.** Code (bash, python, json, yaml, js, diff, http, html) keeps its lines and scrolls, with a fade on whichever side has more code. `text`, `markdown`, `prompt` and unlabeled blocks soft-wrap: they hold prompts, templates and tool output with lines up to 312 characters.
- **Copy.** The button is added by `main.js`, so without JavaScript there is no dead button. It is a real `<button>` with an `aria-label` naming the language, a visible focus ring and an `aria-live` "Copied to clipboard". The head strip has a fixed height, so adding the button moves nothing. It copies the code element's text without the final newline.
- **Inline code.** Inline code of 24 characters or fewer never wraps. Longer inline code (paths, commands) is marked `code-long` at build time and may break only between words or after a `/ . _ = ? & : ,` delimiter. A run of more than 28 characters with no delimiter may break anywhere rather than push the column sideways.
- **Ligatures.** They are off in code, so `==` and `->` show as typed.

## Contrast

Every Pygments token type is checked in both themes by `tests/test_code_blocks.py`. A mutation (comments set to `#9a9a9a`) fails it.

| Theme | Background | Lowest | Colors (ratio) |
|---|---|---|---|
| Light | #ffffff | 5.33 | muted #6b6b6b 5.33 · accent #c23b00 5.36 · green #18794e 5.41 · red #b42318 6.57 · blue #2a5a8c 7.14 · ink-2 #3a3a3a 11.37 · ink #0e0e0e 19.3 |
| Dark | #111111 | 5.47 | muted #8a8a8a 5.47 · accent #ff5f1f 6.21 · red #ff8a80 8.27 · blue #8fb8e8 9.16 · green #7ccf9f 10.15 · ink-2 #c2c2c2 10.6 · ink #f0f0f0 16.57 |

The head strip's label, hover and "Copied" colors are also checked against the head background in both themes.

## Sweep

`node tools/codeblocks_sweep.mjs <main build> <branch build> review/codeblocks <slugs…>` covers 11 articles, chosen to include every language in use and both layouts:

- mcp-server-tutorial (bash, python, text, long lines)
- hyperagents-memory (python)
- memory-versioning (json)
- claude-code-subagents (markdown with a 312-character line, json)
- release-notes-template (markdown, text)
- writing-release-notes (diff, text)
- writing-changelogs (http)
- deerflow-memory (yaml)
- docs-seo (html)
- writing-technical-tutorials (js)
- api-documentation (long tool-output lines)

The sweep runs at 320, 375, 768 and 1366 px in light and dark. Result: 88/88 runs pass, with 464 block measurements, 212 of them with overflowing code.

- **Alignment:** each block's left edge is within 0.5px of the paragraph's.
- **Overflow:** blocks stay inside the column, and no page scrolls sideways.
- **Scrolling:** every overflowing code block scrolls, carries the fade and takes keyboard focus.
- **Inline code:** no short inline code wraps, and no long inline code splits inside a segment.
- **Copy:** at 1366 light, the copy button copies the exact code text and leaves the head height unchanged.
- **No JavaScript:** 11/11 pages ship no copy button.

No article puts code inside a list or blockquote: Python-Markdown's `extra` doesn't nest fenced code. The frame is an ordinary block, so it would align to a list item's content, but the sweep can't exercise that case.

Files are `<slug>.before-after.{light,dark}.png` at 1366, `<slug>.sweep.png` for the eight width and theme combinations, and `sweep.json`.
