"""Guard the claim scanner's contract, because CI now gates on its output.

The scanner is the only automatic check standing between a new Hermes article and
production, since Hermes pushes straight to main. Two properties matter more than its
recall: `--paths` with no values must mean "no posts" rather than "every post", and the
count line must stay machine-readable, because CI parses it to compare a changed post
against its previous version.

An earlier revision got the first one wrong: an empty `--paths` fell through to a full
scan and reported 118 candidates for zero files, which would have made the regression
check compare the whole site against one file and report a number that means nothing.
"""
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "audit_claims.py"
COUNT = re.compile(r"^(\d+) candidate claim", re.M)


def run(*args):
    result = subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=ROOT, capture_output=True, text=True)
    return result.returncode, result.stdout


class AuditClaimsContractTests(unittest.TestCase):
    def test_empty_paths_means_no_posts(self):
        code, out = run("--paths")
        self.assertEqual(code, 0)
        match = COUNT.search(out)
        self.assertIsNotNone(match, out)
        self.assertEqual(match.group(1), "0",
                         "empty --paths must scan nothing, not everything")

    def test_count_line_is_machine_readable(self):
        code, out = run()
        self.assertEqual(code, 0)
        self.assertIsNotNone(COUNT.search(out), "CI parses this line; keep its shape")

    def test_a_nonexistent_path_does_not_crash(self):
        code, out = run("--paths", "content/posts/definitely-not-a-real-post.md")
        self.assertEqual(code, 0)
        self.assertEqual(COUNT.search(out).group(1), "0")

    def test_scanner_reports_candidates_not_verdicts(self):
        """The wording is load-bearing: a hit is for a reviewer to classify."""
        code, out = run()
        self.assertIn("candidate, not a verdict", out)

    def test_first_person_judgment_is_not_flagged(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("audit_claims", TOOL)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        # Judgment Ninad has earned must pass; an action claim must not.
        self.assertEqual(module.classify("What I look for first is the failure mode."), [])
        self.assertEqual(module.classify("I think reference pages age worst."), [])
        self.assertTrue(module.classify("I measured 40ms on an RTX 4090."))
        self.assertTrue(module.classify("I ran the checker against the fixture."))


class NavigationSuppressionTests(unittest.TestCase):
    """36 of 118 candidates were false positives, clustered into three shapes.

    Headings, FAQ questions and reading-list bullets match the patterns syntactically
    while asserting nothing. Suppressing them is what keeps a reviewer's time on real
    claims rather than on navigation.
    """

    @classmethod
    def setUpClass(cls):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("audit_claims_nav", TOOL)
        cls.mod = module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_headings_are_navigation(self):
        self.assertTrue(self.mod._is_navigation("## What I Found Works"))
        self.assertTrue(self.mod._is_navigation("### The Failure Modes I Check"))

    def test_faq_questions_are_navigation(self):
        self.assertTrue(self.mod._is_navigation("Can I run this locally?"))
        self.assertTrue(self.mod._is_navigation("How did I measure 40ms?"))

    def test_reading_list_bullet_is_navigation(self):
        self.assertTrue(self.mod._is_navigation(
            "- [open-source AI memory review](/articles/state-of-open-source-memory-2026/) — an architecture survey"))

    def test_a_real_claim_in_prose_is_not_navigation(self):
        self.assertFalse(self.mod._is_navigation(
            "I measured this on a Llama 3.1 8B model running locally."))
        self.assertFalse(self.mod._is_navigation(
            "I ran the checker against the included fixture and it returned PASS."))

    def test_a_claim_that_merely_mentions_a_link_is_not_suppressed(self):
        """A sentence using a link as proof must still be flagged."""
        self.assertFalse(self.mod._is_navigation(
            "That is exactly what I tested in my [head-to-head benchmark](/articles/agentic-cli-benchmarks/), "
            "which showed the smaller model winning on repository-level edits."))


class ReviewerIdentifiedRefinementTests(unittest.TestCase):
    """Two refinements the reviewer named after classifying 118 candidates by hand.

    Both are narrow on purpose. The valuable property is that an FAQ *answer* is still
    scanned while its question is not — suppressing the whole block would hide real claims
    behind a question mark.
    """

    @classmethod
    def setUpClass(cls):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("audit_claims_refine", TOOL)
        cls.mod = module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def flagged(self, line):
        return bool(self.mod.classify(line)) and not self.mod._is_navigation(line)

    def test_inline_code_is_quoted_not_asserted(self):
        self.assertFalse(self.flagged("Run `I ran the checker` to reproduce it."))

    def test_bold_faq_question_is_suppressed(self):
        self.assertTrue(self.mod._is_navigation("**Can I run this offline?**"))

    def test_the_faq_answer_is_still_scanned(self):
        self.assertTrue(self.flagged("Yes. I ran it offline against the fixture and it passed."))

    def test_real_claims_survive_both_refinements(self):
        self.assertTrue(self.flagged("I measured 40ms on an RTX 4090."))
        self.assertTrue(self.flagged("I built the checker on this site."))

    def test_a_claim_beside_inline_code_still_counts(self):
        """Stripping code spans must not smuggle the surrounding claim out with them."""
        self.assertTrue(self.flagged("I measured 40ms running `npm test` on an RTX 4090."))


class ExperienceClaimTests(unittest.TestCase):
    """Experience asserted without the words "I did" was invisible to the scanner.

    The opening line of the highest-human-demand page on the site — "Two years of running AI
    agents in production taught me that..." — scored zero candidates, because the
    first-person-verb pattern only matches "I <verb>". A duration or a scale attached to
    personal experience is the same falsifiable claim, phrased around the verb instead of
    through it. Closing the gap took candidates from 50 to 83.
    """

    @classmethod
    def setUpClass(cls):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("audit_claims_exp", TOOL)
        cls.mod = module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def flagged(self, line):
        return bool(self.mod.classify(line))

    def test_duration_plus_taught_me_is_a_claim(self):
        self.assertTrue(self.flagged(
            "Two years of running AI agents in production taught me that error handling matters."))

    def test_in_my_experience_is_a_claim(self):
        self.assertTrue(self.flagged("In my experience the reference page ages worst."))

    def test_a_duration_about_something_else_is_not_a_claim(self):
        """The distinction that keeps the detector usable.

        A span of time is only an experience claim when it is someone's own span.
        """
        self.assertFalse(self.flagged("The model takes three years of training data."))
        self.assertFalse(self.flagged("A benchmark over six months of logs shows the drift."))

    def test_a_duration_with_a_first_person_marker_is_a_claim(self):
        self.assertTrue(self.flagged("I spent six months of evenings on the linter."))

    def test_first_person_duration_without_of_is_a_claim(self):
        self.assertTrue(self.flagged(
            "I spent three weeks debugging a retrieval pipeline."))

    def test_possessive_experience_is_a_claim(self):
        self.assertTrue(self.flagged(
            "Across my own testing, lexical retrieval improved recall."))

    def test_have_debugged_is_a_claim(self):
        self.assertTrue(self.flagged(
            "Every agent memory system I have debugged had the same problem."))

    def test_indirect_experience_phrasings_are_claims(self):
        self.assertTrue(self.flagged("There is a second failure I keep hitting."))
        self.assertTrue(self.flagged("A support agent I was working on made this concrete."))
        self.assertTrue(self.flagged("The failure I see most often happens after a demo."))
        self.assertTrue(self.flagged(
            "Three patterns have consistently worked for me in retrieval."))
        self.assertTrue(self.flagged(
            "Concretely, that has meant adding a query expansion step."))
        self.assertTrue(self.flagged("The actual fix was preserving the error term."))

    def test_stated_judgment_is_still_not_flagged(self):
        """my approach / my focus are positions, not events."""
        self.assertFalse(self.flagged("My approach is to keep it short."))
        self.assertFalse(self.flagged("My focus is LLM-based agents that call tools."))


if __name__ == "__main__":
    unittest.main()
