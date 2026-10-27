# Runbook: {{the alert, exactly as it pages}}

<!-- One runbook answers one alert. Keep each Field: line, and write None when a field does not apply.
     Check it with: python3 check_runbook.py --filled runbook.md -->

Service: {{the service and the system these steps act on}}
Alert: {{the exact alert name or error text that sends a responder here}}
Owner: {{the team that owns this runbook, and where to reach them}}
Last tested: {{YYYY-MM-DD, the last time someone ran every step}}
Impact: {{what users see while this is happening}}

## Before you start

Access: {{the roles, hosts and credentials the steps need}}
Stop and escalate if: {{the conditions where this runbook does not apply}}

## Diagnose

<!-- One check per step. Expect is the output that sends you to the next step;
     If not says where to go instead. -->

### 1. {{Confirm the symptom}}

```bash
{{the command, copied from a run that worked}}
```

Expect: {{the output you will see if this runbook applies}}
If not: {{the step to go to, or who to escalate to}}

### 2. {{Find the cause}}

```bash
{{the command}}
```

Expect: {{the output that confirms the cause}}
If not: {{the step to go to, or who to escalate to}}

## Mitigate

<!-- Each change gets an Undo line: the command that reverses it,
     or "Irreversible:" and what is lost. -->

### 3. {{Make one change}}

```bash
{{the command}}
```

Expect: {{the output that shows the change worked}}
If not: {{the step to go to, or who to escalate to}}
Undo: {{the command that reverses this step, or "Irreversible:" and what it loses}}

## Verify

### 4. {{Check that users are no longer affected}}

```bash
{{the command}}
```

Expect: {{the healthy output}}
If not: {{the step to go back to, or who to escalate to}}

## Escalate

Escalate to: {{the team or rotation, and how to page them}}
Escalate after: {{N minutes without the healthy output in Verify}}
Include: {{the outputs and times the next responder needs}}

## Follow-up

{{The ticket that removes the cause, and the date this runbook was last changed.}}
