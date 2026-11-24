"""The checker scripts that shipped with the articles of 2026-11-23.

Each article quotes its checker's verdict on a filled example and on a broken copy, so
these tests pin those verdicts: the blank template fails --filled, the filled example
passes, and the edit the article describes fails with the message the article prints.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "static/templates"
EXAMPLES = ROOT / "static/examples"


def run(script, *args, cwd=None):
    result = subprocess.run([sys.executable, str(script), *map(str, args)],
                            cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def edited_copy(source, replacements, folder):
    text = source.read_text(encoding="utf-8")
    for old, new in replacements:
        if old not in text:
            raise AssertionError(f"{source.name} no longer contains {old!r}")
        text = text.replace(old, new, 1)
    copy = Path(folder) / source.name
    copy.write_text(text, encoding="utf-8")
    return copy


class TroubleshootingGuideCheckerTests(unittest.TestCase):
    checker = TEMPLATES / "check_troubleshooting_guide.py"
    template = TEMPLATES / "troubleshooting-guide-template.md"
    example = EXAMPLES / "troubleshooting-sqlite.md"

    def test_filled_example_passes_with_the_counts_the_article_prints(self):
        code, out = run(self.checker, "--filled", self.example)
        self.assertEqual(code, 0, out)
        for line in ("entries checked: 4", "causes checked: 6",
                     "entries whose heading quotes the error text: 3 of 4", "unfilled placeholders: 0"):
            self.assertIn(line, out)

    def test_blank_template_passes_structure_and_fails_filled(self):
        self.assertEqual(run(self.checker, self.template)[0], 0)
        code, out = run(self.checker, "--filled", self.template)
        self.assertEqual(code, 1, out)
        self.assertIn("placeholder", out)

    def test_retyped_error_text_in_a_heading_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            copy = edited_copy(self.example, [("## `database is locked`", "## `database locked`")], folder)
            code, out = run(self.checker, "--filled", copy)
        self.assertEqual(code, 1, out)
        self.assertIn("which is not in its Symptom block", out)


class PostmortemCheckerTests(unittest.TestCase):
    checker = TEMPLATES / "check_postmortem.py"
    template = TEMPLATES / "postmortem-template.md"
    example = EXAMPLES / "postmortem-intake-writes-failed.md"

    def test_filled_example_passes_and_derives_both_durations(self):
        code, out = run(self.checker, "--filled", self.example)
        self.assertEqual(code, 0, out)
        for line in ("timeline rows checked: 15, time zone UTC", "time to detect: 7 s",
                     "time to mitigate: 21 s", "unfilled placeholders: 0"):
            self.assertIn(line, out)

    def test_blank_template_passes_structure_and_fails_filled(self):
        self.assertEqual(run(self.checker, self.template)[0], 0)
        code, out = run(self.checker, "--filled", self.template)
        self.assertEqual(code, 1, out)
        self.assertIn("unfilled placeholder", out)

    def test_a_stated_duration_that_disagrees_with_the_timeline_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            copy = edited_copy(self.example, [("Duration: 21 s", "Duration: 20 s")], folder)
            code, out = run(self.checker, "--filled", copy)
        self.assertEqual(code, 1, out)
        self.assertIn("'Duration:' says 20 s, and the timeline gives 21 s", out)

    def test_a_blame_phrase_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            copy = edited_copy(self.example, [("Time to detect: 7 s", "Time to detect: 7 s, after human error")], folder)
            code, out = run(self.checker, "--filled", copy)
        self.assertEqual(code, 1, out)
        self.assertIn("blame phrase 'human error'", out)


class ReadmeCheckerTests(unittest.TestCase):
    checker = TEMPLATES / "check_readme.py"
    template = TEMPLATES / "readme-template.md"
    example = EXAMPLES / "readme-example/README.md"

    def test_filled_example_passes_the_structure_checks(self):
        code, out = run(self.checker, "--filled", self.example)
        self.assertEqual(code, 0, out)
        self.assertIn("sections found: Install, Usage, Tests, Help and contributing, License", out)

    def test_blank_template_fails_filled(self):
        code, out = run(self.checker, "--filled", self.template)
        self.assertEqual(code, 1, out)
        self.assertIn("unfilled placeholder", out)

    def test_a_requires_line_without_a_version_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            copy = edited_copy(self.example, [("Requires: Python 3.9 or later", "Requires: Python")], folder)
            code, out = run(self.checker, "--filled", copy)
        self.assertEqual(code, 1, out)
        self.assertIn("Requires", out)


class DocsAsCodeExampleCheckTests(unittest.TestCase):
    repo = EXAMPLES / "docs-as-code"

    def test_every_console_example_on_the_usage_page_prints_what_the_page_shows(self):
        code, out = run(self.repo / "scripts/check_examples.py", "docs/usage.md", cwd=self.repo)
        self.assertEqual(code, 0, out)
        self.assertIn("PASS: examples that print what the page shows: 3 of 3", out)

    def test_the_unit_tests_of_the_example_tool_pass(self):
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                                cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
