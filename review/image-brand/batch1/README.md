# Batch 1 review

- `og-contact-sheet.png`: share cards for the 72 published posts (`node tools/image-brand/contact.mjs`).
- `<slug>.before-after.{light,dark}.png`: the two swapped diagrams, main build vs branch build at 1366.
- `<slug>.sweep.png` + `sweep.json`: each changed figure at 320, 375, 768, 1024, and 1366 px in light and dark. Checks: page overflow, image load, fit, displayed text size (sans ≥12 px, mono ≥8.5 px), and that no variant is stretched past 1.25×. Phones (≤712 px) get the 288 px variant, capped at 360 px; 768 px and up get the wide plate. 20/20 pass.
