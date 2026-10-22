# Batch 2 · group A review

18 iframes replaced by plates (see `tools/image-brand/IFRAME-TRIAGE.md`, group A), plus the two batch-1 figures re-rendered with the 24 px field padding.

- `<slug>.before-after.{light,dark}.png`: the live iframe on main vs the plate on this branch, 1366 px.
- `<slug>.sweep.png` + `sweep.json`: each figure at 320, 375, and 1366 px in light and dark. Phones get the narrow variant; the sweep checks overflow, load, fit, and displayed text size. 120/120 pass; the smallest label is 12.1 px and the smallest mono text is 8.9 px.
