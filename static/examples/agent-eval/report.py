#!/usr/bin/env python3
"""Summarise results.csv from run_eval.py.

  python3 report.py results.csv                         # one table per variant
  python3 report.py results.csv --compare baseline fast # the same tasks under two variants

Reports, per variant: passes per task, the pooled pass rate with a 95% Wilson
score interval, and pass^k, the tau-bench reliability metric (the chance that
k trials of a task all pass, averaged over tasks). Standard library only.
"""
import argparse
import csv
import math
from collections import defaultdict


def wilson(passes, n, z=1.96):
    """95% Wilson score interval for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0
    p = passes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def pass_hat_k(per_task, k):
    """tau-bench's estimate: mean over tasks of C(c, k) / C(n, k), for c passes in n trials."""
    return sum(math.comb(c, k) / math.comb(n, k) for c, n in per_task) / len(per_task)


def fisher_two_sided(a, b, c, d):
    """Fisher's exact test for the table [[a, b], [c, d]]: passes and fails under two variants."""
    row1, row2, col1, total = a + b, c + d, a + c, a + b + c + d

    def prob(x):
        return math.comb(row1, x) * math.comb(row2, col1 - x) / math.comb(total, col1)

    observed = prob(a)
    low, high = max(0, col1 - row2), min(row1, col1)
    return min(1.0, sum(prob(x) for x in range(low, high + 1) if prob(x) <= observed * (1 + 1e-9)))


def load(path):
    rows = defaultdict(lambda: defaultdict(list))
    for row in csv.DictReader(open(path)):
        rows[row["variant"]][row["task"]].append(row)
    return rows


def mean(values):
    values = [float(value) for value in values if value != ""]
    return sum(values) / len(values) if values else 0.0


def summarise(name, tasks):
    print(f"\nvariant: {name}   model: {next(iter(tasks.values()))[0]['model']}   Claude Code {next(iter(tasks.values()))[0]['claude_code']}")
    print(f"{'task':<30}{'passed':<8}{'turns':>6}{'tools':>7}{'seconds':>9}{'cost':>9}")
    per_task, everything = [], []
    for task in sorted(tasks):
        runs = tasks[task]
        passes = sum(int(run["passed"]) for run in runs)
        per_task.append((passes, len(runs)))
        everything += runs
        print(f"{task:<30}{f'{passes}/{len(runs)}':<8}{mean(r['turns'] for r in runs):>6.1f}{mean(r['tool_calls'] for r in runs):>7.1f}"
              f"{mean(r['wall_seconds'] for r in runs):>9.1f}{mean(r['cost_usd'] for r in runs):>9.4f}")
    passes, n = sum(c for c, _ in per_task), len(everything)
    low, high = wilson(passes, n)
    print(f"{'all runs':<30}{f'{passes}/{n}':<8}{mean(r['turns'] for r in everything):>6.1f}{mean(r['tool_calls'] for r in everything):>7.1f}"
          f"{mean(r['wall_seconds'] for r in everything):>9.1f}{mean(r['cost_usd'] for r in everything):>9.4f}")
    print(f"pass rate: {passes / n:.1%}   95% Wilson interval: {low:.1%} to {high:.1%}")
    trials = min(n for _, n in per_task)
    print("pass^k:   " + "  ".join(f"k={k}: {pass_hat_k(per_task, k):.1%}" for k in range(1, trials + 1)))
    print(f"tasks passed in every trial: {sum(c == n for c, n in per_task)} of {len(per_task)}")
    flipped = sum(r.get("end_state") == "1" and r.get("transcript_check") == "0" for r in everything)
    print(f"runs the end-state check passed and the transcript check failed: {flipped}")
    print(f"denied tool calls: {sum(int(r['denied_calls'] or 0) for r in everything)}   tool calls that returned an error: {sum(int(r['tool_errors']) for r in everything)}")
    print(f"total reported cost: ${sum(float(r['cost_usd'] or 0) for r in everything):.4f}")


def compare(rows, first, second):
    shared = sorted(set(rows[first]) & set(rows[second]))
    print(f"\n{first} vs {second}, on the {len(shared)} tasks both ran")
    print(f"{'task':<30}{first:<12}{second:<12}{'Fisher p':>9}")
    totals = [0, 0, 0, 0]
    for task in shared:
        a = sum(int(r["passed"]) for r in rows[first][task]); b = len(rows[first][task]) - a
        c = sum(int(r["passed"]) for r in rows[second][task]); d = len(rows[second][task]) - c
        totals = [totals[0] + a, totals[1] + b, totals[2] + c, totals[3] + d]
        print(f"{task:<30}{f'{a}/{a + b}':<12}{f'{c}/{c + d}':<12}{fisher_two_sided(a, b, c, d):>9.3f}")
    a, b, c, d = totals
    print(f"{'all runs':<30}{f'{a}/{a + b}':<12}{f'{c}/{c + d}':<12}{fisher_two_sided(a, b, c, d):>9.3f}")
    for name, passes, n in ((first, a, a + b), (second, c, c + d)):
        low, high = wilson(passes, n)
        print(f"{name}: {passes / n:.1%}, 95% Wilson interval {low:.1%} to {high:.1%}")
    for label, column in (("mean turns", "turns"), ("mean cost", "cost_usd"), ("mean seconds", "wall_seconds")):
        values = [mean(r[column] for task in shared for r in rows[name][task]) for name in (first, second)]
        print(f"{label}: {values[0]:.4g} vs {values[1]:.4g}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results")
    parser.add_argument("--compare", nargs=2, metavar=("FIRST", "SECOND"))
    args = parser.parse_args()
    rows = load(args.results)
    if args.compare:
        compare(rows, *args.compare)
    else:
        for name, tasks in rows.items():
            summarise(name, tasks)


if __name__ == "__main__":
    main()
