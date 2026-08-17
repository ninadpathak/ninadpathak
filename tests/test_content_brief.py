"""Contract tests for the queue-to-prepared-brief guard."""
from __future__ import annotations

import csv
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "check_content_brief.py"


class ContentBriefGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tmp.name)
        self.queue = root / "queue.csv"
        self.briefs = root / "briefs"
        self.briefs.mkdir()
        self.row = {
            "Order": "20",
            "Release Date": "2026-08-18",
            "Title": "Code Documentation: Comments, Generated Reference, and External Guides",
            "Cluster": "Documentation",
            "Subcluster": "Documentation formats",
            "Experience": "A",
            "Status": "In Progress",
        }
        self.write_queue([self.row])

    def tearDown(self):
        self.tmp.cleanup()

    def write_queue(self, rows):
        with self.queue.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.row.keys())
            writer.writeheader()
            writer.writerows(rows)

    def write_brief(self, name="brief-test.md", *, title=None, cluster="Documentation",
                    subcluster=None, experience="A", order="20", date="2026-08-18"):
        sub = f" | **Subcluster:** {subcluster}" if subcluster is not None else ""
        text = (
            f"# Brief: {title or self.row['Title']}\n\n"
            f"**Slot:** {date} | Order {order} | **Cluster:** {cluster}{sub}\n"
            f"**Experience: {experience}**\n\n## Reader task\nDo the task.\n"
        )
        (self.briefs / name).write_text(text, encoding="utf-8")

    def run_tool(self):
        return subprocess.run(
            [sys.executable, str(TOOL), "--queue", str(self.queue), "--order", "20",
             "--brief-root", str(self.briefs)],
            text=True, capture_output=True, check=False,
        )

    def test_matching_brief_passes_when_optional_subcluster_is_absent(self):
        self.write_brief()
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("BRIEF OK: order 20", result.stdout)

    def test_wrapped_cluster_and_matching_subcluster_pass(self):
        self.write_brief(cluster="AI agents, memory,\nRAG, inference",
                         subcluster="AI-ready documentation")
        self.row.update({"Cluster": "AI agents, memory, RAG, inference",
                         "Subcluster": "AI-ready documentation"})
        self.write_queue([self.row])
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fixed_field_mismatch_refuses(self):
        self.write_brief(cluster="Retired cluster")
        result = self.run_tool()
        self.assertEqual(result.returncode, 2)
        self.assertIn("cluster: queue='Documentation', brief='Retired cluster'", result.stdout)

    def test_declared_subcluster_may_not_contradict_queue(self):
        self.write_brief(subcluster="Wrong lane")
        result = self.run_tool()
        self.assertEqual(result.returncode, 2)
        self.assertIn("subcluster", result.stdout)

    def test_missing_brief_refuses(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 2)
        self.assertIn("matched 0 files", result.stdout)

    def test_duplicate_brief_refuses(self):
        self.write_brief("brief-a.md")
        self.write_brief("brief-b.md")
        result = self.run_tool()
        self.assertEqual(result.returncode, 2)
        self.assertIn("matched 2 files", result.stdout)

    def test_queue_order_must_be_unique(self):
        self.write_brief()
        self.write_queue([self.row, self.row])
        result = self.run_tool()
        self.assertEqual(result.returncode, 2)
        self.assertIn("queue order 20 matched 2 rows", result.stdout)


if __name__ == "__main__":
    unittest.main()
