import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

from build import (
    SiteBuilder,
    estimate_reading_time,
    extract_faqs,
    format_date_iso,
    optimize_content_images,
    slugify,
    sort_key,
)


class BuildHelperTests(unittest.TestCase):
    def test_slugify_normalizes_punctuation_and_spacing(self):
        self.assertEqual(slugify("  LLM Context: A Practical Guide  "), "llm-context-a-practical-guide")

    def test_reading_time_has_one_minute_minimum(self):
        self.assertEqual(estimate_reading_time("short post"), 1)
        self.assertEqual(estimate_reading_time("word " * 400), 2)

    def test_format_date_iso_accepts_dates_and_datetimes(self):
        self.assertEqual(format_date_iso(date(2026, 7, 31)), "2026-07-31")
        self.assertEqual(format_date_iso(datetime(2026, 7, 31, 12, 30)), "2026-07-31")

    def test_sort_key_falls_back_for_invalid_dates(self):
        self.assertEqual(sort_key({"date": "2026-07-31", "slug": "alpha"}), (date(2026, 7, 31), "alpha"))
        self.assertEqual(sort_key({"date": "not-a-date", "slug": "zeta"}), (date.min, "zeta"))

    def test_sort_key_breaks_same_date_ties_by_slug(self):
        posts = [
            {"date": "2026-07-31", "slug": "zeta"},
            {"date": "2026-07-31", "slug": "alpha"},
        ]
        self.assertEqual([post["slug"] for post in sorted(posts, key=sort_key, reverse=True)], ["zeta", "alpha"])

    def test_extract_faqs_supports_heading_and_bold_questions(self):
        markdown = """## FAQ

### What is llms.txt?

It is a plain-text discovery file.

**Who is it for?**

People and AI systems reading a site.

## Next section

Ignored.
"""
        self.assertEqual(
            extract_faqs(markdown),
            [
                {"question": "What is llms.txt?", "answer": "It is a plain-text discovery file."},
                {"question": "Who is it for?", "answer": "People and AI systems reading a site."},
            ],
        )

    def test_content_images_get_lazy_loading_and_intrinsic_dimensions(self):
        rendered = optimize_content_images(
            '<p><img src="/static/favicon.png?v=1" alt="Ninad Pathak"></p>'
        )

        self.assertIn('loading="lazy"', rendered)
        self.assertIn('decoding="async"', rendered)
        self.assertIn('width="512"', rendered)
        self.assertIn('height="512"', rendered)

    def test_content_image_optimization_preserves_explicit_loading(self):
        rendered = optimize_content_images(
            '<img src="/static/favicon.png" alt="Ninad Pathak" loading="eager">'
        )

        self.assertEqual(rendered.count("loading="), 1)


class CategoryArchiveTests(unittest.TestCase):
    def test_category_loader_assigns_each_post_once_and_uses_explicit_category(self):
        builder = SiteBuilder.__new__(SiteBuilder)
        builder.config = {
            "content": {
                "categories": [
                    {
                        "slug": "ai-memory",
                        "title": "AI Memory",
                        "description": "Memory systems for AI agents.",
                        "tag_matches": ["memory", "agent-memory"],
                    },
                    {
                        "slug": "technical-documentation",
                        "title": "Technical Documentation",
                        "description": "Developer documentation.",
                        "tag_matches": ["documentation"],
                    },
                ]
            }
        }
        posts = [
            {"slug": "agent-memory", "tags": ["agent-memory", "documentation"]},
            {"slug": "docs", "tags": ["documentation"]},
            {"slug": "explicit", "category": "technical-documentation", "tags": ["memory"]},
        ]

        categories = builder.load_categories(posts)

        self.assertEqual([category["slug"] for category in categories], ["ai-memory", "technical-documentation"])
        self.assertEqual([post["slug"] for post in categories[0]["posts"]], ["agent-memory"])
        self.assertEqual([post["slug"] for post in categories[1]["posts"]], ["docs", "explicit"])
        self.assertEqual(posts[0]["category"]["url"], "/articles/ai-memory/")
        self.assertEqual(posts[2]["category"]["slug"], "technical-documentation")

    def _sitemap_urls_for(self, categories):
        builder = SiteBuilder.__new__(SiteBuilder)
        builder.config = {"site": {"url": "https://example.com"}}
        with tempfile.TemporaryDirectory() as directory:
            builder.output = Path(directory)
            builder.build_sitemap([], [], [], categories=categories)
            root = ET.parse(builder.output / "sitemap.xml").getroot()
            namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            return {node.find("s:loc", namespace).text for node in root.findall("s:url", namespace)}

    def test_sitemap_includes_category_archives(self):
        # A category is only rendered, and so only listed, once it has a post.
        # The fixture carries one for that reason.
        categories = [{
            "slug": "ai-memory",
            "url": "/articles/ai-memory/",
            "posts": [{"date": date(2026, 7, 31)}],
        }]
        self.assertIn("https://example.com/articles/ai-memory/", self._sitemap_urls_for(categories))

    def test_sitemap_omits_a_category_with_no_posts(self):
        """An empty category renders no page, so listing it would be a soft 404."""
        categories = [{"slug": "ai-search-optimization", "url": "/articles/ai-search-optimization/", "posts": []}]
        self.assertNotIn(
            "https://example.com/articles/ai-search-optimization/",
            self._sitemap_urls_for(categories),
        )


class SitemapTests(unittest.TestCase):
    def test_static_tool_page_does_not_get_build_date_as_lastmod(self):
        builder = SiteBuilder.__new__(SiteBuilder)
        builder.config = {"site": {"url": "https://example.com"}}

        with tempfile.TemporaryDirectory() as directory:
            builder.output = Path(directory)
            builder.build_sitemap([], [], [])
            root = ET.parse(builder.output / "sitemap.xml").getroot()
            namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            entries = {
                node.find("s:loc", namespace).text: node.find("s:lastmod", namespace)
                for node in root.findall("s:url", namespace)
            }

        self.assertIn("https://example.com/llms-txt-generator/", entries)
        self.assertIsNone(entries["https://example.com/llms-txt-generator/"])

    def test_both_llms_txt_tools_are_in_the_sitemap(self):
        """Neither tool may fall out of the sitemap: each is a separate search intent."""
        builder = SiteBuilder.__new__(SiteBuilder)
        builder.config = {"site": {"url": "https://example.com"}}

        with tempfile.TemporaryDirectory() as directory:
            builder.output = Path(directory)
            builder.build_sitemap([], [], [])
            root = ET.parse(builder.output / "sitemap.xml").getroot()
            namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locations = {node.find("s:loc", namespace).text for node in root.findall("s:url", namespace)}

        self.assertIn("https://example.com/llms-txt-generator/", locations)
        self.assertIn("https://example.com/llms-txt-validator/", locations)
        self.assertIn("https://example.com/ai-overviews-checker/", locations)
        self.assertIn("https://example.com/ai-crawler-checker/", locations)
        self.assertIn("https://example.com/linter/", locations)


class ToolDiscoverabilityTests(unittest.TestCase):
    """Guards the discoverability work: the tools were effectively unlinked and
    /llms-txt-generator/ had earned three lifetime impressions."""

    repo_root = Path(__file__).resolve().parent.parent

    def test_site_llms_txt_lists_every_tool(self):
        source = (self.repo_root / "build.py").read_text(encoding="utf-8")
        self.assertIn("## Tools", source)
        for path in ("/llms-txt-generator/", "/llms-txt-validator/", "/linter/"):
            self.assertIn(f"{{base}}{path}", source, f"{path} missing from llms.txt output")

    def test_footer_links_both_llms_txt_tools(self):
        base_html = (self.repo_root / "templates" / "base.html").read_text(encoding="utf-8")
        self.assertIn('href="/llms-txt-generator/"', base_html)
        self.assertIn('href="/llms-txt-validator/"', base_html)

    def test_projects_yaml_lists_both_llms_txt_tools(self):
        projects = (self.repo_root / "content" / "projects.yaml").read_text(encoding="utf-8")
        self.assertIn('url: "/llms-txt-generator/"', projects)
        self.assertIn('url: "/llms-txt-validator/"', projects)

    def test_generator_no_longer_claims_it_sends_nothing_to_a_server(self):
        """It POSTs the domain and discovered URLs to /api/discover-site, so the
        old 'without sending site data to a server' claim was falsifiable."""
        projects = (self.repo_root / "content" / "projects.yaml").read_text(encoding="utf-8")
        self.assertNotIn("without sending site data to a server", projects)

    def test_both_tools_declare_software_application_schema(self):
        for template in ("llms_txt_generator.html", "llms_txt_validator.html"):
            markup = (self.repo_root / "templates" / template).read_text(encoding="utf-8")
            self.assertIn("SoftwareApplication", markup, template)
            self.assertIn("isAccessibleForFree", markup, template)

    def test_tools_cross_reference_each_other_in_schema(self):
        generator = (self.repo_root / "templates" / "llms_txt_generator.html").read_text(encoding="utf-8")
        validator = (self.repo_root / "templates" / "llms_txt_validator.html").read_text(encoding="utf-8")
        self.assertIn("/llms-txt-validator/", generator)
        self.assertIn("/llms-txt-generator/", validator)

    def test_validator_reuses_linter_css_and_adds_none(self):
        markup = (self.repo_root / "templates" / "llms_txt_validator.html").read_text(encoding="utf-8")
        self.assertIn("/static/css/linter.css", markup)
        self.assertNotIn("<style", markup)
        self.assertNotIn("style=", markup)

    def test_ai_overviews_checker_is_wired_everywhere(self):
        """Primary tool target: "ai overviews checker", 700/mo, KD 0, no AI
        Overview on its SERP as of the 2026-08-17 recompute."""
        build = (self.repo_root / "build.py").read_text(encoding="utf-8")
        self.assertIn("build_ai_overviews_checker", build)
        self.assertIn('("/ai-overviews-checker/", "0.9", "monthly", None)', build)
        self.assertIn("{base}/ai-overviews-checker/", build)

        base_html = (self.repo_root / "templates" / "base.html").read_text(encoding="utf-8")
        self.assertIn('href="/ai-overviews-checker/"', base_html)

        projects = (self.repo_root / "content" / "projects.yaml").read_text(encoding="utf-8")
        self.assertIn('url: "/ai-overviews-checker/"', projects)

    def test_checker_declares_software_application_schema(self):
        markup = (self.repo_root / "templates" / "ai_overviews_checker.html").read_text(encoding="utf-8")
        self.assertIn("SoftwareApplication", markup)
        self.assertIn("isAccessibleForFree", markup)

    def test_checker_reuses_linter_css_and_adds_none(self):
        markup = (self.repo_root / "templates" / "ai_overviews_checker.html").read_text(encoding="utf-8")
        self.assertIn("/static/css/linter.css", markup)
        self.assertNotIn("<style", markup)
        self.assertNotIn("style=", markup)

    def test_checker_never_promises_ai_overview_placement(self):
        """Google states there are no special optimisations for AI Overviews, so
        the page must not imply placement can be engineered."""
        markup = (self.repo_root / "templates" / "ai_overviews_checker.html").read_text(encoding="utf-8").lower()
        for forbidden in ("guarantee", "get into ai overviews", "rank in ai overviews", "boost your ai overview"):
            self.assertNotIn(forbidden, markup, forbidden)

    def test_checker_paste_path_never_transmits_input(self):
        script = (self.repo_root / "static" / "js" / "aio-checker.js").read_text(encoding="utf-8")
        network_calls = [line for line in script.splitlines() if "fetch(" in line]
        self.assertEqual(len(network_calls), 1, network_calls)
        self.assertIn("/api/fetch-page", network_calls[0])
        for forbidden in ("sendBeacon", "localStorage", "sessionStorage", "new WebSocket"):
            self.assertNotIn(forbidden, script)

    def test_ai_crawler_checker_is_wired_everywhere(self):
        build = (self.repo_root / "build.py").read_text(encoding="utf-8")
        self.assertIn("build_ai_crawler_checker", build)
        self.assertIn('("/ai-crawler-checker/", "0.9", "monthly", None)', build)
        self.assertIn("{base}/ai-crawler-checker/", build)

        base_html = (self.repo_root / "templates" / "base.html").read_text(encoding="utf-8")
        self.assertIn('href="/ai-crawler-checker/"', base_html)

        projects = (self.repo_root / "content" / "projects.yaml").read_text(encoding="utf-8")
        self.assertIn('url: "/ai-crawler-checker/"', projects)

    def test_crawler_checker_declares_software_application_schema(self):
        markup = (self.repo_root / "templates" / "ai_crawler_checker.html").read_text(encoding="utf-8")
        self.assertIn("SoftwareApplication", markup)
        self.assertIn("isAccessibleForFree", markup)

    def test_crawler_checker_declares_its_cluster(self):
        markup = (self.repo_root / "templates" / "ai_crawler_checker.html").read_text(encoding="utf-8")
        self.assertIn("ai-search-optimization", markup)

    def test_crawler_checker_states_the_edge_blocking_limit(self):
        """It must never imply robots.txt is enforcement."""
        markup = (self.repo_root / "templates" / "ai_crawler_checker.html").read_text(encoding="utf-8")
        self.assertIn("WAF", markup)

    def test_crawler_checker_paste_path_never_transmits_input(self):
        script = (self.repo_root / "static" / "js" / "robots-access.js").read_text(encoding="utf-8")
        network_calls = [line for line in script.splitlines() if "fetch(" in line]
        self.assertEqual(len(network_calls), 1, network_calls)
        self.assertIn("/api/fetch-robots", network_calls[0])
        for forbidden in ("sendBeacon", "localStorage", "sessionStorage", "new WebSocket"):
            self.assertNotIn(forbidden, script)

    def test_no_template_hardcodes_the_label_slash_prefix(self):
        """.label::before already emits "//", so a hardcoded one renders "// //".
        Fixed on main across 21 templates; this stops it coming back."""
        for template in sorted((self.repo_root / "templates").glob("*.html")):
            markup = template.read_text(encoding="utf-8")
            self.assertNotIn('class="label">//', markup, template.name)

    def test_no_tool_page_adds_inline_css(self):
        """Standing order 4: no new CSS, ever."""
        for template in ("linter.html", "llms_txt_generator.html", "llms_txt_validator.html",
                         "ai_overviews_checker.html"):
            markup = (self.repo_root / "templates" / template).read_text(encoding="utf-8")
            self.assertNotIn("<style", markup, template)

    def test_paste_path_never_transmits_input(self):
        """Privacy contract: only the domain lookup may touch the network."""
        script = (self.repo_root / "static" / "js" / "llms-validator.js").read_text(encoding="utf-8")
        network_calls = [line for line in script.splitlines() if "fetch(" in line]
        self.assertEqual(len(network_calls), 1, network_calls)
        self.assertIn("/api/fetch-llms-txt", network_calls[0])
        for forbidden in ("sendBeacon", "localStorage", "sessionStorage", "new WebSocket"):
            self.assertNotIn(forbidden, script)


class DesignSystemTests(unittest.TestCase):
    css_files = (
        Path("static/css/main.css"),
        Path("static/css/linter.css"),
        Path("static/css/visuals.css"),
        Path("static/css/flowcharts.css"),
    )

    def test_handwritten_css_uses_color_tokens(self):
        raw_color = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(")

        for css_file in self.css_files:
            for line_number, line in enumerate(css_file.read_text().splitlines(), 1):
                if line.lstrip().startswith("--"):
                    continue
                with self.subTest(file=css_file, line=line_number):
                    self.assertIsNone(raw_color.search(line))

    def test_fixed_type_sizes_use_tokens(self):
        fixed_size = re.compile(r"\d+(?:\.\d+)?(?:rem|em|px)\b")

        for css_file in self.css_files:
            for line_number, line in enumerate(css_file.read_text().splitlines(), 1):
                if line.lstrip().startswith("--font"):
                    continue
                declarations = re.findall(r"\b(?:font-size|font):\s*([^;]+)", line)
                for declaration in declarations:
                    if "clamp(" in declaration:
                        continue
                    with self.subTest(file=css_file, line=line_number):
                        self.assertIsNone(fixed_size.search(declaration))

    def test_article_visual_styles_stay_out_of_global_css(self):
        global_css = Path("static/css/main.css").read_text()
        self.assertNotIn(".visual-wrapper", global_css)
        self.assertNotIn(".flowchart {", global_css)

    def test_latest_article_uses_responsive_svg_flowchart_instead_of_raster(self):
        article = Path("content/posts/internal-vs-external-documentation.md").read_text()
        self.assertIn('class="flowchart-image"', article)
        self.assertIn("documentation-placement-flowchart-mobile.svg", article)
        self.assertIn("documentation-placement-flowchart.svg", article)
        self.assertNotIn(".png", article)
        self.assertNotIn("documentation-placement-decision-tree", article)

    def test_flowchart_svgs_include_dark_theme_and_accessible_titles(self):
        directory = Path("static/images/articles/internal-vs-external-documentation")
        for filename in (
            "documentation-placement-flowchart.svg",
            "documentation-placement-flowchart-mobile.svg",
        ):
            svg = (directory / filename).read_text()
            with self.subTest(file=filename):
                self.assertIn("prefers-color-scheme:dark", svg)
                self.assertIn("<title", svg)
                self.assertIn("<desc", svg)
                self.assertIn("role=\"img\"", svg)


if __name__ == "__main__":
    unittest.main()
