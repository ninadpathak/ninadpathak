---
category: technical-documentation
primary_query: troubleshooting guide template
siblings:
- runbook-template
- api-documentation
- quickstart-guide
date: 2026-11-23
description: "A Markdown troubleshooting guide template where each entry starts from the exact error text, with a filled SQLite example and a checker script to run first."
slug: troubleshooting-guide-template
status: published
takeaways:
- Title each troubleshooting entry with the part of the error text every reader sees, and paste the full output under it.
- Give each cause its own check, because SQLite printed the same read-only error for a file without write permission and for a directory without it.
- Run the checker before you publish, so an entry with a retyped error message or a fix that has no command fails.
title: "Troubleshooting Guide Template With a Filled Example and Checker"
work_note: "This template is for the page a developer opens with an error already on screen, and troubleshooting pages are part of the developer documentation I write. I'm Ninad Pathak, a freelance technical writer, and I run every command on a page before it reaches you. [Ask me about yours](/services/developer-documentation/)."
---

Each entry in the troubleshooting guide template on this page starts from the error text a reader pastes into a search box and ends with a command that proves the fix worked. The template is a Markdown file with a filled SQLite example and a checker script, and the checker fails an entry that has a retyped error message or a fix with no command.

To fill the example, I broke a scratch SQLite database four ways on November 23, 2026 and pasted what the terminal printed. A query against a missing table printed a different line for each way the SQL reached SQLite, and every one contained `no such table: orders`.

So that entry's heading is `no such table`, the part of the text every reader will have on screen. A troubleshooting page is the piece of [technical documentation](/articles/technical-documentation/) a developer opens with an error already in front of them, and they find their entry by matching its words.

## What is a troubleshooting guide template?

A troubleshooting guide template is a fixed outline for the page a reader opens after something has failed, so every entry on that page answers the same questions in the same order. Cloudflare's docs style guide, on a page last updated August 20, 2026, says a troubleshooting page ["pairs each failure a reader hits with its cause and the steps that resolve it, organized by symptom rather than by question."](https://developers.cloudflare.com/style-guide/documentation-content-strategy/content-types/troubleshooting/)

My template has a header, one entry per symptom and a closing section:

1. **Header:** the product version the entries were reproduced on, and the date someone last reproduced them.
2. **Entry heading:** the error text in backticks, cut down to the part every reader sees.
3. **Symptom:** the failing command and its output, pasted from a terminal.
4. **Causes:** one `###` block per cause, with the likeliest cause first.
5. **Still stuck?:** what to collect, and where to send it.

Every cause block in the template has the same six labels:

| Label | What goes under it |
|---|---|
| `Why:` | One or two sentences on how this cause produces the symptom |
| `Check:` | A command that tells this cause from the others |
| `Your cause if:` | The output that means this cause is the reader's |
| `Fix:` | The command that removes the cause |
| `Verify:` | The command that failed under Symptom, or one that shows the result |
| `Fixed when:` | The output the reader sees once the fix has worked |

The parts match what other template pages for this search already ask for. [HelpDocs](https://www.helpdocs.io/templates/troubleshooting-guide/) lists seven sections that run from the symptom to related articles, and [Docsie](https://www.docsie.io/solutions/templates/planning/troubleshooting-guide/) lists six that end on prevention.

What I've added is output from real failures and a script that checks the finished page. HelpDocs' sample table has rows such as "Export never finishes", and Docsie's filled example calls a host named `api.internal`.

## Troubleshooting guide vs runbook vs error reference

A troubleshooting guide is for a reader who has a symptom and doesn't know the cause yet, which is what separates it from a runbook and from an error reference.

| Page | The reader arrives with | The page lists | The reader is done when |
|---|---|---|---|
| Troubleshooting guide | An error or wrong behavior, cause unknown | Symptoms, each with its causes | A command shows the symptom is gone |
| Runbook | An alert with a known cause | Steps to run in order | The Verify step prints the healthy output |
| Error reference | A status code or an error code | The codes a product returns | They know what the code means |

The site's [runbook template](/articles/runbook-template/) pairs each step with the output that means it worked, and a responder runs those steps from the top. A troubleshooting reader lands on one entry from a search, so I've made every entry carry its own symptom and its own commands.

Cloudflare's guide keeps the error reference off the troubleshooting page and calls a "complete per-code catalog" reference material. The responses table in my [API documentation example](/articles/api-documentation/) is a catalog like that for one endpoint, and a troubleshooting entry covers what one of its rows can't hold, such as a message with two causes.

## Copy the template, the example and the checker

All three files are plain text, and the checker needs only Python 3:

- [Troubleshooting guide template (Markdown)](/static/templates/troubleshooting-guide-template.md)
- [Checker script](/static/templates/check_troubleshooting_guide.py)
- [Filled example: SQLite from the command line](/static/examples/troubleshooting-sqlite.md)

## Start each entry from the exact error text

<!-- evidence-three: the table below has one row per line the failed query printed, and it has three rows --> The heading of an entry is the error text itself, copied from the output and cut down to the words every reader will see. A single failed query printed three different lines on the `sqlite3` shell 3.45.1 and Python 3.12.3, after I misspelled the file name as `shops.db`:

| How the SQL reached SQLite | What the terminal printed |
|---|---|
| As an argument to `sqlite3` | `Error: in prepare, no such table: orders` |
| Piped to `sqlite3` | `Parse error near line 1: no such table: orders` |
| From Python's `sqlite3` module | `sqlite3.OperationalError: no such table: orders` |

A heading that copied the first line whole wouldn't match what someone piping SQL or using Python sees. And the table name belongs to whoever hit the error, so the heading drops `orders` and keeps `no such table`.

The full lines stay in the entry's Symptom block, and the checker holds the heading to them. Any text in backticks in an entry heading has to appear word for word in that block, so a message retyped from memory fails.

## A filled troubleshooting guide for SQLite

The filled example covers four symptoms and six causes on a scratch database, `shop.db`, with a `customers` table and an `orders` table. Every command in it ran with the `sqlite3` shell 3.45.1 on Ubuntu 24.04 on November 23, 2026, and a script that reran the sequence from an empty directory printed the same errors.

| Entry heading | Causes | How I triggered it |
|---|---|---|
| `no such table` | 1 | Misspelled the database file name |
| `database is locked` | 2 | Held a write transaction open in a second `sqlite3` process |
| `attempt to write a readonly database` | 2 | Removed write permission from the file, then from its directory |
| A row that points at a missing parent row is inserted with no error | 1 | Inserted an order for a customer id that doesn't exist |

The read-only entry shows why each cause needs its own check. An insert printed the same line when the file had no write permission and again when only the directory lacked it:

```text
$ sqlite3 shop.db "insert into orders (customer_id, total_cents) values (1, 2600);"
Error: stepping, attempt to write a readonly database (8)
```

Only the permissions told the two causes apart, so the second cause's Check lists the file and its directory, and the `Your cause if:` line quotes the result:

```bash
ls -l shop.db
ls -ld .
```

```text
-rw-r--r-- 1 dev dev 16384 Nov 23 19:18 shop.db
dr-xr-xr-x 2 dev dev 4096 Nov 23 19:18 .
```

The file is writable and the directory isn't. SQLite's [result code list](https://www.sqlite.org/rescode.html) says a database counts as read-only when the process lacks permission to create a journal file "in the same directory as the database".

After `chmod u+w .` the same insert returned with no output and the row count went to 5 from 4, which is what the cause's `Fixed when:` line tells the reader to look for.

The locked entry orders its causes so that a failed first fix leads to the second cause. With another process partway through a write, rerunning the insert with `-cmd ".timeout 10000"` waited 4.5 seconds and then succeeded.

<!-- evidence-three: the second cause's Check in the filled example runs the insert with .timeout 3000 and that is a wait of 3 seconds --> Against a process that began a transaction and then slept for 300 seconds, an insert with a 3-second timeout printed `database is locked` again, and that output is the second cause's `Your cause if:` line.

The fourth entry has no error text to quote, because the bad insert prints nothing, so its heading is a plain sentence. SQLite's [foreign key documentation](https://www.sqlite.org/foreignkeys.html) says the constraints are "disabled by default" and have to be enabled for each connection.

Which means that entry's `Fixed when:` line is an error message. Once a connection runs `pragma foreign_keys = on`, the same insert fails with `Error: stepping, FOREIGN KEY constraint failed (19)`.

## Check a troubleshooting guide before you publish it

Run the checker with `--filled` on the finished page, and it prints PASS or a list of the lines to fix:

```bash
python3 check_troubleshooting_guide.py --filled troubleshooting-sqlite.md
```

```text
troubleshooting-sqlite.md: PASS
  entries checked: 4
  causes checked: 6
  entries whose heading quotes the error text: 3 of 4
  unfilled placeholders: 0
```

The script reads the one file you give it, skips HTML comments, and makes these checks:

| Part of the page | The checker fails when |
|---|---|
| Header | `Applies to:` or `Last reproduced:` is missing or empty |
| Header | `Last reproduced:` isn't a calendar date, or is older than the `--max-age` you pass |
| Whole file | A code block is opened and never closed |
| Whole file | No entry exists, or two entries share a heading |
| Whole file | With `--filled`, a `{{placeholder}}` is left |
| Entry | The first line isn't `Symptom:`, or no filled code block follows it |
| Entry | Text in backticks in the heading isn't in the Symptom block (a trailing `...` is ignored) |
| Entry | It has no `###` cause |
| Cause | `Why:`, `Your cause if:` or `Fixed when:` is missing or empty |
| Cause | `Check:`, `Fix:` or `Verify:` has no filled code block under it |
| Closing section | `## Still stuck?` is missing, or lacks `Collect:` or `Contact:` |

To see it fail, I copied the example to `draft2.md` and made four edits. I retyped one heading as `database locked`, swapped one Fix block for the sentence "Make sure the database file is writable.", and deleted two lines:

```text
draft2.md: FAIL (4 problem(s))
  - entry '`database locked`': the heading quotes `database locked`, which is not in its Symptom block
  - cause 'Your user cannot write to the database file' of entry '`attempt to write a readonly database`' has no command in a code block under 'Fix:'
  - cause 'Foreign key enforcement is off for the connection' of entry 'A row that points at a missing parent row is inserted with no error' is missing 'Fixed when:'
  - 'Still stuck?' is missing 'Contact:'
```

That run exited with status 1, which lets a CI job stop the merge. Add `--max-age 180` to also fail a page whose `Last reproduced:` date is more than 180 days old.

A PASS means the parts are present. It can't tell you whether `chmod u+w .` still clears the error, and the only test for that is breaking the product again.

## When the template doesn't fit

<!-- evidence-three: the "If it fails" table in the quick start guide's filled example has three rows, one per error --> The template is the wrong shape for a product area with only a few known failures, and for a failure whose next step depends on the state the system is in. The [quick start guide template](/articles/quickstart-guide/) keeps three errors in an "If it fails" table under its steps, and Cloudflare's guide moves entries to a dedicated page once an area passes roughly five.

For the state-dependent kind, the [technical documentation template](/articles/documentation-template/) writes its troubleshooting page as a table with a row for each state.

The example also covers one version of SQLite, 3.45.1, which is what Ubuntu 24.04 packages. SQLite's documentation showed shell sessions from version 3.54.0 when I read it on November 23, 2026, and I haven't run these errors on that version.

The checker also fails a Fix with no code block. For a fix made in a settings file or a dashboard, I'd put the lines to change or the menu path in the block.

## FAQ

An entry below means one symptom, and a cause means one `###` block under it.

### What should a troubleshooting guide include?

It needs a header with the product version and the date the entries were last reproduced, then one entry per symptom that starts from the pasted output. Every cause under an entry gets a command to confirm it and a command to fix it, with the output that proves the fix worked.

### What is the difference between a troubleshooting guide and a runbook?

A troubleshooting guide starts from a symptom and helps the reader find which cause applies. A runbook starts from an alert with a known cause and gives ordered steps, each with its expected output.

### How often should you update a troubleshooting guide?

Reproduce the entries whenever the product version in the header changes, and write the new date in `Last reproduced:`. The checker's `--max-age` flag fails a page that has gone longer than the limit you set.
