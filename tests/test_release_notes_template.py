"""The release notes template ships with a checker the article tells readers to run.

The article quotes the checker's output, so these tests pin that output's verdicts:
the blank template passes structurally but fails --filled, the filled SDK example
passes --filled, and removing the Rollback line or writing a non-date deadline fails.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "static/templates/release-notes-template.md"
EXAMPLE = ROOT / "static/examples/release-notes-sdk-4.0.0.md"

spec = importlib.util.spec_from_file_location("check_release_notes", ROOT / "static/templates/check_release_notes.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ReleaseNotesTemplateTests(unittest.TestCase):
    def test_blank_template_passes_structure_and_fails_filled(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(checker.check(text, filled=False)[0], [])
        errors = checker.check(text, filled=True)[0]
        self.assertEqual(len(errors), 1)
        self.assertIn("unfilled placeholder", errors[0])

    def test_filled_example_passes(self):
        errors, breaking, placeholders = checker.check(EXAMPLE.read_text(encoding="utf-8"), filled=True)
        self.assertEqual(errors, [])
        self.assertEqual((breaking, placeholders), (2, 0))

    def test_missing_rollback_and_vague_deadline_fail(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        text = "\n".join(l for l in text.splitlines() if not l.startswith("Rollback:"))
        text = text.replace("Deadline: 2026-09-30", "Deadline: end of September")
        errors = checker.check(text, filled=True)[0]
        self.assertIn("summary is missing 'Rollback:'", errors)
        self.assertTrue(any("end of September" in e for e in errors))

    def test_breaking_compatibility_needs_an_entry(self):
        text = EXAMPLE.read_text(encoding="utf-8").split("## Breaking changes")[0]
        errors = checker.check(text, filled=True)[0]
        self.assertIn("Compatibility says breaking, but 'Breaking changes' has no ### entry", errors)


if __name__ == "__main__":
    unittest.main()
