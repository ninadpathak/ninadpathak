---
category: coding-agents
primary_query: claude code hooks
siblings:
- claude-code-subagents
- claude-md
- claude-code-memory
date: 2026-11-23
description: "Block an edit before it runs or send a checker’s output back afterward. Two Claude Code hooks show how it works and where a guard can fail."
slug: claude-code-hooks
status: published
takeaways:
- "Use PreToolUse to block a change before it happens. Use PostToolUse to check an edit after it lands."
- "For PreToolUse, exit 2 or return a JSON denial to block the call. In the test, exit 1 let the edit through."
- "Try the rule on each tool that can make the change. The Edit and Write matcher did not cover a Bash edit."
title: "Claude Code Hooks: Events, Exit Codes and Two Tested Examples"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write setup tutorials for your developer tool. [Get in touch](/services/technical-tutorials/)."
---

I asked Claude Code to rename an index in an already-applied migration. A script blocked the edit, and Claude wrote a new migration instead.

That script was a hook. Claude Code ran it before the edit, while there was still time to stop it.

I also set up a hook that sends a checker’s output back after an edit. The difference between the two matters when you get an exit code wrong and a change you meant to block goes through.

## Block an edit before Claude makes it

For [coding agents](/articles/coding-agents/), an instruction file can tell a model what you expect. A hook can hold the tool call until a check makes a decision.

[What to put in CLAUDE.md](/articles/claude-md/)

Use a `PreToolUse` hook for a decision that has to happen before the tool runs. The matcher `Edit|Write` tells Claude Code to call the hook for those tools.

The hook receives JSON on stdin, including the absolute `file_path`.

```json
{
  "session_id": "2fc7420b-aabc-4db9-b4c9-c7b1696d913c",
  "transcript_path": "/home/dev/.claude/projects/-tmp-np-work-claude-code-hooks-repo/2fc7420b-aabc-4db9-b4c9-c7b1696d913c.jsonl",
  "cwd": "/tmp/np-work/claude-code-hooks/repo",
  "prompt_id": "5509ceb2-a581-4164-862f-8e1a46663ccc",
  "permission_mode": "acceptEdits",
  "effort": {
    "level": "medium"
  },
  "hook_event_name": "PreToolUse",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/tmp/np-work/claude-code-hooks/repo/migrations/0002_add_email_index.sql",
    "old_string": "create index users_email_idx on users (email);",
    "new_string": "create index users_email_lower_idx on users (email);",
    "replace_all": false
  },
  "tool_use_id": "toolu_01AbyDHm7iubaLqSEuGMfR54"
}
```

Save this example as `.claude/hooks/protect-migrations.sh`. It denies edits to existing files under `migrations/` and lets Claude create new migrations.

It uses Bash and jq.

```bash
#!/bin/bash
INPUT=$(cat)
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
```

## Put the hook where Claude Code will load it

Use the `hooks` key in `.claude/settings.json` for the repo. Use `.claude/settings.local.json` for a local rule in that project or `~/.claude/settings.json` for a rule across projects.

Claude Code merges hooks from the files. In the test, handlers from both project files ran on the same edit.

This settings file registers the migration guard and the checker in the next section. Make both scripts executable before trying it.

The `args` field starts the command without a shell.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-migrations.sh",
            "args": [],
            "onFailure": "block"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-docs.sh",
            "args": ["python3", "tools/writing/scripts/check_prose.py"]
          }
        ]
      }
    ]
  }
}
```

On an attempt to edit the old migration, the guard returned a JSON denial Claude could read.

```text
PreToolUse:Edit hook error: migrations/0002_add_email_index.sql has already been applied and must not change. Add a new numbered file in migrations/ instead.
```

## Give Claude feedback after a write

Use `PostToolUse` if the change needs to exist before your check can run. The example `check-docs.sh` runs a prose checker after a Markdown edit.

It exits 2 with the checker’s output when the check fails. Point the handler’s `args` at a checker that exists in your repo.

The example uses `tools/writing/scripts/check_prose.py`, which was the path in the test project.

In the test, Claude added a subsection directly under a heading. The edit succeeded and the checker sent this back.

```text
The checker failed on /tmp/np-work/claude-code-hooks/repo/docs/setup.md after your edit:
== /tmp/np-work/claude-code-hooks/repo/docs/setup.md
FAIL line 15: heading directly after a heading
note first-person tokens: 0
result: FAIL (1 failures, 1 notes)
```

Claude added a sentence between the headings on its next edit. The checker passed silently, so Claude’s final reply still said the pass was unverified.

If you need the agent to report the result, give it an explicit success message.

- [settings.json](/static/examples/claude-code-hooks/settings.json)
- [protect-migrations.sh](/static/examples/claude-code-hooks/protect-migrations.sh)
- [check-docs.sh](/static/examples/claude-code-hooks/check-docs.sh)

## Check that the guard actually blocks

A `PreToolUse` command can block with exit status 2 or with exit status 0 and a JSON denial. Exit status 1 records a non-blocking error.

| The hook | What Claude Code does on `PreToolUse` |
|---|---|
| Exits 0 with no output | Makes no decision, and the normal permission flow applies |
| Exits 0 with one JSON object | Applies the fields, such as a `permissionDecision` of `deny` |
| Exits 2 | Blocks the call and gives Claude the hook's stderr |
| Exits with any other code | Records a non-blocking error, and the call goes ahead |

The guard ran on a direct edit and on an edit from a subagent. These configurations let the change through.

| Setup | What happened | Fix |
|---|---|---|
| Scripts saved without the executable bit | The debug log said `EACCES: permission denied, posix_spawn` | Run `chmod +x`. With `"onFailure": "block"` the same run refused the edit |
| Guard printed its reason to stderr and exited 1 | The debug log recorded `status code 1`, and Claude never saw the reason | Exit 2, or exit 0 with a JSON `deny` |
| Guard slept 5 seconds with `"timeout": 2` | The debug log said `timed out after 2000ms` | Keep a guard fast. The default timeout is 600 seconds |
| Matcher written as `edit|write` | No hook ran, and no hook error was logged | Match the tool name's case, as in `Edit|Write` |
| Claude ran `sed -i` on the file through Bash | No hook ran, because the matcher names `Edit|Write` | A deny rule, `Edit(/migrations/0002_add_email_index.sql)`, refused the same `sed` command |

An `Edit|Write` matcher covers two tools. It has no decision to make when the change goes through Bash.

For a firm file boundary, use the tool’s permissions or sandbox and check that boundary directly. [How sandbox defaults differ](/articles/why-are-coding-agents-so-dumb-notes/)

To see whether the hook ran, start Claude Code with `--debug-file <path>` and look for `Hooks:`.

```text
Hooks: PreToolUse:Edit [${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-migrations.sh] finished with status 0 (29ms)
Hooks: PreToolUse:Edit [${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-migrations.sh] failed to start (6ms)
```

## Which event should you use?

Start with the moment your check needs. A guard uses `PreToolUse`.

A checker that needs the changed file uses `PostToolUse`. These are the events listed when the examples ran on November 23, with the blocking events in bold.

[Claude Code hooks reference](https://code.claude.com/docs/en/hooks)

| Events | When they fire |
|---|---|
| `SessionStart`, `SessionEnd` | A session starts or resumes, and it ends |
| `Setup` | A launch with `--init-only`, or with `--init` or `--maintenance` in `-p` mode |
| **`UserPromptSubmit`**, **`UserPromptExpansion`** | A prompt is submitted, and a typed command expands into a prompt |
| **`PreToolUse`** | Before a tool call runs |
| `PostToolUse`, `PostToolUseFailure` | After a tool call succeeds, and after it fails |
| **`PostToolBatch`** | After a batch of parallel tool calls |
| `PermissionRequest`, `PermissionDenied` | A tool call needs a permission decision, and auto mode denies one |
| **`Stop`**, `StopFailure` | Claude finishes responding, and a turn ends on an API error |
| `SubagentStart`, **`SubagentStop`** | A subagent starts, and it finishes |
| **`TaskCreated`**, **`TaskCompleted`** | A task is created, and it is marked completed |
| **`TeammateIdle`** | An agent-team teammate is about to go idle |
| `Notification`, `MessageDisplay` | Claude Code sends a notification, and assistant text is displayed |
| `InstructionsLoaded` | A CLAUDE.md or rules file loads |
| **`ConfigChange`**, `FileChanged` | A configuration file changes, and a watched file changes |
| `CwdChanged`, `DirectoryAdded` | The working directory changes, and a directory is added |
| **`WorktreeCreate`**, **`WorktreeRemove`** | Claude Code creates a worktree, and removes one a hook created |
| **`PreCompact`**, `PostCompact` | Before and after context compaction |
| **`PreModelSwitch`**, `PostModelSwitch` | Before a requested model switch, and after the model changes |
| **`Elicitation`**, **`ElicitationResult`** | An MCP server asks for input, and the user answers |

Hooks run with your user permissions. Read a repository’s `.claude/` files before scripting a headless run over it.

For an unfamiliar repo you can start with `--settings '{"disableAllHooks": true}'`, which stopped both example hooks from running in the test.

I’d keep standing advice in the project’s instructions and reach for a hook when the rule has to hold even on a delegated edit. [Claude Code memory](/articles/claude-code-memory/) · [Claude Code subagents](/articles/claude-code-subagents/)
