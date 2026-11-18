"""The Mem0 and TinyFish lines say the same thing wherever a buyer or an agent reads them.

The about page says he wrote 11 guides at Mem0 and ran its team of 13 writers. The
homepage and the proof line in config.toml (which feeds llms.txt and llms-full.txt) used to
say only that he managed the team. TinyFish is in the client list, and the AI-companies
page shows published samples for each company it names, so it shows TinyFish ones too.
"""
import re
import tomllib
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
AI_PAGE = REPO / "content" / "services" / "freelance-technical-writer-for-ai-companies.md"


class Mem0CopyTests(unittest.TestCase):
    def test_about_homepage_and_config_agree(self):
        about = (REPO / "content" / "about.md").read_text(encoding="utf-8")
        home = (REPO / "templates" / "index.html").read_text(encoding="utf-8")
        proof = tomllib.loads((REPO / "config.toml").read_text(encoding="utf-8"))["hire"]["proof"]
        mem0 = next(line for line in proof if "Mem0" in line)
        self.assertIn("At Mem0 I wrote 11 guides", about)
        for name, text in (("homepage", home), ("config proof", mem0)):
            with self.subTest(source=name):
                self.assertIn("At Mem0 I wrote 11 guides and", text)
                self.assertRegex(text, r"ran its team of 13 writers")
                self.assertNotIn("managed a team of 13 writers", text)


class TinyFishSampleTests(unittest.TestCase):
    def test_the_ai_companies_page_links_two_bylined_tinyfish_pieces(self):
        page = AI_PAGE.read_text(encoding="utf-8")
        line = next(line for line in page.splitlines() if line.startswith("- **TinyFish"))
        links = re.findall(r"\]\((https://www\.tinyfish\.ai/[^)]+)\)", line)
        self.assertEqual(len(links), 2)
        portfolio = yaml.safe_load((REPO / "content" / "portfolio.yaml").read_text(encoding="utf-8"))
        entries = portfolio if isinstance(portfolio, list) else next(v for v in portfolio.values() if isinstance(v, list))
        published = {entry["url"] for entry in entries if entry.get("client") == "TinyFish"}
        self.assertEqual(len(published), 8)
        for link in links:
            with self.subTest(link=link):
                self.assertIn(link, published)

    def test_the_page_keeps_the_voice_rules(self):
        page = AI_PAGE.read_text(encoding="utf-8").lower()
        for banned in ("hire me", "i sell"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, page)


if __name__ == "__main__":
    unittest.main()
