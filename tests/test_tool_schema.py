"""Every tool page must declare itself as software, with valid JSON-LD.

Tools are this campaign's priority lever: all 15 highest-value keywords in the niche
carry a Google AI Overview and none of the nine build-a-tool keywords do, so tool intent
is the only traffic profile an AI Overview does not tax. Structured data is how a tool
page tells a search engine it is a tool rather than an article.

/linter/ shipped without any of it. It was the oldest tool on the site and inherited the
base Person schema while the four newer tools all declared SoftwareApplication, so it was
describing itself as a person. Nobody noticed for months because nothing checked.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

TOOLS = (
    "linter",
    "llms-txt-generator",
    "llms-txt-validator",
    "ai-overviews-checker",
    "ai-crawler-checker",
)


def schema_objects(path):
    objects = []
    for block in LD_JSON.findall(path.read_text(encoding="utf-8")):
        parsed = json.loads(block)  # a JSON error here is the failure, not an exception to catch
        objects.extend(parsed if isinstance(parsed, list) else [parsed])
    return objects


class ToolSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (OUTPUT / "sitemap.xml").is_file():
            raise unittest.SkipTest("run `python build.py` first — these read the built site")

    def test_every_tool_page_is_built(self):
        for tool in TOOLS:
            self.assertTrue((OUTPUT / tool / "index.html").is_file(), f"/{tool}/ is not built")

    def test_every_tool_declares_software_application(self):
        for tool in TOOLS:
            objects = schema_objects(OUTPUT / tool / "index.html")
            types = []
            for obj in objects:
                declared = obj.get("@type")
                types.extend(declared if isinstance(declared, list) else [declared])
            self.assertIn("SoftwareApplication", types,
                          f"/{tool}/ declares {types} — a tool must say it is software")

    def test_tool_schema_names_a_url_and_is_free(self):
        for tool in TOOLS:
            app = next(o for o in schema_objects(OUTPUT / tool / "index.html")
                       if "SoftwareApplication" in (o.get("@type") or []))
            self.assertTrue(app.get("name"), f"/{tool}/ schema has no name")
            self.assertIn(tool, app.get("url", ""), f"/{tool}/ schema url is wrong")
            # Every tool on this site is free and requires no signup. If that ever stops
            # being true the schema must change with it, not silently keep claiming it.
            self.assertIs(app.get("isAccessibleForFree"), True, f"/{tool}/ must declare free access")

    def test_tool_pages_have_a_title_and_description(self):
        for tool in TOOLS:
            html = (OUTPUT / tool / "index.html").read_text(encoding="utf-8")
            title = re.search(r"<title>(.*?)</title>", html, re.S)
            desc = re.search(r'name="description" content="(.*?)"', html, re.S)
            self.assertTrue(title and title.group(1).strip(), f"/{tool}/ has no title")
            self.assertTrue(desc and desc.group(1).strip(), f"/{tool}/ has no meta description")
            # Long enough to say something, short enough that Google shows it whole.
            self.assertLessEqual(len(desc.group(1).strip()), 165, f"/{tool}/ description is too long")


if __name__ == "__main__":
    unittest.main()
