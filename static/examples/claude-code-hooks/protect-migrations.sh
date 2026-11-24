#!/bin/bash
# PreToolUse hook: a migration file that already exists must not change.
INPUT=$(cat)

# While you build the hook, set HOOK_DEBUG_LOG to a file path to keep a copy of the input.
[ -n "$HOOK_DEBUG_LOG" ] && echo "$INPUT" >> "$HOOK_DEBUG_LOG"

TOOL=$(jq -r '.tool_name' <<<"$INPUT")
FILE=$(jq -r '.tool_input.file_path // empty' <<<"$INPUT")

case "$FILE" in
  */migrations/*) ;;
  *) exit 0 ;;  # not a migration: no decision, the normal permission flow applies
esac

# Writing a new migration file is allowed.
if [ "$TOOL" = "Write" ] && [ ! -e "$FILE" ]; then
  exit 0
fi

jq -n --arg name "${FILE##*/}" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: ("migrations/" + $name + " has already been applied and must not change. Add a new numbered file in migrations/ instead.")
  }
}'
