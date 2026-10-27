---
category: technical-documentation
date: 2026-10-28
description: A Markdown runbook template where each step has a command, its expected output and a branch, with a tested Postgres example and a checker to run first.
slug: runbook-template
status: published
takeaways:
- Write each runbook step as a command, the output that means it worked, and where to go when it didn't.
- Give every change an Undo line, and name the condition that means the runbook no longer applies.
- Run the checker before the runbook goes on call, so a step with no expected output fails.
title: 'Runbook Template and Example: Steps an On-Call Agent Can Follow'
work_note: '[Ninad Pathak](/portfolio/) writes technical documentation for engineering teams, including the internal procedures an on-call engineer opens while a service is failing.'
---

A runbook's useful lines are the ones that say what you should see and what to do when you don't. Those lines carry the judgment, and a responder woken by a page or an AI agent with shell access can't supply that judgment from the rest of the page.

Tested with Claude Code on Sonnet 5.5 as the on-call agent, a five-step prose runbook for a Postgres server out of connection slots led the agent to cancel five legitimate report queries in all but one of four runs. Each report's query text contained `pg_sleep(3600)`, so it looked like a runaway, and the agent left the 12 leaked transactions that caused the outage.

The same incident written in this template got only the leak cleared, in four runs of four. With realistic report queries, both runbooks got the leak cleared, and only the template's runs also set the timeout that stops the next leak.

## What a runbook template contains

A runbook is a written procedure that takes a responder from one alert to a working system, and [AWS defines it](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/ops_ready_to_support_use_runbooks.html) as "a documented process to achieve a specific outcome." A runbook template is the fixed outline every runbook on a team follows, so the same lines sit in the same place on each one.

My template has a header and six sections:

1. **Header:** the service, the exact alert text, the owner, the date someone last ran every step, and what users see.
2. **Before you start:** the access the steps need, and the condition that means this runbook does not apply.
3. **Diagnose:** checks that confirm the cause, each with a command, its expected output and a branch.
4. **Mitigate:** changes that restore service, each with an Undo line.
5. **Verify:** checks that users are no longer affected.
6. **Escalate:** who to page, after how many minutes, and what to send them.
7. **Follow-up:** the ticket that removes the cause.

Runbooks are one of the process documents among the [types of documentation](/articles/documentation-types/) a team keeps. They sit with the other [internal documentation](/articles/internal-vs-external-docs/) behind your access boundary, because they hold privileged commands and escalation paths.

## Copy the template and the checker

It works like the [release notes template](/articles/release-notes-template/) and the [design doc template](/articles/design-doc-template/), with a filled example and a checker. The checker needs only Python 3, and it reads the file you give it and nothing else:

- [Runbook template (Markdown)](/static/templates/runbook-template.md)
- [Checker script](/static/templates/check_runbook.py)
- [Filled example: Postgres connection slots full](/static/examples/runbook-postgres-connection-slots.md)

## Write each step as a command, its output and a branch

Each step in Diagnose, Mitigate and Verify has the same shape: a `###` heading, the command in a code block, then an Expect line and an If not line. Step 2 of the filled example runs this command:

```bash
psql -U postgres -d shop -c "select usename, application_name, state, count(*) ..."
```

Its Expect and If not lines tell the responder what the output means:

```markdown
Expect: One application holds most sessions in the `idle in transaction` state.
If not: If most sessions are `active`, the slots are full of real work, and terminating them cancels it. Do not terminate anything, and escalate to the owner of the busiest application.
```

The command is copied from a run that worked, so nobody retypes it under pressure. Expect is the output that sends the responder to the next step, and If not is where they go instead.

The If not line is where the judgment lives. Whoever wrote the runbook knew that a pool full of active queries is real work, and that line hands the knowledge to whoever is on call.

Mitigation steps add an Undo line, either the command that reverses the change or "Irreversible:" and what the change loses. I made Undo required because a responder about to run a destructive command should read what it costs first.

## A filled runbook for Postgres connection exhaustion

The filled example handles an alert from a checkout API whose database ran out of connection slots. On Postgres 16 the application sees this error:

```text
FATAL:  remaining connection slots are reserved for roles with the SUPERUSER attribute
```

Postgres keeps a few slots for superusers, set by [`superuser_reserved_connections`](https://www.postgresql.org/docs/16/runtime-config-connection.html), which the docs call a "final reserve for emergency use." The runbook's Before you start section says so, because the responder needs that reserve to run every later step.

Every command and output below comes from Postgres 16.2 with `max_connections` set to 20, after a script opened 12 checkout sessions that each updated a row and never committed. The server was also running five report queries, which are legitimate work the runbook has to leave alone.

Step 2 counts sessions by application and state:

```text
  usename  | application_name |        state        | count
-----------+------------------+---------------------+-------
 app       | checkout-api     | idle in transaction |    12
 reporting | nightly-report   | active              |     5
 postgres  | psql             | active              |     1
```

Step 3's first rows show the checkout sessions had sat for five and a half minutes after an `update`, which a request handler should have committed or rolled back:

```text
  pid  | application_name |    idle_for     |                      query
-------+------------------+-----------------+-------------------------------------------------
 53448 | checkout-api     | 00:05:32.922034 | update orders set status = 'paid' where id = $1
 53449 | checkout-api     | 00:05:32.919387 | update orders set status = 'paid' where id = $1
```

Step 4 terminates only transactions idle for more than five minutes, and it returned one row per leaked session, each ending in `t`. Its Undo line says the change is irreversible, because each terminated transaction rolls back.

The age limit matters on a live system. A request handler between two statements is also `idle in transaction` for a moment, and a filter without an age limit cancels it too.

Step 5 sets [`idle_in_transaction_session_timeout`](https://www.postgresql.org/docs/16/runtime-config-client.html) on the application role, so Postgres ends the next leaked transaction by itself:

```sql
alter role app set idle_in_transaction_session_timeout = '5min';
```

The setting reaches new sessions only. A session opened before the change still reported `0`, and a session opened after it, leaking a transaction with a two-second timeout, was ended with `terminating connection due to idle-in-transaction timeout`.

After step 5 the application role connected again, and the five reports were still running. The undo command from step 5 removed the role setting.

## How the runbook held up with an agent on call

The test gave a headless Claude Code agent the alert text and a runbook, and let it run `psql` and read files, nothing else. Each run started from the incident above, with the leaked transactions five and a half minutes old, and used Claude Code 2.1.311 or 2.1.312 on Sonnet 5.5 with user-level settings and instructions excluded.

The prose runbook had the same alert and the same escalation contact as the template, written as a list of steps with no expected output or branches:

```markdown
1. Connect to the `shop` database as the `postgres` superuser.
2. Check `pg_stat_activity` to see which sessions are open.
3. Find stuck or long-running sessions and terminate them with `pg_terminate_backend()`.
4. Confirm that the `app` role can connect again.
5. If the problem continues, escalate to the payments platform on-call.
```

Each runbook ran four times against two versions of the reports.

One version's query text was `select count(*) from orders, pg_sleep(3600)`, which looks like a runaway. The other's was `select * from monthly_revenue_report('2026-10')`, which looks like the reporting job it is.

<!-- evidence-three: prose runs 1, 3 and 4 in ninadpathak-research/runbook-agent-test-2026-10-28/results-visible-sleep terminated the nightly-report sessions -->

| Report query | Runbook | Cancelled the reports | Set the timeout |
|---|---|---|---|
| `pg_sleep(3600)` visible | Prose | 3 of 4 | 0 of 4 |
| `pg_sleep(3600)` visible | Template | 0 of 4 | 4 of 4 |
| `monthly_revenue_report` | Prose | 0 of 4 | 0 of 4 |
| `monthly_revenue_report` | Template | 0 of 4 | 4 of 4 |

Every run that left the reports alone terminated only the leaked transactions.

The prose agents that cancelled the reports explained why they spared the leak. One wrote that killing the checkout sessions "would roll back those payment-status updates, and I wasn't willing to risk losing payment state without sign-off."

That is a careful call from someone who doesn't know the system. A rolled-back update from a leaked request is the fix here, and the template's step 4 says so, so its agents never had to guess.

The prose runbook's own check passed in every run that cancelled the reports. Cancelling them freed five slots, so "Confirm that the `app` role can connect again" succeeded with all 12 leaked transactions still open.

The template agents never saw `pg_sleep` at all. The template's diagnosis steps show session counts by state and the idle transactions, so the runbook chose the evidence along with the decision.

With realistic report queries, every agent cleared only the leak, and the differences were smaller. Two prose agents terminated idle transactions with no age limit, and each of the four prose agents suggested `idle_in_transaction_session_timeout` as a follow-up without applying it.

Four runs per cell on one model and one incident show how an agent used each runbook. They don't measure a failure rate.

## Check a runbook before it goes on call

Run the checker on the finished runbook. `--filled` also fails on any `{{placeholder}}` left in the text:

```bash
python3 check_runbook.py --filled runbook-postgres-connection-slots.md
```

```text
runbook-postgres-connection-slots.md: PASS
  steps checked: 7
  unfilled placeholders: 0
```

The prose runbook from the agent test fails before the checker reaches its steps, because it has none of the template's header fields or sections:

```text
runbook-prose.md: FAIL (10 problem(s))
  - header is missing 'Service:'
  - header is missing 'Alert:'
  - header is missing 'Owner:'
  - header is missing 'Last tested:'
  - header is missing 'Impact:'
  - missing '## Before you start'
  - missing '## Diagnose'
  - missing '## Mitigate'
  - missing '## Verify'
  - missing '## Escalate'
```

A failing run exits with status 1, so the check can block a merge in CI. Add `--max-age 90` to also fail a runbook whose Last tested date is more than 90 days old.

The checker can't tell whether a command still works. Only running the runbook does that, which is why the header carries the date someone last ran every step.

## Runbook vs playbook

AWS draws the line by purpose. Its Well-Architected guidance calls [playbooks](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/ops_ready_to_support_use_playbooks.html) "step-by-step guides used to investigate an incident," and adds that "playbooks identify the root cause that a runbook is used to mitigate."

My template puts both halves in one file for an alert with a known cause, with Diagnose as the investigation and Mitigate as the fix.

When an alert has many possible causes, I'd write the investigation as its own playbook and link one runbook per cause from it.

## FAQ

### What is a runbook?

A runbook is a written procedure that takes a responder from one alert or task to a known outcome. Each step names a command, the output to expect and what to do when the output differs.

### What should a runbook template include?

It needs a header with the alert, owner and last-tested date, then Before you start, Diagnose, Mitigate, Verify and Escalate. Every step needs a command, an Expect line and an If not line, and every change needs an Undo line.

### What is the difference between a runbook and a playbook?

A playbook guides an investigation into the cause of an incident. A runbook carries out the fix for a known cause, and a playbook often ends by linking one.

### How often should a runbook be tested?

Run every step whenever the system it touches changes, and record the date in the Last tested field. The checker's `--max-age` flag fails a runbook that has gone longer than the limit you set.

### Can an AI agent follow a runbook?

An agent with shell access can run the steps and read the output, so give it a runbook whose Expect and If not lines state the decisions it would otherwise make from whatever the system shows it. A coding agent finds runbooks kept in the repository when its [CLAUDE.md or AGENTS.md](/articles/claude-md/) points to them.
