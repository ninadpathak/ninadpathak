"""The top bar holds four doors: Services, Work, Articles, About.

Portfolio and Projects left the bar and are reached through Work, so these tests hold
the three things that keep them findable: Work reads as the current section on both
pages, the mobile menu and footer still list them, and /work/ links to both.
"""
import re
import unittest
from pathlib import Path

from build import SiteBuilder

REPO = Path(__file__).resolve().parent.parent
TOP_BAR = ["/services/", "/work/", "/articles/", "/about/"]


def render_chrome(page: str, path: str) -> str:
    builder = SiteBuilder()
    template = builder.env.from_string(
        '{% extends "base.html" %}{% block canonical %}' + path + "{% endblock %}"
    )
    return template.render(
        site=builder.config["site"],
        contact=builder.config["contact"],
        current_page=page,
        person_schema={},
        latest_posts=[],
        build_year=2026,
    )


def region(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.S)
    assert match, f"region not found: {pattern}"
    return match.group(0)


def top_bar(html: str) -> str:
    return region(html, r'<ul class="nav-links".*?</ul>')


def mobile_menu(html: str) -> str:
    return region(html, r'<nav class="mobile-nav-links".*?</nav>')


def links(fragment: str) -> list[tuple[str, str]]:
    """(href, rest of the opening tag) for every anchor in the fragment."""
    return re.findall(r'<a href="([^"]+)"([^>]*)>', fragment)


class TopBarTests(unittest.TestCase):
    def test_top_bar_holds_exactly_the_four_doors_in_order(self):
        bar = top_bar(render_chrome("home", "/"))
        self.assertEqual([href for href, _ in links(bar)], TOP_BAR)

    def test_home_and_contact_mark_no_link_current(self):
        for page, path in (("home", "/"), ("contact", "/contact/"), ("tools", "/tools/"), ("404", "/404.html")):
            with self.subTest(page=page):
                bar = top_bar(render_chrome(page, path))
                self.assertNotIn("active", bar)
                self.assertNotIn("aria-current", bar)

    def test_each_section_marks_its_own_door_and_no_other(self):
        cases = [
            ("services", "/services/", "/services/", "page"),
            ("services", "/services/api-documentation-writer/", "/services/", "true"),
            ("work", "/work/", "/work/", "page"),
            ("work", "/work/centus/", "/work/", "true"),
            ("portfolio", "/portfolio/", "/work/", "true"),
            ("projects", "/projects/", "/work/", "true"),
            ("articles", "/articles/", "/articles/", "page"),
            ("articles", "/articles/claude-md/", "/articles/", "true"),
            ("about", "/about/", "/about/", "page"),
        ]
        for page, path, door, current in cases:
            with self.subTest(path=path):
                marked = [
                    (href, attrs) for href, attrs in links(top_bar(render_chrome(page, path)))
                    if "active" in attrs or "aria-current" in attrs
                ]
                self.assertEqual(len(marked), 1, marked)
                href, attrs = marked[0]
                self.assertEqual(href, door)
                self.assertIn('class="nav-link active"', attrs)
                self.assertIn(f'aria-current="{current}"', attrs)


class MobileMenuTests(unittest.TestCase):
    def test_menu_lists_the_doors_with_portfolio_and_projects_under_work(self):
        menu = mobile_menu(render_chrome("home", "/"))
        self.assertEqual(
            [href for href, _ in links(menu)],
            ["/services/", "/work/", "/portfolio/", "/projects/", "/articles/", "/about/", "/contact/"],
        )
        sub = region(menu, r'<div class="mobile-nav-sub">.*?</div>')
        self.assertEqual([href for href, _ in links(sub)], ["/portfolio/", "/projects/"])
        self.assertLess(menu.index('href="/work/"'), menu.index("mobile-nav-sub"))

    def test_menu_marks_the_open_page_and_its_section(self):
        menu = mobile_menu(render_chrome("portfolio", "/portfolio/"))
        current = {href: attrs for href, attrs in links(menu) if "aria-current" in attrs}
        self.assertEqual(set(current), {"/work/", "/portfolio/"})
        self.assertIn('aria-current="true"', current["/work/"])
        self.assertIn('aria-current="page"', current["/portfolio/"])

        menu = mobile_menu(render_chrome("contact", "/contact/"))
        current = [href for href, attrs in links(menu) if "aria-current" in attrs]
        self.assertEqual(current, ["/contact/"])

    def test_menu_stays_closed_to_assistive_tech_until_opened(self):
        html = render_chrome("home", "/")
        self.assertIn('<div class="mobile-nav" id="mobileNav" aria-hidden="true" inert>', html)
        self.assertIn('aria-controls="mobileNav" aria-expanded="false"', html)


class ProofStaysReachableTests(unittest.TestCase):
    def test_footer_still_links_portfolio_projects_and_contact(self):
        footer = region(render_chrome("home", "/"), r"<footer\b.*?</footer>")
        for href in ("/portfolio/", "/projects/", "/contact/", "/work/"):
            self.assertIn(f'href="{href}" class="footer-link"', footer)

    def test_work_page_links_to_portfolio_and_projects_in_its_content(self):
        work = (REPO / "templates" / "work.html").read_text(encoding="utf-8")
        lead = region(work, r'<p class="lead">.*?</p>')
        for href in ("/portfolio/", "/projects/"):
            self.assertIn(f'<a href="{href}" class="work-card">', work)
            self.assertIn(f'<a href="{href}">', lead, f"the lead paragraph should link {href}")

    def test_the_stylesheet_styles_the_menu_row_under_work(self):
        css = (REPO / "static" / "css" / "main.css").read_text(encoding="utf-8")
        for selector in (".mobile-nav-sub {", ".mobile-nav-sublink {", ".mobile-nav-link:has(+ .mobile-nav-sub) {"):
            self.assertIn(selector, css, "without this rule Portfolio and Projects lose their place under Work")

    def test_service_pages_link_to_both(self):
        services = (REPO / "templates" / "services.html").read_text(encoding="utf-8")
        for href in ("/portfolio/", "/projects/"):
            self.assertIn(f'<a href="{href}" class="arrow-link arrow-link-block">', services)


if __name__ == "__main__":
    unittest.main()
