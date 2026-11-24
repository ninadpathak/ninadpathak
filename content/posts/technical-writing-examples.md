---
category: technical-documentation
primary_query: technical writing examples
siblings:
- documentation-types
- documentation-template
- documentation-best-practices
date: 2026-11-23
description: "The technical writing examples here are ten files from software docs, each with the check that ran on it, and seven show the weak line beside the finished one."
slug: technical-writing-examples
status: published
takeaways:
- Of the ten technical writing examples checked on November 23, 2026, the only command that failed was a quickstart line with no expected output written under it.
- An API reference row said the Content-Type header was required until a request without the header returned 202, and the row now says Recommended.
- The checker scripts passed a troubleshooting heading rewritten as "Database write problems" and a release note rewritten as "Fixed an issue with webhook retries", so a person still has to read those lines.
title: "Technical Writing Examples: 10 Tested Samples With Edits Shown"
work_note: "I'm Ninad Pathak, a freelance technical writer, and the samples on this page are the kind of quickstart and reference page I write for developer products. Each one was checked before it was listed, and the pages I write for you would be too. [Get in touch](/services/developer-documentation/)."
---

Every available check ran on eight documentation files from this site on November 23, 2026, and one command printed nothing. It was the last command in the GitHub quickstart, and the file showed no expected output under it.

Those eight files are the technical writing examples on this page, along with an error message and a how-to step I wrote today. The table below links each file and names the check it went through, and seven of the ten examples show a weaker version of a line beside the finished one.

All ten are software [technical documentation](/articles/technical-documentation/), so you won't find a white paper or a press release here. I'll go through the list first, then the edits.

## What counts as a technical writing example

A technical writing example is a finished document, or one part of it, that you can read and copy the shape of. A whole quickstart counts, and so does a single runbook step.

[Whatfix's list](https://whatfix.com/blog/technical-writing-examples/), updated on February 17, 2026, counts press releases and business plans among its twelve kinds. [Mintlify's page](https://www.mintlify.com/library/technical-writing-examples) from September 30, 2026 annotates seven pages from other companies' software docs, and its advice to "Test every command and code example against the supported product version" is the standard I've held my own examples to.

## The ten examples and the check I ran on each

Each row is one example, the check that ran on it on November 23, 2026 and what the check printed. The machine was Ubuntu 24.04 with Python 3.12.3 and Node.js 26.13.1.

| Kind | Example | Check | Result |
|---|---|---|---|
| Quickstart | [GitHub REST API quickstart](/static/examples/github-rest-quickstart.md), from the [quick start guide template](/articles/quickstart-guide/) | Every command in the file, by hand, with curl 8.5.0 and jq 1.7 | Step 2 printed the output under "See it work". The last command under "Next steps" printed nothing. |
| How-to step | The rate-limit step near the end of this page | The command, against the live GitHub API | `44` |
| API reference | The `POST /exports` entry in the [API documentation guide](/articles/api-documentation/) | `node api-reference-check.mjs` | `PASS: 9 of 9 documented responses match` |
| Error message | The missing-key response near the end of this page | The request, against a patched copy of the service | The rewritten body, with status 400 |
| Troubleshooting guide | [SQLite troubleshooting guide](/static/examples/troubleshooting-sqlite.md), from the [troubleshooting guide template](/articles/troubleshooting-guide-template/) | `python3 check_troubleshooting_guide.py --filled troubleshooting-sqlite.md` | `PASS`, with `causes checked: 6` |
| README | [mdoutline README](/static/examples/readme-example/README.md), from the [README template](/articles/readme-template/) | `python3 check_readme.py --filled --run readme-example/README.md` | `PASS`, with `command blocks run: 3 of 3` |
| Release notes | [SDK 4.0.0 release notes](/static/examples/release-notes-sdk-4.0.0.md), from the [release notes template](/articles/release-notes-template/) | `python3 check_release_notes.py --filled release-notes-sdk-4.0.0.md` | `PASS`, with `summary fields: 6/6` |
| Runbook | [Postgres connection slots runbook](/static/examples/runbook-postgres-connection-slots.md), from the [runbook template](/articles/runbook-template/) | `python3 check_runbook.py --filled runbook-postgres-connection-slots.md`, then all seven steps on Postgres 16.15 | `PASS`, with `steps checked: 7`. Each step printed what its Expect line describes. |
| Design doc | [Export records design doc](/static/examples/design-doc-persist-exports.md), from the [design doc template](/articles/design-doc-template/) | `python3 check_design_doc.py --filled design-doc-persist-exports.md` | `PASS`, with `sections: 8/8` |
| Postmortem | [Intake write failure postmortem](/static/examples/postmortem-intake-writes-failed.md), from the [postmortem template](/articles/postmortem-template/) | `python3 check_postmortem.py --filled postmortem-intake-writes-failed.md` | `PASS`, with `time to detect: 7 s` |

Every script printed PASS, and the one failure came from the quickstart, which has no script. If you came for a user manual or a standard operating procedure, I'd copy the how-to step for the manual and the runbook for the procedure.

Which reader question each kind answers is on my page about the [types of technical documentation](/articles/documentation-types/), so this page skips it.

## Technical writing examples with the edit shown

Each pair below is a weaker version of one line and the line as the file has it today. Every section says whether the weaker version is real, taken from the site's git history, or one I wrote for this page.

### API reference: a header that wasn't required

Both versions of this row are in git history. The reference entry for `POST /exports` listed its `Content-Type` header like this when the page was first committed on October 22, 2026:

```markdown
| `Content-Type` | Yes | `application/json` |
```

A correction committed 28 minutes later gave the row the text it has now:

```markdown
| `Content-Type` | Recommended | `application/json`. The service parses the body as JSON whatever this header says. |
```

I sent the request today with the header removed and again with `text/plain`, and both returned `202 Accepted`. A Required column is a claim about the service, so the correction also gave the check script a ninth case that sends no `Content-Type` and expects 202.

### Design doc: a rejection reason that was false

The design doc's two versions are in git history too. Its first version, also from October 22, 2026, rejected SQLite with this line:

```markdown
Rejected because: it adds a native dependency to a fixture that has none, for a single table that a line-per-record file handles.
```

The file now says:

```markdown
Rejected because: the fixture exists to be read, and a line-per-record file can be inspected with `cat` while someone follows the docs. SQLite's transactions add little for one append per request.
```

The first reason reads well and was wrong. The [Node.js 24 documentation](https://nodejs.org/docs/latest-v24.x/api/sqlite.html) lists a built-in `node:sqlite` module, added in v22.5.0 and marked "Release candidate", so SQLite would have added no dependency.

The rewrite still rejects SQLite, and its reason holds up, because a reader following the docs can open a line-per-record file with `cat`.

### Troubleshooting guide: the error text as the heading

The troubleshooting guide was written today and has no earlier version, so the first heading is a weak one I wrote for this page:

```markdown
## Database write problems
```

The heading in the file is the error text:

```markdown
## `database is locked`
```

I held a write lock open today on SQLite 3.45.1 and ran one insert from the `sqlite3` shell and from Python. The shell printed the first line for SQL passed as an argument and the second for SQL piped in, and Python printed the last:

```text
Error: stepping, database is locked (5)
Runtime error near line 1: database is locked (5)
sqlite3.OperationalError: database is locked
```

A reader arrives with one of those lines on screen and searches the page for it. Every line contains `database is locked`, and "Database write problems" matches none of them.

### Runbook: a step with its output and its undo

The runbook has one commit, so I wrote this weak step for the page:

```markdown
4. Kill the stuck database sessions.
```

Step 4 in the file gives the command, and the lines under it say what the output should be and what running it costs:

```bash
psql -U postgres -d shop -c "select pid, application_name, pg_terminate_backend(pid)
  from pg_stat_activity where state = 'idle in transaction'
  and now() - state_change > interval '5 minutes'"
```

```markdown
Expect: One row per leaked session, each ending in `t`.
If not: Zero rows means no transaction has been idle that long, so go back to step 3.
Undo: Irreversible: each terminated session's open transaction rolls back, so its uncommitted writes are lost.
```

The weak step leaves "stuck" to whoever is on call, and the real one defines it as idle inside a transaction for more than five minutes. I rebuilt the incident today on Postgres 16.15 in Docker, with 12 sessions that each updated a row of `orders` and never committed.

With those sessions idle for `00:03:48`, the command returned `(0 rows)`, which is the If not line. At `00:05:20` it returned 12 rows ending in `t`, and afterwards all 50 rows of `orders` still had the status `new`, which is the lost write the Undo line describes.

### Release notes: a fix that says who saw the bug

The release notes also have one commit, so I wrote this weak line for the page:

```markdown
- Fixed an issue with webhook retries.
```

The file has this line under Fixes:

```markdown
- Webhook retries no longer resend an event after a `2xx` response: integrations that saw duplicate deliveries.
```

The real line names the old behavior and the reader it reached, so someone who received duplicate deliveries knows the release fixes their bug. The checker printed PASS for both versions, because it never reads the Fixes list.

## An error message and a how-to step, written today

The site had no error message and no how-to step to show, so I wrote one of each today against tools I could run. Both weak versions are real, since one is a response the service sends now and the other is the quickstart command that printed nothing.

### Error message: say what the server received

The export service from the [technical documentation template](/articles/documentation-template/) answers a request that has no `Idempotency-Key` header with status 400 and this body:

```json
{"error":"invalid_key"}
```

A developer who sent no key is told that their key is invalid. I gave that case its own code and a message in a copy of the service, and the same request returned this:

```json
{"error":"missing_key","message":"This request has no Idempotency-Key header. Send one with 1 to 64 letters, digits or hyphens, and reuse it when you retry."}
```

The message says what the server received and what to send. The reference check then printed `FAIL: 1 of 9 documented responses differ` against the copy, because an error body is part of what the reference promises and its row has to change in the same commit.

### How-to step: show the output under the command

The quickstart command that printed nothing was `curl -sS -I https://api.github.com/rate_limit | grep -i x-ratelimit-remaining`. `curl -I` sends a HEAD request, and on November 23 GitHub answered a HEAD to `/rate_limit` with a 404 and a GET with a 200, so `grep` had no header to match.

Here is the step rewritten with a GET and the output under it, and the quickstart file now carries this command:

```bash
curl -sS https://api.github.com/rate_limit | jq '.resources.core.remaining'
```

You should see a number no higher than 60, and on my run it was this:

```text
44
```

A reader comparing their terminal with `44` sees at once that an empty line is wrong. If the step prints `0`, the unauthenticated requests for the hour are used up, and `jq -r '.resources.core.reset | todate'` on the same response prints when the count resets.

## What the checks don't catch

The scripts check that the parts of a document are present, and four of the seven weak versions put through them still passed:

| Weak version | Script | Result |
|---|---|---|
| Troubleshooting heading "Database write problems" | `check_troubleshooting_guide.py` | `PASS`, with its count of headings that quote the error text down from `3 of 4` to `2 of 4` |
| The same heading retyped as `database locked` | `check_troubleshooting_guide.py` | `FAIL`: the quoted text "is not in its Symptom block" |
| Release notes fix line "Fixed an issue with webhook retries." | `check_release_notes.py` | `PASS` |
| Breaking change field "What changed: Improved pagination." | `check_release_notes.py` | `PASS` |
| Breaking change field "Verify: Test your integration." | `check_release_notes.py` | `PASS` |
| README usage command replaced by a sentence | `check_readme.py` | `FAIL`: `'Usage' has no command in a bash, sh or shell code block` |
| Postmortem summary with no numbers, "a brief outage caused by a storage issue" | `check_postmortem.py` | `FAIL`: `Summary has no count with a unit (how many requests, users or minutes)` |

A script can demand a command or a number. It can't tell whether a heading is the text a reader will search for, and that call stays with the reviewer.

The release notes are for a made-up SDK, so their PASS covers structure only. The design doc proposes a change nobody has built, and the part I could run was its Problem section, where a retry after a restart got `202` and a new `exp_1` as the doc says.

For a check that needs a person, my page on [technical documentation best practices](/articles/documentation-best-practices/) has a one-page review card to fill in as you do a page's task from a clean account.

## FAQ

Each answer is about software documentation.

### What are examples of technical writing in software?

The table on this page lists ten, from a quickstart to a postmortem. Outside software the term also covers appliance manuals and standard operating procedures.

### What makes a technical writing example worth copying?

Copy an example that shows the output under each command, because that output is how a reader sees that a step has failed. Of the ten here, the one command that failed had no expected output under it.

### How do you test a technical writing sample?

Run every command it shows in a clean directory and compare what prints with what the page says. For a line with no command, such as a heading or a release note, write the weak version next to it and ask what a reader loses.
