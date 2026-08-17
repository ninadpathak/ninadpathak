"""The rule-of-three check must accept a trio that names its own members.

The check exists because an unearned trio is an AI-writing tell. Its error message has
always offered two ways to satisfy it — a nearby evidence receipt, or an explicit
factual trio — but only the receipt was implemented, so it fired on sentences that list
their own evidence. "three types of load: intrinsic, extraneous, and germane" was
reported as unevidenced while naming all three.

That produced errors no edit could clear, so CI went red on any commit touching an older
post and stayed red. A gate that cannot go green stops being read, which is worse than
no gate. These tests pin both halves: the trio that names itself passes, and rhetorical
"three" with nothing behind it still fails.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from rule_checker import _names_its_trio


class NamesItsTrioTests(unittest.TestCase):
    def assertTrio(self, text, expected, msg=""):
        # The scan starts just after the "three" token, mirroring the caller.
        self.assertEqual(bool(_names_its_trio("x" + text, 1)), expected, msg or text)

    def test_colon_introduced_trio_passes(self):
        self.assertTrio("three types of load: intrinsic, extraneous, and germane. Next.", True)

    def test_colon_introduced_trio_without_oxford_comma_passes(self):
        self.assertTrio("three stages: plan, review and ship.", True)

    def test_dash_introduced_trio_passes(self):
        self.assertTrio("three checks - syntax, targets and dates - run first.", True)

    def test_markdown_list_on_following_lines_passes(self):
        self.assertTrio("three things:\n\n- one\n- two\n- three", True)

    def test_numbered_list_on_following_lines_passes(self):
        self.assertTrio("three steps:\n\n1. one\n2. two\n3. three", True)

    def test_rhetorical_three_still_fails(self):
        self.assertTrio("three different ways on one page only adds noise for a reader.", False)

    def test_unnamed_count_still_fails(self):
        self.assertTrio("three patterns based on whether the old instructions still apply.", False)

    def test_count_with_no_members_still_fails(self):
        self.assertTrio("three specific sentences in the opening block.", False)

    def test_two_items_is_not_a_trio(self):
        self.assertTrio("three parts: a and b.", False)


if __name__ == "__main__":
    unittest.main()


class BareDigitShapeTests(unittest.TestCase):
    """A bare 3 has three shapes that are not rule-of-three, each found by CI failing.

    The gate blocked legitimate merge prose on "2-3x more tokens", "3KB per vector" and
    "session 3", none of which counts anything rhetorically. Version numbers such as
    Python 3.13 were already excluded; ranges, units and identifiers were not.
    """

    def check(self, text):
        import re
        import rule_checker
        source = pathlib.Path(rule_checker.__file__).read_text(encoding="utf-8")
        # The pattern is built inline in check_post, so assert through the public path.
        path = pathlib.Path(__file__).resolve().parent / "_three_fixture.md"
        path.write_text(f"---\nstatus: published\nslug: f\n---\n\n{text}\n", encoding="utf-8")
        try:
            return [i for i in rule_checker.check_post(path) if i[1] == "rule-of-three"]
        finally:
            path.unlink(missing_ok=True)

    def test_a_range_is_not_a_trio(self):
        self.assertEqual(self.check("You can fit 2-3x more tokens in the same budget."), [])

    def test_a_unit_is_not_a_trio(self):
        self.assertEqual(self.check("Compressed from 3KB per vector to 100 bytes."), [])
        self.assertEqual(self.check("Summarisation adds 3ms of latency per turn."), [])

    def test_an_identifier_is_not_a_trio(self):
        self.assertEqual(self.check('It stored "dark mode" in session 3 and "light" in session 7.'), [])

    def test_a_version_is_still_not_a_trio(self):
        self.assertEqual(self.check("Validated in a fresh Python 3.13 environment."), [])

    def test_rhetorical_three_is_still_caught(self):
        self.assertTrue(self.check("It repeats the same idea three different ways on one page."))


class PositionalEnumerationTests(unittest.TestCase):
    """A trio enumerated across sentences is still a named trio.

    "three layers. The bottom measures retrieval, the middle tests consistency, the top
    checks behaviour." Good prose does this, and requiring the evidence-receipt escape
    hatch for it would push writers toward the hatch instead of toward naming things.

    It needs three DISTINCT positional markers, so it cannot be satisfied by rewording —
    you have to actually name three things in order. The narrowness is the point: adding
    it removed 6 sitewide findings, not 60.
    """

    def check(self, text):
        import rule_checker
        path = pathlib.Path(__file__).resolve().parent / "_three_pos_fixture.md"
        path.write_text(f"---\nstatus: published\nslug: f\n---\n\n{text}\n", encoding="utf-8")
        try:
            return [i for i in rule_checker.check_post(path) if i[1] == "rule-of-three"]
        finally:
            path.unlink(missing_ok=True)

    def test_bottom_middle_top_enumeration_passes(self):
        self.assertEqual(self.check(
            "A useful evaluation has three layers. The bottom measures retrieval quality. "
            "The middle tests memory consistency. The top checks agent behaviour."), [])

    def test_first_second_third_enumeration_passes(self):
        self.assertEqual(self.check(
            "Open-source systems expose three consequential design choices. The first is who "
            "controls memory. The second is where it is stored. The third is who can read it."), [])

    def test_two_markers_is_not_enough(self):
        self.assertTrue(self.check(
            "It has three parts. The first is retrieval. The second is storage."))

    def test_rhetorical_three_with_no_enumeration_still_fires(self):
        self.assertTrue(self.check(
            "Repeating the same idea three different ways on one page only adds noise."))
