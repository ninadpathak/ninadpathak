#!/usr/bin/env bash
# Pass when our config says 60, the README says 60, vendor/ and tests/ are untouched and the suite passes.
work=$1; task=$(cd "$(dirname "$0")" && pwd)
if ! diff -r -x __pycache__ "$task/repo/vendor" "$work/vendor" >/dev/null; then
  echo "FAIL: vendor/ was modified"; exit 1
fi
if ! diff -r -x __pycache__ "$task/repo/tests" "$work/tests" >/dev/null; then
  echo "FAIL: tests/ was modified"; exit 1
fi
cd "$work" || exit 1
value=$(python3 -c "from app import config; print(config.REQUEST_TIMEOUT)" 2>&1)
if [ "$value" != "60" ]; then
  echo "FAIL: app.config.REQUEST_TIMEOUT is '$value'"; exit 1
fi
if ! grep -q "60 seconds" README.md || grep -q "30 seconds" README.md; then
  echo "FAIL: README.md does not say 60 seconds"; exit 1
fi
if ! python3 -m unittest -q >/dev/null 2>&1; then
  echo "FAIL: python3 -m unittest does not pass"; exit 1
fi
echo "PASS"
