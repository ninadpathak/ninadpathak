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
description: "Michael Lynch says the software around coding models is the weak part. I checked four of the complaints against the Claude Code, Codex and OpenCode docs and found a Claude Code setting behind each. The sandbox complaint held up in a test on Ubuntu 24.04."
slug: why-are-coding-agents-so-dumb-notes
status: published
title: "Notes on Michael Lynch's 'Why are coding agents so dumb?'"
work_note: "The settings in this essay were all in the docs, and I still had to go looking for each one. I'm Ninad Pathak, a freelance technical writer for AI companies, and I write tutorials and technical articles that put a setting in front of the developer who needs it, after running it myself. [Talk to me about yours](/services/freelance-technical-writer-for-ai-companies/)."
---

On October 9, Michael Lynch published [Why are coding agents so dumb?](https://mtlynch.io/why-are-coding-agents-so-dumb/), six complaints from a developer who uses Claude Code and OpenCode daily. Lynch argues that the models keep improving while the program that runs them stays bad, the program the post calls the agent and benchmark authors call the harness.

I think Lynch is right about the defaults, and that a heading like "Agents can't delegate" claims more than the docs support. Configuring agents is a subject of my [coding agents](/articles/coding-agents/) topic, so on November 23 I read the docs for Claude Code, Codex and OpenCode against four of the six complaints, and two of the Claude Code settings in those docs then ran in version 2.1.330.

## Benchmarks have started measuring the harness

I agree with Lynch that the harness deserves its own numbers, and two studies had started producing them a few weeks before Lynch wrote that barely any benchmark measures the agents themselves.

<!-- evidence-three: HarnessTax's method text says each model and harness pair ran three times per task, which gives the 90 attempts per harness on 30 tasks --> [HarnessTax](https://harnesstax.github.io/), a study from UC Berkeley and Arena Intelligence that [reached Hacker News on September 16](https://news.ycombinator.com/item?id=49733726), ran the same 30 SWE-bench Lite tasks three times each through Claude Code, Codex CLI and Pi. Claude Fable 5 solved 88 of 90 attempts in Claude Code and 87 of 90 in each of the other two harnesses, at a mean cost of 133 cents per attempt in Claude Code and 67 cents in Pi.

So on that benchmark Claude Code didn't make the model dumber, and it made nearly the same result cost twice as much.

A second study, [submitted to arXiv on September 17](https://arxiv.org/abs/2609.20804), kept one harness fixed and changed one part of it at a time. When the file and search tools were removed and the model was left with a shell, Mistral Medium 3.5 fell to 45.4% of 500 SWE-Bench Verified tasks from 68.6%, and Nemotron-3 550B rose to 69.4% from 65.8%.

The file tools that helped Mistral Medium 3.5 held Nemotron-3 550B back, so I'm wary of any list of what every agent should do out of the box, and Lynch's post has one. My [agent harness explainer](/articles/agent-harnesses/) covers a third benchmark, and the [Vercel agent study](/articles/vercel-agent-study-by-harness/) I split by harness showed two Claude models fetching pages differently under two harnesses.

Neither HarnessTax nor the arXiv study can see an agent stopping to ask for a branch name, so for Lynch's complaints I went to the docs.

## The settings behind four complaints

Claude Code documents a setting for each of the four complaints I checked, and three of the four are off until you turn them on: the cheaper subagent model, the question timeout and the sandbox. Here is where each lives in the three agents' docs:

| Lynch's complaint | Claude Code | Codex CLI | OpenCode V2 |
|---|---|---|---|
| Subtasks run one at a time | [Subagents](https://code.claude.com/docs/en/sub-agents) start in the background, up to 20 at once | [Spawns subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) when you or AGENTS.md ask | [Subagents](https://opencode.ai/docs/agents/) always run in the background |
| Gruntwork stays on the expensive model | `CLAUDE_CODE_SUBAGENT_MODEL`, or `model:` in a subagent file | `agents.default_subagent_model` in `config.toml` | `model:` in an agent file |
| An unanswered question stops the run | [`askUserQuestionTimeout`](https://code.claude.com/docs/en/tools-reference), default `never` | No key found in the [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) | A `question` [permission](https://opencode.ai/docs/permissions/) that a rule can deny |
| No boundary on files | [`sandbox.enabled`](https://code.claude.com/docs/en/sandboxing), default off | [OS-enforced sandbox](https://learn.chatgpt.com/docs/agent-approvals-security), on by default | `external_directory` rule, default allow |

## Lynch's 10 subtasks weren't parallel work

I don't buy the example Lynch opens with, where OpenCode splits a feature into 10 todos and Lynch asks why it's doing "these embarrassingly parallel tasks one at a time". In Lynch's screenshot the second todo migrates authentication to the Passphrase type that the first todo adds, and the tenth is a final verification run.

The screenshot shows OpenCode committing step one before it starts step two, so I read the 10 todos as a chain of commits. A commenter, eviks, [made the same objection](https://news.ycombinator.com/item?id=50029126) on October 10.

Lynch is right that the harness decides whether independent work runs in parallel, and a commenter, kgeist, [described](https://news.ycombinator.com/item?id=50026656) one Qwen model that ran sequential todos under OpenCode and about six parallel subagents under another harness, QwenCode. The docs I read name no setting that tells an agent which todos are independent, or that it could draft a commit message during a test run, which is Lynch's Claude Code example.

## Cheaper subagents and unanswered questions are one setting each

In Claude Code each of these two complaints comes down to one setting. The test of the first, `CLAUDE_CODE_SUBAGENT_MODEL`, ran in version 2.1.330, with a prompt that told a Sonnet session to delegate one file search to a subagent.

Without the variable the subagent's replies came from `claude-sonnet-5-5`, and with it set to `haiku` they came from `claude-haiku-5-5`. The setting works, and Lynch's real complaint stands, that the agent doesn't choose a cheaper model for itself.

Claude Code's docs say Claude can pass a model when it starts a subagent, and in Lynch's screenshot Claude Code admits it named Opus for a routine job only because Opus is the default. I'd set the model per role in a subagent file, and my [subagents guide](/articles/claude-code-subagents/) has a tested one with a `model: haiku` line.

Lynch's wish list asks for an agent that decides alone after 30 minutes without an answer, and the second setting, `askUserQuestionTimeout`, closes an unanswered question after up to 10 minutes and tells Claude to proceed on its own judgment. I didn't test it, because its timer belongs to the interactive question dialog and my runs were headless.

Lynch doesn't name the agent that stopped to ask for a branch name and then waited all night, and I'd put a decision like that in the task brief, which the frame stage of my [agentic workflows](/articles/agentic-workflows/) page covers.

## The sandbox complaint is the one I'd keep

Lynch's sandbox complaint holds up against the docs and a test. Claude Code's sandboxing page says the sandbox is off by default, and that a sandboxed command can still read credential files such as `~/.ssh` unless you list them.

The same page says Claude can ask to rerun a blocked command outside the sandbox unless `allowUnsandboxedCommands` is `false`. OpenCode's permissions page gives every agent a base policy whose first rule allows every action, and its [migration guide](https://opencode.ai/docs/migrate-v1/) says V1 asked before touching paths outside the project and V2 doesn't.

But Codex is the exception to Lynch's claim that agents are only usable with access to everything, because its docs describe an OS-enforced sandbox that is on by default with the network off.

The test ran in Claude Code 2.1.330 on Ubuntu 24.04 on November 23, in a scratch repository with a fake key file in a folder beside it:

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

The sandboxing page documents this fallback in a warning box and names the fix, a third key, `"failIfUnavailable": true`. With that key added, the same command exited with status 1 and the message "Refusing to start without a working sandbox", and no file was created.

OpenAI's sandbox docs are a vendor describing its own product, and the one part tested here, the `codex sandbox` helper in codex-cli 0.171.0, hit the same bubblewrap error and ran nothing.

Lynch asks for access control that is deterministic, and a sandbox that falls back to no sandbox behind a warning on stderr doesn't meet that standard. I'd set `failIfUnavailable` wherever I'd enabled the sandbox.

## Where "out of the box" is the right standard

"Out of the box" is the right standard for the sandbox and too strict for model choice. Lynch uses the phrase against readers who'd say the fix is to edit a config file.

HarnessTax is why I'd leave model choice to configuration, because it shows one harness's defaults costing twice as much for nearly the same result, and a default that picks a cheaper model can also pick one too weak for the task. A file boundary costs something too, and Claude Code's sandboxing page lists `jest` and `docker` among the tools its sandbox breaks.

I'd still want the boundary on by default, and an agent that refuses to start when the boundary can't.

And I don't buy Lynch's guess that vendors underinvest in the harness, because Claude Code documents a setting for each of the four complaints I checked. The setting that stops the sandbox from falling back, `failIfUnavailable`, is one of them, and its default is `false`.
