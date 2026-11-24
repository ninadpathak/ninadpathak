# Postmortem: {{what users saw and what caused it, in one line}}

<!-- One postmortem covers one incident on a software service. Keep every Field: line.
     Write people by role ("the on-call engineer") unless your team prefers names.
     Check it with: python3 check_postmortem.py --filled postmortem.md -->

Status: {{Draft | In review | Final}}
Service: {{the service that failed}}
Incident date: {{YYYY-MM-DD}}
Authors: {{who wrote this}}

## Summary

{{Two to four sentences. Say what users saw, how many requests, users or accounts it hit and for how long, the cause in one line, and what stopped it. The count comes before the cause.}}

## Impact

What users saw: {{the error or the wrong behaviour, in the user's terms}}
Scope: {{a count with its unit and its denominator, such as "155 of 156 write requests"}}
Duration: {{the time from Impact starts to Mitigated in the timeline, such as "21 s" or "1 h 12 min"}}
Data loss: {{what was lost, corrupted or exposed, with a count, or None}}

## Timeline

Time zone: {{UTC, or an offset such as UTC+05:30}}

<!-- One row per event, oldest first, starting before the incident. A row's time is HH:MM or HH:MM:SS
     on the incident date, or YYYY-MM-DD HH:MM when the incident crossed midnight.
     Tag one row each **Impact starts**, **Detected** and **Mitigated**, and one **Resolved** once the
     cause is removed. Evidence is the log line, graph or command output the time came from. -->

| Time | Event | Evidence |
|---|---|---|
| {{HH:MM}} | {{the last change or condition before the incident}} | {{deploy log, commit or graph}} |
| {{HH:MM}} | **Impact starts**: {{the first failed request or the first user who saw it}} | {{log line}} |
| {{HH:MM}} | **Detected**: {{the alert that fired, or the report that came in}} | {{alert history or ticket}} |
| {{HH:MM}} | {{a decision, a finding or a dead end}} | {{command output}} |
| {{HH:MM}} | **Mitigated**: {{the change after which users stopped seeing the failure}} | {{log line or graph}} |
| {{HH:MM}} | **Resolved**: {{the change that removed the cause}} | {{commit or deploy log}} |

## Detection and response

Detected by: {{the alert name, or who reported it}}
Time to detect: {{the time from Impact starts to Detected}}
Mitigation: {{what stopped the impact, and what it cost}}
Resolution: {{what removed the cause, or the action item that will}}

## Root cause

Trigger: {{the event that started the incident}}
Mechanism: {{how the trigger became the impact, step by step, naming the `setting`, `file`, `function` or `error text` involved}}
Believed before: {{what the team expected to happen instead, and why that looked safe}}

Contributing factors:

- {{a condition that made the incident possible, longer or harder to see}}

## Lessons learned

What went well:

- {{what worked and should be kept}}

What went wrong:

- {{what added time or confusion}}

Where we got lucky:

- {{what could have made it worse and didn't, or None}}

## Action items

<!-- Type is prevent, detect, mitigate or process. Status is Open, Done YYYY-MM-DD, or Won't do: the reason. -->

| Action | Type | Owner | Due | Status |
|---|---|---|---|---|
| {{starts with a verb and says what will exist when it is done}} | {{prevent}} | {{one person or role}} | {{YYYY-MM-DD}} | {{Open}} |
