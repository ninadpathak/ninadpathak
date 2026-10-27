"""/work/ has to add trust, so its numbers have to add up and agree with each other.

On 2026-10-27 the page's lead told readers to treat the cards as "claims, not proof",
its meta description quoted "sessions" where the case studies said visits, the
LinuxForDevices title said 203,000 where its card said 203,400, and the multiplier
was written 64x in one place and 64× in another. These tests hold the arithmetic and
the wording together. Whether a client's analytics back a number is a sourcing
question the build cannot answer; `headline_source` in a case's frontmatter is where
that answer goes, and the case page prints it.
"""
import re
import unittest
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "content" / "work"


def number(text):
    """'7K' -> 7000, '203,400' -> 203400, '450K' -> 450000."""
    text = text.strip().replace(",", "")
    scale = 1000 if text[-1:].lower() == "k" else 1
    return float(text.rstrip("kK")) * scale


def cases():
    return {path.stem: frontmatter.load(path) for path in sorted(WORK.glob("*.md"))}


class CaseArithmeticTests(unittest.TestCase):
    def test_multipliers_match_their_endpoints(self):
        checked = 0
        for slug, case in cases().items():
            hero = str(case.get("hero_metric", ""))
            match = re.fullmatch(r"(\d+)×", hero)
            ends = re.search(r"\(([\d,.]+K?) → ([\d,.]+K?)\)", case.get("hero_metric_label", ""))
            if not (match and ends):
                continue
            ratio = number(ends.group(2)) / number(ends.group(1))
            self.assertEqual(round(ratio), int(match.group(1)), f"{slug}: {hero} vs {ends.group(0)}")
            checked += 1
        self.assertGreaterEqual(checked, 2)

    def test_numbers_in_a_title_appear_in_its_case_study(self):
        for slug, case in cases().items():
            for figure in re.findall(r"\d{1,3}(?:,\d{3})+", case["title"]):
                self.assertIn(figure, case.content + case.get("summary", ""),
                              f"{slug}: title says {figure}, the case study never does")

    def test_one_multiplication_sign(self):
        for slug, case in cases().items():
            text = case["title"] + case.content + str(case.get("hero_metric", ""))
            self.assertNotRegex(text, r"\b\d+x\b", f"{slug}: write × for a multiplier")


class WorkPageCopyTests(unittest.TestCase):
    template = (ROOT / "templates" / "work.html").read_text(encoding="utf-8")

    def test_the_lead_does_not_disown_the_cards(self):
        for phrase in ("claims, not proof", "rented attention", "still need checking"):
            self.assertNotIn(phrase, self.template)

    def test_meta_description_quotes_no_unsourced_number(self):
        description = re.search(r"{% block description %}(.*?){% endblock %}", self.template).group(1)
        # A figure, not a digit inside a name such as Mem0.
        self.assertNotRegex(description, r"(?<![A-Za-z])\d")
        self.assertLessEqual(len(description), 160)


class HeadlineSourceTests(unittest.TestCase):
    def test_case_page_prints_its_headline_source(self):
        import os
        cwd = os.getcwd()
        os.chdir(ROOT)
        try:
            from build import SiteBuilder
            builder = SiteBuilder()
            case = dict(builder.load_work()[0], headline_source="Search Console, March 2026",
                        headline_source_url="https://example.com/report")
            html = builder.env.get_template("work_single.html").render(
                case=case, site=builder.config["site"], contact=builder.config["contact"],
                latest_posts=[], build_year=2026)
        finally:
            os.chdir(cwd)
        self.assertIn(f"Source for {case['hero_metric']}:", html)
        self.assertIn('<a href="https://example.com/report" rel="noopener" target="_blank">Search Console, March 2026</a>', html)


if __name__ == "__main__":
    unittest.main()
