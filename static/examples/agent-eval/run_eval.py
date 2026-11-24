#!/usr/bin/env python3
"""Run a small agent eval: each task several times, each run in a fresh repo, graded by a check script.

The agent under test is Claude Code in headless mode. Every trial gets its own
temporary git repository copied from tasks/<task>/repo, the agent works there,
and tasks/<task>/check.sh inspects what is left and exits 0 (pass) or 1 (fail).
A task may also carry check_transcript.py, a second grader that reads the saved
transcript. A run passes when every grader it has passes.

  python3 run_eval.py --selftest                      # prove the checks before spending anything
  python3 run_eval.py --variant baseline              # every task, 5 trials each
  python3 run_eval.py --variant sonnet --model sonnet --tasks rename-function,parse-duration
  python3 run_eval.py --regrade results.csv           # rerun the transcript graders on saved transcripts
  python3 report.py results.csv

Needs Python 3.9+, git and the `claude` CLI. Standard library only.
"""
import argparse
import csv
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
TASKS = HERE / "tasks"

# The harness under test. Change any line here and you are evaluating a different agent.
BUILT_IN_TOOLS = "Bash,Edit,Read,Write,Glob,Grep"
ALLOWED = [
    "Read", "Edit", "Write", "Glob", "Grep",
    "Bash(python3 *)", "Bash(ls *)", "Bash(cat *)", "Bash(rm *)", "Bash(mv *)",
    "Bash(git status*)", "Bash(git diff*)", "Bash(git mv *)", "Bash(git rm *)",
]
FIELDS = [
    "variant", "task", "trial", "passed", "end_state", "transcript_check", "check", "turns", "tool_calls",
    "tool_errors", "denied_calls", "wall_seconds", "cost_usd", "stop", "model", "claude_code",
]


def make_workdir(task):
    """Copy the task's starting repo into a new temporary directory and commit it."""
    work = pathlib.Path(tempfile.mkdtemp(prefix=f"agent-eval-{task}-"))
    shutil.copytree(TASKS / task / "repo", work, dirs_exist_ok=True)
    git = ["git", "-c", "user.name=eval", "-c", "user.email=eval@example.com"]
    subprocess.run(git + ["init", "-q", "-b", "main"], cwd=work, check=True)
    (work / ".git" / "info" / "exclude").write_text("__pycache__/\n")
    subprocess.run(git + ["add", "-A"], cwd=work, check=True)
    subprocess.run(git + ["commit", "-q", "-m", "start"], cwd=work, check=True)
    return work


def run_check(task, work):
    """Grade the end state. Returns (passed, the check's one line of output)."""
    done = subprocess.run(["bash", str(TASKS / task / "check.sh"), str(work)], capture_output=True, text=True)
    return done.returncode == 0, done.stdout.strip().splitlines()[-1] if done.stdout.strip() else "no output"


def run_transcript_check(task, transcript):
    """Grade the transcript, for tasks that have a second grader. Returns (passed or None, output)."""
    script = TASKS / task / "check_transcript.py"
    if not script.exists():
        return None, ""
    done = subprocess.run([sys.executable, str(script), str(transcript)], capture_output=True, text=True)
    return done.returncode == 0, done.stdout.strip().splitlines()[-1] if done.stdout.strip() else "no output"


def grade(row, task, end_state, reason, transcript):
    """Fill the verdict columns. The transcript grader only runs when the end state passed."""
    row.update(end_state=int(end_state), transcript_check="", passed=int(end_state), check=reason)
    if end_state:
        ok, why = run_transcript_check(task, transcript)
        if ok is not None:
            row.update(transcript_check=int(ok), passed=int(ok), check=why)
    return row


def regrade(path):
    """Rerun the transcript graders over a results file, using the transcripts saved beside it."""
    out = pathlib.Path(path)
    rows = list(csv.DictReader(out.open()))
    changed = 0
    for row in rows:
        before = row["passed"]
        transcript = out.parent / "transcripts" / row["variant"] / f"{row['task']}-{row['trial']}.jsonl"
        end_state = int(row.get("end_state") or row["passed"])
        reason = row["check"] if not row.get("transcript_check") else "PASS"
        grade(row, row["task"], end_state, reason, transcript)
        if str(row["passed"]) != str(before):
            changed += 1
            print(f"{row['variant']} {row['task']} trial {row['trial']}: passed {before} -> {row['passed']}  ({row['check']})")
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"regraded {len(rows)} rows, {changed} verdict(s) changed")


def run_agent(prompt, work, args, transcript):
    """Run one headless Claude Code session in the work directory and save its event stream."""
    command = [
        "claude", "-p", prompt,
        "--model", args.model,
        "--output-format", "stream-json", "--verbose",
        "--setting-sources", "project",      # skip user-level settings and instructions
        "--strict-mcp-config",               # no MCP servers
        "--disable-slash-commands",          # no skills
        "--no-session-persistence",
        "--tools", BUILT_IN_TOOLS,
        "--permission-mode", "dontAsk",      # anything not allowed below is denied, never prompted
        "--allowedTools", *ALLOWED,
        "--max-turns", str(args.max_turns),
        "--max-budget-usd", str(args.max_budget_usd),
    ]
    started = time.monotonic()
    try:
        done = subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=args.timeout)
        stdout = done.stdout
    except subprocess.TimeoutExpired as expired:
        stdout = (expired.stdout or b"").decode() if isinstance(expired.stdout, bytes) else (expired.stdout or "")
    wall = time.monotonic() - started
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_text(stdout)

    row = {"turns": "", "tool_calls": 0, "tool_errors": 0, "denied_calls": "", "cost_usd": "", "stop": "no result event", "model": "", "claude_code": ""}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            row["model"], row["claude_code"] = event.get("model", ""), event.get("claude_code_version", "")
        elif kind == "assistant":
            row["tool_calls"] += sum(1 for block in event["message"]["content"] if block.get("type") == "tool_use")
        elif kind == "user":
            content = event["message"]["content"]
            if isinstance(content, list):
                row["tool_errors"] += sum(1 for block in content if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("is_error"))
        elif kind == "result":
            row.update(turns=event.get("num_turns", ""), cost_usd=f"{event.get('total_cost_usd', 0):.4f}",
                       stop=event.get("subtype", ""), denied_calls=len(event.get("permission_denials", [])))
    row["wall_seconds"] = f"{wall:.1f}"
    return row


def selftest():
    """Run every check on the untouched repo, the reference solution and a known wrong solution."""
    problems = 0
    print(f"{'task':<30}{'untouched':<12}{'solution.sh':<14}{'wrong.sh':<10}")
    for task in sorted(path.name for path in TASKS.iterdir()):
        verdicts = []
        for script in (None, "solution.sh", "wrong.sh"):
            work = make_workdir(task)
            if script:
                subprocess.run(["bash", str(TASKS / task / script)], cwd=work, check=True)
            verdicts.append(run_check(task, work))
            shutil.rmtree(work)
        untouched_should_pass = (TASKS / task / "solution.sh").read_text().strip().endswith("true")
        expected = [untouched_should_pass, True, False]
        problems += [passed for passed, _ in verdicts] != expected
        print(f"{task:<30}" + "".join(f"{'pass' if passed else 'fail':<{width}}" for (passed, _), width in zip(verdicts, (12, 14, 10))))
        print(f"{'':<30}wrong.sh -> {verdicts[2][1]}")
    print("selftest:", "ok" if not problems else f"{problems} task(s) graded a known state wrongly")
    return 1 if problems else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selftest", action="store_true", help="check the graders against known states and exit")
    parser.add_argument("--regrade", metavar="CSV", help="rerun the transcript graders over a results file and exit")
    parser.add_argument("--variant", default="baseline", help="label written to every row of this batch")
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--tasks", default="", help="comma-separated task names (default: all)")
    parser.add_argument("--append-prompt", default="", help="text added to the end of every task prompt")
    parser.add_argument("--out", default="results.csv")
    parser.add_argument("--max-turns", type=int, default=25)
    parser.add_argument("--max-budget-usd", type=float, default=0.50)
    parser.add_argument("--timeout", type=int, default=600, help="wall-clock limit per run, in seconds")
    parser.add_argument("--keep", action="store_true", help="keep every work directory, not only the failed ones")
    args = parser.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.regrade:
        sys.exit(regrade(args.regrade))

    tasks = [name for name in args.tasks.split(",") if name] or sorted(path.name for path in TASKS.iterdir())
    out = pathlib.Path(args.out)
    new_file = not out.exists()
    with out.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for task in tasks:
            prompt = (TASKS / task / "prompt.txt").read_text().strip()
            if args.append_prompt:
                prompt = f"{prompt}\n\n{args.append_prompt}"
            for trial in range(1, args.trials + 1):
                work = make_workdir(task)
                transcript = out.parent / "transcripts" / args.variant / f"{task}-{trial}.jsonl"
                row = run_agent(prompt, work, args, transcript)
                end_state, reason = run_check(task, work)
                grade(row, task, end_state, reason, transcript)
                row.update(variant=args.variant, task=task, trial=trial)
                passed, reason = bool(row["passed"]), row["check"]
                writer.writerow(row)
                handle.flush()
                print(f"{args.variant:<12}{task:<30}{trial}  {'pass' if passed else 'FAIL'}  turns={row['turns']} tools={row['tool_calls']} "
                      f"{row['wall_seconds']}s ${row['cost_usd']}  {'' if passed else reason + '  kept: ' + str(work)}", flush=True)
                if end_state and not args.keep:
                    shutil.rmtree(work)


if __name__ == "__main__":
    main()
