#!/usr/bin/env bash
# Pass when the suite is green and nothing under tests/ changed.
# usage: check.sh <workdir>   (run by run_eval.py; the agent never sees this file)
work=$1; task=$(cd "$(dirname "$0")" && pwd)
if ! diff -r -x __pycache__ "$task/repo/tests" "$work/tests" >/dev/null; then
  echo "FAIL: tests/ was modified"; exit 1
fi
if ! (cd "$work" && python3 -m unittest -q >/dev/null 2>&1); then
  echo "FAIL: python3 -m unittest does not pass"; exit 1
fi
echo "PASS"
