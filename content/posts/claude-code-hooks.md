---
category: coding-agents
primary_query: claude code hooks
siblings:
- claude-code-subagents
- claude-md
- claude-code-memory
date: 2026-11-23
description: "Claude Code hooks, tested on version 2.1.330: what a hook receives on stdin and which exit code blocks a tool call, with two working hooks and five failures."
slug: claude-code-hooks
status: published
takeaways:
- A Claude Code hook is a command in a settings file that Claude Code runs at a lifecycle event, with the event's JSON on stdin.
- On PreToolUse only exit code 2 or a JSON deny blocks the tool call, and a guard hook that exited 1 or timed out let the edit through in Claude Code 2.1.330.
- Hooks from settings files fire inside subagents, where the input also carries agent_id and agent_type.
title: "Claude Code Hooks: Events, Exit Codes and Two Tested Examples"
work_note: "The runs where the guard failed taught me more than the runs where it held, and a good setup tutorial keeps both. I'm Ninad Pathak, a freelance technical writer for AI companies, and I run each product before I write its tutorial. [Get in touch about yours](/services/freelance-technical-writer-for-ai-companies/)."
---

A Claude Code hook is a command that Claude Code runs by itself at a fixed point in a session, such as before a tool call or after a file edit. The command gets the event as JSON on stdin, and its exit code or printed JSON can block the action.

Hooks are registered under a `hooks` key in a settings file and run by Claude Code itself, so a rule in a hook doesn't depend on the model remembering it. That makes them the enforcing half of setting up [coding agents](/articles/coding-agents/), beside an instruction file such as [CLAUDE.md](/articles/claude-md/) that can only advise.

The two hooks built for this page ran in Claude Code 2.1.330 on 2026-11-23. The first blocked an edit to a database migration, the second sent a checker's report back to Claude, and five other setups let the protected file change anyway.

## What is a Claude Code hook?

A Claude Code hook is a handler that Claude Code runs automatically when a named lifecycle event fires. [Anthropic's hooks reference](https://code.claude.com/docs/en/hooks) lists five handler types, and this page uses `command`, a shell command that reads the event from stdin.

A hook entry in a settings file has three levels:

- the **hook event**, such as `PreToolUse` or `Stop`
- a **matcher** that narrows the event, such as `Edit|Write` for those two tools
- the **handlers**, each a command with optional fields such as `timeout`

Anthropic's [memory docs](https://code.claude.com/docs/en/memory) say CLAUDE.md files "aren't enforced configuration", a limit my [Claude Code memory page](/articles/claude-code-memory/) covers, and that to block an action you should "use a PreToolUse hook instead".

## Claude Code hook events and when each fires

The hooks reference listed 33 hook events when I read it on 2026-11-23, and exit code 2 blocks the action on the 16 in bold:

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

## Where to configure Claude Code hooks

Hooks go in a `hooks` object in a settings JSON file, and the file you choose decides who gets the hook:

- `~/.claude/settings.json` for every project on your machine
- `.claude/settings.json` for one repository, shared once it's committed
- `.claude/settings.local.json` for you alone in one repository

Claude Code reads `.claude/settings.json` from the directory you start it in, with no fallback to a parent directory, according to the [permissions docs](https://code.claude.com/docs/en/permissions).

## Which settings file wins for hooks?

No settings file wins, because Claude Code merges the hooks from all of them. In my test one `Edit` call ran handlers from both `.claude/settings.json` and `.claude/settings.local.json`.

## What a hook receives on stdin

A command hook receives one JSON object on stdin. My `PreToolUse` hook received this one when Claude tried to edit a migration file:

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

`file_path` arrived absolute, which the reference says is always the case for the file tools. So match a path segment such as `/migrations/`, because a pattern anchored at `migrations/` can never match.

A `PostToolUse` hook also gets `tool_response`, and for an `Edit` call its `originalFile` field held the whole file from before the edit. So a log of hook input is a copy of your files.

## How exit codes and JSON output change what Claude does

A hook answers with its exit code, and on `PreToolUse` only exit code 2 blocks the tool call:

| The hook | What Claude Code does on `PreToolUse` |
|---|---|
| Exits 0 with no output | Makes no decision, and the normal permission flow applies |
| Exits 0 with one JSON object | Applies the fields, such as a `permissionDecision` of `deny` |
| Exits 2 | Blocks the call and gives Claude the hook's stderr |
| Exits with any other code | Records a non-blocking error, and the call goes ahead |

Exit code 1, the usual Unix failure code, lets the call through. So the reference says to "use `exit 2`" when a hook is "meant to enforce a policy".

For more than block or pass, exit 0 and print one JSON object. `PreToolUse` reads `permissionDecision` inside `hookSpecificOutput`, while `PostToolUse` and `Stop` read a top-level `decision` of `"block"`.

## Example 1: a PreToolUse hook that blocks an edit

This hook denies any `Edit` or `Write` call that would change an existing file under `migrations/`, and it lets a new migration file through. Save it as `.claude/hooks/protect-migrations.sh`:

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

This `.claude/settings.json` registers both example hooks:

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

The `args` key makes Claude Code start the script without a shell, and both scripts need `chmod +x` first.

The test ran as `claude -p` on the `haiku` alias with `--permission-mode acceptEdits`, so nothing but the hook stood between Claude and the file. Asked to rename the index in `migrations/0002_add_email_index.sql`, Claude got this back from its `Edit` call:

```text
PreToolUse:Edit hook error: migrations/0002_add_email_index.sql has already been applied and must not change. Add a new numbered file in migrations/ instead.
```

Claude then wrote `migrations/0003_rename_email_index.sql` containing `alter index users_email_idx rename to users_email_lower_idx;`, and its reply began "I didn't edit `migrations/0002_add_email_index.sql`." The hook ran again for that `Write` call and exited 0, because the file didn't exist yet.

## Example 2: a PostToolUse hook that runs a checker

The second hook, `check-docs.sh`, runs a checker on a Markdown file after Claude edits it and exits 2 to hand Claude the report. The checker is whatever command `args` holds, and mine is `check_prose.py` from this site's repository, which fails a file that has two headings with no prose between them.

I asked for a Troubleshooting section with one subsection, and Claude's first edit to `docs/setup.md` put `### Missing token` directly under `## Troubleshooting`. The `Edit` tool reported success, and the hook exited 2 with this on stderr:

```text
The checker failed on /tmp/np-work/claude-code-hooks/repo/docs/setup.md after your edit:
== /tmp/np-work/claude-code-hooks/repo/docs/setup.md
FAIL line 15: heading directly after a heading
note first-person tokens: 0
result: FAIL (1 failures, 1 notes)
```

Claude's next message began "The checker flagged line 15", and its second edit put a sentence between the headings, which the hook passed with exit 0. Exit 0 with no output tells Claude nothing, and its final reply said "the pass is unverified".

Download the files, where each script has an optional extra line that logs the input when `HOOK_DEBUG_LOG` is set:

- [settings.json](/static/examples/claude-code-hooks/settings.json)
- [protect-migrations.sh](/static/examples/claude-code-hooks/protect-migrations.sh)
- [check-docs.sh](/static/examples/claude-code-hooks/check-docs.sh)

## What each hook received and what Claude did

Both hooks worked in the main session, and the guard held when a subagent made the edit:

| Run | The hook received | It returned | What Claude did |
|---|---|---|---|
| Rename an index in `0002_add_email_index.sql` | `PreToolUse` for `Edit`, with an absolute `file_path` | Exit 0 and a JSON `deny` | Left `0002` unchanged and wrote a `0003` file |
| The same rename by a `general-purpose` subagent | The same fields plus `agent_id` and `agent_type` | The same JSON `deny` | The subagent stopped and reported the block |
| Add a section to `docs/setup.md` | `PostToolUse` for `Edit`, with `tool_response` | Exit 2 and the checker's report on stderr | Fixed the headings in a second edit |

The second row matches the reference, which says hooks from settings files "also run inside subagents". For when to pick a hook over a skill or a subagent, my [Claude Code subagents guide](/articles/claude-code-subagents/) has a table.

## Why a hook doesn't fire or doesn't block

A hook that fails or never matches blocks nothing, and Claude's reply doesn't mention it. That happened five ways in my runs, and each time the change to `0002_add_email_index.sql` went through:

| Setup | What happened | Fix |
|---|---|---|
| Scripts saved without the executable bit | The debug log said `EACCES: permission denied, posix_spawn` | Run `chmod +x`. With `"onFailure": "block"` the same run refused the edit |
| Guard printed its reason to stderr and exited 1 | The debug log recorded `status code 1`, and Claude never saw the reason | Exit 2, or exit 0 with a JSON `deny` |
| Guard slept 5 seconds with `"timeout": 2` | The debug log said `timed out after 2000ms` | Keep a guard fast. The default timeout is 600 seconds |
| Matcher written as `edit|write` | No hook ran, and no hook error was logged | Match the tool name's case, as in `Edit|Write` |
| Claude ran `sed -i` on the file through Bash | No hook ran, because the matcher names `Edit|Write` | A deny rule, `Edit(/migrations/0002_add_email_index.sql)`, refused the same `sed` command |

To find the cause, start Claude Code with `--debug-file <path>` and search the file for `Hooks:`. The first line below is from a hook that ran, and the second from one that couldn't start (timestamps removed):

```text
Hooks: PreToolUse:Edit [${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-migrations.sh] finished with status 0 (29ms)
Hooks: PreToolUse:Edit [${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-migrations.sh] failed to start (6ms)
```

A tool call with no `Hooks:` line had no hook run for it, as with the lowercase matcher. The `sed` command ran without a prompt because `acceptEdits` mode approves `sed`, according to the [permission modes page](https://code.claude.com/docs/en/permission-modes).

The deny rule worked because Edit deny rules also cover file commands that Claude Code recognizes inside Bash, and the [hooks guide](https://code.claude.com/docs/en/hooks-guide) points to sandboxing for the rest. I'd keep the hook too, because its reason told Claude what to do next and the deny rule's message didn't.

## Are Claude Code hooks safe to run?

A hook is only as safe as its command, and the reference warns that "Command hooks execute shell commands with your full user permissions." A `-p` run shows no trust dialog, so the reference says hooks committed to a repository "run in a folder you've never trusted".

So read a repository's `.claude/` folder before you script `claude -p` over it, or pass `--settings '{"disableAllHooks": true}'`. That flag outranks the project's settings, and in my run with it neither hook ran.

## FAQ

These answers come from the hooks reference and the runs above.

### What are Claude Code hooks?

Claude Code hooks are commands, or other handlers such as HTTP endpoints, that Claude Code runs automatically at lifecycle events such as `PreToolUse`. Each one receives the event as JSON, and on some events its exit code can block the action.

### Do Claude Code hooks run inside subagents?

Yes, hooks from settings files fire for a subagent's tool calls. In my test a `PreToolUse` hook blocked an edit by a `general-purpose` subagent.

### Which exit code blocks a tool call?

Exit code 2 blocks the call on `PreToolUse`, and Claude gets the hook's stderr as the reason. Exit code 1 is a non-blocking error, so the call goes ahead.
