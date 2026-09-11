"""Compare only surviving changed posts against HEAD; removed sources are archived."""
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
paths = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=ACMR', 'HEAD', '--', 'content/posts/*.md'], cwd=ROOT, text=True).splitlines()
reports = []
with tempfile.TemporaryDirectory(prefix='ninad-removal-writing-') as directory:
    baseline = []
    for name in paths:
        target = Path(directory) / Path(name).name
        target.write_bytes(subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT))
        baseline.append(str(target))
    for label, command, pattern in [
        ('writing', ['python3', 'rule_checker.py', '--summary'], r'TOTAL: (\d+) errors'),
        ('claims', ['python3', 'tools/audit_claims.py', '--paths'], r'(\d+) candidate claim'),
    ]:
        runs = {}
        for state, inputs in [('before', baseline), ('after', paths)]:
            result = subprocess.run(command + inputs, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            match = re.search(pattern, result.stdout)
            assert match, result.stdout
            runs[state] = {'count': int(match.group(1)), 'exit_code': result.returncode, 'output': result.stdout}
        assert runs['after']['count'] <= runs['before']['count'], label
        reports.append({'check': label, **runs})
(HERE / 'writing-regressions.json').write_text(json.dumps({'paths': paths, 'reports': reports}, indent=2) + '\n')
for report in reports:
    print(f'{report["check"]}: {report["before"]["count"]} -> {report["after"]["count"]}; no regression')
