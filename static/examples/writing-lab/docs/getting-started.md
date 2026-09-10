# Accept a local export request

Use Node.js 24.18.0 and curl in a POSIX shell. Run commands from the extracted `writing-lab` directory. The fixture has no third-party dependencies. It binds to loopback on a port assigned by the operating system.

```bash
node --version
node check.mjs
node service.mjs
```

The check must end with `PASS`. If it fails, stop and retain the error before using the manual instructions. The server prints a URL such as `http://127.0.0.1:49152` and remains running. If startup exits, inspect that terminal's error instead of guessing a port.

In a second terminal, set the URL to the value actually printed:

```bash
export LAB_URL=http://127.0.0.1:49152
curl --fail-with-body "$LAB_URL/health"
curl -i "$LAB_URL/exports" \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: report-a' \
  --data '{"format":"csv"}'
```

The health response is `{"status":"ok"}`. On a fresh server the export returns HTTP 202 with `{"id":"exp_1","format":"csv","status":"accepted"}`. The response means a record was stored; it does not mean a file exists. HTTP 200 means that this key already identifies the same request. If you receive another status or no response, use [troubleshooting](troubleshooting.md).

Leave this server running for [the recovery experiment](send-a-request.md). Press Ctrl-C in its terminal when finished; stopping it erases every stored request.
