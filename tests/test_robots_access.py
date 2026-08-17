"""Deterministic tests for the AI crawler access checker.

The engine ships as browser JavaScript. These tests drive that exact file through
node, so there is one implementation.

The tool's whole value is that it applies robots.txt matching correctly, because
the rules are counter-intuitive and reading a list of user agents tells nobody
what their own file does. So the RFC 9309 semantics are tested hard:

  - only the single most specific matching User-agent group applies
  - within a group the longest matching rule wins, and Allow wins a tie
  - an empty Disallow permits everything
  - "*" and "$" behave as wildcard and end-anchor

The citation/training split is also pinned, because reporting a training opt-out
as a defect would be wrong: it is a legitimate editorial choice.
"""

import json
import shutil
import subprocess
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE = REPO_ROOT / "static" / "js" / "robots-access-core.js"
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


def by_token(result: dict) -> dict:
    return {item["token"]: item for item in result["results"]}


def allowed(result: dict, token: str) -> bool:
    table = by_token(result)
    if token not in table:
        raise AssertionError(f"agent {token!r} not in registry; got {sorted(table)}")
    return table[token]["allowed"]


# The live file from ninadpathak.com, read 2026-08-17. It is the motivating case:
# the block list looks alarming and is in fact a clean training opt-out that
# preserves every citation crawler.
NINAD_ROBOTS = """# As a condition of accessing this website, you agree to abide by the following
# content signals:

User-agent: *
Content-Signal: search=yes,ai-train=no,use=reference
Allow: /

User-agent: Amazonbot
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: meta-externalagent
Disallow: /
"""


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class EngineContractTests(unittest.TestCase):
    def test_engine_exists_and_is_pure(self):
        self.assertTrue(ENGINE.is_file())
        source = ENGINE.read_text(encoding="utf-8")
        for forbidden in ("document.", "window.", "fetch(", "XMLHttpRequest", "localStorage"):
            self.assertNotIn(forbidden, source, f"engine must not reference {forbidden}")

    def test_every_agent_declares_purpose_note_and_dated_source(self):
        result = run_check("User-agent: *\nAllow: /\n")
        self.assertTrue(result["results"])
        for item in result["results"]:
            self.assertIn(item["purpose"], ("cite", "train", "user"), item["token"])
            self.assertTrue(item["note"].strip(), item["token"])
            self.assertRegex(
                item["source"],
                r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b",
                f"{item['token']} source lacks a date: {item['source']}",
            )
            self.assertTrue(item["explanation"].strip(), item["token"])

    def test_no_weighted_score_is_exposed(self):
        result = run_check(NINAD_ROBOTS)
        self.assertNotIn("score", result["summary"])
        self.assertIn("citationAllowed", result["summary"])
        self.assertIn("trainingBlocked", result["summary"])
        self.assertIn("postureLabel", result["summary"])

    def test_edge_blocking_limitation_is_always_reported(self):
        """The tool must never imply robots.txt is the whole story."""
        for source in ("", "User-agent: *\nDisallow:\n", NINAD_ROBOTS):
            note_ids = [n["id"] for n in run_check(source)["notes"]]
            self.assertIn("edge-blocking", note_ids)

    def test_deterministic(self):
        self.assertEqual(run_check(NINAD_ROBOTS), run_check(NINAD_ROBOTS))


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class Rfc9309GroupSelectionTests(unittest.TestCase):
    def test_only_the_most_specific_group_applies(self):
        """The counter-intuitive core rule: a named group replaces the "*" group
        entirely rather than adding to it."""
        source = "User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n"
        result = run_check(source)
        # GPTBot has its own group allowing everything, so the "*" Disallow does
        # not apply to it.
        self.assertTrue(allowed(result, "GPTBot"))
        # Everything unnamed still falls under "*" and is blocked.
        self.assertFalse(allowed(result, "OAI-SearchBot"))

    def test_named_group_wins_even_when_it_is_more_permissive(self):
        source = "User-agent: *\nDisallow: /private/\n\nUser-agent: ClaudeBot\nDisallow: /\n"
        result = run_check(source, {"path": "/docs/"})
        self.assertFalse(allowed(result, "ClaudeBot"))
        self.assertTrue(allowed(result, "Claude-SearchBot"))

    def test_unnamed_agent_falls_under_wildcard(self):
        result = run_check("User-agent: *\nDisallow: /\n")
        self.assertEqual(by_token(result)["PerplexityBot"]["matchedBy"], "wildcard")
        self.assertFalse(allowed(result, "PerplexityBot"))

    def test_no_wildcard_and_no_named_group_means_allowed(self):
        result = run_check("User-agent: SomeOtherBot\nDisallow: /\n")
        item = by_token(result)["OAI-SearchBot"]
        self.assertEqual(item["matchedBy"], "none")
        self.assertTrue(item["allowed"])

    def test_user_agent_matching_is_case_insensitive(self):
        result = run_check("User-agent: gptbot\nDisallow: /\n")
        self.assertFalse(allowed(result, "GPTBot"))
        self.assertEqual(by_token(result)["GPTBot"]["matchedBy"], "explicit")

    def test_consecutive_user_agent_lines_share_one_group(self):
        source = "User-agent: GPTBot\nUser-agent: CCBot\nDisallow: /\n"
        result = run_check(source)
        self.assertFalse(allowed(result, "GPTBot"))
        self.assertFalse(allowed(result, "CCBot"))
        self.assertTrue(allowed(result, "OAI-SearchBot"))

    def test_longer_token_prefix_wins_between_named_groups(self):
        """"Claude-SearchBot" must not be captured by a "ClaudeBot" group, and a
        "Claude" group must lose to a more specific "Claude-SearchBot" group."""
        source = (
            "User-agent: Claude\nDisallow: /\n\n"
            "User-agent: Claude-SearchBot\nAllow: /\n"
        )
        result = run_check(source)
        self.assertTrue(allowed(result, "Claude-SearchBot"))

    def test_claudebot_group_does_not_capture_claude_searchbot(self):
        result = run_check("User-agent: ClaudeBot\nDisallow: /\n")
        self.assertFalse(allowed(result, "ClaudeBot"))
        self.assertTrue(allowed(result, "Claude-SearchBot"))
        self.assertEqual(by_token(result)["Claude-SearchBot"]["matchedBy"], "none")


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class Rfc9309RulePrecedenceTests(unittest.TestCase):
    def test_longest_matching_rule_wins(self):
        source = "User-agent: *\nDisallow: /docs/\nAllow: /docs/public/\n"
        self.assertTrue(allowed(run_check(source, {"path": "/docs/public/a"}), "Googlebot"))
        self.assertFalse(allowed(run_check(source, {"path": "/docs/private/a"}), "Googlebot"))

    def test_allow_wins_an_equal_length_tie(self):
        source = "User-agent: *\nDisallow: /a\nAllow: /a\n"
        self.assertTrue(allowed(run_check(source, {"path": "/a"}), "Googlebot"))

    def test_empty_disallow_permits_everything(self):
        result = run_check("User-agent: *\nDisallow:\n")
        self.assertTrue(allowed(result, "Googlebot"))
        self.assertEqual(result["summary"]["citationBlocked"], 0)

    def test_wildcard_in_path_is_honoured(self):
        source = "User-agent: *\nDisallow: /*.pdf\n"
        self.assertFalse(allowed(run_check(source, {"path": "/files/report.pdf"}), "Googlebot"))
        self.assertTrue(allowed(run_check(source, {"path": "/files/report.html"}), "Googlebot"))

    def test_dollar_anchors_the_end_of_the_path(self):
        source = "User-agent: *\nDisallow: /*.php$\n"
        self.assertFalse(allowed(run_check(source, {"path": "/index.php"}), "Googlebot"))
        self.assertTrue(allowed(run_check(source, {"path": "/index.php?a=1"}), "Googlebot"))

    def test_no_matching_rule_means_allowed(self):
        result = run_check("User-agent: *\nDisallow: /admin/\n", {"path": "/docs/"})
        self.assertTrue(allowed(result, "Googlebot"))

    def test_comments_are_stripped(self):
        result = run_check("User-agent: *  # everyone\nDisallow: /   # everything\n")
        self.assertFalse(allowed(result, "Googlebot"))

    def test_rule_before_any_user_agent_is_ignored_and_flagged(self):
        result = run_check("Disallow: /\n\nUser-agent: *\nAllow: /\n")
        self.assertTrue(allowed(result, "Googlebot"))
        self.assertIn("rule-before-user-agent", [n["id"] for n in result["notes"]])

    def test_default_path_is_root(self):
        self.assertEqual(run_check("User-agent: *\nAllow: /\n")["summary"]["path"], "/")


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class CitationVersusTrainingTests(unittest.TestCase):
    """The distinction the tool exists to make."""

    def test_ninads_live_file_allows_every_citation_crawler(self):
        result = run_check(NINAD_ROBOTS)
        self.assertEqual(result["summary"]["citationBlocked"], 1, by_token(result))
        # Amazonbot is the single citation crawler that file blocks; the AI
        # assistants people actually care about are all allowed.
        for token in ("OAI-SearchBot", "Claude-SearchBot", "PerplexityBot", "Googlebot", "Bingbot"):
            self.assertTrue(allowed(result, token), token)

    def test_ninads_live_file_blocks_the_training_crawlers(self):
        result = run_check(NINAD_ROBOTS)
        for token in ("GPTBot", "ClaudeBot", "Google-Extended", "CCBot",
                      "Applebot-Extended", "meta-externalagent", "Bytespider"):
            self.assertFalse(allowed(result, token), token)

    def test_training_opt_out_is_not_reported_as_citation_damage(self):
        """A training opt-out is an editorial choice, not a defect."""
        source = (
            "User-agent: *\nAllow: /\n\n"
            "User-agent: GPTBot\nDisallow: /\n\n"
            "User-agent: ClaudeBot\nDisallow: /\n\n"
            "User-agent: Google-Extended\nDisallow: /\n\n"
            "User-agent: CCBot\nDisallow: /\n\n"
            "User-agent: Applebot-Extended\nDisallow: /\n\n"
            "User-agent: meta-externalagent\nDisallow: /\n\n"
            "User-agent: Bytespider\nDisallow: /\n"
        )
        result = run_check(source)
        self.assertEqual(result["summary"]["citationBlocked"], 0)
        self.assertEqual(result["summary"]["posture"], "cite-only")
        self.assertEqual(result["summary"]["grade"], "a")

    def test_blocking_a_citation_crawler_lowers_the_grade(self):
        source = "User-agent: *\nAllow: /\n\nUser-agent: OAI-SearchBot\nDisallow: /\n"
        result = run_check(source)
        self.assertFalse(allowed(result, "OAI-SearchBot"))
        self.assertEqual(result["summary"]["citationBlocked"], 1)
        self.assertNotEqual(result["summary"]["grade"], "a")

    def test_blocking_everything_is_the_worst_grade(self):
        result = run_check("User-agent: *\nDisallow: /\n")
        self.assertEqual(result["summary"]["grade"], "f")
        self.assertEqual(result["summary"]["posture"], "closed")
        self.assertEqual(result["summary"]["citationBlocked"], result["summary"]["citationTotal"])

    def test_google_extended_is_classified_as_training_not_citation(self):
        """Blocking Google-Extended must not be read as blocking AI Overviews."""
        table = by_token(run_check("User-agent: *\nAllow: /\n"))
        self.assertEqual(table["Google-Extended"]["purpose"], "train")
        self.assertEqual(table["Googlebot"]["purpose"], "cite")
        self.assertIn("does not affect Google Search", table["Google-Extended"]["note"])

    def test_empty_file_allows_everything(self):
        result = run_check("")
        self.assertTrue(result["summary"]["fileIsEmpty"])
        self.assertEqual(result["summary"]["citationBlocked"], 0)
        self.assertEqual(result["summary"]["trainingBlocked"], 0)


@unittest.skipIf(NODE is None, "node is required to exercise the JavaScript engine")
class ReportingTests(unittest.TestCase):
    def test_explanation_names_the_governing_rule_and_line(self):
        result = run_check("User-agent: *\nDisallow: /\n")
        explanation = by_token(result)["Googlebot"]["explanation"]
        self.assertIn("Disallow: /", explanation)
        self.assertIn("line 2", explanation)

    def test_explanation_says_when_the_wildcard_group_was_used(self):
        explanation = by_token(run_check("User-agent: *\nDisallow: /\n"))["PerplexityBot"]["explanation"]
        self.assertIn('"User-agent: *"', explanation)

    def test_explanation_says_when_a_named_group_overrode_the_wildcard(self):
        source = "User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n"
        explanation = by_token(run_check(source))["GPTBot"]["explanation"]
        self.assertIn("most specific matching group", explanation)

    def test_content_signal_without_ai_input_is_reported(self):
        result = run_check(NINAD_ROBOTS)
        note = next(n for n in result["notes"] if n["id"] == "content-signal")
        self.assertIn("does not declare ai-input", note["message"])

    def test_content_signal_with_ai_input_is_reported_as_declared(self):
        source = "User-agent: *\nContent-Signal: search=yes,ai-input=yes\nAllow: /\n"
        note = next(n for n in run_check(source)["notes"] if n["id"] == "content-signal")
        self.assertIn("declares ai-input", note["message"])

    def test_sitemap_absence_is_info_not_a_problem(self):
        note = next(n for n in run_check("User-agent: *\nAllow: /\n")["notes"] if n["id"] == "no-sitemap")
        self.assertEqual(note["severity"], "info")

    def test_sitemap_presence_suppresses_the_note(self):
        source = "Sitemap: https://example.com/sitemap.xml\n\nUser-agent: *\nAllow: /\n"
        result = run_check(source)
        self.assertEqual(result["summary"]["sitemaps"], 1)
        self.assertNotIn("no-sitemap", [n["id"] for n in result["notes"]])

    def test_file_with_no_user_agent_group_is_flagged(self):
        result = run_check("Sitemap: https://example.com/sitemap.xml\n")
        self.assertIn("no-groups", [n["id"] for n in result["notes"]])

    def test_every_note_carries_a_basis(self):
        for source in ("", NINAD_ROBOTS, "Disallow: /\n"):
            for note in run_check(source)["notes"]:
                self.assertTrue(note["basis"].strip(), note["id"])
                self.assertIn(note["severity"], ("warning", "info"), note["id"])

    def test_groups_with_the_same_token_are_merged(self):
        """Real files rely on this: nytimes.com carried two "User-agent: Googlebot"
        groups when read 2026-08-17, and honouring only the first drops rules."""
        source = (
            "User-agent: Googlebot\nDisallow: /ads/\n\n"
            "User-agent: Googlebot\nDisallow: /private/\n"
        )
        self.assertFalse(allowed(run_check(source, {"path": "/ads/x"}), "Googlebot"))
        self.assertFalse(allowed(run_check(source, {"path": "/private/x"}), "Googlebot"))
        self.assertTrue(allowed(run_check(source, {"path": "/docs/x"}), "Googlebot"))

    def test_multiple_wildcard_groups_are_merged(self):
        source = "User-agent: *\nDisallow: /a/\n\nUser-agent: *\nDisallow: /b/\n"
        self.assertFalse(allowed(run_check(source, {"path": "/a/x"}), "Googlebot"))
        self.assertFalse(allowed(run_check(source, {"path": "/b/x"}), "Googlebot"))

    def test_crlf_line_endings_parse_identically(self):
        self.assertEqual(
            run_check(NINAD_ROBOTS)["summary"],
            run_check(NINAD_ROBOTS.replace("\n", "\r\n"))["summary"],
        )


if __name__ == "__main__":
    unittest.main()
