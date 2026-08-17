"""End-to-end tests for the five interactive tools.

WHAT THIS COVERS THAT THE UNIT TESTS DO NOT

The rule engines have 184 unit tests between them, and every one loads the engine through
`require()`. That takes the CommonJS branch of each engine's UMD wrapper. A browser takes
the other branch and assigns a global. Nothing tested that branch, nor that the wiring
script finds the global, nor that the element ids the wiring queries exist in the built
page, nor that the page loads both scripts in the right order.

So a tool could pass every unit test and be dead on the page. That is the gap.

These tests load the BUILT html, run the SHIPPED scripts against it in a sandbox where
`module` is absent, drive a real interaction, and assert on the graded output the render
function actually produced.

WHY NOT A HEADLESS BROWSER

Because it would not survive CI. Playwright and Selenium need a browser binary and a
driver, neither of which exists on Cloudflare's Python 3.9 build image, and pinning a
browser download into this repo to test five static pages is a worse trade than the gap it
closes. Node is already a dependency of the engine tests, so the shim in tools_harness.js
costs nothing new.

WHAT THIS DELIBERATELY DOES NOT CLAIM

The shim is not a browser. It does not lay out, style or paint. It does not run main.js. It
cannot catch anything that depends on real browser behaviour: contenteditable quirks,
clipboard permissions, focus, CSS, or a layout that renders the results panel off-screen.
Those still need a human with a browser, and one manual pass is what the tools have had.

What it does catch is the class of break that has actually happened in this repo: a renamed
id, a renamed global, a script that stopped loading, a changed engine output shape, a
wiring script referencing an element the template no longer has, and a Function that
disappeared from under a page that still renders.

The two named near-misses both have a test here:
  * a redirect shadowing a live page — the /glossary/ case, RedirectShadowingTests
  * a tool page rendering while its Function 404s — PagesFunctionContractTests

Live HTTP checks are gated behind NINADPATHAK_LIVE_TESTS=1 so the suite stays deterministic
and offline by default.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"
HARNESS = ROOT / "tests" / "tool_harness.js"
NODE = shutil.which("node")
LIVE = os.environ.get("NINADPATHAK_LIVE_TESTS") == "1"


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.classes = set()
        self.scripts = []
        self.stylesheets = []
        self.inline_style_tags = 0
        self.inline_style_attrs = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for cls in (a.get("class") or "").split():
            self.classes.add(cls)
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        if tag == "link" and "stylesheet" in (a.get("rel") or ""):
            self.stylesheets.append(a.get("href", ""))
        if tag == "style":
            self.inline_style_tags += 1
        if a.get("style"):
            self.inline_style_attrs += 1


class ToolPage:
    """A built tool page, plus the ability to drive its shipped client logic."""

    def __init__(self, path, wiring, engine=None, endpoint=None):
        self.path = path
        self.wiring = wiring          # static/js filename carrying the DOM wiring
        self.engine = engine          # static/js filename carrying the rule engine, if split
        self.endpoint = endpoint      # /api/... the page calls, if any
        self.html_file = OUTPUT / path.strip("/") / "index.html"
        self._parsed = None

    @property
    def parsed(self):
        if self._parsed is None:
            parser = _PageParser()
            parser.feed(self.html_file.read_text(encoding="utf-8"))
            self._parsed = parser
        return self._parsed

    @property
    def tool_scripts(self):
        """Scripts this tool needs, in page order. main.js is sitewide, not the tool."""
        return [s for s in self.parsed.scripts if "/js/" in s and not s.endswith("main.js")]

    def wiring_source(self):
        return (ROOT / "static" / "js" / self.wiring).read_text(encoding="utf-8")

    def queried_ids(self):
        return set(re.findall(r'getElementById\(["\']([^"\']+)["\']\)', self.wiring_source()))

    def drive(self, **spec):
        """Load the shipped scripts against the built page's DOM and run an interaction."""
        payload = {
            "ids": sorted(self.parsed.ids),
            "classes": sorted(self.parsed.classes),
            "scripts": [str(OUTPUT / s.lstrip("/")) for s in self.tool_scripts],
        }
        payload.update(spec)
        done = subprocess.run([NODE, str(HARNESS)], input=json.dumps(payload),
                             capture_output=True, text=True)
        if done.returncode != 0:
            raise AssertionError(f"harness exited {done.returncode}: {done.stderr[:2000]}")
        return json.loads(done.stdout)


TOOLS = [
    ToolPage("/linter/", "linter.js"),
    ToolPage("/llms-txt-generator/", "llms-generator.js", endpoint="/api/discover-site"),
    ToolPage("/llms-txt-validator/", "llms-validator.js", "llms-validator-core.js",
             "/api/fetch-llms-txt"),
    ToolPage("/ai-overviews-checker/", "aio-checker.js", "aio-checker-core.js",
             "/api/fetch-page"),
    ToolPage("/ai-crawler-checker/", "robots-access.js", "robots-access-core.js",
             "/api/fetch-robots"),
]
BY_PATH = {t.path: t for t in TOOLS}


class BuildPrerequisiteTests(unittest.TestCase):
    """These tests are meaningless without a build, so a missing build fails loudly.

    Skipping instead would leave a suite that passes whether or not the tools work, which
    is the exact failure mode this file exists to close.
    """

    def test_the_build_exists(self):
        self.assertTrue(OUTPUT.is_dir(),
                        "output/ is missing — run `python3 build.py` before the suite")

    def test_every_tool_page_was_built(self):
        for tool in TOOLS:
            self.assertTrue(tool.html_file.is_file(), f"{tool.path} was not built")

    def test_the_harness_is_present(self):
        self.assertTrue(HARNESS.is_file())


class StructuralContractTests(unittest.TestCase):
    """The seam between the template and the wiring script."""

    def test_every_queried_id_exists_in_the_built_page(self):
        """Rename an id in a template and the tool dies silently. This is that check."""
        for tool in TOOLS:
            missing = tool.queried_ids() - tool.parsed.ids
            self.assertEqual(missing, set(),
                             f"{tool.path} wiring queries ids the built page lacks: {sorted(missing)}")

    def test_each_tool_page_loads_its_wiring_script(self):
        for tool in TOOLS:
            self.assertIn(f"/static/js/{tool.wiring}", tool.tool_scripts, tool.path)

    def test_a_split_engine_loads_before_its_wiring(self):
        """The wiring reads a global the engine assigns, so order is load-bearing."""
        for tool in TOOLS:
            if not tool.engine:
                continue
            scripts = tool.tool_scripts
            self.assertIn(f"/static/js/{tool.engine}", scripts, tool.path)
            self.assertLess(scripts.index(f"/static/js/{tool.engine}"),
                            scripts.index(f"/static/js/{tool.wiring}"),
                            f"{tool.path} loads its wiring before its engine")

    def test_the_global_the_wiring_reads_is_the_one_the_engine_assigns(self):
        for tool in TOOLS:
            if not tool.engine:
                continue
            engine_src = (ROOT / "static" / "js" / tool.engine).read_text(encoding="utf-8")
            assigned = set(re.findall(r"root\.([A-Za-z]+)\s*=\s*factory\(\)", engine_src))
            read = set(re.findall(r"window\.([A-Za-z]+Core)\b", tool.wiring_source()))
            self.assertTrue(assigned, f"{tool.engine} assigns no global")
            self.assertTrue(read, f"{tool.wiring} reads no global")
            self.assertTrue(read <= assigned,
                            f"{tool.path} reads {read} but the engine assigns {assigned}")

    def test_no_tool_template_adds_inline_css(self):
        """Standing order 4: no new CSS, ever.

        Asserted against the tool templates, not the built pages: base.html carries one
        deliberate sitewide <style> block that sets the theme background before paint, and
        every page inherits it. Counting that would make this test unfailable.
        """
        for tool in TOOLS:
            template = ROOT / "templates" / (tool.path.strip("/").replace("-", "_") + ".html")
            candidates = [template,
                          ROOT / "templates" / "linter.html",
                          ROOT / "templates" / "llms_txt_generator.html",
                          ROOT / "templates" / "llms_txt_validator.html",
                          ROOT / "templates" / "ai_overviews_checker.html",
                          ROOT / "templates" / "ai_crawler_checker.html"]
            found = next((c for c in candidates if c.is_file() and tool.path in c.read_text(encoding="utf-8")), None)
            self.assertIsNotNone(found, f"no template found for {tool.path}")
            markup = found.read_text(encoding="utf-8")
            self.assertNotIn("<style", markup, f"{found.name} adds a <style> tag")
            self.assertNotIn("style=", markup, f"{found.name} adds a style= attribute")

    def test_the_only_inline_style_on_a_tool_page_is_the_sitewide_theme_block(self):
        """Pins the exception so a second one cannot slip in unnoticed."""
        for tool in TOOLS:
            self.assertLessEqual(tool.parsed.inline_style_tags, 1,
                                 f"{tool.path} has more than the one sitewide <style>")
            self.assertEqual(tool.parsed.inline_style_attrs, 0,
                             f"{tool.path} has a style= attribute")

    def test_pages_using_lint_classes_link_linter_css(self):
        for tool in TOOLS:
            uses_lint = any(c.startswith(("lint-", "linter-")) for c in tool.parsed.classes)
            if uses_lint:
                self.assertTrue(any("linter.css" in s for s in tool.parsed.stylesheets),
                                f"{tool.path} uses lint-* classes without linking linter.css")

    def test_every_tool_declares_software_application_schema(self):
        for tool in TOOLS:
            html = tool.html_file.read_text(encoding="utf-8")
            self.assertIn("SoftwareApplication", html, tool.path)


@unittest.skipIf(NODE is None, "node is required to run the shipped client logic")
class ClientLogicTests(unittest.TestCase):
    """Run each tool's real client logic against a known input; assert graded output."""

    def test_linter_grades_a_defective_article(self):
        planted = ("In today's fast-paced landscape, we will simply delve into leveraging "
                   "robust synergy. This is very obviously easy.")
        got = BY_PATH["/linter/"].drive(
            text={"linterInput": planted}, click="lintBtn",
            collect=["lintScore", "lintGrade", "lintScoreBar", "lintIssues",
                     "linterResults", "linterEmpty", "lintStats"])
        self.assertEqual(got["errors"], [])
        el = got["elements"]
        self.assertRegex(el["lintScoreBar"]["className"], r"lint-grade-[a-f]")
        self.assertIn(el["lintGrade"]["text"], list("ABCDF"))
        self.assertFalse(el["linterResults"]["hidden"])
        self.assertTrue(el["linterEmpty"]["hidden"])
        issues = el["lintIssues"]["html"].lower()
        for planted_word in ("delve", "simply", "leverag", "robust", "synergy", "obviously"):
            self.assertIn(planted_word, issues, f"linter missed {planted_word}")

    def test_linter_ignores_an_empty_input(self):
        got = BY_PATH["/linter/"].drive(text={"linterInput": "   "}, click="lintBtn",
                                        collect=["linterResults", "lintIssues"])
        self.assertEqual(got["errors"], [])
        self.assertEqual(got["elements"]["lintIssues"]["html"], "")

    def test_validator_grades_a_conforming_llms_txt(self):
        source = "# Title\n\n> A summary.\n\n## Docs\n\n- [A](https://example.com/a): note\n"
        got = BY_PATH["/llms-txt-validator/"].drive(
            text={"validatorInput": source}, click="validateBtn",
            collect=["validatorScore", "validatorGrade", "validatorScoreBar",
                     "validatorFindings", "validatorStats", "validatorResults"])
        self.assertEqual(got["errors"], [])
        el = got["elements"]
        self.assertEqual(el["validatorScore"]["text"], "100")
        self.assertEqual(el["validatorGrade"]["text"], "A")
        self.assertIn("lint-grade-a", el["validatorScoreBar"]["className"])
        self.assertFalse(el["validatorResults"]["hidden"])

    def test_validator_reports_a_missing_h1_as_a_spec_violation(self):
        got = BY_PATH["/llms-txt-validator/"].drive(
            text={"validatorInput": "> summary only\n"}, click="validateBtn",
            collect=["validatorGrade", "validatorFindings"])
        self.assertEqual(got["errors"], [])
        self.assertEqual(got["elements"]["validatorGrade"]["text"], "F")
        self.assertIn("missing-h1", got["elements"]["validatorFindings"]["html"])

    def test_checker_grades_a_page_and_cites_its_sources(self):
        page = ("# Keep one URL per version\n\nPublished 2026-08-14. Version URLs stay "
                "stable across releases.\n\n## Redirect retired versions to the nearest "
                "live page\n\nRetired versions redirect to the nearest live equivalent.\n\n"
                "## Where this does not apply\n\nThis does not apply to nightly builds, "
                "and I did not test monorepos.\n")
        got = BY_PATH["/ai-overviews-checker/"].drive(
            text={"aioInput": page}, click="aioRunBtn",
            collect=["aioScoreNumber", "aioBand", "aioBandDesc", "aioScoreBar",
                     "aioFindings", "aioStats"])
        self.assertEqual(got["errors"], [])
        el = got["elements"]
        self.assertRegex(el["aioScoreNumber"]["text"], r"^\d+/\d+$")
        self.assertRegex(el["aioScoreBar"]["className"], r"lint-grade-[a-f]")
        # Every check must show the dated source it rests on. That is the tool's whole claim.
        self.assertIn("Based on:", el["aioFindings"]["html"])
        self.assertRegex(el["aioFindings"]["html"], r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")

    def test_checker_flags_a_preamble_opening(self):
        got = BY_PATH["/ai-overviews-checker/"].drive(
            text={"aioInput": "# T\n\nIn today's fast-paced world, docs matter to teams.\n"},
            click="aioRunBtn", collect=["aioFindings"])
        self.assertEqual(got["errors"], [])
        # The render shows each check's human title, not its rule id.
        html = got["elements"]["aioFindings"]["html"]
        self.assertIn("A direct answer opens the page", html)
        self.assertIn("establishes a topic before answering it", html)

    def test_crawler_checker_separates_citation_from_training(self):
        robots = ("User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n\n"
                  "User-agent: ClaudeBot\nDisallow: /\n")
        got = BY_PATH["/ai-crawler-checker/"].drive(
            text={"robotsInput": robots}, values={"robotsPath": "/"}, click="robotsRunBtn",
            collect=["robotsScoreNumber", "robotsPosture", "robotsPostureDesc",
                     "robotsScoreBar", "robotsFindings", "robotsStats"])
        self.assertEqual(got["errors"], [])
        el = got["elements"]
        # Every citation crawler is allowed here, so the headline must be clean even though
        # two training crawlers are blocked. Reporting a training opt-out as damage would be
        # wrong, and this is the assertion that holds that line.
        self.assertEqual(el["robotsScoreNumber"]["text"], "7/7")
        self.assertIn("lint-grade-a", el["robotsScoreBar"]["className"])
        self.assertIn("cite-only", el["robotsPosture"]["text"])
        findings = el["robotsFindings"]["html"]
        self.assertIn("GPTBot", findings)
        self.assertIn("OAI-SearchBot", findings)
        self.assertIn("WAF", findings + el["robotsStats"]["html"] or "")

    def test_crawler_checker_alarms_when_a_citation_crawler_is_blocked(self):
        got = BY_PATH["/ai-crawler-checker/"].drive(
            text={"robotsInput": "User-agent: *\nDisallow: /\n"},
            values={"robotsPath": "/"}, click="robotsRunBtn",
            collect=["robotsScoreNumber", "robotsScoreBar", "robotsPosture"])
        self.assertEqual(got["errors"], [])
        el = got["elements"]
        self.assertEqual(el["robotsScoreNumber"]["text"], "0/7")
        self.assertIn("lint-grade-f", el["robotsScoreBar"]["className"])

    def test_generator_scan_populates_the_workspace(self):
        """The generator's flow is a form submit, not a button click."""
        discovery = {"status": 200, "body": {
            "site": {"name": "Example", "url": "https://example.com",
                     "description": "A site.", "language": "en"},
            "urls": ["https://example.com/"], "sitemapFound": True,
            "sitemapCount": 1, "truncated": False, "limit": 100}}
        metadata = {"status": 200, "body": {"pages": [
            {"title": "Home", "url": "https://example.com/", "description": "A site."}]}}
        got = BY_PATH["/llms-txt-generator/"].drive(
            values={"llmsSiteUrl": "example.com"}, submit="llmsScanForm",
            fetch=[discovery, metadata],
            collect=["llmsStatus", "llmsWorkspace", "llmsSiteName", "llmsCanonicalUrl",
                     "llmsSiteDescription", "llmsPages"])
        self.assertEqual(got["errors"], [])
        el = got["elements"]
        self.assertFalse(el["llmsWorkspace"]["hidden"], "workspace stayed hidden after a scan")
        self.assertEqual(el["llmsSiteName"]["value"], "Example")
        self.assertEqual(el["llmsCanonicalUrl"]["value"], "https://example.com")
        self.assertEqual([c["url"] for c in got["fetchCalls"]],
                         ["/api/discover-site", "/api/discover-site"])

    def test_every_tool_loads_without_throwing(self):
        """A load-time throw kills every handler on the page at once."""
        for tool in TOOLS:
            got = tool.drive(collect=[])
            self.assertEqual(got["errors"], [], f"{tool.path} threw while loading")

    def test_split_engines_assign_their_global_under_the_browser_branch(self):
        """The require()-based unit tests never exercise this branch of the UMD wrapper."""
        for tool in TOOLS:
            if not tool.engine:
                continue
            got = tool.drive(collect=[])
            self.assertTrue(got["globals"],
                            f"{tool.path} assigned no *Core global under the browser branch")


@unittest.skipIf(NODE is None, "node is required")
class PrivacyContractTests(unittest.TestCase):
    """Nothing the user pastes may leave the browser. Easy to regress, invisible when it does."""

    def test_running_a_pasted_input_makes_no_network_call(self):
        """Measured, not grepped: drive the paste path and count the fetches."""
        cases = [
            ("/linter/", {"text": {"linterInput": "Simply delve into it."}, "click": "lintBtn"}),
            ("/llms-txt-validator/", {"text": {"validatorInput": "# T\n"}, "click": "validateBtn"}),
            ("/ai-overviews-checker/", {"text": {"aioInput": "# T\n\nA claim here.\n"},
                                        "click": "aioRunBtn"}),
            ("/ai-crawler-checker/", {"text": {"robotsInput": "User-agent: *\nAllow: /\n"},
                                      "click": "robotsRunBtn"}),
        ]
        for path, spec in cases:
            got = BY_PATH[path].drive(collect=[], **spec)
            self.assertEqual(got["fetchCalls"], [],
                             f"{path} transmitted something while checking a pasted input")

    def test_the_linter_never_calls_the_network_at_all(self):
        source = BY_PATH["/linter/"].wiring_source()
        self.assertNotIn("fetch(", source)

    def test_each_networked_tool_holds_exactly_one_endpoint(self):
        for tool in TOOLS:
            source = tool.wiring_source()
            calls = re.findall(r'fetch\(\s*["\']([^"\']+)["\']', source)
            if tool.endpoint is None:
                self.assertEqual(calls, [], f"{tool.path} should make no fetch call")
            else:
                self.assertEqual(calls, [tool.endpoint],
                                 f"{tool.path} calls {calls}, expected only {tool.endpoint}")

    def test_no_tool_uses_a_storage_or_beacon_api(self):
        for tool in TOOLS:
            source = tool.wiring_source()
            for banned in ("sendBeacon", "localStorage", "sessionStorage", "new WebSocket",
                           "indexedDB"):
                self.assertNotIn(banned, source, f"{tool.path} uses {banned}")

    def test_no_tool_page_loads_a_third_party_script(self):
        """Analytics is sitewide in base.html; a tool must not add its own."""
        for tool in TOOLS:
            for src in tool.tool_scripts:
                self.assertTrue(src.startswith("/static/"), f"{tool.path} loads {src}")


class PagesFunctionContractTests(unittest.TestCase):
    """The named near-miss: a tool page that renders while its Function 404s.

    The page is static and will render whatever happens to the Function, so the only
    mechanical guard is that the endpoint the page calls exists in the deployed source and
    still carries its safety rails.
    """

    def test_every_endpoint_a_tool_calls_exists_as_a_function(self):
        for tool in TOOLS:
            if tool.endpoint is None:
                continue
            name = tool.endpoint.rsplit("/", 1)[-1]
            path = ROOT / "functions" / "api" / f"{name}.js"
            self.assertTrue(path.is_file(),
                            f"{tool.path} calls {tool.endpoint} but {path.name} does not exist")

    def test_no_function_is_orphaned_without_a_caller(self):
        """An unreferenced Function is either dead code or a page that lost its wiring."""
        called = {t.endpoint.rsplit("/", 1)[-1] for t in TOOLS if t.endpoint}
        on_disk = {p.stem for p in (ROOT / "functions" / "api").glob("*.js")}
        self.assertEqual(on_disk - called, set(), "functions with no caller")

    def test_every_function_exports_the_post_handler(self):
        for path in sorted((ROOT / "functions" / "api").glob("*.js")):
            source = path.read_text(encoding="utf-8")
            self.assertIn("export async function onRequestPost", source, path.name)

    def test_every_function_keeps_its_safety_rails(self):
        """SSRF guard, redirect handling, a timeout and a body ceiling, on every endpoint."""
        for path in sorted((ROOT / "functions" / "api").glob("*.js")):
            source = path.read_text(encoding="utf-8")
            self.assertIn("isPrivateIpv4", source, f"{path.name} lost its private-IP guard")
            self.assertIn("localhost", source, f"{path.name} lost its localhost guard")
            self.assertIn("FETCH_TIMEOUT_MS", source, f"{path.name} lost its fetch timeout")
            self.assertIn("MAX_BODY_BYTES", source, f"{path.name} lost its body ceiling")
            self.assertIn('redirect: "manual"', source,
                          f"{path.name} stopped handling redirects explicitly")

    def test_every_function_identifies_itself_by_user_agent(self):
        for path in sorted((ROOT / "functions" / "api").glob("*.js")):
            source = path.read_text(encoding="utf-8")
            self.assertIn("ninadpathak", source.lower(), f"{path.name} has no honest UA")


class RedirectShadowingTests(unittest.TestCase):
    """The other named near-miss: /glossary/ was redirected while dead, then republished.

    Cloudflare's _redirects takes precedence over a static file, so the stale rule would
    have sent every visitor and crawler away from the page that had just come back.
    daily_cycle.py checks this; nothing tested the check.
    """

    def setUp(self):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        import daily_cycle
        self.dc = daily_cycle

    def test_no_redirect_currently_shadows_a_built_page(self):
        self.assertEqual(self.dc.shadowing_redirects(), [])

    def test_the_check_detects_a_shadowing_rule(self):
        """Proves the check can fail, which is the only thing that makes a green run mean
        anything."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            (tmp / "static").mkdir()
            (tmp / "output" / "glossary").mkdir(parents=True)
            (tmp / "output" / "glossary" / "index.html").write_text("live page")
            (tmp / "static" / "_redirects").write_text("/glossary/ /articles/ 301\n")
            original = self.dc.ROOT
            try:
                self.dc.ROOT = tmp
                problems = self.dc.shadowing_redirects()
            finally:
                self.dc.ROOT = original
        self.assertTrue(problems)
        self.assertIn("/glossary/", problems[0])

    def test_glossary_is_built_and_therefore_must_not_be_redirected(self):
        """The specific page the near-miss was about."""
        if not (OUTPUT / "glossary" / "index.html").is_file():
            self.skipTest("/glossary/ is not currently built")
        redirects = ROOT / "static" / "_redirects"
        for line in redirects.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            self.assertNotEqual(line.split()[0].rstrip("/"), "/glossary",
                                "a redirect points away from the live /glossary/")

    def test_no_redirect_source_is_a_built_tool_page(self):
        redirects = ROOT / "static" / "_redirects"
        sources = set()
        for line in redirects.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and line.startswith("/"):
                sources.add(line.split()[0].rstrip("/") + "/")
        for tool in TOOLS:
            self.assertNotIn(tool.path, sources, f"{tool.path} is being redirected away")


class DailyCycleFunctionsProbeTests(unittest.TestCase):
    """The production half of the Function-404 bug lives in the daily loop, not only here."""

    def setUp(self):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        import daily_cycle
        self.dc = daily_cycle

    def test_the_daily_cycle_probes_every_tool_function(self):
        probed = {endpoint for _, endpoint in self.dc.TOOL_FUNCTIONS}
        expected = {t.endpoint for t in TOOLS if t.endpoint}
        self.assertEqual(probed, expected,
                         "the daily probe and the tool list have drifted apart")

    def test_each_probed_page_matches_its_endpoint(self):
        for page, endpoint in self.dc.TOOL_FUNCTIONS:
            self.assertIn(page, BY_PATH, page)
            self.assertEqual(BY_PATH[page].endpoint, endpoint, page)

    def test_a_broken_function_fails_the_daily_cycle(self):
        source = (ROOT / "tools" / "daily_cycle.py").read_text(encoding="utf-8")
        self.assertIn("functions = functions_check()", source)
        self.assertIn("or functions or", source)
        self.assertIn("Tool Functions:", source)


@unittest.skipUnless(LIVE, "set NINADPATHAK_LIVE_TESTS=1 to probe production")
class LiveSmokeTests(unittest.TestCase):
    """Optional production probes. Off by default so the suite is deterministic offline.

    A Pages Function can only really be verified against the deployment; everything the
    repo can check without the network is checked in PagesFunctionContractTests.
    """

    def _post(self, endpoint, payload):
        import urllib.error
        import urllib.request
        request = urllib.request.Request(
            "https://ninadpathak.com" + endpoint,
            data=json.dumps(payload).encode(),
            headers={"content-type": "application/json",
                     "user-agent": "ninadpathak-tool-e2e/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=30) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode()
            try:
                return exc.code, json.loads(body)
            except ValueError:
                return exc.code, {}

    def test_each_tool_page_serves_200(self):
        import urllib.request
        for tool in TOOLS:
            request = urllib.request.Request("https://ninadpathak.com" + tool.path,
                                            headers={"user-agent": "ninadpathak-tool-e2e/1.0"})
            with urllib.request.urlopen(request, timeout=30) as r:
                self.assertEqual(r.status, 200, tool.path)

    def test_each_function_answers_rather_than_404s(self):
        """The named near-miss, checked against production."""
        for tool in TOOLS:
            if tool.endpoint is None:
                continue
            status, _ = self._post(tool.endpoint, {"url": "example.com"})
            self.assertNotEqual(status, 404,
                                f"{tool.endpoint} 404s while {tool.path} still renders")
            self.assertIn(status, (200, 400, 422), f"{tool.endpoint} returned {status}")

    def test_every_function_refuses_a_private_address(self):
        for tool in TOOLS:
            if tool.endpoint is None:
                continue
            status, body = self._post(tool.endpoint, {"url": "http://127.0.0.1/"})
            self.assertEqual(status, 422, tool.endpoint)
            self.assertIn("rivate", body.get("error", ""), tool.endpoint)

    def test_every_function_rejects_a_malformed_body(self):
        import urllib.error
        import urllib.request
        for tool in TOOLS:
            if tool.endpoint is None:
                continue
            request = urllib.request.Request(
                "https://ninadpathak.com" + tool.endpoint, data=b"not json",
                headers={"content-type": "application/json",
                         "user-agent": "ninadpathak-tool-e2e/1.0"})
            try:
                with urllib.request.urlopen(request, timeout=30) as r:
                    status = r.status
            except urllib.error.HTTPError as exc:
                status = exc.code
            self.assertEqual(status, 400, tool.endpoint)


if __name__ == "__main__":
    unittest.main()
