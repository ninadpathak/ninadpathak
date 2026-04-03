#!/bin/zsh
set -euo pipefail

ROOT="/Users/ninad/Development/NinadPathak/.ops/catchup-2026-04-04"
STATE="$ROOT/state"
LOGS="$STATE/launcher-logs"

mkdir -p "$LOGS"

nohup python3 "$ROOT/writer_lane.py" writer1 >"$LOGS/writer1.out" 2>&1 &
echo $! >"$STATE/writer1.pid"

nohup python3 "$ROOT/writer_lane.py" writer2 >"$LOGS/writer2.out" 2>&1 &
echo $! >"$STATE/writer2.pid"

nohup python3 "$ROOT/writer_lane.py" writer3 >"$LOGS/writer3.out" 2>&1 &
echo $! >"$STATE/writer3.pid"

nohup python3 "$ROOT/editor_loop.py" >"$LOGS/editor.out" 2>&1 &
echo $! >"$STATE/editor.pid"

nohup python3 "$ROOT/build_loop.py" >"$LOGS/build.out" 2>&1 &
echo $! >"$STATE/build.pid"

echo "launched"
