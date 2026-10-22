"""The API documentation article quotes api-reference-check.mjs, which checks the
documented POST /exports reference against the writing-lab service it describes.

Pins the two verdicts the article shows: every documented response matches the real
fixture, and a one-status change in a copy of the service is reported as a DIFF with
exit status 1. Also checks the script leaves no files behind in its working directory.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "static/examples"
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "node is not installed")
class ApiReferenceCheckTests(unittest.TestCase):
    def run_check(self, *args, cwd):
        return subprocess.run([NODE, str(EXAMPLES / "api-reference-check.mjs"), *args],
                              cwd=cwd, capture_output=True, text=True, timeout=60)

    def test_reference_matches_the_fixture_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as cwd:
            result = self.run_check(str(EXAMPLES / "writing-lab/service.mjs"), cwd=cwd)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS: 9 of 9 documented responses match", result.stdout)
            self.assertEqual(list(Path(cwd).iterdir()), [])

    def run_module(self, body):
        script = f"import {{ REFERENCE, buildRequest }} from '{(EXAMPLES / 'api-reference-check.mjs').as_uri()}';\n{body}"
        result = subprocess.run([NODE, "--input-type=module", "-e", script],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_no_content_type_row_really_omits_the_header(self):
        # Review round 4, finding 5: a string body made fetch add text/plain;charset=UTF-8,
        # so the "no Content-Type header" row tested a different request. A local server
        # records the Content-Type each documented row actually arrives with.
        seen = json.loads(self.run_module("""
import { createServer } from 'node:http';
const seen = [];
const server = createServer((req, res) => { seen.push(req.headers['content-type'] ?? null); req.resume(); req.on('end', () => res.end('{}')); });
await new Promise((done) => server.listen(0, '127.0.0.1', done));
const base = `http://127.0.0.1:${server.address().port}`;
for (const row of REFERENCE) await (await fetch(buildRequest(base, row))).text();
server.close();
console.log(JSON.stringify(seen));
"""))
        self.assertEqual(len(seen), 9)
        self.assertIsNone(seen[-1])
        self.assertEqual(set(seen[:-1]), {"application/json"})

    def test_a_string_body_would_have_carried_the_header(self):
        # Pins the cause of finding 5, so a later edit back to a string body is caught.
        header = self.run_module("console.log(new Request('http://x/', { method: 'POST', body: '{}' }).headers.get('content-type'));")
        self.assertEqual(header, "text/plain;charset=UTF-8")

    def test_a_changed_status_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            for source in (EXAMPLES / "writing-lab").glob("*.mjs"):
                shutil.copy(source, tmp)
            service = Path(tmp) / "service.mjs"
            text = service.read_text()
            self.assertIn("prior ? 200 : 202", text)
            service.write_text(text.replace("prior ? 200 : 202", "prior ? 200 : 201"))
            result = self.run_check(str(service), cwd=tmp)
            self.assertEqual(result.returncode, 1)
            self.assertIn("DIFF 202 new key   got 201", result.stdout)
            self.assertIn("FAIL: 2 of 9 documented responses differ", result.stdout)


if __name__ == "__main__":
    unittest.main()
