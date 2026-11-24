---
category: technical-documentation
primary_query: troubleshooting guide template
siblings:
- runbook-template
- api-documentation
- quickstart-guide
date: 2026-11-23
description: "Start a troubleshooting entry with the error the reader sees, then show how to identify the cause and confirm the fix. Copy the Markdown template."
slug: troubleshooting-guide-template
status: published
takeaways:
- "Name the entry with the part of the error a reader can search for."
- "Give each possible cause its own check. The same SQLite error came from the file permissions and the directory permissions."
- "Give the reader a command that verifies the fix. The template checker checks for that command without running it."
title: "Troubleshooting Guide Template With a Filled Example and Checker"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write your troubleshooting pages and the rest of your developer documentation. [Get in touch](/services/developer-documentation/)."
---

SQLite printed `attempt to write a readonly database` when I removed write permission from the file. It printed the same thing when I put the permission back and removed it from the directory.

I'd want a troubleshooting guide to start with that exact error and show me how to tell those two cases apart. The Markdown template below gives each cause its own check, fix, and way to verify it.

## Copy the troubleshooting guide template

Troubleshooting is the part of [technical documentation](/articles/technical-documentation/) a reader opens with an error already on the screen.

The downloads include the Markdown template, a filled SQLite example, and a checker that reads the finished page. The checker needs Python 3.

- [Troubleshooting guide template (Markdown)](/static/templates/troubleshooting-guide-template.md)
- [Checker script](/static/templates/check_troubleshooting_guide.py)
- [Filled example: SQLite from the command line](/static/examples/troubleshooting-sqlite.md)

Start with the product version and the date you last reproduced the failures. Give each symptom its own heading and put the command and copied output beneath it.

When more than one cause can produce the same symptom, give each cause its own check and its own fix.

| Label | What goes under it |
|---|---|
| `Why:` | One or two sentences on how this cause produces the symptom |
| `Check:` | A command that tells this cause from the others |
| `Your cause if:` | The output that means this cause is the reader's |
| `Fix:` | The command that removes the cause |
| `Verify:` | The command that failed under Symptom, or one that shows the result |
| `Fixed when:` | The output the reader sees once the fix has worked |

## Name the symptom in the words the reader has

I misspelled the SQLite database filename and ran the same query through the command-line shell and through Python. The wording changed, but the middle of the error stayed the same.

| How the SQL reached SQLite | What the terminal printed |
|---|---|
| As an argument to `sqlite3` | `Error: in prepare, no such table: orders` |
| Piped to `sqlite3` | `Parse error near line 1: no such table: orders` |
| From Python's `sqlite3` module | `sqlite3.OperationalError: no such table: orders` |

I'd use `no such table` as the heading. It works for a person looking up the error from Python and for someone piping the query to the shell.

Keep the full output in the entry so the reader can check they have the same symptom.

## Make each check rule in a cause

The SQLite example covers these cases. The commands ran with SQLite 3.45.1 on Ubuntu 24.04.

| Entry heading | Causes | How I triggered it |
|---|---|---|
| `no such table` | 1 | Misspelled the database file name |
| `database is locked` | 2 | Held a write transaction open in a second `sqlite3` process |
| `attempt to write a readonly database` | 2 | Removed write permission from the file, then from its directory |
| A row that points at a missing parent row is inserted with no error | 1 | Inserted an order for a customer id that doesn't exist |

For the read-only error, trying the insert again just gives you the same message.

```text
$ sqlite3 shop.db "insert into orders (customer_id, total_cents) values (1, 2600);"
Error: stepping, attempt to write a readonly database (8)
```

Check the file and directory separately.

```bash
ls -l shop.db
ls -ld .
```

```text
-rw-r--r-- 1 dev dev 16384 Nov 23 19:18 shop.db
dr-xr-xr-x 2 dev dev 4096 Nov 23 19:18 .
```

Here the file is writable and the directory has no write bit. Fix the permission on the directory and run the insert again to verify it.

With a writable directory and a read-only file, fix the file instead.

## Check the finished guide

This checker verifies that the quoted heading occurs in the symptom output and that each cause has a command under Check, Fix, and Verify. It reads the Markdown.

It doesn't run the commands for you.

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

I intentionally retyped a heading and replaced a command with a sentence. Here's what the checker reported after those and two other edits.

```text
draft2.md: FAIL (4 problem(s))
  - entry '`database locked`': the heading quotes `database locked`, which is not in its Symptom block
  - cause 'Your user cannot write to the database file' of entry '`attempt to write a readonly database`' has no command in a code block under 'Fix:'
  - cause 'Foreign key enforcement is off for the connection' of entry 'A row that points at a missing parent row is inserted with no error' is missing 'Fixed when:'
  - 'Still stuck?' is missing 'Contact:'
```

I’d still reproduce each failure on the version named in the header and follow the entry as a reader. If you already know what failed and only need to restore service, the same checks can go in a [runbook](/articles/runbook-template/) in the order you want a responder to run them.

For a failure common on the first run, put the first check beside the command in the [quickstart](/articles/quickstart-guide/). Let the [API reference](/articles/api-documentation/) list all the error codes and send readers to the guide when a code has more than one cause.
