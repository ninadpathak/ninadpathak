#!/usr/bin/env bash
# A wrong solution: rename in the Python imports and calls, miss the string in registry.py and the docs.
sed -i 's/parse_ts/parse_timestamp/g' timeutil.py ingest.py report.py tests/test_time.py
