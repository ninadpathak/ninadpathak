#!/usr/bin/env python3
"""intake: a small event-intake API over SQLite, built as a local test service.

  POST /events         store one event, reply 201 with its id
  GET  /events/latest  the ten newest events
  GET  /health         200 when the database answers a query, with the size of the
                       database file and the file-size limit it runs under

Every request prints one access-log line to stdout. Do not deploy this.
"""
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import resource
import sqlite3
import time

DB = os.environ.get("INTAKE_DB", "data/events.db")
PORT = int(os.environ.get("INTAKE_PORT", "8471"))
KEEP = int(os.environ.get("INTAKE_KEEP", "1500"))   # newest events to keep; 0 keeps everything
PRUNE_EVERY = 100                                   # prune once per this many inserts


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def db_state():
    """Size of the database file and the per-file limit (None when there is no limit)."""
    limit = resource.getrlimit(resource.RLIMIT_FSIZE)[0]
    size = os.path.getsize(DB) if os.path.exists(DB) else 0
    return {"db_bytes": size, "limit_bytes": None if limit == resource.RLIM_INFINITY else limit}


def connect():
    return sqlite3.connect(DB, timeout=2)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, body, started, error="", extra=""):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        took = int((time.monotonic() - started) * 1000)
        tail = f' error="{error}"{extra}' if error else ""
        print(f"{utc_now()} {self.command} {self.path} {status} {took}ms{tail}", flush=True)

    def do_GET(self):
        started = time.monotonic()
        try:
            conn = connect()
            try:
                if self.path == "/health":
                    conn.execute("select 1").fetchone()
                    return self.reply(200, {"status": "ok", **db_state()}, started)
                if self.path == "/events/latest":
                    rows = conn.execute(
                        "select id, received_at, source from events order by id desc limit 10").fetchall()
                    return self.reply(200, {"events": rows}, started)
            finally:
                conn.close()
        except sqlite3.Error as exc:
            return self.reply(500, {"error": str(exc)}, started, str(exc))
        self.reply(404, {"error": "not found"}, started)

    def do_POST(self):
        started = time.monotonic()
        if self.path != "/events":
            return self.reply(404, {"error": "not found"}, started)
        try:
            event = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            source, payload = str(event["source"]), str(event["payload"])
        except (ValueError, KeyError, TypeError):
            return self.reply(400, {"error": "body must be JSON with source and payload"}, started)
        try:
            conn = connect()
            try:
                with conn:
                    cursor = conn.execute(
                        "insert into events (received_at, source, payload) values (?, ?, ?)",
                        (utc_now(), source, payload))
                    if KEEP and cursor.lastrowid % PRUNE_EVERY == 0:
                        conn.execute("delete from events where id <= ?", (cursor.lastrowid - KEEP,))
                return self.reply(201, {"id": cursor.lastrowid}, started)
            finally:
                conn.close()
        except sqlite3.Error as exc:
            state = db_state()
            sizes = f' db_bytes={state["db_bytes"]} limit_bytes={state["limit_bytes"]}'
            return self.reply(500, {"error": str(exc), **state}, started, str(exc), sizes)


def main():
    os.makedirs(os.path.dirname(DB) or ".", exist_ok=True)
    conn = connect()
    conn.execute("create table if not exists events ("
                 "id integer primary key, received_at text not null, "
                 "source text not null, payload text not null)")
    conn.commit()
    conn.close()
    print(f"{utc_now()} intake listening on 127.0.0.1:{PORT}, db {DB}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
