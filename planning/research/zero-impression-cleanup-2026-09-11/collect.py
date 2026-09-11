"""Read-only GSC collection; writes only this task's evidence bundle."""
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import gsc_report as gr
import frontmatter

HERE = Path(__file__).resolve().parent
if any((HERE / name).exists() for name in ('gsc-page-raw.json', 'cohort.json', 'protected-sha256.json')):
    raise SystemExit('Baseline evidence already exists; refusing to overwrite the pre-removal snapshot.')
svc = gr.search_console()
assert svc is not None, 'GSC client unavailable'
responses = []
start = 0
while True:
    request = {'startDate': '2026-06-11', 'endDate': '2026-09-08',
               'dimensions': ['page'], 'type': 'web', 'dataState': 'final',
               'rowLimit': 25000, 'startRow': start}
    response = svc.searchanalytics().query(siteUrl=gr.SITE, body=request).execute()
    responses.append({'request': request, 'response': response})
    rows = response.get('rows', [])
    if len(rows) < 25000:
        break
    start += len(rows)
all_rows = [row for page in responses for row in page['response'].get('rows', [])]
aliases = {}
for line in (ROOT / 'static/_redirects').read_text().splitlines():
    fields = line.split()
    if len(fields) >= 2 and fields[0].startswith('/'):
        aliases[fields[0].rstrip('/')] = fields[1].rstrip('/')

def resolve(path):
    path = path.rstrip('/')
    seen = set()
    while path in aliases and path not in seen:
        seen.add(path)
        path = aliases[path]
    return path

cohort = []
for path in sorted((ROOT / 'content/posts').glob('*.md')):
    post = frontmatter.load(path)
    if post.get('status') != 'published':
        continue
    slug = post.get('slug', path.stem)
    canonical = '/articles/' + slug
    variants = {canonical, '/blog/' + slug, '/blog/' + path.stem,
                '/articles/' + path.stem, '/' + slug, '/' + path.stem}
    matches = [row for row in all_rows
               if resolve(urlsplit(row['keys'][0]).path) in variants]
    impressions = sum(row['impressions'] for row in matches)
    cohort.append({'source': str(path.relative_to(ROOT)), 'slug': slug,
                   'date': str(post.get('date')), 'title': post.get('title'),
                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                   'canonical': canonical + '/', 'matched_rows': matches,
                   'impressions': impressions,
                   'disposition': 'ARCHIVE_ZERO_RECORDED_IMPRESSIONS' if not impressions else 'RETAIN'})
protected = [p for p in (ROOT / 'planning').rglob('*') if p.is_file() and str(p.relative_to(ROOT)) in {
 'planning/attribution.md', 'planning/daily-cycle.md', 'planning/leading-indicators.md',
 'planning/position.md', 'planning/research/essay-rewrite-2026-09-10/handoff.md',
 'planning/scoreboard.md', 'planning/url-inventory.json', 'planning/video/brief-001.md',
 'planning/research/essay-rewrite-2026-09-10/publication.json', 'planning/video/review-001.md'}]
for name, data in [('gsc-page-raw.json', {'property': gr.SITE, 'pages': responses}),
                   ('cohort.json', cohort),
                   ('protected-sha256.json', {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected})]:
    (HERE / name).write_text(json.dumps(data, indent=2) + '\n')
print(f'{len(all_rows)} raw rows; {len(cohort)} published; {sum(not p["impressions"] for p in cohort)} zero-recorded-impression articles')
for post in cohort:
    if not post['impressions']:
        print(post['source'], post['date'])
