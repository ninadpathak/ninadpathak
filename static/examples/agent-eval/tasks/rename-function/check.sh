#!/usr/bin/env bash
# Pass when the old name is gone from every file, the new one is defined, and all 5 tests still run and pass.
work=$1
cd "$work" || exit 1
left=$(grep -rn "parse_ts" --exclude-dir=.git --exclude-dir=__pycache__ . | head -3)
if [ -n "$left" ]; then
  echo "FAIL: parse_ts still appears: $(echo "$left" | head -1)"; exit 1
fi
if ! grep -q "^def parse_timestamp(" timeutil.py; then
  echo "FAIL: timeutil.py does not define parse_timestamp"; exit 1
fi
out=$(python3 -m unittest 2>&1)
if ! echo "$out" | grep -q "^Ran 5 tests" || ! echo "$out" | grep -q "^OK"; then
  echo "FAIL: expected 5 passing tests, got: $(echo "$out" | grep -E '^(Ran|OK|FAILED)' | tr '\n' ' ')"; exit 1
fi
echo "PASS"
