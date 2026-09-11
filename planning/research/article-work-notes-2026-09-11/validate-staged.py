"""Build and test an isolated export of the exact Git index, not dirty work."""
import io
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
tree = subprocess.check_output(["git", "write-tree"], cwd=ROOT, text=True).strip()
archive = subprocess.check_output(["git", "archive", tree], cwd=ROOT)
commands = [
    ["python3", "build.py"],
    ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
    ["python3", "tools/content_inventory_gate.py", "--strict"],
    ["python3", "tools/audit_clusters.py", "--strict"],
    ["python3", "tools/audit_stylesheets.py", "--strict"],
    ["python3", "tools/audit_structure.py", "--strict"],
    ["python3", "tools/audit_inert_css.py", "--strict"],
]
results = []
with tempfile.TemporaryDirectory(prefix="ninad-work-note-staged-") as directory:
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(directory)
    for index, command in enumerate(commands):
        result = subprocess.run(command, cwd=directory, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log = f"staged-{index:02}.log"
        (HERE / log).write_text("\n".join(line.rstrip() for line in result.stdout.splitlines()) + "\n")
        results.append({"command": command, "exit_code": result.returncode, "log": log})
        print(f"{result.returncode}: {' '.join(command)}", flush=True)
        assert result.returncode == 0, result.stdout[-4000:]
(HERE / "staged-validation.json").write_text(json.dumps({"validated_tree": tree, "method": "git archive of index tree into disposable directory; generated evidence is added afterward", "checks": results, "temporary_export_removed": True}, indent=2) + "\n")
