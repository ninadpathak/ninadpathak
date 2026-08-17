# Brief: Internal link triage across the unpublished corpus

**Slot:** 2026-08-18 | **Type:** FIX | **Writer:** none, this is a repo task for Claude/Ninad

## Why this is a scheduled slot

The August audit found 45 obsolete `/blog/` links across the 16 unpublished posts. 14
resolve through generated redirects. The other 31 hard-404. Left alone, they become live
defects the moment any review post ships.

## The rule

Do not bulk-rewrite `/blog/` to `/articles/`. The correct action depends on the target's
status, and a blind rewrite converts 31 dead links into 31 differently dead links.

| Target status | Count | Action |
|---|---:|---|
| Published | 14 | Mechanical rewrite to `/articles/<slug>/`. Safe. |
| Review | 19 | Leave. Resolves when the target ships, or cut the link during that post's REWRITE slot. |
| Retired | 12 | Delete the link, or repoint at a live page that genuinely serves the sentence. Never rewrite the path. |

## Also in this slot

Correct `text-embedding-3d-small` to `text-embedding-3-small` at
`content/posts/embedding-models-compared.md` lines 34 and 132. The audit named this the
cheapest, highest-priority factual fix. The post is retired, so the change is two strings
and no rebuild risk.

## Done when

- The 14 published-target links are rewritten and `python build.py` passes.
- The remaining 31 are listed by file, line, target, and required action in
  `planning/content-cleanup-register.md`.
- The embedding identifier is corrected in both places.
