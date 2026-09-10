import { createServer } from 'node:http';
import { pathToFileURL } from 'node:url';
import { verify } from './webhook.mjs';

export function createFixture() {
  const exportsByKey = new Map();
  const events = [];
  const send = (res, status, value) => {
    res.writeHead(status, { 'content-type': 'application/json' });
    res.end(JSON.stringify(value));
  };
  return createServer(async (req, res) => {
    if (req.method === 'GET' && req.url === '/health') return send(res, 200, { status: 'ok' });
    if (req.method === 'GET' && req.url === '/state') {
      return send(res, 200, { exports: exportsByKey.size, events: events.length });
    }
    if (req.method !== 'POST' || !['/exports', '/webhooks/orders'].includes(req.url)) {
      return send(res, 404, { error: 'not_found' });
    }
    const chunks = [];
    let size = 0;
    for await (const chunk of req) {
      size += chunk.length;
      if (size > 4096) return send(res, 413, { error: 'body_too_large' });
      chunks.push(chunk);
    }
    const raw = Buffer.concat(chunks);
    if (req.url === '/webhooks/orders' && !verify(raw, req.headers['x-example-signature'])) {
      return send(res, 401, { error: 'invalid_signature' });
    }
    let body;
    try { body = JSON.parse(raw.toString('utf8')); }
    catch { return send(res, 400, { error: 'invalid_json' }); }
    if (req.url === '/webhooks/orders') {
      if (!body || body.type !== 'order.created' || typeof body.id !== 'string') {
        return send(res, 400, { error: 'invalid_event' });
      }
      events.push(body.id);
      res.writeHead(204);
      return res.end();
    }
    const key = req.headers['idempotency-key'];
    if (typeof key !== 'string' || !/^[a-zA-Z0-9-]{1,64}$/.test(key)) {
      return send(res, 400, { error: 'invalid_key' });
    }
    if (!body || !['csv', 'json'].includes(body.format) || Object.keys(body).length !== 1) {
      return send(res, 400, { error: 'invalid_format' });
    }
    const prior = exportsByKey.get(key);
    if (prior && prior.format !== body.format) return send(res, 409, { error: 'key_conflict' });
    const entry = prior || { id: `exp_${exportsByKey.size + 1}`, format: body.format, status: 'accepted' };
    exportsByKey.set(key, entry);
    // Simulate losing a response after storing the request, once per new key.
    if (!prior && req.headers['x-fixture-drop-response'] === 'yes') return res.destroy();
    return send(res, prior ? 200 : 202, entry);
  });
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const server = createFixture();
  server.listen(0, '127.0.0.1', () => console.log(`http://127.0.0.1:${server.address().port}`));
}
