#!/bin/bash
# PostToolUse hook: run a checker on a Markdown file Claude just edited.
# The checker command is whatever "args" holds in settings.json.
INPUT=$(cat)

# While you build the hook, set HOOK_DEBUG_LOG to a file path to keep a copy of the input.
[ -n "$HOOK_DEBUG_LOG" ] && echo "$INPUT" >> "$HOOK_DEBUG_LOG"

FILE=$(jq -r '.tool_input.file_path // empty' <<<"$INPUT")
case "$FILE" in
  *.md) ;;
  *) exit 0 ;;
esac

cd "$CLAUDE_PROJECT_DIR" || exit 1
if ! REPORT=$("$@" "$FILE" 2>&1); then
  echo "The checker failed on $FILE after your edit:" >&2
  echo "$REPORT" >&2
  exit 2  # the edit has already happened; exit 2 shows stderr to Claude
fi
exit 0
