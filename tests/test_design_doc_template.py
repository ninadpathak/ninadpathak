"""The design doc template ships with a checker the article tells readers to run.

Pins the verdicts the article quotes (blank template passes structure and fails
--filled, the filled example passes) and each failure mode the checker exists for,
including the two bugs the release-notes checker had: empty values passing, and
ordinary bracketed code being read as a placeholder.
"""

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "static/templates/design-doc-template.md"
EXAMPLE = ROOT / "static/examples/design-doc-persist-exports.md"

spec = importlib.util.spec_from_file_location("check_design_doc", ROOT / "static/templates/check_design_doc.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def example():
    return EXAMPLE.read_text(encoding="utf-8")


class DesignDocTemplateTests(unittest.TestCase):
    def test_blank_template_passes_structure_and_fails_filled(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(checker.check(text, filled=False)[0], [])
        errors = checker.check(text, filled=True)[0]
        self.assertEqual(len(errors), 1)
        self.assertIn("20 unfilled placeholder(s)", errors[0])

    def test_filled_example_passes(self):
        self.assertEqual(checker.check(example(), filled=True), ([], 2, 0))

    def test_missing_do_nothing_alternative_fails(self):
        errors = checker.check(example().replace("### Do nothing", "### Keep records in memory"), True)[0]
        self.assertIn("'Alternatives considered' has no '### Do nothing' entry", errors)

    def test_alternative_without_reason_fails(self):
        text = re.sub(r"^Rejected because: it adds.*$", "Rejected because:", example(), flags=re.M)
        self.assertIn("alternative 'SQLite database' has no 'Rejected because:' reason",
                      checker.check(text, True)[0])

    def test_accepted_doc_with_open_question_fails(self):
        text = example().replace("- None\n", "- Should the file rotate after 10,000 records?\n")
        self.assertIn("Status is Accepted but 'Open questions' is not None", checker.check(text, True)[0])

    def test_empty_section_and_header_value_fail(self):
        text = re.sub(r"## Non-goals\n\n(- .*\n)+", "## Non-goals\n\n", example())
        text = text.replace("Author: Service owner (example)", "Author:")
        errors = checker.check(text, True)[0]
        self.assertIn("section '## Non-goals' is empty (write None if it has nothing to say)", errors)
        self.assertIn("header 'Author:' is empty", errors)

    def test_unknown_status_and_bad_date_fail(self):
        text = example().replace("Status: Accepted", "Status: Approved").replace("Date: 2026-10-20", "Date: last week")
        errors = checker.check(text, True)[0]
        self.assertTrue(any("Status must start with" in e for e in errors))
        self.assertTrue(any("Date is not a calendar date" in e for e in errors))

    def test_bracketed_code_is_not_a_placeholder(self):
        text = example().replace("## Goals", "Reads `records[0]` at startup.\n\n## Goals")
        self.assertEqual(checker.check(text, True)[0], [])


if __name__ == "__main__":
    unittest.main()
