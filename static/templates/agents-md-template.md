# AGENTS.md

<!--
Template for an AGENTS.md that Codex, Cursor, Gemini CLI and Claude Code can all read.
Keep it short: Claude Code's docs target under 200 lines per instruction file, and Codex
stops reading project files at 32 KiB by default. Put only what an agent cannot work out
from the code, and write each rule so someone could check whether it was followed.
For Claude-only rules, add a CLAUDE.md next to this file:

    @AGENTS.md

    ## Claude Code
    [Claude-only rule]

Block-level HTML comments like this one are stripped before Claude Code reads the file.
-->

[One sentence: what this repository builds and who runs it.]

## Commands

- Install: `[exact command]`
- Build: `[exact command]`
- Test everything: `[exact command]`
- Test one file: `[exact command with a path placeholder]`
- Lint and format: `[exact command]`

Run `[the test command]` before you report a change as done.

## Conventions that differ from the defaults

- [A rule a new contributor would get wrong, e.g. "Use pnpm, not npm."]
- [Where things live when it is not obvious, e.g. "API handlers live in src/api/handlers/."]

## Do not

- [A change that needs a human, e.g. "Do not edit migrations under db/migrations/."]
- [A file or directory agents must leave alone, and why.]

## Pull requests

- [Commit message or PR title format.]
- [What a PR description must include.]
