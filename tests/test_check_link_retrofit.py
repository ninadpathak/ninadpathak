"""Contract tests for the inbound-link publication gate."""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_link_retrofit as gate  # noqa: E402


class LinkRetrofitGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.posts = pathlib.Path(self.tmp.name)
        (self.posts / "target.md").write_text("# Target\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_accepts_another_post_linking_to_the_target_article(self):
        (self.posts / "source.md").write_text(
            "Read [the target](/articles/target/).\n", encoding="utf-8"
        )
        self.assertEqual(gate.check_inbound_link("target", self.posts), [])

    def test_rejects_a_target_without_an_inbound_post_link(self):
        failures = gate.check_inbound_link("target", self.posts)
        self.assertEqual(len(failures), 1)
        self.assertIn("no inbound link", failures[0])

    def test_does_not_count_the_target_post_linking_to_itself(self):
        (self.posts / "target.md").write_text(
            "Read [this](/articles/target/).\n", encoding="utf-8"
        )
        failures = gate.check_inbound_link("target", self.posts)
        self.assertEqual(len(failures), 1)
        self.assertIn("no inbound link", failures[0])


if __name__ == "__main__":
    unittest.main()
