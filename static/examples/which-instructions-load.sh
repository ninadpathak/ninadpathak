#!/usr/bin/env bash
# Which instruction file does each coding agent load?
#
# Builds four throwaway repositories, each with a different combination of
# AGENTS.md and CLAUDE.md, puts a unique codeword in each file, and asks the
# agent which codewords it was given. Nothing is edited; the agents only answer.
#
# Usage: ./which-instructions-load.sh [workdir]
# Needs: claude (Claude Code) and/or codex (Codex CLI) on PATH, logged in.
set -euo pipefail

WORK="${1:-$(mktemp -d)}"
PROMPT='Your project instructions contain one or more codewords in the form WORD-1234. List every codeword you were given, comma-separated, and nothing else. If you were given none, reply NONE.'

make_case() {  # name, then the files to create
  local dir="$WORK/$1"; shift
  rm -rf "$dir"; mkdir -p "$dir"
  (cd "$dir" && git init -q)
  for file in "$@"; do
    case "$file" in
      AGENTS.md)        printf 'Codeword: AGENTS-4417\n' > "$dir/AGENTS.md" ;;
      CLAUDE.md)        printf 'Codeword: CLAUDE-2093\n' > "$dir/CLAUDE.md" ;;
      CLAUDE.md+import) printf '@AGENTS.md\n\nCodeword: CLAUDE-2093\n' > "$dir/CLAUDE.md" ;;
    esac
  done
}

make_case 1-agents-only        AGENTS.md
make_case 2-claude-only        CLAUDE.md
make_case 3-both               AGENTS.md CLAUDE.md
make_case 4-claude-imports     AGENTS.md CLAUDE.md+import

printf '%-20s %-28s %s\n' "case" "Claude Code" "Codex"
for dir in "$WORK"/*/; do
  name=$(basename "$dir")
  claude_out="-"; codex_out="-"
  if command -v claude >/dev/null; then
    # --setting-sources project,local leaves out ~/.claude/CLAUDE.md, so only
    # the files in this case directory can supply a codeword.
    claude_out=$(cd "$dir" && command claude -p "$PROMPT" --model haiku \
      --setting-sources project,local </dev/null 2>/dev/null | tr -d '\n' | head -c 60)
  fi
  if command -v codex >/dev/null; then
    codex_out=$(cd "$dir" && command codex exec --skip-git-repo-check -s read-only \
      "$PROMPT" </dev/null 2>/dev/null | tail -1 | tr -d '\n' | head -c 60)
  fi
  printf '%-20s %-28s %s\n' "$name" "$claude_out" "$codex_out"
done
echo "versions: $(command claude --version 2>/dev/null | head -1) / $(command codex --version 2>/dev/null | head -1)"
