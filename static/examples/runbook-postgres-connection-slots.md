# Runbook: checkout-api cannot connect to Postgres (connection slots full)

Service: checkout-api and its Postgres 16 database `shop`
Alert: checkout-api logs `FATAL:  remaining connection slots are reserved for roles with the SUPERUSER attribute`
Owner: Payments platform team, #payments-oncall
Last tested: 2026-10-28
Impact: Checkout requests fail with a 500 while the API cannot open a database connection.

## Before you start

Access: A shell with `psql` that reaches the database host, and the `postgres` superuser. Superusers connect through the slots Postgres reserves for them (`superuser_reserved_connections`, 3 by default), so this access still works while the alert fires.
Stop and escalate if: The database is unreachable or refuses the superuser too. That is a different incident, and this runbook does not apply.

## Diagnose

### 1. Confirm the application role is locked out

```bash
psql -U app -d shop -c 'select 1'
```

Expect: `FATAL:  remaining connection slots are reserved for roles with the SUPERUSER attribute`
If not: If the query returns a row, the slots have freed up, so go to step 6. Any other error is a different incident, so escalate.

### 2. Count sessions by application and state

```bash
psql -U postgres -d shop -c "select usename, application_name, state, count(*)
  from pg_stat_activity where backend_type = 'client backend'
  group by 1, 2, 3 order by 4 desc"
```

Expect: One application holds most sessions in the `idle in transaction` state.
If not: If most sessions are `active`, the slots are full of real work, and terminating them cancels it. Do not terminate anything, and escalate to the owner of the busiest application.

### 3. Check how long those transactions have been open

```bash
psql -U postgres -d shop -c "select pid, application_name, now() - state_change as idle_for, query
  from pg_stat_activity where state = 'idle in transaction'
  order by idle_for desc limit 5"
```

Expect: Sessions idle for several minutes after a write, which a request handler should have committed or rolled back.
If not: If every session has been idle for under a minute, they may be requests still in flight. Wait two minutes and run this step again.

## Mitigate

### 4. Terminate transactions idle for more than five minutes

```bash
psql -U postgres -d shop -c "select pid, application_name, pg_terminate_backend(pid)
  from pg_stat_activity where state = 'idle in transaction'
  and now() - state_change > interval '5 minutes'"
```

Expect: One row per leaked session, each ending in `t`.
If not: Zero rows means no transaction has been idle that long, so go back to step 3.
Undo: Irreversible: each terminated session's open transaction rolls back, so its uncommitted writes are lost.

### 5. Time out the next leaked transaction automatically

```bash
psql -U postgres -d shop -c "alter role app set idle_in_transaction_session_timeout = '5min'"
```

Expect: `ALTER ROLE`. The setting applies to new `app` sessions only.
If not: Escalate to the database team with the error.
Undo: `psql -U postgres -d shop -c "alter role app reset idle_in_transaction_session_timeout"`

## Verify

### 6. Confirm the application role can connect

```bash
psql -U app -d shop -c 'select 1'
```

Expect: One row containing `1`.
If not: Go back to step 2.

### 7. Confirm nothing else was cancelled

```bash
psql -U postgres -d shop -c "select usename, application_name, state, count(*)
  from pg_stat_activity where backend_type = 'client backend'
  group by 1, 2, 3 order by 4 desc"
```

Expect: No `idle in transaction` sessions from checkout-api, and every session that was `active` in step 2 is still there.
If not: Escalate to the owners of any application whose sessions are missing.

## Escalate

Escalate to: The payments platform on-call, through the #payments-oncall page.
Escalate after: 15 minutes without the healthy output in step 6.
Include: The output of step 2, the rows step 4 terminated, and the time the alert started.

## Follow-up

Open a ticket for the checkout-api code path that returns without committing or rolling back. Keep the role timeout from step 5 until that fix ships.
