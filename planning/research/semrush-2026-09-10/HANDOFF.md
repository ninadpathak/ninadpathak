# Writing strategy handoff

Owner: writing-strategy. Local implementation and evidence complete on 10 September 2026; final acceptance belongs to the director. No push, deployment, PR, or external message was performed.

## Pull and preservation

`git fetch origin` succeeded. `git pull --ff-only` reported `Already up to date.`

Before and after HEAD, and fetched `origin/main`: `1967520f7d64dcbe31637240691c976a5346d7cc`.

The initial dirty files were preserved byte-for-byte: `planning/attribution.md`, `daily-cycle.md`, `leading-indicators.md`, `position.md`, `scoreboard.md`, `url-inventory.json`, `video/brief-001.md`, and untracked `video/review-001.md`. Evidence: `validation/preservation-check.json`.

The pre-existing daily launchd schedule was inspected and left intact. No crontab existed; no matching active project writer or daily-cycle process appeared during initial inspection.

## Implemented surfaces

- `templates/blog_list.html`: removed category navigation and row tag badges. Article links and pagination remain.
- `templates/index.html`: concrete technical-writing introduction; recent articles first; curated writing problems; published-work and contact routes; the six user-confirmed company relationships; no category controls or animated company strip.
- `templates/base.html`: factual footer description and “About this site” label.
- `static/css/home.css`: homepage-only paragraph spacing using existing design tokens.
- `config.toml`: site tagline and description aligned with the writing niche.
- `campaign-90d.md`, `planning/content-plan.md`, `planning/documentation-authority-plan.md`: dated pointers reconcile historical prescriptions without deleting their history.

The homepage no longer repeats metric-led sales sections or testimonial cards. Those underlying case-study and portfolio pages remain intact; no new roles, results, endorsements, or logos were invented for Semrush, Adobe, TinyFish, Mastra, Manicule, or OpenComputer.

## Durable strategy artifacts

- `planning/technical-writing-strategy-2026-09.md`: philosophy, plan reconciliation, measured priorities, discipline-wide coverage horizons, intent ownership, URL protection, internal links, quarter capacity, editorial gate, measurement and stop criteria.
- `planning/technical-writing-briefs-2026-09.md`: ten candidate briefs with hypotheses and evidence requirements; these are not completed experiments.
- `planning/technical-writing-url-decisions-2026-09.csv`: all 96 current post sources, including 87 published posts; proposed dispositions without article mutations.
- `planning/research/semrush-2026-09-10/README.md`: methods, limitations, competitor interpretation and primary writing references.
- This directory's twelve JSON responses retain actual Semrush calls, including both failures and the successful bounded retry.

## Validation

`./.venv/bin/python build.py` passed: 87 articles, 141 HTML pages, 140 sitemap URLs and 140 unique canonicals. The sitemap is byte-identical to the pre-homepage-edit build; this task changes no URL or indexability policy.

`./.venv/bin/python -m unittest discover -s tests -p test_build.py` passed all 40 tests. `git diff --check` passed, and local links in the strategy documents resolve.

Headless Chrome checks passed at 1440×1000 and 390×844 for `/` and `/articles/`: no horizontal overflow or JavaScript page errors. Pagination to page two passed on both sizes; mobile menu and theme controls passed.

Category controls are absent from the homepage and all five article-list pages. Internal category metadata and archive URLs remain; full-page screenshots were refreshed after the footer and category changes.

Screenshots in `validation/`: `home-desktop.png`, `home-mobile.png`, `articles-desktop.png`, `articles-mobile.png`. Browser results, build and test logs, and the local visual script are beside them; homepage desktop/mobile and articles mobile were visually inspected by the owner.

The Browser skill was read, but the required Node REPL browser tool and a tool-discovery search endpoint were absent from the available tool catalog. Local visual checks therefore used the existing Playwright installation and a fresh headless Chrome instance; no signed-in browser profile was read. Production analytics requests were blocked during the local check.

## Remaining boundaries

External Hermes queue adoption is unresolved. This strategy does not change or pause that publisher; its owner must reconcile future assignments before the new production policy can be described as operational.

The dedicated Paul Graham skill was unavailable in the searched skill/repo locations. The installed technical-writing skill, existing editorial synthesis, and primary Graham/Willison essays informed the work.

Semrush uses the US desktop database and latest returned snapshots, with retrieval date 10 September 2026. The competitive comparison is capped at 30 rows and is not a complete keyword universe; the anomalous head-term volume is excluded from priority sizing.

The strategy audits questionable biography and tutorial material but does not rewrite the articles. First-person history still needs Ninad's confirmation; the ten experiments remain proposed. The new homepage company relationships are supported by explicit user confirmation, without additional claims about those engagements.

Director-relayed independent review accepted the research and broader coverage, then requested a concrete homepage heading, removal of homepage category controls, and updated footer copy. Those changes are implemented; final screenshot acceptance remains with the director.

## Cleanup and rollback

The temporary browser instances were closed. The task's localhost preview server is stopped at handoff; existing schedulers and processes remain untouched. No worktree or persistent service was created.

To roll back, reverse only this task's hunks in the seven previously clean tracked files listed above and remove the task-created homepage stylesheet and strategy/research artifacts. Do not reset the checkout or touch the eight pre-existing dirty files. Rebuild `output/` after reversing the template changes; generated output is ignored by Git.
