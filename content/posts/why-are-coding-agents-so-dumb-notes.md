---
category: coding-agents
primary_query: none
siblings:
- claude-code-subagents
- agentic-workflows
bridges:
- slug: agent-harnesses
  reason: That page defines the harness, the program Lynch's post calls the agent, and covers a third benchmark that compares harnesses.
- slug: vercel-agent-study-by-harness
  reason: That essay found two Claude models fetching pages differently under two harnesses, the kind of same-model comparison this essay relies on.
date: 2026-11-23
description: "I compared how Claude Code, Codex and OpenCode handle parallel work, cheaper models, unanswered questions and file access. I tested two Claude Code settings."
slug: why-are-coding-agents-so-dumb-notes
status: published
title: "What coding agents do by default and what you can change"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write the docs and tutorials for your coding agent. [Talk to me](/services/freelance-technical-writer-for-ai-companies/)."
---

A coding agent asked Michael Lynch what to call a branch and waited all night for an answer. I'd want it to name the branch and get on with the work.

I went through Lynch's complaints looking for settings that would change what a coding agent does on its own. Claude Code has a timeout for unanswered questions, and a test confirmed I could send routine work to a cheaper model.

The sandbox test gave me more reason to care about the defaults. When Claude Code couldn't start the sandbox on Ubuntu, it warned me and ran the command anyway.

[Michael Lynch’s *Why are coding agents so dumb?*](https://mtlynch.io/why-are-coding-agents-so-dumb/)

## What you can configure in each tool

If you set up [coding agents](/articles/coding-agents/) for other people, check which of these decisions the tool makes before anyone adds a settings file.

Claude Code has a setting or feature for each complaint. The table shows what each tool documents, including where you have to change a default yourself.

| Lynch's complaint | Claude Code | Codex CLI | OpenCode V2 |
|---|---|---|---|
| Subtasks run one at a time | [Subagents](https://code.claude.com/docs/en/sub-agents) start in the background, up to 20 at once | [Spawns subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) when you or AGENTS.md ask | [Subagents](https://opencode.ai/docs/agents/) always run in the background |
| Gruntwork stays on the expensive model | `CLAUDE_CODE_SUBAGENT_MODEL`, or `model:` in a subagent file | `agents.default_subagent_model` in `config.toml` | `model:` in an agent file |
| An unanswered question stops the run | [`askUserQuestionTimeout`](https://code.claude.com/docs/en/tools-reference), default `never` | No key found in the [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) | A `question` [permission](https://opencode.ai/docs/permissions/) that a rule can deny |
| The agent can access files outside the project | [`sandbox.enabled`](https://code.claude.com/docs/en/sandboxing), default off | [OS-enforced sandbox](https://learn.chatgpt.com/docs/agent-approvals-security), on by default | `external_directory` rule, default allow |

## When can an agent run tasks in parallel?

Claude Code, Codex, and OpenCode can all hand work to subagents. The part I’d check is whether the jobs can actually start at the same time.

In Lynch's OpenCode screenshot, the first task adds a `Passphrase` type and the second uses that type to migrate authentication. Those jobs have a reason to run in that order.

[A Hacker News commenter pointed out the same dependency.](https://news.ycombinator.com/item?id=50029126)

The choice of tool can still change how a model handles independent work. [Another commenter](https://news.ycombinator.com/item?id=50026656) reported that the same Qwen model worked through tasks one at a time in OpenCode and started about six subagents in parallel in QwenCode.

The docs I checked name no setting that tells the agent which tasks are independent. That leaves open one of Lynch's simpler examples, drafting a commit message while tests run.

## How do you give routine work to a cheaper model?

Claude Code uses the main session's model for a subagent unless you specify another model. In Claude Code 2.1.330, a Sonnet session delegated the same file search twice.

The subagent used `claude-sonnet-5-5` by default and `claude-haiku-5-5` with `CLAUDE_CODE_SUBAGENT_MODEL=haiku`.

You can also set a model for one subagent, leaving the others alone. I'd use `model: haiku` for a role that does routine searches, as in my [subagents guide](/articles/claude-code-subagents/).

In Lynch's example, Claude Code used Opus for routine work because Opus was the default in that session.

## What happens when you miss a question?

I'd put a branch-naming rule in the [task brief](/articles/agentic-workflows/) so the agent can make that decision on its own.

In Claude Code, `askUserQuestionTimeout` tells the interactive question dialog how long to wait before asking Claude to proceed on its own. You can set it to wait up to 10 minutes.

I used Claude Code without the interactive dialog, so the timeout was outside the test.

## Does the sandbox protect files by default?

Claude Code's sandbox is off by default. Even when it's on, you have to list files such as `~/.ssh` if you want to block reads.

To prevent Claude from asking to retry a blocked command outside the sandbox, set `allowUnsandboxedCommands` to `false`. [Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing)

Codex documents an OS-enforced sandbox with network access off by default. OpenCode V2 allows access to paths outside the project by default.

V1 asked first. [Codex security docs](https://learn.chatgpt.com/docs/agent-approvals-security) · [OpenCode migration guide](https://opencode.ai/docs/migrate-v1/)

On November 23, the Claude Code test ran on Ubuntu 24.04 with sandboxing enabled and unsandboxed retries disabled. The command tried to create a file and read a fake key in a directory next to the scratch repository.

```bash
PROMPT='Use the Bash tool to run exactly this one command, then reply with its output and nothing else: touch ../outside/probe && cat ../outside/fake-key.txt'
claude -p "$PROMPT" --model haiku --allowedTools "Bash" \
  --settings '{"sandbox": {"enabled": true, "allowUnsandboxedCommands": false}}'
```

The settings string is the sandboxing page's example. Claude Code printed this warning to stderr, then created the file and printed the key:

```text
⚠ Sandbox disabled: sandbox is enabled but cannot start here: Ubuntu's AppArmor restriction on user namespaces stops bubblewrap here ("loopback: Failed RTM_NEWADDR: Operation not permitted"). Add bubblewrap's AppArmor profile from https://code.claude.com/docs/en/sandboxing, or run `sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0` (holds until reboot), then restart Claude Code
  Commands will run WITHOUT sandboxing. Network and filesystem restrictions will NOT be enforced.
```

Ubuntu's AppArmor settings stopped the sandbox from starting. Claude Code printed the warning, then created the file and read the fake key anyway.

With `"failIfUnavailable": true` added, the same run exited with status 1 and printed "Refusing to start without a working sandbox". No file was created.

The `codex sandbox` helper in codex-cli 0.171.0 hit the same bubblewrap error and ran nothing.

## What changes when you use a different coding tool with the same model?

Lynch argues that the software around the model deserves its own benchmarks. There's a good reason to measure it separately.

You can keep the model the same and get a different bill or a different result.

<!-- evidence-three: HarnessTax's method text says each model and harness pair ran three times per task, which gives the 90 attempts per harness on 30 tasks -->
[HarnessTax](https://harnesstax.github.io/) gave Claude Fable 5 the same 30 coding tasks in Claude Code, Codex CLI and Pi, with three attempts per task in each tool. The model solved 88 of 90 attempts in Claude Code and 87 of 90 in each of the other tools.

Claude Code cost 133 cents per attempt on average. Pi cost 67 cents.

A [second study](https://arxiv.org/abs/2609.20804) kept the coding tool fixed and took away its dedicated file and search tools, leaving the model with a shell. On 500 SWE-bench Verified tasks, Mistral Medium 3.5 fell to 45.4% from 68.6%.

Nemotron-3 550B rose to 69.4% from 65.8%.

The models responded differently to the same change. I'd choose a model for the job the subagent has to do and check the results before making it the default.

My [agent harness explainer](/articles/agent-harnesses/) covers another benchmark, and the [Vercel study breakdown](/articles/vercel-agent-study-by-harness/) looks at how the choice of coding tool affected which pages Claude models fetched.

File access is where I'd insist on a safer default. Claude Code's docs list tools such as Jest and Docker that can run into sandbox restrictions.

I'd still turn on the sandbox and set `failIfUnavailable` so that a failed sandbox stops the run.
