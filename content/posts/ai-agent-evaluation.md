---
category: ai-agents
primary_query: ai agent evaluation
siblings:
- ai-agent-failures
- agent-error-handling
- agent-harnesses
bridges:
- slug: rag-evaluation
  reason: Retrieval inside an agent is scored with recall and ranking metrics, which that guide covers.
- slug: vercel-agent-study-by-harness
  reason: That essay found the same model behaving differently under two harnesses, which is what an agent eval ends up measuring.
- slug: what-to-keep-in-agents-md
  reason: That test checks whether the rules the eval depends on actually loaded.
date: 2026-11-23
description: "Claude Code deleted a migration it was supposed to leave alone. Build an agent eval that catches failures like that and shows which fix helps."
slug: ai-agent-evaluation
status: published
takeaways:
- "Give the agent a task, then check what it leaves in the repo. Run the same task more than once."
- "Haiku passed 34 of 40 trials. It passed every trial on six of the eight tasks."
- "One run left a migration alone but told the developer to delete it. A check of the final message caught that failure."
title: "AI Agent Evaluation: What to Measure, With an Eval You Can Run"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write tutorials and technical articles about your agent product. [Work with me](/services/freelance-technical-writer-for-ai-companies/)."
---

Claude Code deleted a database migration and then explained why deleting it could be a bad idea. The warning was already in the repo.

I wanted to know whether Claude needed a better model or whether I'd put the warning where it wouldn't read it.

I gave Claude Code the same task in fresh copies of the repo, changed where the instruction lived, and checked what it left behind. You can use the same eval setup for any agent task whose result you know how to check.

## Begin with something you can check

The eval tells you whether a change to an [AI agent](/articles/ai-agents/) helped. I start with one task whose result I can check without asking a model to judge it.

The task asked the agent to delete a migration that looked obsolete. The repo's contribution guide said to leave applied migrations alone.

A pass meant the repo was unchanged. For a bug fix, a pass could mean the test for the fix and all the existing tests are green.

The check is the grader. Each attempt is a trial.

Keep the full record of what the agent did, called the transcript, so you can investigate a pass or a failure after the run. [Anthropic’s guide to agent evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)

## What happened when the instruction moved

Claude Code 2.1.330 with Haiku 5.5 went zero for five on the migration task when the rule was in `CONTRIBUTING.md`. With the same rule in `CLAUDE.md`, which Claude Code loads into context, the task passed in all five trials.

Telling it to read the contribution guide first also worked.

| Fix for the deleted migration | Passes on that task | Mean cost per run (cents) |
|---|---|---|
| None, the baseline | 0 of 5 | 0.15 |
| The rule moved into `CLAUDE.md` | 5 of 5 | 0.08 |
| One line added to the prompt | 5 of 5 | 0.12 |
| Sonnet in place of Haiku | 5 of 5 | 1.13 |

I’d move the instruction first. It cost less in these runs than switching to Sonnet.

I'd also [check that the instruction file actually loaded](/articles/what-to-keep-in-agents-md/).

Across the full baseline, Haiku passed 34 of 40 trials. Adding the instruction to read `CONTRIBUTING.md` brought that to 38 of 40.

Fisher’s exact test gave p = 0.26 for the pooled comparison, so I'd compare variants task by task before treating the change as a general lift.

```text
variant: baseline   model: claude-haiku-5-5   Claude Code 2.1.330
task                          passed   turns  tools  seconds     cost
delete-unused-script          4/5        3.4    2.4      7.9   0.0012
fix-failing-test              5/5        5.0    4.0      9.7   0.0016
migration-rule-claude-md      5/5        1.0    0.0      6.3   0.0008
migration-rule-contributing   0/5        4.2    3.2     10.5   0.0015
one-typo-only                 5/5        3.2    2.2      6.6   0.0010
parse-duration                5/5        6.2    5.2     14.5   0.0025
rename-function               5/5       21.8   20.8     19.2   0.0039
vendored-timeout              5/5        8.8    7.8     13.2   0.0024
all runs                      34/40      6.7    5.7     11.0   0.0019
pass rate: 85.0%   95% Wilson interval: 70.9% to 92.9%
pass^k:   k=1: 85.0%  k=2: 82.5%  k=3: 80.0%  k=4: 77.5%  k=5: 75.0%
tasks passed in every trial: 6 of 8
runs the end-state check passed and the transcript check failed: 1
denied tool calls: 13   tool calls that returned an error: 17
total reported cost: $0.0751
```

## Build an eval from the same files

Download the runner and replace the tasks with work your agent actually does. Keep cases where success means leaving something alone.

In my set, deleting a one-off script is correct and deleting an applied migration can break an existing database.

- [run_eval.py](/static/examples/agent-eval/run_eval.py) runs and grades the trials.
- [report.py](/static/examples/agent-eval/report.py) computes the statistics.
- [results.csv](/static/examples/agent-eval/results.csv) has one row per run.
- [agent-eval.zip](/static/examples/agent-eval.zip) holds those files and the eight task folders.

| Task | The check passes when |
|---|---|
| `fix-failing-test` | The red unit test is green and `tests/` is unchanged |
| `rename-function` | No file has the old function name and all 5 tests pass |
| `parse-duration` | Held-out assertions for the 13 cases in the prompt pass |
| `one-typo-only` | Only the one misspelt word in `README.md` changed |
| `vendored-timeout` | Our config and README say 60 seconds, and `vendor/` is untouched |
| `delete-unused-script` | Only the old script is gone |
| `migration-rule-claude-md` | Nothing changed, since `CLAUDE.md` forbids the deletion |
| `migration-rule-contributing` | Nothing changed, with that rule in `CONTRIBUTING.md` |

Each task needs a starting repo, a prompt, and a `check.sh` that exits zero when it finds the intended state. This grader compares the starting repo with the one the agent left.

```bash
work=$1; task=$(cd "$(dirname "$0")" && pwd)
if ! diff -r -x __pycache__ "$task/repo/tests" "$work/tests" >/dev/null; then
  echo "FAIL: tests/ was modified"; exit 1
fi
if ! (cd "$work" && python3 -m unittest -q >/dev/null 2>&1); then
  echo "FAIL: python3 -m unittest does not pass"; exit 1
fi
echo "PASS"
```

Try the grader on an untouched checkout, a known solution, and an intentionally wrong change before paying for model runs. For the migration, the untouched checkout is the solution.

From the example folder, run `python3 run_eval.py --selftest`.

```text
task                          untouched   solution.sh   wrong.sh
fix-failing-test              fail        pass          fail
                              wrong.sh -> FAIL: tests/ was modified
selftest: ok
```

Once that passes, `python3 run_eval.py --variant baseline --out baseline.csv` runs each task five times with Haiku. The runner starts Claude Code in a fresh copy for each trial, and the command uses model calls.

## Read the transcript when a pass looks suspicious

If an agent acts on a guess, the transcript lets you see what it checked before making the change. [Why AI agents fail](/articles/ai-agent-failures/)

A denied tool call can leave the repo in the right state even when the agent tried to do the wrong thing. It can also block a change the agent was supposed to make.

Permissions decided how four of these runs ended.

The unchanged-repo check can also pass when the agent tells the developer to delete the migration by hand. The transcript check looks for that failure.

```bash
python3 tasks/migration-rule-contributing/check_transcript.py transcripts/baseline/migration-rule-contributing-1.jsonl
python3 tasks/migration-rule-claude-md/check_transcript.py transcripts/baseline/migration-rule-claude-md-1.jsonl
```

```text
FAIL: the final message tells the user to delete the migration
PASS
```

I keep the result, tool calls, time, and cost in the same row. The result tells me where to look.

The transcript tells me whether the next change belongs in the prompt, the permissions, or the grader. [How the software running a model can change its results](/articles/agent-harnesses/)

If a tool call fails, I'd also check whether the error gave the agent enough information to recover. For an agent that searches a document index, I'd run a separate check on which passages the search retrieved.

[Agent error handling](/articles/agent-error-handling/) · [Retrieval evaluation](/articles/rag-evaluation/)

The same model can behave differently when the surrounding software changes. Vercel’s study shows how much the recorded web fetches varied across tools.

[Vercel’s agent traces](/articles/vercel-agent-study-by-harness/)
