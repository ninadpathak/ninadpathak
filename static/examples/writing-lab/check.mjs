import assert from 'node:assert/strict';
import { once } from 'node:events';
import { connect } from 'node:net';
import { createFixture } from './service.mjs';
import { sign } from './webhook.mjs';

const server = createFixture();
server.listen(0, '127.0.0.1');
await once(server, 'listening');
const base = `http://127.0.0.1:${server.address().port}`;
async function request(path, body, headers = {}) {
  return fetch(base + path, { method: 'POST', headers: { 'content-type': 'application/json', ...headers }, body });
}
try {
  assert.equal((await fetch(base + '/health')).status, 200);
  const raw = '{"type":"order.created","id":"evt_local"}';
  const valid = await request('/webhooks/orders', raw, { 'x-example-signature': sign(raw) });
  assert.equal(valid.status, 204);
  console.log('valid signature: 204');
  for (const signature of ['0'.repeat(64), 'short', undefined]) {
    const headers = signature ? { 'x-example-signature': signature } : {};
    assert.equal((await request('/webhooks/orders', raw, headers)).status, 401);
  }
  console.log('wrong, malformed, missing signatures: 401');
  assert.equal((await request('/webhooks/orders', raw + ' ', { 'x-example-signature': sign(raw) })).status, 401);
  console.log('body changed after signing: 401');
  assert.equal((await request('/webhooks/orders', '{', { 'x-example-signature': sign('{') })).status, 400);
  console.log('signed invalid JSON: 400');
  let dropped = false;
  try { await request('/exports', '{"format":"csv"}', { 'idempotency-key': 'report-a', 'x-fixture-drop-response': 'yes' }); }
  catch { dropped = true; }
  assert.ok(dropped, 'the fixture should close the connection without a response');
  console.log('response dropped after storage: client fetch rejected');
  const retry = await request('/exports', '{"format":"csv"}', { 'idempotency-key': 'report-a' });
  assert.equal(retry.status, 200);
  assert.equal((await retry.json()).id, 'exp_1');
  console.log('same key and payload: 200 exp_1');
  const conflict = await request('/exports', '{"format":"json"}', { 'idempotency-key': 'report-a' });
  assert.equal(conflict.status, 409);
  console.log('same key, changed format: 409');
  const duplicate = await request('/exports', '{"format":"csv"}', { 'idempotency-key': 'report-b' });
  assert.equal(duplicate.status, 202);
  assert.equal((await duplicate.json()).id, 'exp_2');
  console.log('new key for same format: 202 exp_2');
  assert.equal((await request('/exports', '{"format":"csv"}')).status, 400);
  assert.equal((await request('/exports', '{"format":"xml"}', { 'idempotency-key': 'report-c' })).status, 400);
  const state = await (await fetch(base + '/state')).json();
  assert.deepEqual(state, { exports: 2, events: 1 });
  console.log('stored state: ' + JSON.stringify(state));
  const socket = connect(server.address().port, '127.0.0.1');
  await once(socket, 'connect');
  const incoming = once(server, 'request');
  socket.write('POST /exports HTTP/1.1\r\nHost: localhost\r\nContent-Length: 100\r\nIdempotency-Key: aborted\r\n\r\n{');
  const [partialRequest] = await incoming;
  const aborted = once(partialRequest, 'aborted');
  socket.destroy();
  await aborted;
  const afterAbort = await (await fetch(base + '/state')).json();
  assert.deepEqual(afterAbort, state);
  console.log('partial upload disconnected: server alive, prior state intact');
  const payload = '{"format":"csv"}';
  const boundary = await request('/exports', payload.padEnd(4096, ' '), { 'idempotency-key': 'boundary-ok' });
  assert.equal(boundary.status, 202);
  const oversized = await request('/exports', payload.padEnd(4097, ' '), { 'idempotency-key': 'boundary-rejected' });
  assert.equal(oversized.status, 413);
  assert.deepEqual(await (await fetch(base + '/state')).json(), { exports: 3, events: 1 });
  console.log('body limits: 4096 bytes accepted, 4097 bytes rejected; rejected body not stored');
  const replay = await request('/webhooks/orders', raw, { 'x-example-signature': sign(raw) });
  assert.equal(replay.status, 204);
  assert.deepEqual(await (await fetch(base + '/state')).json(), { exports: 3, events: 2 });
  console.log('replayed valid event: 204; event count increased from 1 to 2');


} finally {
  server.closeAllConnections();
  await new Promise(resolve => server.close(resolve));
}
// A new fixture has no retention from the previous process instance.
const restarted = createFixture();
restarted.listen(0, '127.0.0.1');
await once(restarted, 'listening');
try {
  const state = await (await fetch(`http://127.0.0.1:${restarted.address().port}/state`)).json();
  assert.deepEqual(state, { exports: 0, events: 0 });
  console.log('new fixture state: ' + JSON.stringify(state));
} finally {
  restarted.closeAllConnections();
  await new Promise(resolve => restarted.close(resolve));
}
console.log('PASS');
