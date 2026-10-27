"""The runbook template ships with a checker the article tells readers to run.

The article quotes the checker's output, so these tests pin that output's verdicts:
the blank template passes structurally but fails --filled, the filled Postgres example
passes --filled, and removing an Undo line or an Escalate time limit fails.
"""

import importlib.util
import re
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "static/templates/runbook-template.md"
EXAMPLE = ROOT / "static/examples/runbook-postgres-connection-slots.md"

spec = importlib.util.spec_from_file_location("check_runbook", ROOT / "static/templates/check_runbook.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class RunbookTemplateTests(unittest.TestCase):
    def test_blank_template_passes_structure_and_fails_filled(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        errors, steps, placeholders = checker.check(text, filled=False)
        self.assertEqual(errors, [])
        self.assertEqual(steps, 4)
        errors = checker.check(text, filled=True)[0]
        self.assertEqual(len(errors), 1)
        self.assertIn("unfilled placeholder", errors[0])

    def test_filled_example_passes(self):
        errors, steps, placeholders = checker.check(EXAMPLE.read_text(encoding="utf-8"), filled=True)
        self.assertEqual(errors, [])
        self.assertEqual((steps, placeholders), (7, 0))

    def test_missing_undo_and_vague_escalation_fail(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        text = "\n".join(l for l in text.splitlines() if not l.startswith("Undo: `psql"))
        text = text.replace("Escalate after: 15 minutes without the healthy output in step 6.",
                            "Escalate after: if it keeps happening.")
        errors = checker.check(text, filled=True)[0]
        self.assertIn("step '5. Time out the next leaked transaction automatically' is missing 'Undo:'", errors)
        self.assertTrue(any("needs a time limit in minutes" in e for e in errors))

    def test_step_without_command_or_branch_fails(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        verify = text.index("### 6.")
        block = text[verify:text.index("### 7.")]
        stripped = re.sub(r"```bash\n.*?```\n", "", block, flags=re.S).replace("If not: Go back to step 2.\n", "")
        errors = checker.check(text.replace(block, stripped), filled=True)[0]
        self.assertIn("step '6. Confirm the application role can connect' has no command in a code block", errors)
        self.assertIn("step '6. Confirm the application role can connect' is missing 'If not:'", errors)

    def test_field_inside_a_code_block_does_not_count(self):
        text = EXAMPLE.read_text(encoding="utf-8").replace("Expect: One row containing `1`.\n", "")
        text = text.replace("psql -U app -d shop -c 'select 1'\n```\n\nIf not: Go back",
                            "psql -U app -d shop -c 'select 1'\nExpect: 1\n```\n\nIf not: Go back")
        errors = checker.check(text, filled=True)[0]
        self.assertIn("step '6. Confirm the application role can connect' is missing 'Expect:'", errors)

    def test_last_tested_age_is_checked_only_when_asked(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        self.assertEqual(checker.check(text, filled=True, max_age=90, today=date(2027, 1, 26))[0], [])
        errors = checker.check(text, filled=True, max_age=90, today=date(2027, 1, 27))[0]
        self.assertEqual(errors, ["'Last tested:' 2026-10-28 is more than 90 days old"])
        bad = text.replace("Last tested: 2026-10-28", "Last tested: last week")
        self.assertIn("'Last tested:' is not a calendar date (YYYY-MM-DD): 'last week'",
                      checker.check(bad, filled=True)[0])

    def test_missing_sections_fail(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        text = text.split("## Escalate")[0].replace("## Before you start", "## Access")
        errors = checker.check(text, filled=True)[0]
        self.assertIn("missing '## Before you start'", errors)
        self.assertIn("missing '## Escalate'", errors)


if __name__ == "__main__":
    unittest.main()
