"""Run current-tree checks and retain exact outputs under this task only."""
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
commands = [
    ["python3", "build.py"],
    ["python3", str(HERE / "verify.py")],
    ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
    ["python3", "tools/content_inventory_gate.py", "--strict"],
    ["python3", "tools/audit_clusters.py", "--strict"],
    ["python3", "tools/audit_stylesheets.py", "--strict"],
    ["python3", "tools/audit_structure.py", "--strict"],
    ["python3", "tools/audit_inert_css.py", "--strict"],
    ["git", "diff", "--check"],
]
results = []
for index, command in enumerate(commands):
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = f"check-{index:02}.log"
    (HERE / log).write_text(result.stdout)
    results.append({"command": command, "exit_code": result.returncode, "log": log})
    print(f"{result.returncode}: {' '.join(command)}", flush=True)
    assert result.returncode == 0, result.stdout[-4000:]
paths = [row["source"] for row in json.loads((HERE / "note-review-map.json").read_text())]
regressions = []
with tempfile.TemporaryDirectory(prefix="ninad-work-note-baseline-") as temporary:
    baseline = []
    for name in paths:
        target = Path(temporary) / Path(name).name
        target.write_bytes(subprocess.check_output(["git", "show", "60909b2c:" + name], cwd=ROOT))
        baseline.append(str(target))
    for label, command, pattern in [
        ("writing", ["python3", "rule_checker.py", "--summary"], r"TOTAL: (\d+) errors"),
        ("claims", ["python3", "tools/audit_claims.py", "--paths"], r"(\d+) candidate claim"),
    ]:
        runs = {}
        for state, inputs in [("before", baseline), ("after", paths)]:
            result = subprocess.run(command + inputs, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            match = re.search(pattern, result.stdout)
            assert match, result.stdout
            log = f"{label}-{state}.log"
            (HERE / log).write_text("\n".join(line.rstrip() for line in result.stdout.splitlines()) + "\n")
            runs[state] = {"count": int(match.group(1)), "exit_code": result.returncode, "log": log}
        assert runs["after"]["count"] <= runs["before"]["count"], label
        regressions.append({"check": label, **runs})
        print(f"{label}: {runs['before']['count']} -> {runs['after']['count']}", flush=True)
(HERE / "checks.json").write_text(json.dumps({"checks": results, "regressions": regressions}, indent=2) + "\n")
