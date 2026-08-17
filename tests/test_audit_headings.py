"""Guard the heading audit's detection, since a craft rule with no instrument decays.

CHARTER 2c-quater made nested headings binding: each h2 is one complete chain of thought,
h3s are the steps within it, never skip a level, never head a single short paragraph, never
leave an h2 with exactly one h3. Nothing could check it. First run found 119 issues across
80 of 90 published posts — 64 entirely flat — so the rule was 71% unmet the hour it landed.

These tests pin the detectors rather than the corpus numbers, which will move.
"""
import pathlib
import sys
import unittest
from importlib.util import module_from_spec, spec_from_file_location

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = spec_from_file_location("audit_headings", ROOT / "tools" / "audit_headings.py")
audit_headings = module_from_spec(spec)
sys.modules["audit_headings"] = audit_headings
spec.loader.exec_module(audit_headings)

WORDS = " ".join(["word"] * 80)


class HeadingParsingTests(unittest.TestCase):
    def test_headings_inside_code_fences_are_not_document_headings(self):
        """A `## ` in a shell or YAML sample is not structure."""
        content = f"## Real heading\n\n{WORDS}\n\n```yaml\n## not a heading\n```\n"
        items = audit_headings.headings_and_bodies(content)
        self.assertEqual([h["text"] for h in items], ["Real heading"])

    def test_h1_is_ignored_because_the_template_owns_it(self):
        items = audit_headings.headings_and_bodies(f"# Title\n\n{WORDS}\n")
        self.assertEqual(items, [])

    def test_prose_is_attributed_to_the_heading_above_it(self):
        items = audit_headings.headings_and_bodies(f"## One\n\n{WORDS}\n\n## Two\n\nshort\n")
        self.assertEqual(len(items), 2)
        self.assertGreater(len(" ".join(items[0]["body"]).split()), 40)


class RuleDetectionTests(unittest.TestCase):
    def audit_text(self, body):
        path = ROOT / "tests" / "_heading_fixture.md"
        path.write_text(f"---\nstatus: published\nslug: fixture\n---\n\n{body}", encoding="utf-8")
        try:
            return audit_headings.audit(path)
        finally:
            path.unlink(missing_ok=True)

    def kinds(self, body):
        return {kind for kind, _ in self.audit_text(body)["problems"]}

    def test_all_h2s_is_flat(self):
        body = "".join(f"## Chain {i}\n\n{WORDS}\n\n" for i in range(4))
        self.assertIn("flat", self.kinds(body))

    def test_a_nested_document_is_not_flat(self):
        body = (f"## Chain one\n\n{WORDS}\n\n### Step A\n\n{WORDS}\n\n### Step B\n\n{WORDS}\n\n"
                f"## Chain two\n\n{WORDS}\n\n### Step C\n\n{WORDS}\n\n### Step D\n\n{WORDS}\n\n")
        self.assertNotIn("flat", self.kinds(body))
        self.assertNotIn("solo-h3", self.kinds(body))

    def test_one_h3_under_an_h2_is_flagged(self):
        body = (f"## Chain one\n\n{WORDS}\n\n### Only step\n\n{WORDS}\n\n"
                f"## Chain two\n\n{WORDS}\n\n### A\n\n{WORDS}\n\n### B\n\n{WORDS}\n\n")
        self.assertIn("solo-h3", self.kinds(body))

    def test_two_h3s_under_an_h2_is_not_flagged(self):
        body = (f"## Chain one\n\n{WORDS}\n\n### A\n\n{WORDS}\n\n### B\n\n{WORDS}\n\n"
                f"## Chain two\n\n{WORDS}\n\n### C\n\n{WORDS}\n\n### D\n\n{WORDS}\n\n")
        self.assertNotIn("solo-h3", self.kinds(body))

    def test_skipping_a_level_is_flagged(self):
        body = f"## Chain\n\n{WORDS}\n\n#### Too deep\n\n{WORDS}\n\n"
        self.assertIn("skipped-level", self.kinds(body))

    def test_a_heading_over_a_short_paragraph_is_flagged(self):
        body = f"## Chain one\n\n{WORDS}\n\n## Chain two\n\nToo little prose here.\n\n"
        self.assertIn("thin-section", self.kinds(body))

    def test_a_draft_is_not_audited(self):
        path = ROOT / "tests" / "_heading_draft.md"
        path.write_text("---\nstatus: draft\nslug: d\n---\n\n## A\n\nshort\n", encoding="utf-8")
        try:
            self.assertIsNone(audit_headings.audit(path))
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
