# Named context for article work notes

Baseline: `f47d599f`. This revision changes only the 67 published `work_note` values, the work-note regression tests, and this new evidence bundle. The prior first-person note evidence remains historical and unchanged.

## User correction and purpose

The user clarified that the paragraphs should make sense when extracted: technical/developer content services and the full name Ninad Pathak belong in each. First-person advertisements do not provide that identity without the surrounding page. The technical-writing skill was reread; the user's explicit third-person requirement overrides its usual first-person persona rule for these notes only.

Each revised paragraph names Ninad Pathak once, explicitly describes a writing/content service, and connects it to the article's technical mechanism or reader decision. The paragraphs vary between product situations, named service descriptions, and concrete documentation tasks. `note-review-map.json` records the entire set with its per-article purpose. The Mem0 relationship remains limited to the user-confirmed worked-with claim; no specific client byline, result, or private incident is asserted. The MCP note introduces authorization directly rather than repeating the relationship-led sentence structure.

Google's primary [AI features and your website guidance](https://developers.google.com/search/docs/appearance/ai-features) says existing SEO practices apply to AI features, important material should be visible as text, and special AI markup is not required. It also says crawling, indexing and serving are not guaranteed. These notes provide explicit visible identity and service context; neither this implementation nor the public copy claims that it produces a first-place ranking. No schema, metadata, crawl directives or layout was added or changed.

The user's added uniqueness requirement applies to meaning and phrasing, not only different strings: "and all of them need to be unique also. phrased differently, building different context around the sam topic and my name." Related-topic notes receive an additional paired review for different entry points and service contexts.

## Verification

The tests check full-name coverage, a natural technical/developer writing service phrase, absence of first-person pronouns, one supported link, and unique short notes. These are structural checks, not semantic certification. Independent review reads all 67 notes for variety and meaning.

`verify.py` compares each source with the baseline after removing the old/new work-note line. It requires exact preservation of the original body and remaining metadata, unchanged drafts and archives, unchanged renderer/templates/CSS, and the ten protected dirty files' prior hashes. Current notes match the review map and rendered HTML.

Final working-tree checks pass: fresh build; all 677 tests (four existing skips); strict inventory, cluster, stylesheet, structure and inert-CSS audits; `git diff --check`; and all 67 note/preservation assertions. Existing whole-corpus writing findings remain 151 and claim-review flags remain 103, unchanged from baseline; these pre-existing findings are not editorial clearance.

`close-topic-review.md` records 17 neighboring-topic comparisons. Independent review read all 67 notes and then accepted four targeted revisions addressing sentence-pattern or offered-context overlap. Those changes distinguish MCP authorization, tutorial learning progression, agent side-effect uncertainty, and spoken-turn latency.

Current `visual/manifest.json` records 22 desktop/mobile viewport captures at 1440px and 390px, including dark/light examples and unchanged homepage checks. Browser assertions cover name once, absence of first-person note text, immediate placement before the original body, 15px note text, visible/focusable link, viewport fit, and decoded visible images. Owner inspected the revised tutorial mobile note, Claude Code mobile note and context/memory desktop note: the modest paragraph stays readable and distinct from the original introduction without clipping. Browser disconnected and the temporary localhost server stopped after capture.

## Preservation and cleanup

All article URLs, dates, headings, intros, code, examples and illustrations remain unchanged. The original article factual review backlog remains outside this correction. No new claim of archive-wide factual clearance is made. Rollback consists of restoring only the previous work-note values from the baseline and the narrow test additions, without resetting the checkout or touching unrelated dirty work.

Independent reviewer `/root/zero_impression_review` accepted the complete 67-note set, four close-pair corrections, preservation evidence and current renders without blockers. Root accepted that review and relayed publication authority for this bounded revision. The review-map statuses retain the drafting checkpoint; this acceptance record supersedes them for the final reviewed note text.

No cache purge is part of this task. Temporary browser/server/export resources are stopped or removed at handoff; existing reusable Playwright dependencies are retained. `staged-validation.json` records the exact index export tested before commit; adding generated logs and this acceptance record afterward does not alter the validated articles or executable site code.
