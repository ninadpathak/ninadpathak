---
category: technical-documentation
primary_query: postmortem template
siblings:
- runbook-template
- cloudflare-kv-cache-incident-report
- troubleshooting-guide-template
date: 2026-11-23
description: "A Markdown postmortem template for software incidents, with a filled example from a test incident and a checker that derives time to detect from the timeline."
slug: postmortem-template
status: published
takeaways:
- Put the count of failed requests or affected users in the summary before the cause, because the checker fails a summary with no number in it.
- Tag the timeline rows where impact started, where it was detected and where it was mitigated, so the checker can recompute the durations the postmortem states.
- A health check that only reads returned 200 at every poll of the test incident while 156 of 156 write requests failed.
title: "Postmortem Template for Software Incidents, With a Checker"
work_note: "Your team writes the postmortem, and your users still need a page that explains the error they saw. I'm Ninad Pathak, a freelance technical writer, and I write troubleshooting pages after running the product myself. [Ask me about that page](/services/developer-documentation/)."
---

The postmortem template on this page is a Markdown file with seven sections, and it comes with a filled example and a checker script. The checker recomputes the time to detect and the time to mitigate from the timeline, so a postmortem that states 20 seconds fails when its timeline shows 21.

The example's numbers come from a small API built on November 23, 2026, with a 2 MiB size limit on its database file. Under steady traffic it rejected 156 of 156 write requests for 21 seconds with `disk I/O error`, while its health check kept returning 200.

A postmortem is the piece of [technical documentation](/articles/technical-documentation/) a team writes after a failure, for the people who weren't on call. The page covers software incidents such as an outage or a failed deploy, so it has nothing for a workplace incident report form.

## What is a postmortem template?

A postmortem template is a fixed outline for the written record of one incident, which the team fills in once the incident is over. Atlassian's guide also calls a postmortem a post-incident review, and a team that calls its internal write-up an incident report means the same document.

My template has a header and seven sections:

1. **Header:** status, service, incident date and authors.
2. **Summary:** what users saw, how many and for how long, then the cause in one line.
3. **Impact:** what users saw, a count with its unit, the duration and any data loss.
4. **Timeline:** one row per event in one stated time zone, each with its evidence.
5. **Detection and response:** the alert, the time to detect, the mitigation and the resolution.
6. **Root cause:** the trigger, the mechanism, what the team believed beforehand and the contributing factors.
7. **Lessons learned:** what went well, what went wrong and where the team got lucky.
8. **Action items:** each with a type, one owner, a due date and a status.

## Copy the template, the example and the checker

The checker needs only Python 3 and reads the one file you give it:

- [Postmortem template (Markdown)](/static/templates/postmortem-template.md)
- [Checker script](/static/templates/check_postmortem.py)
- [Filled example: intake rejected every write for 21 seconds](/static/examples/postmortem-intake-writes-failed.md)

## What Google, PagerDuty and Atlassian ask for

Google's example postmortem, PagerDuty's template and Atlassian's template each have a counterpart for all seven of my sections, under different names. I read them on November 23, 2026, and the last row lists the parts I left out:

| My section | [Google's example](https://sre.google/sre-book/example-postmortem/), in the SRE book's first edition (2016) | [PagerDuty's template](https://docs.pagerduty.com/ops-guides/incident-response-guide/postmortem-template) | [Atlassian's template](https://www.atlassian.com/incident-management/postmortem/templates) |
|---|---|---|---|
| Summary | Summary | Overview, What Happened | Incident summary |
| Impact, Timeline | Impact, Timeline | Impact, Timeline | Impact, Timeline |
| Detection and response | Detection, Resolution | Resolution | Detection, Response, Recovery |
| Root cause | Root Causes, Trigger | Contributing Factors | Leadup, Fault, Five Whys, Root cause |
| Lessons learned | Lessons Learned | How'd We Do? | Lessons learned |
| Action items | Action Items | Action Items | Corrective actions |
| Left out | Supporting information | Responders, Messaging | Backlog check, Recurrence |

Mine differs in four places:

| Where mine differs | Why |
|---|---|
| Each timeline row has an Evidence cell | PagerDuty's template has a Data Link column, and its [step-by-step guide](https://docs.pagerduty.com/ops-guides/postmortem-best-practices/step-by-step) wants a metric or page behind every item |
| Root cause is split into a trigger, a mechanism and contributing factors | Google and Atlassian ask for a root cause, and PagerDuty's guide says to "Find contributing factors, not the root cause" |
| Root cause has a `Believed before:` line | Google's example, PagerDuty's template and Atlassian's template have no field for what the team expected |
| Each action item has a due date | Google's example gives its nine action items an owner and no due date, and [Atlassian's handbook](https://www.atlassian.com/incident-management/handbook/postmortems) asks "Who will take the actions and by when?" |

The `Believed before:` line comes from my essay on [Cloudflare's KV cache incident report](/articles/cloudflare-kv-cache-incident-report/), which argues that what a team believed when it shipped is the part other teams can learn from. That essay is also why the summary states the count before the cause.

[OpenStatus's guide](https://www.openstatus.dev/guides/postmortem-template) from November 20, 2026 also ranks for this search, with a Markdown template and an example written "for a fictional startup", where mine records an incident that happened.

## A filled postmortem example from a test incident

The filled example is the postmortem for a test incident I caused on a local service on November 23, 2026, and its numbers and error text come from published logs, such as [the log of each command and its output](/static/examples/postmortem-intake-api/logs/response.log). [The service](/static/examples/postmortem-intake-api/service.py), which I named intake, is a Python 3.12.3 `http.server` program that stores events in SQLite 3.45.1 on Ubuntu 24.04.

I started it under `ulimit -f 2048`, a 2 MiB cap on any file the process writes. The cap stands in for a small volume, which I had no root to mount.

A load script sent about ten requests a second, and a monitor script polled every 5 seconds for a 5xx rate of 5% or more. The first write failed at 19:54:08 UTC and the alert printed 7 seconds later, and my second command after it put the database file's size beside the process limit and the free disk:

```text
$ ls -l data/; grep "Max file size" /proc/$(cat logs/service.pid)/limits; df -k data | tail -1
total 2052
-rw-r--r-- 1 dev dev 2097152 Nov 23 19:54 events.db
Max file size             2097152              2097152              bytes     
/dev/sda1      100476656 88269364  12190908  88% /
```

The file was exactly as long as the limit, and the disk had 12 GB free. SQLite's `disk I/O error` points at the disk, and I checked `/proc/<pid>/limits` only because I'd set the limit myself five minutes earlier.

`prlimit` couldn't raise the limit on the running process, so I restarted the service under a 64 MiB limit at 19:54:29 and the errors stopped. A cap that keeps the newest 1,500 events removed the cause 39 seconds later.

The example's timeline has 15 rows, and the checker reads the bold tags on rows like these two:

```markdown
| Time | Event | Evidence |
|---|---|---|
| 19:54:08 | **Impact starts**: the first `POST /events` returns 500 with `disk I/O error`, after 2,040 accepted writes | `logs/client-incident-window.log` at 19:54:08.553 |
| 19:54:15 | **Detected**: the monitor prints `ALERT Intake5xxRate: 81% of requests returned 5xx for two polls` | `logs/monitor.log` |
```

Now, a planted failure with its author on call says little about how long a real team would take. What it does show is in the Contributing factors list, where `GET /health` runs `select 1` and returned 200 at each of the 4 polls during the incident.

The obvious fix is a write probe in the health check, and that action item is marked `Won't do`. In a second run a one-character insert still succeeded at the limit and every 900-character write failed, so a small probe would have passed.

The other four action items are done. In that run, with the cap turned off, a new alert at 80% of the limit printed 49 seconds before the first failed write.

The restart belongs in a runbook for this alert, and my [runbook template](/articles/runbook-template/) gives each step the output that means it worked. And `disk I/O error` on a disk that isn't full has more than one cause, which is the case the [troubleshooting guide template](/articles/troubleshooting-guide-template/) is built for.

## Check a postmortem before review

Run the checker with `--filled` on the finished postmortem, and it prints PASS with the two durations it derived or a list of lines to fix:

```bash
python3 check_postmortem.py --filled postmortem-intake-writes-failed.md
```

```text
postmortem-intake-writes-failed.md: PASS
  timeline rows checked: 15, time zone UTC
  time to detect: 7 s
  time to mitigate: 21 s
  action items with an owner and a due date: 4
  action items marked Won't do, with a reason: 1
  unfilled placeholders: 0
```

The script skips HTML comments and code blocks, and makes these checks:

| Part | The checker fails when |
|---|---|
| Header | `Status:`, `Service:`, `Incident date:` or `Authors:` is missing or empty; the status isn't Draft, In review or Final; the date isn't a calendar date |
| Sections | One of the seven is missing, empty or out of order |
| Summary | It has no count with a unit |
| Impact | `What users saw:`, `Scope:`, `Duration:` or `Data loss:` is missing or empty; `Scope:` has no count with a unit |
| Timeline | `Time zone:` is missing, or isn't UTC or an offset such as UTC+05:30; the table lacks the columns Time, Event and Evidence |
| Timeline rows | A time isn't a real `HH:MM`, `HH:MM:SS` or `YYYY-MM-DD HH:MM`, has no date, or is earlier than the row above; an Evidence cell is empty or says None, N/A, Unknown or TBD |
| Timeline tags | `**Impact starts**`, `**Detected**` or `**Mitigated**` tags no row or several; `**Resolved**` tags several; Detected or Mitigated comes before Impact starts, or Resolved before Mitigated |
| Durations | `Duration:` or `Time to detect:` has no number with a unit, or differs from what the tagged rows give |
| Detection and response | `Detected by:`, `Time to detect:`, `Mitigation:` or `Resolution:` is missing or empty |
| Root cause | `Trigger:`, `Mechanism:` or `Believed before:` is missing, or says only None, N/A, Unknown or TBD; `Mechanism:` is under 15 words or has nothing in backticks; `Contributing factors:` is missing or has no list item |
| Lessons learned | One of its labelled lists is missing or empty |
| Action items | The table lacks the columns Action, Type, Owner, Due and Status, or has no rows; no open or done item has the type prevent or mitigate |
| Each action item | The action is empty or starts with "Investigate" or "Make sure"; the type isn't prevent, detect, mitigate or process; the status doesn't start with Open, Done or Won't do; a Won't do gives no reason; an open or done item has no calendar due date, or an owner that is empty or a stand-in such as TBD or "team" |
| Whole file | It contains human error, operator error, careless, negligent, incompetent, forgot to, should have known, more careful, or a possessive followed by fault; with `--filled`, a `{{placeholder}}` is left |

<!-- evidence-three: the output below names the edited lines and they are Duration, Mechanism and the row for action item 2 --> To see it fail, I copied the example to `draft2.md` and edited three lines:

```text
draft2.md: FAIL (6 problem(s))
  - 'Duration:' says 20 s, and the timeline gives 21 s
  - 'Mechanism:' is 9 words; explain it in at least 15
  - 'Mechanism:' names no setting, file, function or error text in backticks
  - action item 2 has no owner: 'TBD'
  - action item 2: Due is not a date (YYYY-MM-DD): 'next sprint'
  - blame phrase 'human error' in: Mechanism: The database file filled up because of human error.
```

That run exited with status 1, so a CI job can block a postmortem that fails. A PASS means the parts are present and the arithmetic agrees, and it can't tell you whether the mechanism is true.

The blame check is a list of nine phrases, so a postmortem can still blame a person in other words and pass.

## Postmortem vs incident report

A postmortem is the internal record with the full timeline, and an incident report is the shorter account that customers read. PagerDuty's template drafts that customer message in its Messaging section, and I'd keep it as a separate document.

My table of [internal and external documentation](/articles/internal-vs-external-docs/) has a row for which parts of a production incident go to each reader.

## When the template doesn't fit

A near miss doesn't fit, because the checker wants a row tagged Impact starts and an incident with no user impact has none. A timeline with a zone name such as Europe/Berlin fails too, since the checker accepts only UTC or a fixed offset.

I made that check strict after reading the generated example on [ilert's page](https://www.ilert.com/blog/postmortem-template-to-optimize-your-incident-response) from April 1, 2025, whose header says the timestamps are local to Europe/Berlin while each one ends in `Z`.

## FAQ

Each answer is about a software incident.

### What should a postmortem include?

It needs a summary with a count of affected users or requests, a timeline in one stated time zone and the cause. Each action item at the end needs an owner and a due date.

### What is a blameless postmortem?

A blameless postmortem explains the incident through the system, and [Google's SRE book](https://sre.google/sre-book/postmortem-culture/) says it does so "without indicting any individual or team for bad or inappropriate behavior". Atlassian's handbook gets there by naming people by role in place of their names.

### How soon after an incident should you write a postmortem?

<!-- evidence-three: 3 calendar days is the figure PagerDuty's guide gives for scheduling a Sev-1 review meeting --> Atlassian's guide says to document the incident "ideally within 24 to 48 hours" of resolving it. PagerDuty's guide schedules the review meeting within 3 calendar days for a Sev-1 incident and 5 business days for a Sev-2.
