"""Every script a visitor's browser parses must at least parse.

Two published Three.js visuals declared `const controls` twice, so their module scripts
threw a SyntaxError before running a line, and nothing in the build noticed. This parses
each inline script in static/visuals/ and every file in static/js/ with `node --check`.
It proves syntax only: a visual can still fail at runtime.
"""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


def node_check(source, module):
    suffix = ".mjs" if module else ".js"
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as handle:
        handle.write(source)
    try:
        result = subprocess.run([NODE, "--check", handle.name], capture_output=True, text=True)
    finally:
        Path(handle.name).unlink()
    return result.returncode, result.stderr.strip().splitlines()[-1:] if result.stderr else []


@unittest.skipIf(NODE is None, "node is not installed")
class ScriptSyntaxTests(unittest.TestCase):
    def test_inline_scripts_in_visuals_parse(self):
        for path in sorted((ROOT / "static" / "visuals").glob("*.html")):
            html = path.read_text(encoding="utf-8")
            for index, (attributes, source) in enumerate(re.findall(r"<script([^>]*)>(.*?)</script>", html, re.S)):
                if "src=" in attributes or not source.strip():
                    continue
                with self.subTest(visual=path.name, script=index):
                    if "importmap" in attributes:
                        json.loads(source)
                        continue
                    status, error = node_check(source, 'type="module"' in attributes)
                    self.assertEqual(status, 0, error)

    def test_site_scripts_parse(self):
        for path in sorted((ROOT / "static" / "js").glob("*.js")):
            with self.subTest(script=path.name):
                status, error = node_check(path.read_text(encoding="utf-8"), module=False)
                self.assertEqual(status, 0, error)


if __name__ == "__main__":
    unittest.main()
