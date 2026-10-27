"""One person, described once, in the same words on every page.

Answer engines describe a person from what the pages say about them. Before this test
the homepage called him a "Technical Content Writer" Person, every article named an
Organization called "Ninad Pathak" with the favicon as its logo, and the tool pages
restated a third version inline. A different Ninad Pathak appears in marketing trade
press, so three inconsistent self-descriptions made the collision worse.

The rule now: base.html emits the Person node from config.toml [identity] on every
page, and every author or publisher points at it by @id.

llms.txt is checked here too. Its intro said the articles were grouped by topic while
every article sat under "Other Writing", because the grouping matched tags no post
carried. It now groups by each post's declared editorial category.
"""
import json
import pathlib
import re
import shutil
import subprocess
import textwrap
import unittest

try:
    import tomllib
except ImportError:  # Python < 3.11
    import tomli as tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
CONFIG = tomllib.loads((ROOT / "config.toml").read_text(encoding="utf-8"))
PERSON_ID = CONFIG["site"]["url"].rstrip("/") + "/#person"
NODE = shutil.which("node")


def schema_objects(path):
    objects = []
    for block in LD_JSON.findall(path.read_text(encoding="utf-8")):
        parsed = json.loads(block)
        objects.extend(parsed if isinstance(parsed, list) else [parsed])
    return objects


def walk(value):
    """Every dict nested anywhere inside a JSON-LD object."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def site_pages():
    """Built pages, not the standalone visual embeds and fixtures under /static/."""
    for path in sorted(OUTPUT.rglob("*.html")):
        relative = path.relative_to(OUTPUT)
        if relative.parts[0] == "static":
            continue
        if 'http-equiv="refresh"' in path.read_text(encoding="utf-8"):
            continue
        yield path


class IdentitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (OUTPUT / "sitemap.xml").is_file():
            raise unittest.SkipTest("run `python build.py` first — these read the built site")
        cls.pages = list(site_pages())

    def test_every_page_carries_exactly_one_person_node(self):
        for page in self.pages:
            nodes = [o for o in schema_objects(page)
                     if o.get("@type") == "Person" and "sameAs" in o]
            self.assertEqual(len(nodes), 1, f"{page.relative_to(OUTPUT)} has {len(nodes)} Person nodes")
            self.assertEqual(nodes[0]["@id"], PERSON_ID)

    def test_person_node_matches_the_identity_config(self):
        identity = CONFIG["identity"]
        node = next(o for o in schema_objects(OUTPUT / "index.html")
                    if o.get("@type") == "Person" and "sameAs" in o)
        self.assertEqual(node["name"], identity["name"])
        self.assertEqual(node["jobTitle"], identity["job_title"])
        self.assertEqual(node["description"], identity["description"])
        self.assertEqual(node["disambiguatingDescription"], identity["disambiguating_description"])
        self.assertEqual(node["sameAs"], identity["same_as"])

    def test_every_author_and_publisher_points_at_the_person(self):
        for page in self.pages:
            for obj in schema_objects(page):
                for node in walk(obj):
                    for field in ("author", "publisher"):
                        ref = node.get(field)
                        if isinstance(ref, dict):
                            self.assertEqual(ref.get("@id"), PERSON_ID,
                                             f"{page.relative_to(OUTPUT)} {field} is {ref}")

    def test_no_organization_impersonates_the_person(self):
        for page in self.pages:
            for obj in schema_objects(page):
                for node in walk(obj):
                    if node.get("@type") == "Organization":
                        self.assertNotEqual(node.get("name"), CONFIG["identity"]["name"],
                                            f"{page.relative_to(OUTPUT)} names an Organization after the person")

    def test_about_page_is_the_persons_profile(self):
        objects = schema_objects(OUTPUT / "about" / "index.html")
        profile = next(o for o in objects if o.get("@type") == "ProfilePage")
        self.assertEqual(profile["mainEntity"]["@id"], PERSON_ID)

    def test_article_image_is_the_share_card_when_one_exists(self):
        for page in (OUTPUT / "articles").glob("*/index.html"):
            html = page.read_text(encoding="utf-8")
            card = re.search(r'<meta property="og:image"\s+content="([^"]+)"', html)
            article = next((o for o in schema_objects(page) if o.get("@type") == "TechArticle"), None)
            if article and card:
                self.assertEqual(article["image"], card.group(1), f"{page.relative_to(OUTPUT)}")


class LlmsTxtGroupingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (OUTPUT / "llms.txt").is_file():
            raise unittest.SkipTest("run `python build.py` first — these read the built site")
        cls.text = (OUTPUT / "llms.txt").read_text(encoding="utf-8")

    def test_no_catch_all_section(self):
        self.assertNotIn("## Other Writing", self.text)
        self.assertNotIn("## More Articles", self.text)

    def test_each_configured_category_with_articles_has_a_section(self):
        # Keyed on what posts declare, not on built archives: "distribution" keeps an
        # empty archive route alive for old links and has no articles to list.
        declared = set()
        for post in (ROOT / "content" / "posts").glob("*.md"):
            text = post.read_text(encoding="utf-8")
            if re.search(r"^(status:\s*draft|draft:\s*true)\s*$", text, re.M):
                continue
            match = re.search(r"^category:\s*(\S+)", text, re.M)
            if match:
                declared.add(match.group(1).strip("\"'"))
        headings = set(re.findall(r"^## (.+)$", self.text, re.M))
        titles = {c["slug"]: c["title"] for c in CONFIG["content"]["categories"]}
        self.assertTrue(declared)
        for slug in declared:
            self.assertIn(titles[slug], headings, f"category {slug} has no llms.txt section")

    def test_every_built_article_is_listed_once(self):
        base = CONFIG["site"]["url"].rstrip("/")
        listed = re.findall(r"\]\(" + re.escape(base) + r"/articles/([^/)]+)/\)", self.text)
        built = {p.parent.name for p in (OUTPUT / "articles").glob("*/index.html")
                 if any(o.get("@type") == "TechArticle" for o in schema_objects(p))}
        self.assertEqual(sorted(set(listed)), sorted(built))
        self.assertEqual(len(listed), len(set(listed)), "an article is listed twice")

    @unittest.skipUnless(NODE, "node is required to run the shipped validator")
    def test_passes_this_sites_own_validator(self):
        harness = textwrap.dedent(
            """
            const core = require(process.argv[1]);
            let input = "";
            process.stdin.on("data", (chunk) => { input += chunk; });
            process.stdin.on("end", () => {
              process.stdout.write(JSON.stringify(core.validate(input)));
            });
            """
        )
        completed = subprocess.run(
            [NODE, "-e", harness, str(ROOT / "static" / "js" / "llms-validator-core.js")],
            input=self.text.encode("utf-8"), capture_output=True, check=True,
        )
        result = json.loads(completed.stdout.decode("utf-8"))
        self.assertEqual(result["findings"], [], result["findings"])


if __name__ == "__main__":
    unittest.main()
