---
category: technical-documentation
primary_query: postmortem template
siblings:
- runbook-template
- cloudflare-kv-cache-incident-report
- troubleshooting-guide-template
date: 2026-11-23
description: "The health check stayed green while every write failed. Use this Markdown postmortem template to show what users saw and what the logs prove."
slug: postmortem-template
status: published
takeaways:
- "Open with what users saw and how long it lasted. Put a log or metric behind each timeline entry."
- "The checker reads the timeline and calculates how long it took to detect and stop the failure."
- "The example health check kept returning 200 while all 156 attempts to write failed."
title: "Postmortem Template for Software Incidents, With a Checker"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write your product's troubleshooting and reference pages. [Get in touch](/services/developer-documentation/)."
---

The health check said 200 while the service rejected every write. For 21 seconds, all 156 attempts to store an event failed.

If I'd opened the postmortem with “a brief storage issue,” a reader would have missed what I wanted to understand. How could the service look healthy while it was refusing every event?

I set up that failure locally and filled in this Markdown postmortem template from the logs. The example shows what to put in the timeline, and the checker flags a duration that disagrees with it.

## Copy the postmortem template

A postmortem gives people who weren’t on call a piece of [technical documentation](/articles/technical-documentation/) they can follow back to the evidence.

The template starts with a short summary of what users saw and how long they saw it. The impact section adds scope and data loss.

The timeline shows what happened in order, with an evidence link for each event.

- [Postmortem template (Markdown)](/static/templates/postmortem-template.md)
- [Checker script](/static/templates/check_postmortem.py)
- [Filled example: intake rejected every write for 21 seconds](/static/examples/postmortem-intake-writes-failed.md)

After the timeline, describe how you detected and stopped the failure. Explain what made it possible, including what the team believed beforehand.

Finish with what you learned and changes people can deliver, each with an owner and due date. [Why I keep a line for what the team believed](/articles/cloudflare-kv-cache-incident-report/)

## What the health check missed

A person who sees the same SQLite error on a different system could have a different cause. The [troubleshooting guide template](/articles/troubleshooting-guide-template/) shows how I'd write separate checks for the possible causes.

The test service stored events in a SQLite database. I started it with a 2 MiB limit on files the process could write and sent it a steady stream of events.

The disk had room. The database file had reached its own limit.

```text
$ ls -l data/; grep "Max file size" /proc/$(cat logs/service.pid)/limits; df -k data | tail -1
total 2052
-rw-r--r-- 1 dev dev 2097152 Nov 23 19:54 events.db
Max file size             2097152              2097152              bytes     
/dev/sda1      100476656 88269364  12190908  88% /
```

SQLite reported `disk I/O error`. I knew to check the process limit because I'd set it myself, which gave me a head start a responder wouldn't have.

[Service code](/static/examples/postmortem-intake-api/service.py) · [Response log](/static/examples/postmortem-intake-api/logs/response.log)

The health check ran `select 1`. It returned 200 on all four polls during the incident because that query made no write.

Even adding a tiny write would have missed the problem. In a separate test a one-character insert succeeded at the limit while every 900-character write failed.

## Write down the timeline before you write the diagnosis

The first failure was at 19:54:08 UTC. The alert came seven seconds later.

I restarted the service with a higher limit at 19:54:29 and the errors stopped. A cap on how many events it kept removed the cause 39 seconds later.

The example records the times with the logs that support them.

```markdown
| Time | Event | Evidence |
|---|---|---|
| 19:54:08 | **Impact starts**: the first `POST /events` returns 500 with `disk I/O error`, after 2,040 accepted writes | `logs/client-incident-window.log` at 19:54:08.553 |
| 19:54:15 | **Detected**: the monitor prints `ALERT Intake5xxRate: 81% of requests returned 5xx for two polls` | `logs/monitor.log` |
```

I'd give the restart its own [runbook step](/articles/runbook-template/) with the result the responder should see. In the postmortem, I'd record why I thought that restart would help and when the first successful requests showed that it did.

## Make the stated durations agree with the logs

Run the checker against the filled report. It reads the timestamped rows for when impact started, when it was detected, and when it was mitigated.

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

It also looks for evidence in the timeline, a named owner and due date for each action someone has agreed to take, and missing placeholders. I changed the duration to 20 seconds, shortened the cause, and removed the real owner and due date from an action.

The checker showed what each edit had broken.

```text
draft2.md: FAIL (6 problem(s))
  - 'Duration:' says 20 s, and the timeline gives 21 s
  - 'Mechanism:' is 9 words; explain it in at least 15
  - 'Mechanism:' names no setting, file, function or error text in backticks
  - action item 2 has no owner: 'TBD'
  - action item 2: Due is not a date (YYYY-MM-DD): 'next sprint'
  - blame phrase 'human error' in: Mechanism: The database file filled up because of human error.
```

A pass tells me the times agree and the right fields are there. I'd still ask someone who wasn't on call to read the explanation and tell me what they think caused the failure.

If they can't point to a line of evidence, that’s where I'd revise the report.
