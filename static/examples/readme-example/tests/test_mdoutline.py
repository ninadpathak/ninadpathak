import unittest
from pathlib import Path

import mdoutline

GUIDE = Path(__file__).resolve().parent.parent / "examples" / "guide.md"


class OutlineTest(unittest.TestCase):
    def test_finds_every_heading_with_its_line_number(self):
        found = mdoutline.outline(GUIDE.read_text(encoding="utf-8"))
        self.assertEqual(found[0], (1, 1, "Export service guide"))
        self.assertEqual(len(found), 6)

    def test_skips_a_shell_comment_inside_a_code_block(self):
        text = "# Title\n\n```bash\n# not a heading\n```\n\n## Real\n"
        self.assertEqual(mdoutline.outline(text), [(1, 1, "Title"), (7, 2, "Real")])

    def test_max_level_drops_deeper_headings(self):
        found = mdoutline.outline(GUIDE.read_text(encoding="utf-8"), max_level=2)
        self.assertEqual([level for _, level, _ in found], [1, 2, 2, 2])

    def test_missing_file_exits_1(self):
        self.assertEqual(mdoutline.main(["no-such-file.md"]), 1)


if __name__ == "__main__":
    unittest.main()
