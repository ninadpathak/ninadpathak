"""Rebuild and verify the bounded removal against the immutable pre-removal cohort."""
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
cohort = json.loads((HERE / 'cohort.json').read_text())
protected = json.loads((HERE / 'protected-sha256.json').read_text())
checks = []
commands = [
    ['python3', '-m', 'compileall', '-q', 'build.py', 'check_rules.py', 'rule_checker.py', 'seo_audit.py', 'tests'],
    ['python3', 'build.py'],
    ['python3', 'tools/content_inventory_gate.py', '--strict'],
    ['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
    *[['python3', 'tools/' + tool + '.py', '--strict'] for tool in
      ['audit_clusters', 'audit_stylesheets', 'audit_structure', 'audit_inert_css']],
    ['python3', 'tools/audit_claims.py', '--count'],
    ['python3', str(HERE / 'check-writing-regressions.py')],
    ['git', 'diff', '--check'],
]
for index, command in enumerate(commands):
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = f'check-{index:02d}.log'
    (HERE / log).write_text(result.stdout)
    checks.append({'command': command, 'exit_code': result.returncode, 'log': log})
    print('exit', result.returncode, ' '.join(command), flush=True)

for path, digest in protected.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path

output = ROOT / 'output'
sitemap = (output / 'sitemap.xml').read_text()
feeds = '\n'.join(p.read_text() for p in [output / 'llms.txt', output / 'feed.xml'] if p.exists())
redirects = (output / '_redirects').read_text()
dispositions = []
for post in cohort:
    source = ROOT / post['source']
    generated = output / post['canonical'].strip('/') / 'index.html'
    days = (date(2026, 9, 8) - max(date(2026, 6, 11), date.fromisoformat(post['date'][:10]))).days + 1
    if not post['impressions']:
        archive = HERE / 'archived-posts' / source.name
        assert not source.exists() and not generated.exists(), post['source']
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == post['sha256'], str(archive)
        assert post['canonical'] not in sitemap + feeds + redirects, post['canonical']
    else:
        assert source.is_file() and generated.is_file(), post['source']
        assert post['canonical'] in sitemap, post['canonical']
    dispositions.append({**post, 'eligible_calendar_days_from_source_date': max(0, days)})

for line in redirects.splitlines():
    parts = line.split()
    if len(parts) >= 2 and parts[0].startswith('/') and parts[1].startswith('/'):
        target = output / parts[1].strip('/')
        assert target.is_file() or (target / 'index.html').is_file(), line

for slug in ['ai-search-optimization', 'distribution']:
    html = (output / 'articles' / slug / 'index.html').read_text()
    assert 'noindex, follow' in html and 'No articles are currently published' in html
    assert '/articles/' + slug + '/' not in sitemap

summary = {'checks': checks, 'cohort_total': len(cohort),
           'archived': sum(not p['impressions'] for p in cohort),
           'retained': sum(bool(p['impressions']) for p in cohort),
           'archive_hashes_match': True, 'protected_hashes_match': True,
           'redirect_destinations_exist': True, 'empty_category_routes_noindex': True,
           'generated_html_count': len(list(output.rglob('*.html'))),
           'sitemap_url_count': len(ET.fromstring(sitemap)),
           'dispositions': dispositions}
(HERE / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
print('Archive, protected files, published routes, sitemap/feed, redirects and retained empty-category assertions passed.')
sys.exit(1 if any(c['exit_code'] for c in checks) else 0)
