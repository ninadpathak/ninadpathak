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
