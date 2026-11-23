# Skills

These are the agent skills I write with. Each folder is a skill in the `SKILL.md` format that Claude Code and Codex load.

| Skill | What it does |
|---|---|
| [writing](writing/SKILL.md) | My writing standard for articles, docs, essays, narrative pieces, video scripts and social posts. It also edits a draft or audits one for AI slop. |
| [no-ai-slop](no-ai-slop/SKILL.md) | An entry point that runs the edit and detect modes of `writing`. |

## Essays

The essay rules are in [writing/references/essay.md](writing/references/essay.md). The research behind them is in [writing/references/essay-research](writing/references/essay-research): reading notes on Paul Graham's essays, the test rounds, and the log of corrections I gave while the skill was being built.

## Install

The skills refer to themselves at `~/.agents/skills`, so copy them there. Run this from the root of the repository.

```bash
mkdir -p ~/.agents/skills
cp -R skills/writing skills/no-ai-slop ~/.agents/skills/
```

For Claude Code, link each one into `~/.claude/skills`.

```bash
mkdir -p ~/.claude/skills
ln -s ~/.agents/skills/writing ~/.claude/skills/writing
ln -s ~/.agents/skills/no-ai-slop ~/.claude/skills/no-ai-slop
```

`writing/core.md` holds the sentence rules and the banned-word list. Load it at session start, for example with an `@~/.agents/skills/writing/core.md` import in your `CLAUDE.md`.

For Codex, `python3 ~/.agents/skills/writing/scripts/sync_core.py` writes the same core into `~/.codex/AGENTS.md`.

The statistics scripts in `essay-research` read a local copy of the essay corpus, which this repository leaves out.
