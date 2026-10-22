# Batch 2 · group A review

18 iframes replaced by plates (see `tools/image-brand/IFRAME-TRIAGE.md`, group A), plus the two batch-1 figures re-rendered with the 24 px field padding.

- `<slug>.before-after.{light,dark}.png`: the live iframe on main vs the plate on this branch, 1366 px.
- `<slug>.sweep.png` + `sweep.json`: each figure at 320, 375, 768, 1024, and 1366 px in light and dark. Phones (≤712 px) get the narrow variant, capped at 1.25×; tablets and up get the wide plate. The sweep checks overflow, load, fit, displayed text size, and stretch. 200/200 pass; the smallest label is 12.1 px, the smallest mono text 8.9 px, and the largest stretch 1.14×.
