"""Deterministic tests for the llms.txt validator rule engine.

The engine ships as browser JavaScript. These tests drive that exact file
through node, so there is one implementation and no Python copy to drift from
it. If node is unavailable the suite skips rather than passing silently.

Rule severities are asserted against the llms.txt proposal v2
(llmstxt.org/index.md, retrieved 2026-08-17), whose only stated requirement is
an H1. Tests therefore pin the calibration as much as the parsing: a spec
violation must be an error, and anything the spec calls optional must not be.
"""

import json
import shutil
import subprocess
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE = REPO_ROOT / "static" / "js" / "llms-validator-core.js"
NODE = shutil.which("node")


def validate(source: str) -> dict:
    """Run the shipped engine over `source` and return its result as a dict."""
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
        [NODE, "-e", harness, str(ENGINE)],
        input=source.encode("utf-8"),
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout.decode("utf-8"))


def rules(result: dict) -> set:
    return {finding["rule"] for finding in result["findings"]}


def severity_of(result: dict, rule: str) -> str:
    for finding in result["findings"]:
        if finding["rule"] == rule:
            return finding["severity"]
    raise AssertionError(f"rule {rule!r} not raised; got {sorted(rules(result))}")


# The spec's mock example verbatim, except that its two placeholder links both
# read `https://link_url`. That repetition is an artefact of it being a template,
# and it correctly trips duplicate detection, so the fixture gives each link a
# distinct URL. Duplicate detection is covered separately in WarningRuleTests.
SPEC_EXAMPLE = """# Title

> Optional description goes here

Optional details go here

## Section name

- [Link title](https://example.com/primary): Optional link details

## Optional

- [Link title](https://example.com/secondary)
"""


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class EngineAvailabilityTests(unittest.TestCase):
    def test_engine_file_exists(self):
        self.assertTrue(ENGINE.is_file(), f"missing engine at {ENGINE}")

    def test_engine_has_no_dom_dependency(self):
        """The engine must stay pure so it can run in node and in the browser."""
        source = ENGINE.read_text(encoding="utf-8")
        for forbidden in ("document.", "window.", "fetch(", "XMLHttpRequest", "localStorage"):
            self.assertNotIn(forbidden, source, f"engine must not reference {forbidden}")


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class SpecConformanceTests(unittest.TestCase):
    def test_spec_example_is_clean(self):
        """The spec's own mock example must raise no errors or warnings."""
        result = validate(SPEC_EXAMPLE)
        self.assertEqual(result["stats"]["errors"], 0, result["findings"])
        self.assertEqual(result["stats"]["warnings"], 0, result["findings"])
        self.assertEqual(result["grade"], "A")
        self.assertEqual(result["title"], "Title")

    def test_real_world_file_from_llmstxt_org_is_clean(self):
        """The spec author's own published llms.txt must validate cleanly."""
        source = (
            "# llms.txt\n\n"
            "> A proposal that those interested in providing LLM-friendly content add a "
            "/llms.txt file to their site.\n\n"
            "## Docs\n\n"
            "- [llms.txt proposal](https://llmstxt.org/index.md): The proposal for llms.txt\n"
            "- [Python library docs](https://llmstxt.org/intro.html.md): Docs for `llms-txt` python lib\n"
        )
        result = validate(source)
        self.assertEqual(result["stats"]["errors"], 0, result["findings"])
        self.assertEqual(result["stats"]["warnings"], 0, result["findings"])

    def test_minimal_valid_file_is_only_an_h1(self):
        """The spec calls the H1 the only required section, so this must not error."""
        result = validate("# Just A Title\n")
        self.assertEqual(result["stats"]["errors"], 0, result["findings"])
        self.assertIn("missing-summary", rules(result))
        self.assertIn("no-sections", rules(result))
        self.assertEqual(severity_of(result, "missing-summary"), "warning")
        self.assertEqual(severity_of(result, "no-sections"), "warning")

    def test_optional_elements_are_never_errors(self):
        """Nothing the spec marks optional may be reported as an error."""
        result = validate("# Title\n\n## Docs\n\n- [A](https://example.com/a)\n")
        for rule in ("missing-summary", "link-without-notes"):
            self.assertIn(rule, rules(result))
            self.assertNotEqual(severity_of(result, rule), "error", rule)


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class ErrorRuleTests(unittest.TestCase):
    def test_empty_input_is_an_error(self):
        result = validate("   \n\n  ")
        self.assertIn("empty-input", rules(result))
        self.assertEqual(result["grade"], "F")
        self.assertEqual(result["score"], 0)

    def test_missing_h1_is_an_error_and_caps_the_score(self):
        result = validate("> A summary with no title\n\n## Docs\n\n- [A](https://example.com/a): note\n")
        self.assertEqual(severity_of(result, "missing-h1"), "error")
        self.assertLessEqual(result["score"], 40)
        self.assertEqual(result["grade"], "F")

    def test_second_h1_is_an_error(self):
        result = validate("# One\n\n> s\n\n# Two\n")
        self.assertEqual(severity_of(result, "multiple-h1"), "error")

    def test_content_before_h1_is_an_error(self):
        result = validate("Some preamble prose\n\n# Title\n\n> s\n")
        self.assertEqual(severity_of(result, "content-before-h1"), "error")

    def test_blockquote_before_h1_is_an_error(self):
        result = validate("> summary first\n\n# Title\n")
        self.assertEqual(severity_of(result, "blockquote-before-h1"), "error")

    def test_empty_h1_is_an_error(self):
        result = validate("#\n\n> s\n")
        self.assertEqual(severity_of(result, "empty-h1"), "error")

    def test_heading_before_first_section_is_an_error(self):
        """The spec allows any markdown except headings in the details region."""
        result = validate("# Title\n\n> s\n\n### Notes\n\nprose\n")
        self.assertEqual(severity_of(result, "heading-in-details"), "error")

    def test_nested_heading_inside_section_is_an_error(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n### Sub\n\n- [A](https://example.com/a): n\n")
        self.assertEqual(severity_of(result, "nested-heading-in-section"), "error")

    def test_list_item_without_a_link_is_an_error(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n- just some plain text\n")
        self.assertEqual(severity_of(result, "list-item-without-link"), "error")

    def test_malformed_link_is_an_error(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n- [Broken] (https://example.com/a)\n")
        self.assertEqual(severity_of(result, "malformed-link"), "error")

    def test_empty_link_url_is_an_error(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n- [Name]()\n")
        self.assertEqual(severity_of(result, "empty-link-url"), "error")

    def test_empty_link_name_is_an_error(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n- [](https://example.com/a): n\n")
        self.assertEqual(severity_of(result, "empty-link-name"), "error")


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class WarningRuleTests(unittest.TestCase):
    def test_relative_url_is_a_warning_not_an_error(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n- [A](/docs/a.md): note\n")
        self.assertEqual(severity_of(result, "relative-link-url"), "warning")

    def test_http_url_is_a_warning(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n- [A](http://example.com/a): note\n")
        self.assertEqual(severity_of(result, "insecure-link-url"), "warning")

    def test_duplicate_url_is_reported_once(self):
        source = (
            "# Title\n\n> s\n\n## Docs\n\n"
            "- [A](https://example.com/a): note\n"
            "- [B](https://example.com/a): note\n"
        )
        result = validate(source)
        duplicates = [f for f in result["findings"] if f["rule"] == "duplicate-link-url"]
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["severity"], "warning")

    def test_empty_section_is_a_warning(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n## More\n\n- [A](https://example.com/a): n\n")
        self.assertEqual(severity_of(result, "empty-section"), "warning")

    def test_duplicate_section_name_is_a_warning(self):
        source = (
            "# Title\n\n> s\n\n"
            "## Docs\n\n- [A](https://example.com/a): n\n\n"
            "## docs\n\n- [B](https://example.com/b): n\n"
        )
        result = validate(source)
        self.assertEqual(severity_of(result, "duplicate-section-name"), "warning")

    def test_optional_section_must_come_last(self):
        source = (
            "# Title\n\n> s\n\n"
            "## Optional\n\n- [A](https://example.com/a): n\n\n"
            "## Docs\n\n- [B](https://example.com/b): n\n"
        )
        result = validate(source)
        self.assertEqual(severity_of(result, "optional-section-not-last"), "warning")

    def test_optional_section_last_is_accepted(self):
        result = validate(SPEC_EXAMPLE)
        self.assertNotIn("optional-section-not-last", rules(result))

    def test_prose_inside_a_section_is_a_warning(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\nsome prose here\n\n- [A](https://example.com/a): n\n")
        self.assertEqual(severity_of(result, "non-list-content-in-section"), "warning")

    def test_trailing_text_after_link_without_colon(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n- [A](https://example.com/a) trailing words\n")
        self.assertEqual(severity_of(result, "unparsed-trailing-text"), "warning")

    def test_summary_not_adjacent_to_h1_is_a_warning(self):
        result = validate("# Title\n\nprose before the summary\n\n> the summary\n")
        self.assertEqual(severity_of(result, "summary-not-adjacent"), "warning")


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class ParsingRobustnessTests(unittest.TestCase):
    def test_fenced_code_block_is_not_parsed_as_structure(self):
        """Pasting the spec example inside a fence must not create a second H1."""
        source = (
            "# Real Title\n\n> s\n\n"
            "Here is an example:\n\n"
            "```markdown\n"
            "# Not A Real Title\n"
            "## Not A Real Section\n"
            "- plain text that is not a link\n"
            "```\n\n"
            "## Docs\n\n- [A](https://example.com/a): n\n"
        )
        result = validate(source)
        self.assertNotIn("multiple-h1", rules(result))
        self.assertNotIn("list-item-without-link", rules(result))
        self.assertEqual(result["stats"]["sections"], 1)
        self.assertEqual(result["title"], "Real Title")

    def test_byte_order_mark_is_permitted_and_noted(self):
        result = validate("﻿# Title\n\n> s\n")
        self.assertEqual(severity_of(result, "bom-present"), "info")
        self.assertNotIn("content-before-h1", rules(result))
        self.assertEqual(result["title"], "Title")

    def test_crlf_line_endings_parse_identically(self):
        unix = validate(SPEC_EXAMPLE)
        windows = validate(SPEC_EXAMPLE.replace("\n", "\r\n"))
        self.assertEqual(unix["stats"], windows["stats"])
        self.assertEqual(unix["score"], windows["score"])

    def test_url_containing_parentheses_is_parsed(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n- [A](https://ex.com/a_(b)): note\n")
        self.assertNotIn("malformed-link", rules(result))
        self.assertNotIn("empty-link-url", rules(result))
        self.assertEqual(result["stats"]["links"], 1)

    def test_asterisk_and_ordered_list_markers_are_recognised(self):
        result = validate("# Title\n\n> s\n\n## Docs\n\n* [A](https://example.com/a): n\n1. [B](https://example.com/b): n\n")
        self.assertEqual(result["stats"]["links"], 2)
        self.assertNotIn("list-item-without-link", rules(result))

    def test_multiline_blockquote_counts_as_a_summary(self):
        result = validate("# Title\n\n> line one\n> line two\n\n## Docs\n\n- [A](https://example.com/a): n\n")
        self.assertNotIn("missing-summary", rules(result))
        self.assertNotIn("empty-summary", rules(result))

    def test_findings_are_ordered_errors_first(self):
        source = "# Title\n\n## Docs\n\n- plain text\n- [A](http://example.com/a)\n"
        result = validate(source)
        severities = [f["severity"] for f in result["findings"]]
        rank = {"error": 0, "warning": 1, "info": 2}
        self.assertEqual(severities, sorted(severities, key=lambda s: rank[s]))

    def test_every_finding_declares_a_basis(self):
        """Each rule must say whether it rests on the spec or on convention."""
        result = validate("# Title\n\n## Docs\n\n- [A](/rel)\n- plain\n")
        for item in result["findings"]:
            self.assertIn(item["basis"], ("spec", "convention"), item)
            self.assertIn(item["severity"], ("error", "warning", "info"), item)
            self.assertTrue(item["message"].strip(), item)


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class ScoringTests(unittest.TestCase):
    def test_score_is_deterministic(self):
        first = validate(SPEC_EXAMPLE)
        second = validate(SPEC_EXAMPLE)
        self.assertEqual(first, second)

    def test_errors_cost_more_than_warnings(self):
        with_warning = validate("# Title\n\n> s\n\n## Docs\n\n- [A](http://example.com/a): n\n")
        with_error = validate("# Title\n\n> s\n\n## Docs\n\n- plain text\n")
        self.assertGreater(with_warning["score"], with_error["score"])

    def test_score_never_goes_negative(self):
        source = "# T\n\n# T2\n\n# T3\n\n## S\n\n" + "".join(f"- plain {i}\n" for i in range(20))
        result = validate(source)
        self.assertGreaterEqual(result["score"], 0)
        self.assertEqual(result["grade"], "F")

    def test_grade_boundaries(self):
        clean = validate(SPEC_EXAMPLE)
        self.assertEqual(clean["grade"], "A")
        self.assertGreaterEqual(clean["score"], 90)


if __name__ == "__main__":
    unittest.main()
