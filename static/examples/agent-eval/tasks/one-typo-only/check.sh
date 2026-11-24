#!/usr/bin/env bash
# Pass when README.md differs from the original by that one word and no other file changed.
work=$1; task=$(cd "$(dirname "$0")" && pwd)
if ! sed 's/recieve/receive/' "$task/repo/README.md" | cmp -s - "$work/README.md"; then
  if grep -q "recieve" "$work/README.md"; then
    echo "FAIL: README.md still says recieve"; exit 1
  fi
  echo "FAIL: README.md changed beyond the one word: $(diff <(sed 's/recieve/receive/' "$task/repo/README.md") "$work/README.md" | grep '^>' | head -1)"; exit 1
fi
other=$(cd "$work" && git status --porcelain | grep -v '^ M README.md$')
if [ -n "$other" ]; then
  echo "FAIL: other files changed: $(echo "$other" | tr '\n' ';')"; exit 1
fi
echo "PASS"
