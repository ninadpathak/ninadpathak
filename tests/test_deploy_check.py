"""The deploy check must tell "not deployed yet" apart from "deployed wrong".

Cloudflare Pages serialises builds, so production legitimately trails main for a few
minutes after a push. On 2026-08-17 a mismatch read mid-deploy was treated as a build
failure, and the false alarm cost more time than a real failure would have — two stale
reads agreed with each other and the agreement was mistaken for confirmation.

So the check reports WAITING inside a grace window and ALARM past it, and the clock
starts from the newest commit that changed something the build actually renders. A
documentation-only commit must not start that clock, or every campaign-doc edit reports
a phantom deploy lag.
"""
import importlib.util
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("daily_cycle", ROOT / "tools" / "daily_cycle.py")
daily_cycle = importlib.util.module_from_spec(spec)
sys.modules["daily_cycle"] = daily_cycle
spec.loader.exec_module(daily_cycle)


class DeployLineTests(unittest.TestCase):
    def test_no_problems_reads_as_live(self):
        line = daily_cycle._deploy_line([], False, 120)
        self.assertIn("LIVE", line)
        self.assertNotIn("ALARM", line)

    def test_mismatch_inside_grace_window_is_waiting_not_alarm(self):
        line = daily_cycle._deploy_line(["sitemap 142 vs 144"], True, 300)
        self.assertIn("WAITING", line)
        self.assertIn("not an alarm", line)
        self.assertNotIn("ALARM", line)
        self.assertIn("5m since the last rendering commit", line)

    def test_mismatch_past_grace_window_is_an_alarm(self):
        line = daily_cycle._deploy_line(["sitemap 142 vs 144"], False, 3600)
        self.assertIn("ALARM", line)
        self.assertIn("past the grace window", line)
        self.assertIn("60m since the last rendering commit", line)

    def test_unknown_lag_is_reported_not_hidden(self):
        line = daily_cycle._deploy_line(["sitemap mismatch"], False, None)
        self.assertIn("unknown age", line)

    def test_grace_window_is_a_named_constant(self):
        self.assertGreaterEqual(daily_cycle.DEPLOY_GRACE_SECONDS, 60)


class DeployLagTests(unittest.TestCase):
    def test_lag_is_none_or_a_non_negative_int(self):
        """Runs against the real repo, so it asserts the shape rather than a value."""
        lag = daily_cycle.deploy_lag_seconds()
        self.assertTrue(lag is None or (isinstance(lag, int) and lag >= 0), lag)

    def test_rendering_paths_are_the_ones_that_matter(self):
        """A guard on intent: docs and planning must not start the deploy clock."""
        source = (ROOT / "tools" / "daily_cycle.py").read_text(encoding="utf-8")
        for path in ("content/", "templates/", "static/", "functions/", "build.py"):
            self.assertIn(path, source, f"{path} should count as a rendering change")
        # These would produce phantom lag on every campaign-document edit.
        self.assertNotIn('"planning/"', source)
        self.assertNotIn('"campaign-90d.md"', source)


class PublishGateOrderTests(unittest.TestCase):
    def test_build_precedes_every_check_that_reads_generated_output(self):
        events = []

        def run(*command, **_kwargs):
            if command[-1] == "build.py":
                events.append("build")
                return 0, "SEO audit passed"
            return 0, ""

        def shadowing():
            events.append("redirects")
            return []

        def stylesheets():
            events.append("stylesheets")
            return []

        with mock.patch.object(daily_cycle, "run", side_effect=run), \
             mock.patch.object(daily_cycle, "shadowing_redirects", side_effect=shadowing), \
             mock.patch.object(daily_cycle, "unstyled_pages", side_effect=stylesheets), \
             mock.patch.object(daily_cycle, "url_inventory_check", return_value=([], "")):
            self.assertEqual(daily_cycle.publish_gate(), [])

        self.assertLess(events.index("build"), events.index("redirects"))
        self.assertLess(events.index("build"), events.index("stylesheets"))


if __name__ == "__main__":
    unittest.main()
