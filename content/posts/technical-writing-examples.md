---
category: technical-documentation
primary_query: technical writing examples
siblings:
- documentation-types
- documentation-template
- documentation-best-practices
date: 2026-11-23
description: "Ten software documentation examples, with before-and-after edits and the commands and checks that show where each version holds up."
slug: technical-writing-examples
status: published
takeaways:
- "Put the old line beside the edit. Run the request or command that can settle what it should say."
- "A request without Content-Type got 202, so the reference now says the header is recommended."
- "A checker passed a vague troubleshooting heading and a vague release note. Both needed a person to read the line in context."
title: "Technical Writing Examples: 10 Tested Samples With Edits Shown"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write quickstarts, reference pages and tutorials like the samples on this page. [Get in touch](/services/developer-documentation/)."
---

The reference said `Content-Type` was required. I left it out and got `202 Accepted`.

Then I sent `text/plain` and got another 202.

That's the kind of edit I want before a page goes out. Change what the table promises and add a test for the request that proved it wrong.

These examples show the old line beside the edit and, where you can run something, what it printed.

## The examples and what I checked

These examples are all [technical documentation](/articles/technical-documentation/) for software. A first run, a reference entry, and an incident procedure answer different questions.

[How to pick the document type](/articles/documentation-types/)

These examples cover software docs, from a first API call to the steps someone takes during an incident. The linked files are complete samples.

The checks ran on November 23 on Ubuntu 24.04.

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

## Fix the claim before you polish the line

The old API reference row and the correction are both in Git. The first said the header was required.

The new one says what the service actually does.

```markdown
| `Content-Type` | Yes | `application/json` |
```

```markdown
| `Content-Type` | Recommended | `application/json`. The service parses the body as JSON whatever this header says. |
```

The design doc had a similar problem. It rejected SQLite on the grounds that we'd need a native dependency, but Node already shipped `node:sqlite`.

The rewrite still rejects SQLite because a plain file lets someone inspect the fixture with `cat`. That was the property the example needed.

[Node.js SQLite documentation](https://nodejs.org/docs/latest-v24.x/api/sqlite.html)

```markdown
Rejected because: it adds a native dependency to a fixture that has none, for a single table that a line-per-record file handles.
```

```markdown
Rejected because: the fixture exists to be read, and a line-per-record file can be inspected with `cat` while someone follows the docs. SQLite's transactions add little for one append per request.
```

## Write for the screen the reader is looking at

The export service below comes from a [complete documentation example](/articles/documentation-template/) with a reference page you can check against it.

I could have titled an entry “Database write problems.” I made SQLite fail from the shell and from Python, and this is what readers would actually have in front of them.

```text
Error: stepping, database is locked (5)
Runtime error near line 1: database is locked (5)
sqlite3.OperationalError: database is locked
```

I'd use `database is locked` as the heading. It's the part all of those readers can search for.

An error message has the same job. The export service returned this when the request sent no idempotency key.

```json
{"error":"invalid_key"}
```

I gave the missing-key case its own response in a copy of the service.

```json
{"error":"missing_key","message":"This request has no Idempotency-Key header. Send one with 1 to 64 letters, digits or hyphens, and reuse it when you retry."}
```

Now the message says what the server received and what to send next. The reference checker failed one case against the copy.

The error body is part of the interface, so the reference has to change with it.

## Let the reader tell when a command worked

The last command in my GitHub quickstart printed nothing. There was no example output under it.

For a rate-limit check, I'd show the reader both the command and the shape of its result.

```bash
curl -sS https://api.github.com/rate_limit | jq '.resources.core.remaining'
```

```text
44
```

That number was the remaining allowance in my run. The reader should expect an integer, and their number will depend on their own requests.

An on-call reader also needs to know what happens if there's no result. In the Postgres runbook, “Kill the stuck database sessions” would make the responder decide what stuck means.

The actual step targets sessions idle in a transaction for more than five minutes and explains what a zero-row result means. It also says what the command can't recover.

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

My test got zero rows before the threshold and 12 rows ending in `t` after it. Those uncommitted changes rolled back, as the step says they will.

## Give the reviewer the parts a script can't see

The release notes checker passed both “Fixed an issue with webhook retries” and the line explaining what the fix does. The second tells people who saw duplicate deliveries that they can expect a change.

```markdown
- Webhook retries no longer resend an event after a `2xx` response: integrations that saw duplicate deliveries.
```

Several checks made the same distinction. They could ask for a command, a heading, or a number.

A loose sentence could still pass.

| Weak version | Script | Result |
|---|---|---|
| Troubleshooting heading "Database write problems" | `check_troubleshooting_guide.py` | `PASS`, with its count of headings that quote the error text down from `3 of 4` to `2 of 4` |
| The same heading retyped as `database locked` | `check_troubleshooting_guide.py` | `FAIL`: the quoted text "is not in its Symptom block" |
| Release notes fix line "Fixed an issue with webhook retries." | `check_release_notes.py` | `PASS` |
| Breaking change field "What changed: Improved pagination." | `check_release_notes.py` | `PASS` |
| Breaking change field "Verify: Test your integration." | `check_release_notes.py` | `PASS` |
| README usage command replaced by a sentence | `check_readme.py` | `FAIL`: `'Usage' has no command in a bash, sh or shell code block` |
| Postmortem summary with no numbers, "a brief outage caused by a storage issue" | `check_postmortem.py` | `FAIL`: `Summary has no count with a unit (how many requests, users or minutes)` |

I'd use the checker for the parts it can prove. During review, I'd put the developer's error, output, or prior behavior next to the sentence they're about to read.

If the sentence doesn't tell them what to do with what's on their screen, I'd fix that before asking whether it sounds better.

For a page your team already owns, use the same test on its first command. [Documentation best practices](/articles/documentation-best-practices/)
