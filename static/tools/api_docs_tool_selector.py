#!/usr/bin/env python3
import json, sys
choices = json.load(open(sys.argv[1]))
required = {'source_of_truth', 'review_path', 'deployment'}
missing = required - choices.keys()
if missing:
    raise SystemExit('FAIL: missing ' + ', '.join(sorted(missing)))
rows = {
 'openapi-and-repository': 'Swagger UI or Redocly',
 'openapi-with-release-diffs': 'Bump.sh',
 'markdown-and-managed-portal': 'Mintlify',
}
key = choices['source_of_truth']
if key not in rows:
    raise SystemExit('FAIL: unknown source_of_truth')
print('PASS: ' + rows[key])
print('review=' + choices['review_path'] + ' deployment=' + choices['deployment'])
