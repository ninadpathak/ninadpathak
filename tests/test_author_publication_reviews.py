import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tools.content_inventory_gate import apply_author_reviews

class AuthorPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.posts = Path(self.temp.name)
        self.note = self.posts / "essay.md"
        self.note.write_text("---\nstatus: published\n---\nAn essay.\n")
        self.record = {"state": "PROVISIONAL_REVIEW", "status": "published", "sha256": hashlib.sha256(self.note.read_bytes()).hexdigest(), "approved_at": "2026-10-04T10:00:00Z", "approval_source": "obsidian_author_confirmation"}
        self.reviews = self.posts / "reviews.json"
    def apply(self, name="essay.md"):
        self.reviews.write_text(json.dumps({name: self.record}))
        return apply_author_reviews({"other.md": "PHASE_A_EDITED", "essay.md": "PHASE_A_EDITED"}, self.posts, self.reviews)
    def test_exact_revision_approval(self):
        self.assertEqual(self.apply()["essay.md"], "PROVISIONAL_REVIEW")
    def test_changed_revision_rejected(self):
        self.note.write_text(self.note.read_text() + "Another sentence.")
        with self.assertRaises(ValueError): self.apply()
    def test_draft_removes_only_selected_inventory_row(self):
        self.note.write_text("---\nstatus: draft\n---\nPrivate essay.\n")
        self.record.update(status="draft", sha256=hashlib.sha256(self.note.read_bytes()).hexdigest())
        self.assertEqual(self.apply(), {"other.md": "PHASE_A_EDITED"})
    def test_invalid_approval_fields_rejected(self):
        for key, value in [("approval_source", "automatic"), ("state", "approved"), ("status", "deleted"), ("sha256", "bad"), ("approved_at", "2026-10-04T10:00:00")]:
            with self.subTest(key=key):
                original = self.record[key]; self.record[key] = value
                with self.assertRaises(ValueError): self.apply()
                self.record[key] = original
    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError): self.apply("../essay.md")
    def test_status_mismatch_rejected(self):
        self.record["status"] = "draft"
        with self.assertRaises(ValueError): self.apply()
