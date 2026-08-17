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


if __name__ == "__main__":
    unittest.main()
