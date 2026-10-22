# Batch 1 review

- `og-contact-sheet.png`: share cards for the 67 published posts plus the 5 pending art-* posts (`node tools/image-brand/contact.mjs`).
- `<slug>.before-after.{light,dark}.png`: the two swapped diagrams, main build vs branch build at 1366.
- `<slug>.sweep.png` + `sweep.json`: each changed figure at 320, 375, and 1366 px in light and dark. The sweep checks page overflow, image load, fit, and **displayed text size** (sans ≥12 px, mono ≥8.5 px), and records which variant (narrow or wide) the page served. 12/12 pass; the smallest label is 12.1 px, at 1366.
