#!/usr/bin/env bash
# Reference solution: replace the name in every tracked file.
grep -rl "parse_ts" --exclude-dir=.git . | xargs sed -i 's/parse_ts/parse_timestamp/g'
