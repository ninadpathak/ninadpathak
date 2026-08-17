"""Guard the glossary's internal references.

The glossary sat at `status: retired` for months with 25 complete terms behind it, while
24 of its URLs stayed indexed in Google at positions 7 to 76 and returned 404s. Turning it
back on immediately failed the SEO audit on two `related_terms` entries pointing at terms
that do not exist — `process-reward-models` and `compound-ai-systems`.

That is a data defect the build can only catch after rendering, so it gets caught here
instead. A dangling related term is a hard-404 internal link on a page that is trying to
rank.
"""
import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
GLOSSARY = ROOT / "content" / "data" / "glossary.yaml"


class GlossaryIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(GLOSSARY.read_text(encoding="utf-8"))
        cls.terms = cls.data.get("terms", [])
        cls.slugs = {t["slug"] for t in cls.terms}

    def test_glossary_has_terms(self):
        self.assertTrue(self.terms, "glossary.yaml defines no terms")

    def test_every_slug_is_unique(self):
        slugs = [t["slug"] for t in self.terms]
        duplicates = {s for s in slugs if slugs.count(s) > 1}
        self.assertFalse(duplicates, f"duplicate glossary slugs: {sorted(duplicates)}")

    def test_related_terms_all_resolve(self):
        dangling = []
        for term in self.terms:
            for related in term.get("related_terms") or []:
                if related["slug"] not in self.slugs:
                    dangling.append(f"{term['slug']} -> {related['slug']}")
        self.assertFalse(
            dangling,
            "related_terms point at slugs with no term, which renders a hard-404 "
            f"internal link: {dangling}",
        )

    def test_every_term_has_a_real_definition(self):
        """A published term must not ship a placeholder.

        An earlier revision of this file carried TODO placeholders in every definition
        while the file was retired. Publishing that would have put placeholder prose on
        25 indexed URLs.
        """
        placeholders = []
        for term in self.terms:
            for field in ("opening_definition", "body_html"):
                value = str(term.get(field, "")).strip()
                if not value or "TODO" in value:
                    placeholders.append(f"{term['slug']}.{field}")
        self.assertFalse(placeholders, f"placeholder or empty definitions: {placeholders}")


if __name__ == "__main__":
    unittest.main()
