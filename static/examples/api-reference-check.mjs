// Check a documented API reference against the service it describes.
//
// Each row of REFERENCE is one documented request and the status and body the
// reference page promises. The script starts its own copy of the writing-lab export
// service on 127.0.0.1 with a random port, sends the rows in order, compares each
// response with the documentation, then stops the server. It writes no files.
//
// Usage (Node.js 18 or later, next to the extracted writing-lab folder):
//   node api-reference-check.mjs                       # checks ./writing-lab/service.mjs
//   node api-reference-check.mjs path/to/service.mjs   # checks another copy
// Exit status: 0 when every row matches, 1 when any row differs.
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

// Order matters: rows 1-3 reuse the key "report-a" to document idempotency.
export const REFERENCE = [
  { case: 'new key', key: 'report-a', body: '{"format":"csv"}', status: 202, json: { id: 'exp_1', format: 'csv', status: 'accepted' } },
  { case: 'same key, same body', key: 'report-a', body: '{"format":"csv"}', status: 200, json: { id: 'exp_1', format: 'csv', status: 'accepted' } },
  { case: 'same key, different body', key: 'report-a', body: '{"format":"json"}', status: 409, json: { error: 'key_conflict' } },
  { case: 'missing key', key: null, body: '{"format":"csv"}', status: 400, json: { error: 'invalid_key' } },
  { case: 'unsupported format', key: 'report-b', body: '{"format":"pdf"}', status: 400, json: { error: 'invalid_format' } },
  { case: 'extra field', key: 'report-b', body: '{"format":"csv","limit":5}', status: 400, json: { error: 'invalid_format' } },
  { case: 'malformed JSON', key: 'report-b', body: '{format:csv}', status: 400, json: { error: 'invalid_json' } },
  { case: 'body over 4 KB', key: 'report-c', body: JSON.stringify({ format: 'x'.repeat(5000) }), status: 413, json: { error: 'body_too_large' } },
];

export async function check(servicePath) {
  const { createFixture } = await import(pathToFileURL(resolve(servicePath)).href);
  const server = createFixture();
  await new Promise((done) => server.listen(0, '127.0.0.1', done));
  const base = `http://127.0.0.1:${server.address().port}`;
  const rows = [];
  try {
    for (const row of REFERENCE) {
      const headers = { 'Content-Type': 'application/json' };
      if (row.key) headers['Idempotency-Key'] = row.key;
      const response = await fetch(`${base}/exports`, { method: 'POST', headers, body: row.body });
      const text = await response.text();
      let body;
      try { body = JSON.parse(text); } catch { body = text; }
      const ok = response.status === row.status && JSON.stringify(body) === JSON.stringify(row.json);
      rows.push({ ...row, ok, gotStatus: response.status, gotBody: body });
    }
  } finally {
    await new Promise((done) => server.close(done));
  }
  return rows;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const rows = await check(process.argv[2] || './writing-lab/service.mjs');
  for (const row of rows) {
    const verdict = row.ok ? 'ok  ' : 'DIFF';
    const got = row.ok ? '' : `   got ${row.gotStatus} ${JSON.stringify(row.gotBody)}`;
    console.log(`${verdict} ${String(row.status).padEnd(4)}${row.case}${got}`);
  }
  const failed = rows.filter((row) => !row.ok).length;
  console.log(failed ? `FAIL: ${failed} of ${rows.length} documented responses differ` : `PASS: ${rows.length} of ${rows.length} documented responses match`);
  process.exitCode = failed ? 1 : 0;
}
