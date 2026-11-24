#!/usr/bin/env bash
# probe.sh <db>: under the 2 MiB file-size limit, try a one-character insert twice,
# rolled back and then committed, to see whether a write probe would notice the limit.
ulimit -f 2048
sqlite3 -cmd ".timeout 5000" "$1" "begin; insert into events (received_at, source, payload) values ('probe', 'health', 'x'); rollback;" && echo "tiny insert, rolled back: ok"
sqlite3 -cmd ".timeout 5000" "$1" "insert into events (received_at, source, payload) values ('probe', 'health', 'x');" && echo "tiny insert, committed: ok"
