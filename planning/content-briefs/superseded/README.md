# Superseded briefs

Briefs written before a topic shipped on `main`. Kept as a record of what was planned and
why it was dropped. **Do not write from anything in this folder.**

## Superseded 2026-08-17 by the four API articles published on `main`

I branched from `d59de3ca` and wrote the weeks 1 and 2 briefs before rebasing onto
`5af0889b`, which carried four published API documentation articles. Four of my six API
targets were already live. These three briefs died:

| Brief | Killed by |
|---|---|
| `brief-2026-08-20-api-documentation-best-practices.md` | `api-documentation-best-practices-reference-guides-and-working-requests` |
| `brief-2026-08-29-api-documentation-example.md` | `api-documentation-examples-what-the-best-developer-portals-get-right` |
| `brief-2026-08-24-what-is-api-documentation.md` | Not directly published, but its parent topic `api documentation` is now owned by the best-practices anchor. The brief flagged this risk itself and said to escalate rather than ship two competing pages. Escalated, and dropped. |

Two more targets are on hold in `semrush-opportunity-backlog.csv` for the same reason:
`api reference` and `what is api documentation`.

## The lesson, applied going forward

Rebase onto `origin/main` and re-read `output/llms.txt` **before** writing any brief, not
after. The do-not-repeat register in
`/Users/ninad/.claude/orchestration/ninadpathak-seo/LEDGER.md` is the check.
