#!/usr/bin/env bash
# Which instruction file does each coding agent load by default?
#
# Creates its own temporary directory with mktemp, builds four git repositories in
# it (different combinations of AGENTS.md and CLAUDE.md, each file carrying a
# unique codeword), asks each agent which codewords it was given, and deletes the
# temporary directory on exit. It takes no path argument and never touches a
# directory it did not create.
#
# Controls, so an answer can only come from instructions the agent loaded:
#   - Aborts if any parent of the temp directory holds an instruction file.
#   - Claude Code: --tools "" (no tools), --strict-mcp-config (no MCP servers),
#     --setting-sources project,local (no user settings). The script reads the
#     stream-json trace and reports TOOLS if any tool was available or used.
#   - Codex: read-only sandbox, ephemeral session, and the two settings that
#     decide file loading pinned to their defaults (no fallback filenames,
#     32 KiB limit). The script reads the --json trace and reports TOOLS if the
#     agent ran a command or any other tool.
#
# Needs: bash, git, python3, and claude and/or codex on PATH, logged in.
# Usage: bash which-instructions-load.sh
set -euo pipefail

if [ "$#" -gt 0 ]; then
  echo "usage: bash which-instructions-load.sh   (takes no arguments)" >&2
  exit 2
fi

WORK=$(mktemp -d "${TMPDIR:-/tmp}/which-instructions.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

# Claude Code reads instruction files from every parent directory, so a stray one
# above the temp directory would contaminate the result.
dir=$(dirname "$WORK")
while :; do
  for name in CLAUDE.md CLAUDE.local.md .claude/CLAUDE.md AGENTS.md AGENTS.override.md; do
    if [ -e "$dir/$name" ]; then
      echo "abort: $dir/$name exists above the test directory; set TMPDIR elsewhere" >&2
      exit 3
    fi
  done
  [ "$dir" = "/" ] && break
  dir=$(dirname "$dir")
done

PROMPT='Your project instructions contain one or more codewords in the form WORD-1234. List every codeword you were given, comma-separated, and nothing else. If you were given none, reply NONE.'

make_case() {  # name, then the files to create
  local dir="$WORK/$1"; shift
  mkdir "$dir"
  git -C "$dir" init -q
  for file in "$@"; do
    case "$file" in
      AGENTS.md)        printf 'Codeword: AGENTS-4417\n' > "$dir/AGENTS.md" ;;
      CLAUDE.md)        printf 'Codeword: CLAUDE-2093\n' > "$dir/CLAUDE.md" ;;
      CLAUDE.md+import) printf '@AGENTS.md\n\nCodeword: CLAUDE-2093\n' > "$dir/CLAUDE.md" ;;
    esac
  done
}

CASES="1-agents-only 2-claude-only 3-both 4-claude-imports"
make_case 1-agents-only    AGENTS.md
make_case 2-claude-only    CLAUDE.md
make_case 3-both           AGENTS.md CLAUDE.md
make_case 4-claude-imports AGENTS.md CLAUDE.md+import

claude_answer() {
  command claude -p "$PROMPT" --model haiku --tools "" --strict-mcp-config \
    --setting-sources project,local --output-format stream-json --verbose </dev/null 2>/dev/null |
  python3 -c '
import json, sys
answer, tools = "", 0
for line in sys.stdin:
    try: event = json.loads(line)
    except ValueError: continue
    if event.get("type") == "system" and event.get("subtype") == "init":
        tools += len(event.get("tools") or []) + len(event.get("mcp_servers") or [])
    if event.get("type") == "assistant":
        tools += sum(1 for c in event["message"]["content"] if c.get("type") == "tool_use")
    if event.get("type") == "result":
        answer = (event.get("result") or "").strip()
print("TOOLS" if tools else (answer or "ERROR"))'
}

codex_answer() {
  command codex exec --json --ephemeral --skip-git-repo-check -s read-only \
    -c 'project_doc_fallback_filenames=[]' -c 'project_doc_max_bytes=32768' \
    "$PROMPT" </dev/null 2>/dev/null |
  python3 -c '
import json, sys
answer, tools = "", 0
for line in sys.stdin:
    try: event = json.loads(line)
    except ValueError: continue
    item = event.get("item") or {}
    kind = item.get("type")
    if kind == "agent_message":
        answer = (item.get("text") or "").strip()
    elif kind and kind != "reasoning":
        tools += 1
print("TOOLS" if tools else (answer or "ERROR"))'
}

printf '%-18s %-28s %s\n' "case" "Claude Code" "Codex"
for name in $CASES; do
  claude_out="-"; codex_out="-"
  if command -v claude >/dev/null; then claude_out=$(cd "$WORK/$name" && claude_answer); fi
  if command -v codex >/dev/null; then codex_out=$(cd "$WORK/$name" && codex_answer); fi
  printf '%-18s %-28s %s\n' "$name" "$claude_out" "$codex_out"
done
echo "versions: $(command claude --version 2>/dev/null | head -1) / $(command codex --version 2>/dev/null | head -1)"
