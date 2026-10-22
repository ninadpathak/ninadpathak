"""Deterministic tests for the AI Overviews extractability checker.

The engine ships as browser JavaScript. These tests drive that exact file through
node, so there is one implementation.

Two properties matter as much as the parsing, and are pinned here:

1. The tool must not imply precision it does not have. There is no weighted
   score, bands are coarse, and every check declares its confidence as either
   "documented" (it restates a primary source) or "heuristic" (a text pattern
   that can be wrong).
2. Snippet eligibility is the only documented hard requirement, per Google's
   generative-AI guidance of 2026-07-10. Schema must never be reported as an
   AI Overview requirement, because Google states it is not one.
"""

import json
import shutil
import subprocess
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE = REPO_ROOT / "static" / "js" / "aio-checker-core.js"
NODE = shutil.which("node")


def run_check(source: str, options: dict = None) -> dict:
    harness = textwrap.dedent(
        """
        const core = require(process.argv[1]);
        const options = JSON.parse(process.argv[2] || "{}");
        let input = "";
        process.stdin.on("data", (chunk) => { input += chunk; });
        process.stdin.on("end", () => {
          process.stdout.write(JSON.stringify(core.check(input, options)));
        });
        """
    )
    completed = subprocess.run(
        [NODE, "-e", harness, str(ENGINE), json.dumps(options or {})],
        input=source.encode("utf-8"),
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout.decode("utf-8"))


def by_id(result: dict) -> dict:
    return {item["id"]: item for item in result["checks"]}


def status_of(result: dict, check_id: str) -> str:
    checks = by_id(result)
    if check_id not in checks:
        raise AssertionError(f"check {check_id!r} missing; got {sorted(checks)}")
    return checks[check_id]["status"]


GOOD_PAGE = """# Keep one URL per documentation version

Documentation for multiple versions belongs on one URL per version, with the
current version canonical. That rule survives every migration I have run.

## A version selector belongs in the page shell, not the sidebar

A version selector placed in the sidebar disappears on mobile, where the sidebar
collapses. Readers on a phone then have no way to tell which version they are
reading, measured across 30 developer docs sites on 2026-08-14.

## Redirect retired versions to the nearest live equivalent

Retired versions should redirect to the nearest live page rather than the docs
home. According to the Google Search Central documentation, a redirect to an
unrelated page is treated as a soft 404.

## This approach does not apply to pre-release branches

Pre-release documentation is a limitation of this scheme: nightly builds change
too often for stable URLs to be worth maintaining, so the trade-off is to leave
them unindexed. I did not test this on monorepos with more than 40 packages.
"""

BAD_PAGE = """# Documentation

In today's fast-paced development landscape, documentation has become
increasingly important for every engineering team.

## Overview

This is the part where teams usually struggle. It affects everything downstream.

## Best Practices

They should be followed carefully. There are 12 of them and most teams adopt 40
before shipping.

## Conclusion

In conclusion, documentation matters.
"""


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class EngineContractTests(unittest.TestCase):
    def test_engine_exists_and_is_pure(self):
        self.assertTrue(ENGINE.is_file())
        source = ENGINE.read_text(encoding="utf-8")
        for forbidden in ("document.", "window.", "fetch(", "XMLHttpRequest", "localStorage"):
            self.assertNotIn(forbidden, source, f"engine must not reference {forbidden}")

    def test_no_weighted_score_is_exposed(self):
        """Ninad's constraint: expose the method, never a formula implying precision."""
        result = run_check(GOOD_PAGE)
        self.assertNotIn("score", result["summary"])
        self.assertIn("passed", result["summary"])
        self.assertIn("attention", result["summary"])
        self.assertIn("bandLabel", result["summary"])

    def test_every_check_declares_a_basis_and_confidence(self):
        result = run_check(GOOD_PAGE)
        self.assertTrue(result["checks"])
        for item in result["checks"]:
            self.assertIn(item["confidence"], ("documented", "heuristic"), item["id"])
            self.assertIn(item["status"], ("pass", "attention", "info", "skipped"), item["id"])
            self.assertTrue(item["basis"].strip(), item["id"])
            self.assertTrue(item["detail"].strip(), item["id"])
            self.assertTrue(item["title"].strip(), item["id"])

    def test_every_basis_carries_a_date(self):
        """An undated basis is not defensible, so each one must cite a dated source."""
        import re

        result = run_check(GOOD_PAGE)
        for item in result["checks"]:
            self.assertRegex(
                item["basis"],
                r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b",
                f"{item['id']} basis lacks an ISO date: {item['basis']}",
            )

    def test_only_documented_checks_are_snippet_and_schema(self):
        result = run_check("<html><head></head><body><h1>x</h1><p>y</p></body></html>")
        documented = {i["id"] for i in result["checks"] if i["confidence"] == "documented"}
        self.assertEqual(documented, {"snippet-eligibility", "schema-present"})

    def test_empty_input_returns_no_checks(self):
        result = run_check("   \n  ")
        self.assertEqual(result["checks"], [])
        self.assertEqual(result["summary"]["applicable"], 0)
        self.assertEqual(result["summary"]["band"], "none")

    def test_deterministic(self):
        self.assertEqual(run_check(GOOD_PAGE), run_check(GOOD_PAGE))


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class DiscriminationTests(unittest.TestCase):
    """A checker that always passes, or always fails, is useless."""

    def test_good_page_passes_more_than_bad_page(self):
        good = run_check(GOOD_PAGE)
        bad = run_check(BAD_PAGE)
        self.assertGreater(good["summary"]["passed"], bad["summary"]["passed"])
        self.assertLess(good["summary"]["attention"], bad["summary"]["attention"])

    def test_good_page_reaches_a_high_band(self):
        good = run_check(GOOD_PAGE)
        self.assertIn(good["summary"]["grade"], ("a", "b"), good["checks"])

    def test_bad_page_reaches_a_low_band(self):
        bad = run_check(BAD_PAGE)
        self.assertIn(bad["summary"]["grade"], ("d", "f"), bad["checks"])


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class IndividualCheckTests(unittest.TestCase):
    def test_preamble_opening_is_flagged(self):
        result = run_check("# Title\n\nIn today's fast-paced world, docs matter a great deal to teams.\n")
        self.assertEqual(status_of(result, "direct-answer-first"), "attention")

    def test_direct_opening_passes(self):
        result = run_check(
            "# Title\n\nEvery API reference page needs a request a reader can paste without editing it first.\n"
        )
        self.assertEqual(status_of(result, "direct-answer-first"), "pass")

    def test_topic_label_headings_are_flagged(self):
        result = run_check("# T\n\nOpening sentence that asserts something specific and useful here.\n\n## Overview\n\nBody text here.\n")
        self.assertEqual(status_of(result, "headings-carry-claims"), "attention")

    def test_question_heading_passes(self):
        result = run_check(
            "# T\n\nOpening sentence that asserts something specific and useful here.\n\n"
            "## What does a version selector belong in?\n\nA version selector belongs in the shell.\n"
        )
        self.assertEqual(status_of(result, "headings-carry-claims"), "pass")

    def test_assertive_heading_passes(self):
        result = run_check(
            "# T\n\nOpening sentence that asserts something specific and useful here.\n\n"
            "## Keep one URL per version and canonicalise to the current one\n\nCanonical rules follow.\n"
        )
        self.assertEqual(status_of(result, "headings-carry-claims"), "pass")

    def test_no_subheadings_is_flagged(self):
        result = run_check("# Only a title\n\nOne paragraph asserting something specific and reasonably long here.\n")
        self.assertEqual(status_of(result, "headings-carry-claims"), "attention")

    def test_pronoun_section_opening_is_flagged(self):
        result = run_check(
            "# T\n\nOpening asserts something specific and useful for the reader here.\n\n"
            "## Redirect retired versions to the nearest live page\n\n"
            "This is why it matters so much for crawl budget.\n"
        )
        self.assertEqual(status_of(result, "self-contained-passages"), "attention")

    def test_named_subject_section_opening_passes(self):
        result = run_check(
            "# T\n\nOpening asserts something specific and useful for the reader here.\n\n"
            "## Redirect retired versions to the nearest live page\n\n"
            "Retired version pages should redirect to the nearest live equivalent page.\n"
        )
        self.assertEqual(status_of(result, "self-contained-passages"), "pass")

    def test_definition_sentence_is_detected(self):
        result = run_check(
            "# Docs as code\n\nDocs as code is the practice of storing documentation in the "
            "same repository as the software it describes.\n"
        )
        self.assertEqual(status_of(result, "liftable-definition"), "pass")

    def test_missing_definition_is_flagged(self):
        result = run_check("# Guide\n\nStore documentation beside the code, then review it the same way.\n")
        self.assertEqual(status_of(result, "liftable-definition"), "attention")

    def test_undated_page_is_flagged(self):
        result = run_check("# T\n\nDocumentation belongs beside the code it describes, without exception.\n")
        self.assertEqual(status_of(result, "dated-evidence"), "attention")

    def test_time_relative_claim_without_a_date_is_flagged(self):
        result = run_check(
            "# T\n\nPublished 2026-08-14. Documentation belongs beside the code.\n\n"
            "## Keep versions on separate URLs\n\nMost teams currently ship three supported versions.\n"
        )
        self.assertEqual(status_of(result, "dated-evidence"), "attention")

    def test_dated_page_without_time_relative_claims_passes(self):
        result = run_check(
            "# T\n\nPublished 2026-08-14. Documentation belongs beside the code it describes.\n"
        )
        self.assertEqual(status_of(result, "dated-evidence"), "pass")

    def test_limits_section_passes(self):
        result = run_check(
            "# T\n\nDocumentation belongs beside the code.\n\n"
            "## Where this does not apply\n\n"
            "This scheme does not apply to nightly builds, and I did not test it on monorepos.\n"
        )
        self.assertEqual(status_of(result, "states-its-limits"), "pass")

    def test_no_limits_is_flagged(self):
        result = run_check("# T\n\nDocumentation belongs beside the code, always, for every team.\n")
        self.assertEqual(status_of(result, "states-its-limits"), "attention")

    def test_dangling_number_is_flagged(self):
        """A number trailed only by punctuation cannot be interpreted once lifted."""
        result = run_check("# T\n\nAfter the rewrite, documentation quality improved by 40.\n")
        self.assertEqual(status_of(result, "quantities-carry-units"), "attention")

    def test_numbers_with_units_pass(self):
        result = run_check("# T\n\nBuilds finished in 340 ms on average across 30 sites we measured.\n")
        self.assertEqual(status_of(result, "quantities-carry-units"), "pass")

    def test_number_followed_by_the_noun_it_counts_passes(self):
        """"47 problems" names its own unit, so it must not be flagged."""
        result = run_check("# T\n\nWe reviewed the docs and found 47 problems worth fixing before release.\n")
        self.assertEqual(status_of(result, "quantities-carry-units"), "pass")

    def test_percentage_passes(self):
        result = run_check("# T\n\nAI Overviews reduced clicks by 35% on the queries that carried one.\n")
        self.assertEqual(status_of(result, "quantities-carry-units"), "pass")

    def test_no_numbers_skips_the_numeric_checks(self):
        result = run_check("# T\n\nDocumentation belongs beside the code it describes, without exception.\n")
        self.assertEqual(status_of(result, "quantities-carry-units"), "skipped")
        self.assertEqual(status_of(result, "claims-carry-sources"), "skipped")


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class HtmlModeTests(unittest.TestCase):
    def test_nosnippet_is_flagged_as_documented(self):
        html = '<html><head><meta name="robots" content="index, nosnippet"></head><body><h1>T</h1><p>Body.</p></body></html>'
        result = run_check(html)
        check = by_id(result)["snippet-eligibility"]
        self.assertEqual(check["status"], "attention")
        self.assertEqual(check["confidence"], "documented")

    def test_noindex_is_flagged(self):
        html = '<html><head><meta name="robots" content="noindex"></head><body><h1>T</h1><p>Body.</p></body></html>'
        self.assertEqual(status_of(run_check(html), "snippet-eligibility"), "attention")

    def test_positive_max_snippet_only_limits_length(self):
        # Review finding: max-snippet:160 was reported as making the page ineligible. Google
        # documents a positive value as a maximum snippet length and only 0 as nosnippet.
        for value in ("50", "160"):
            html = f'<html><head><meta name="robots" content="max-snippet:{value}"></head><body><h1>T</h1><p>B.</p></body></html>'
            check = by_id(run_check(html))["snippet-eligibility"]
            with self.subTest(value=value):
                self.assertEqual(check["status"], "pass")
                self.assertIn(f"max-snippet:{value}", check["detail"])

    def snippet(self, head, headers=None):
        html = f"<html><head>{head}</head><body><h1>T</h1><p>B.</p></body></html>"
        return by_id(run_check(html, headers or {}))["snippet-eligibility"]

    def test_most_restrictive_directive_wins_in_either_order(self):
        # Review round 3, finding 1: only the first max-snippet was read, so
        # "max-snippet:160, max-snippet:0" passed while the reverse order failed.
        for content in ("max-snippet:160, max-snippet:0", "max-snippet:0, max-snippet:160",
                        "max-snippet:160, nosnippet", "nosnippet, max-snippet:160"):
            with self.subTest(content=content):
                self.assertEqual(self.snippet(f'<meta name="robots" content="{content}">')["status"], "attention")

    def test_every_robots_meta_tag_is_read(self):
        head = '<meta name="robots" content="max-snippet:160"><meta name="robots" content="noindex">'
        self.assertEqual(self.snippet(head)["status"], "attention")

    def test_header_and_meta_are_combined(self):
        # Review round 3, finding 1: HTML max-snippet:160 plus X-Robots-Tag max-snippet:0 passed.
        meta = '<meta name="robots" content="max-snippet:160">'
        self.assertEqual(self.snippet(meta, {"xRobotsTag": "max-snippet:0"})["status"], "attention")
        self.assertEqual(self.snippet('<meta name="robots" content="max-snippet:0">',
                                      {"xRobotsTag": "max-snippet:160"})["status"], "attention")

    def test_googlebot_meta_applies_and_other_bots_do_not(self):
        self.assertEqual(self.snippet('<meta name="googlebot" content="nosnippet">')["status"], "attention")
        self.assertEqual(self.snippet('<meta content="nosnippet" name="googlebot">')["status"], "attention")
        self.assertEqual(self.snippet('<meta name="bingbot" content="nosnippet">')["status"], "pass")

    def test_any_scoped_header_is_a_manual_check_never_a_pass(self):
        # Round 4 changed this deliberately: duplicate X-Robots-Tag fields arrive flattened,
        # so a scoped header cannot be attributed safely, whichever agent it names.
        for value in ("googlebot: nosnippet", "otherbot: noindex, nosnippet",
                      "otherbot: noindex, googlebot: max-snippet:0"):
            with self.subTest(value=value):
                check = self.snippet("", {"xRobotsTag": value})
                self.assertEqual(check["status"], "attention")
                self.assertIn("manual check", check["detail"])

    def test_none_counts_as_noindex(self):
        self.assertEqual(self.snippet('<meta name="robots" content="none">')["status"], "attention")

    def test_smallest_positive_limit_is_reported(self):
        check = self.snippet('<meta name="robots" content="max-snippet:300">', {"xRobotsTag": "max-snippet:120"})
        self.assertEqual(check["status"], "pass")
        self.assertIn("max-snippet:120", check["detail"])

    def assert_not_pass(self, head, headers=None, manual=True):
        check = self.snippet(head, headers)
        self.assertNotEqual(check["status"], "pass", check["detail"])
        if manual:
            self.assertIn("manual check", check["detail"])
        return check

    def test_extra_attributes_or_entities_need_a_manual_check(self):
        # Review round 4, finding 1: both passed although they contain noindex.
        self.assert_not_pass('<meta data-name="otherbot" name="robots" content="noindex">')
        self.assert_not_pass('<meta name="robots" content="index&#44;noindex">')

    def test_unquoted_and_quoted_angle_bracket_need_a_manual_check(self):
        self.assert_not_pass("<meta name=robots content=noindex>")
        self.assert_not_pass('<meta name="robots" content="x>y, noindex">')
        self.assert_not_pass('<meta name="r&#111;bots" content="noindex">')

    def test_robots_tag_inside_comment_or_script_needs_a_manual_check(self):
        self.assert_not_pass('<!-- <meta name="robots" content="noindex"> -->')
        self.assert_not_pass('<script>var t = \'<meta name="robots" content="noindex">\';</script>')

    def test_scoped_header_needs_a_manual_check(self):
        # Review round 4, finding 2: two X-Robots-Tag fields flattened into
        # "otherbot: nofollow, noindex" lost their boundary and passed.
        self.assert_not_pass("", {"xRobotsTag": "otherbot: nofollow, noindex"})
        self.assert_not_pass("", {"xRobotsTag": "googlebot: max-snippet:160"})

    def test_unknown_directive_needs_a_manual_check(self):
        self.assert_not_pass('<meta name="robots" content="noindx">')

    def test_past_unavailable_after_fails(self):
        # Review round 4, finding 3: an expired page passed.
        for head, headers in (('<meta name="robots" content="unavailable_after: 2000-01-01">', None),
                              ("", {"xRobotsTag": "unavailable_after: 2000-01-01"})):
            with self.subTest(head=head, headers=headers):
                check = self.assert_not_pass(head, headers, manual=False)
                self.assertIn("unavailable_after", check["detail"] + str(check.get("evidence")))

    def test_future_unavailable_after_passes_and_bad_date_needs_a_manual_check(self):
        check = self.snippet('<meta name="robots" content="unavailable_after: 2099-01-01">')
        self.assertEqual(check["status"], "pass")
        self.assert_not_pass('<meta name="robots" content="unavailable_after: someday">')

    def test_quoted_angle_bracket_before_name_needs_a_manual_check(self):
        # Review round 5, finding 1: a quoted "<" ended the scan early and the
        # noindex tag was discarded, so the page passed.
        self.assert_not_pass('<meta data-label="<example>" name="robots" content="noindex">')
        self.assert_not_pass('<meta data-label="<example>" name="&#114;obots" content="noindex">')
        self.assert_not_pass("<meta content='x<y' name=\"googlebot\" content=\"noindex\">")

    def test_every_robots_mention_must_be_accounted_for(self):
        # Invariant: any robots, googlebot or x-robots text outside a cleanly read
        # robots meta tag makes the result a manual check.
        for head in ('<meta name="robots" content="index"><link rel="x-robots" href="/r">',
                     '<meta name="robots" content="index"><p>Googlebot reads this page.</p>',
                     '<meta property="robots" content="noindex">',
                     '<meta name="robots" content="index"><meta name="robots" content="follow" data-x="1">'):
            with self.subTest(head=head):
                self.assert_not_pass(head)
        self.assertEqual(self.snippet('<meta name="robots" content="index"><meta name="googlebot" content="follow">')["status"], "pass")
        self.assertEqual(self.snippet('<meta name="description" content="Tom &amp; Jerry">')["status"], "pass")

    def test_header_that_is_not_plain_directives_needs_a_manual_check(self):
        for header in ("noindex\n", "max-snippet:\u0661\u0666\u0660", "index; noindex"):
            with self.subTest(header=header):
                self.assert_not_pass("", {"xRobotsTag": header})

    def test_max_snippet_must_be_minus_one_or_up_to_nine_digits(self):
        # Review round 5, finding 2: a 400-digit value passed as "Infinity characters".
        for value in ("9" * 400, "1234567890", "-2", "+5", "1e3"):
            with self.subTest(value=value):
                self.assert_not_pass(f'<meta name="robots" content="max-snippet:{value}">')
        self.assertEqual(self.snippet('<meta name="robots" content="max-snippet:999999999">')["status"], "pass")

    def test_impossible_or_near_now_dates_need_a_manual_check(self):
        # Review round 5, finding 2: 2099-02-31 rolled over to March and passed.
        import datetime
        # Without a time zone, the current UTC minute could be past or future.
        now_no_zone = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M")
        for value in ("2099-02-31", "2099-13-01", "2099-01-01T25:00Z", "2099-01-01T10:00+15:00", now_no_zone):
            with self.subTest(value=value):
                self.assert_not_pass(f'<meta name="robots" content="unavailable_after: {value}">')
        for value in ("2099-02-28", "2099-01-01T10:00:00+05:30", "2099-01-01t10:00z"):
            with self.subTest(value=value):
                self.assertEqual(self.snippet(f'<meta name="robots" content="unavailable_after: {value}">')["status"], "pass")
        check = self.assert_not_pass('<meta name="robots" content="unavailable_after: 2000-02-29T00:00Z">', manual=False)
        self.assertNotIn("manual check", check["detail"])

    def test_stray_equals_before_an_encoded_name_needs_a_manual_check(self):
        # Review round 6, finding 1: "=" swallowed name=... as its value, the encoded
        # name was never seen, and an active noindex passed.
        for head in ('<meta = name="&#114;obots" content="noindex">',
                     '<meta = name=&#114;obots content=noindex>',
                     '<meta name="robots" content="max-image-preview:noindex"><meta = name="&#114;obots" content="noindex">',
                     '<meta =x name="description" content="noindex">'):
            with self.subTest(head=head):
                self.assert_not_pass(head)

    def test_character_references_are_decoded_before_counting(self):
        # Decimal, hex and named references, with or without a semicolon, must not
        # hide robots or googlebot from the invariant.
        for text in ("&#114;obots", "&#x72;obots", "&#X52;OBOTS", "&#114obots", "&#0000114;obots",
                     "g&#111;&#x6F;glebot", "rob&#111ts"):
            with self.subTest(text=text):
                self.assert_not_pass(f'<meta name="robots" content="index"><meta property="og:title" content="{text}">')
        self.assertEqual(self.snippet('<meta name="description" content="Tom &amp; Jerry &rarr; &#169; &lt;3">')["status"], "pass")

    def test_inherited_object_properties_are_not_directives(self):
        # Review round 6, finding 2: "constructor" and "__proto__" were looked up on
        # plain objects, found on the prototype, and passed.
        for content in ("constructor", "__proto__", "toString", "hasOwnProperty", "__proto__: noindex", "constructor: x"):
            with self.subTest(content=content):
                self.assert_not_pass(f'<meta name="robots" content="{content}">')
        for header in ("constructor: noindex", "__proto__", "valueOf"):
            with self.subTest(header=header):
                self.assert_not_pass("", {"xRobotsTag": header})

    def test_offset_beyond_fourteen_hours_needs_a_manual_check(self):
        for value in ("2099-01-01T10:00+14:59", "2099-01-01T10:00-14:01", "2099-01-01T10:00+1401"):
            with self.subTest(value=value):
                self.assert_not_pass(f'<meta name="robots" content="unavailable_after: {value}">')
        for value in ("2099-01-01T10:00+14:00", "2099-01-01T10:00-13:59"):
            with self.subTest(value=value):
                self.assertEqual(self.snippet(f'<meta name="robots" content="unavailable_after: {value}">')["status"], "pass")

    def test_preview_values_must_be_documented(self):
        for content in ("max-image-preview:noindex", "max-video-preview:soon", "max-video-preview:9999999999"):
            with self.subTest(content=content):
                self.assert_not_pass(f'<meta name="robots" content="{content}">')
        self.assertEqual(self.snippet('<meta name="robots" content="max-image-preview:large, max-video-preview:-1">')["status"], "pass")

    def test_clean_single_quoted_and_reordered_tags_still_work(self):
        self.assertEqual(self.snippet("<meta content='index, follow' name='robots'>")["status"], "pass")
        self.assertEqual(self.snippet('<META NAME="ROBOTS" CONTENT="NOSNIPPET">')["status"], "attention")

    def test_max_snippet_zero_is_flagged_as_nosnippet(self):
        html = '<html><head><meta name="robots" content="max-snippet:0"></head><body><h1>T</h1><p>B.</p></body></html>'
        check = by_id(run_check(html))["snippet-eligibility"]
        self.assertEqual(check["status"], "attention")
        self.assertEqual(check["confidence"], "documented")

    def test_pass_names_the_search_console_control_it_cannot_see(self):
        html = "<html><head></head><body><h1>T</h1><p>Body text.</p></body></html>"
        self.assertIn("Search Console", by_id(run_check(html))["snippet-eligibility"]["detail"])

    def test_unrestricted_max_snippet_passes(self):
        html = '<html><head><meta name="robots" content="index, follow, max-snippet:-1"></head><body><h1>T</h1><p>B.</p></body></html>'
        self.assertEqual(status_of(run_check(html), "snippet-eligibility"), "pass")

    def test_no_robots_tag_passes(self):
        html = "<html><head></head><body><h1>T</h1><p>Body text.</p></body></html>"
        self.assertEqual(status_of(run_check(html), "snippet-eligibility"), "pass")

    def test_x_robots_tag_header_alone_blocks_snippets(self):
        """A page can be excluded by the header with nothing in its markup."""
        html = "<html><head></head><body><h1>T</h1><p>Body text.</p></body></html>"
        result = run_check(html, {"xRobotsTag": "noindex, nosnippet"})
        check = by_id(result)["snippet-eligibility"]
        self.assertEqual(check["status"], "attention")
        self.assertEqual(check["confidence"], "documented")

    def test_x_robots_tag_without_directives_still_passes(self):
        html = "<html><head></head><body><h1>T</h1><p>Body text.</p></body></html>"
        self.assertEqual(
            status_of(run_check(html, {"xRobotsTag": "index, follow"}), "snippet-eligibility"),
            "pass",
        )

    def test_schema_is_never_an_attention_status(self):
        """Google states schema is not required for generative AI features."""
        without = run_check("<html><head></head><body><h1>T</h1><p>B.</p></body></html>")
        self.assertEqual(status_of(without, "schema-present"), "info")

        with_schema = run_check(
            '<html><head><script type="application/ld+json">{"@type":"Article"}</script>'
            "</head><body><h1>T</h1><p>B.</p></body></html>"
        )
        self.assertEqual(status_of(with_schema, "schema-present"), "info")
        self.assertIn("Article", [e["excerpt"] for e in by_id(with_schema)["schema-present"]["evidence"]])

    def test_schema_type_array_is_parsed(self):
        html = (
            '<html><head><script type="application/ld+json">'
            '{"@type":["SoftwareApplication","WebApplication"]}</script>'
            "</head><body><h1>T</h1><p>B.</p></body></html>"
        )
        excerpts = [e["excerpt"] for e in by_id(run_check(html))["schema-present"]["evidence"]]
        self.assertIn("SoftwareApplication", excerpts)
        self.assertIn("WebApplication", excerpts)

    def test_markdown_input_skips_html_only_checks(self):
        result = run_check(GOOD_PAGE)
        self.assertEqual(status_of(result, "snippet-eligibility"), "skipped")
        self.assertEqual(status_of(result, "schema-present"), "skipped")

    def test_html_headings_and_paragraphs_are_extracted(self):
        html = (
            "<html><body><h1>Title</h1>"
            "<p>Every API reference page needs a request a reader can paste unchanged.</p>"
            "<h2>Keep one URL per version and canonicalise the current one</h2>"
            "<p>Version URLs stay stable across releases for this reason.</p>"
            "</body></html>"
        )
        result = run_check(html)
        self.assertTrue(result["summary"]["isHtml"])
        self.assertEqual(result["summary"]["headings"], 2)
        self.assertEqual(status_of(result, "headings-carry-claims"), "pass")

    def test_script_and_style_content_is_not_treated_as_prose(self):
        html = (
            "<html><head><style>.a{color:red}</style>"
            "<script>var x = 'In today\\'s fast-paced world';</script></head>"
            "<body><h1>T</h1><p>Version URLs stay stable across releases, without exception.</p></body></html>"
        )
        result = run_check(html)
        self.assertEqual(status_of(result, "direct-answer-first"), "pass")

    def test_html_entities_are_decoded(self):
        html = "<html><body><h1>T</h1><p>Docs &amp; code belong together in one repository, always.</p></body></html>"
        result = run_check(html)
        excerpt = by_id(result)["direct-answer-first"]["evidence"][0]["excerpt"]
        self.assertIn("&", excerpt)
        self.assertNotIn("&amp;", excerpt)


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class RealPageTests(unittest.TestCase):
    def test_fenced_code_is_not_parsed_as_headings(self):
        source = (
            "# Real title\n\nVersion URLs stay stable across releases, without exception.\n\n"
            "```markdown\n# Not a heading\n## Overview\n```\n\n"
            "## Keep one URL per version and canonicalise the current one\n\n"
            "Version URLs stay stable for this reason.\n"
        )
        result = run_check(source)
        self.assertEqual(result["summary"]["headings"], 2)
        self.assertEqual(status_of(result, "headings-carry-claims"), "pass")

    def test_checks_are_ordered_with_the_hard_requirement_first(self):
        result = run_check(GOOD_PAGE)
        self.assertEqual(result["checks"][0]["id"], "snippet-eligibility")

    def test_navigation_and_footer_are_not_analysed_as_prose(self):
        """Regression: a footer "Latest posts" list registered as an undated
        time-relative claim on this site's own article pages, 2026-08-17."""
        html = (
            "<html><head></head><body>"
            "<nav><a href='/'>Home</a><a href='/articles/'>Articles</a></nav>"
            "<main>"
            "<h1>Keep one URL per version</h1>"
            "<p>Published 2026-08-14. Version URLs stay stable across releases.</p>"
            "<h2>Redirect retired versions to the nearest live page</h2>"
            "<p>Retired versions redirect to the nearest live equivalent page.</p>"
            "</main>"
            "<footer><h2>Latest posts</h2><a href='/a/'>Newest thing</a></footer>"
            "</body></html>"
        )
        result = run_check(html)
        self.assertEqual(status_of(result, "dated-evidence"), "pass", by_id(result)["dated-evidence"])
        # Only the two headings inside <main> should be counted.
        self.assertEqual(result["summary"]["headings"], 2)

    def test_preamble_in_navigation_does_not_fail_the_opening_check(self):
        html = (
            "<html><body>"
            "<nav><p>In today's fast-paced landscape, welcome to our site.</p></nav>"
            "<main><h1>T</h1>"
            "<p>Version URLs stay stable across releases, and that rule survives migrations.</p>"
            "</main></body></html>"
        )
        self.assertEqual(status_of(run_check(html), "direct-answer-first"), "pass")

    def test_json_ld_in_head_is_still_found_when_prose_comes_from_main(self):
        html = (
            '<html><head><script type="application/ld+json">{"@type":"Article"}</script></head>'
            "<body><nav>nav</nav><main><h1>T</h1>"
            "<p>Version URLs stay stable across releases, without exception, for every team.</p>"
            "</main></body></html>"
        )
        result = run_check(html)
        excerpts = [e["excerpt"] for e in by_id(result)["schema-present"]["evidence"]]
        self.assertIn("Article", excerpts)

    def test_robots_meta_in_head_is_still_found(self):
        html = (
            '<html><head><meta name="robots" content="nosnippet"></head>'
            "<body><main><h1>T</h1><p>Body text that is long enough to be prose here.</p></main></body></html>"
        )
        self.assertEqual(status_of(run_check(html), "snippet-eligibility"), "attention")


if __name__ == "__main__":
    unittest.main()
