# Postmortem: intake rejected every write for 21 seconds when its database file hit a size limit

Status: Final
Service: intake, a local event-intake API (Python 3.12.3 `http.server` over SQLite 3.45.1)
Incident date: 2026-11-23
Authors: Ninad Pathak

This was a test incident. The service ran on one Ubuntu 24.04 machine, a script sent the traffic, and the service was given a 2 MiB file-size limit so that it would fail. Every time, count and error text below comes from the files in `postmortem-intake-api/logs/`. The responder worked in the terminal session that had built the service, which is why the response times are short.

## Summary

On 2026-11-23, from 19:54:08 to 19:54:29 UTC, `POST /events` on intake failed for 21 seconds. The service rejected 156 of 156 write requests, 155 of them with HTTP 500 and the text `disk I/O error`. The SQLite database file had reached the 2 MiB file-size limit the service process ran under, because nothing deleted old rows from the `events` table. A restart under a 64 MiB limit stopped the errors, and a cap of 1,500 stored events removed the cause 39 seconds later.

## Impact

What users saw: `POST /events` returned HTTP 500 with the body `{"error": "disk I/O error"}`, while `GET /events/latest` kept returning 200.
Scope: 156 of 156 write requests failed, and 1 of 45 read requests was refused during the restart.
Duration: 21 s (19:54:08 to 19:54:29 UTC)
Data loss: 156 events were rejected and never stored, because the load script does not retry. No stored event was lost: ids 1 to 2,350 were all in the table at 19:55:10.

## Timeline

Time zone: UTC

| Time | Event | Evidence |
|---|---|---|
| 19:49:39 | Service started under `ulimit -f 2048`, a limit of 2,097,152 bytes on any file it writes | `logs/response.log` |
| 19:49:40 | Monitor and load script started. The load averaged 9.6 requests a second, 7.6 of them writes | `logs/response.log`, `logs/client-per-minute.txt` |
| 19:54:08 | **Impact starts**: the first `POST /events` returns 500 with `disk I/O error`, after 2,040 accepted writes | `logs/client-incident-window.log` at 19:54:08.553 |
| 19:54:10 | Monitor poll counts 20 of 48 requests as 5xx, and `/health` returns 200 | `logs/monitor.log` |
| 19:54:15 | **Detected**: the monitor prints `ALERT Intake5xxRate: 81% of requests returned 5xx for two polls` | `logs/monitor.log` |
| 19:54:19 | Responder reads the newest access-log lines: writes fail with `disk I/O error`, reads return 200 | `logs/response.log` |
| 19:54:21 | Responder finds `events.db` at 2,097,152 bytes, equal to `Max file size` in `/proc/<pid>/limits`, while `df` shows 12,190,908 KB free | `logs/response.log` |
| 19:54:25 | Dead end: `prlimit --fsize` on the running process fails with `Operation not permitted` | `logs/response.log` |
| 19:54:29 | **Mitigated**: service restarted under `ulimit -f 65536`. The restart refuses 2 requests, and the next write returns 201 at 19:54:29.369 | `logs/response.log`, `logs/client-incident-window.log` |
| 19:54:34 | `pragma integrity_check` fails with `database is locked (5)`, because the `sqlite3` shell was run with no busy timeout | `logs/response.log` |
| 19:54:39 | The same check with `.timeout 5000` prints `ok` | `logs/response.log` |
| 19:54:40 | The monitor prints `RECOVERED: two clean polls` | `logs/monitor.log` |
| 19:54:59 | Retention change tested on a scratch database: 230 inserts with a cap of 50 leave 80 rows | `logs/response.log` |
| 19:55:08 | **Resolved**: service restarted with a cap of 1,500 stored events. The restart refuses 1 write | `logs/response.log`, `logs/client-incident-window.log` |
| 20:05:00 | `events.db` has measured 2,473,984 bytes at each of 39 samples since 19:55:29. From 19:56 through 20:04 the service accepted 4,182 writes and failed none | `logs/size.log`, `logs/client-per-minute.txt` |

## Detection and response

Detected by: the `Intake5xxRate` alert in `monitor.py`, which prints when 5% or more of requests return a 5xx status in two 5-second polls in a row.
Time to detect: 7 s
Mitigation: Restarting the service under a 64 MiB file-size limit. The restart refused 2 requests.
Resolution: A cap in `service.py` that keeps the newest 1,500 events and deletes older ones once per 100 inserts. Deploying it refused 1 write, and from then on the service deletes old events by design.

## Root cause

Trigger: The database file `data/events.db` reached 2,097,152 bytes, the file-size limit of the service process, after 2,040 writes in 4 minutes 28 seconds of load.
Mechanism: Each `POST /events` inserted a row of about 1,028 bytes and nothing deleted rows, so `events.db` grew by about 7.8 KB a second. The process ran under `ulimit -f 2048`, and a write past that limit fails with `[Errno 27] File too large`. SQLite reported the failed write as `disk I/O error` on every insert that needed a new page, and the handler returned 500. A read needs no new page, so `GET /events/latest` and `GET /health` kept returning 200.
Believed before: The limit was planted, so nobody believed this service was safe. The author wrote seven predictions before the run (`logs/predictions.txt`) and five held. Both misses were about timing. The limit was predicted 3 to 4 minutes into the load and took 4 minutes 28 seconds, because a 6-second smoke test had measured 1,238 bytes a write and the average over the run was 1,028. The alert was predicted 10 to 15 seconds after the first failure and printed after 7.

Contributing factors:

- `GET /health` runs `select 1`, which needs no new page. The health probe returned 200 at each of the monitor's 236 polls, 4 of them during the incident.
- The error text pointed at the disk. SQLite said `disk I/O error` while `df` showed 12,190,908 KB free, and only `/proc/<pid>/limits` showed the limit.
- Nothing watched the size of the database file, so 4 minutes 28 seconds of growth produced no warning.
- `ulimit -f` in bash set the hard limit along with the soft one, so the limit could not be raised on the running process and mitigation needed a restart.

## Lessons learned

What went well:

- The `Intake5xxRate` alert printed 7 seconds after the first failed write.
- The access log carried SQLite's error text, so the first command the responder ran showed which endpoint was failing and with what error.
- Reads kept working. During the incident 44 of 45 `GET /events/latest` requests returned 200.
- The database needed no repair. `pragma integrity_check` printed `ok` ten seconds after the restart.

What went wrong:

- `/health` returned 200 for all 21 seconds, so anything that trusted it saw a healthy service.
- The first integrity check failed with `database is locked (5)` and had to be rerun with a timeout, which took 5 seconds.
- Each restart refused requests: 2 during mitigation and 1 when the cap was deployed.
- The attempt to raise the limit with `prlimit` took 4 seconds and could not have worked.

Where we got lucky:

- The responder had built the service minutes earlier and knew it ran under `ulimit -f`, so the second command compared the file size with `/proc/<pid>/limits`. The error text and `df` both pointed somewhere else.
- Every write in the load carried a 900-character payload, so every write failed and the 5xx rate reached 81%. In a second run a one-character insert still succeeded at the limit (`probe.sh`), so traffic made of small events would have failed only in part.

## Action items

| Action | Type | Owner | Due | Status |
|---|---|---|---|---|
| Cap the `events` table at the newest 1,500 rows, pruned once per 100 inserts | prevent | Service author | 2026-11-23 | Done 2026-11-23: the file stayed at 2,473,984 bytes for 39 samples under the same load (`logs/size.log`) |
| Report `db_bytes` and `limit_bytes` from `GET /health`, and print `ALERT IntakeDbNearLimit` at 80% of the limit | detect | Service author | 2026-11-23 | Done 2026-11-23: in a second run with the cap off, the alert printed 49 s before the first failed write (`logs/rerun-monitor.log`) |
| Add `db_bytes` and `limit_bytes` to the access-log line of every failed write | mitigate | Service author | 2026-11-23 | Done 2026-11-23: seen in the second run (`logs/response.log` at 20:03:20) |
| Start the service with a soft limit only (`ulimit -S -f` in `start.sh`), so `prlimit` can raise it with no restart | mitigate | Service author | 2026-11-23 | Done 2026-11-23: in a third run the limit was raised when the 80% alert printed, and 2,326 of 2,326 writes succeeded (`logs/drill-monitor.log`) |
| Add a write probe to `GET /health` | detect | Service author | 2026-11-23 | Won't do: a one-character insert succeeded at the limit while every 900-character write failed, so the probe would have passed (`probe.sh`) |
