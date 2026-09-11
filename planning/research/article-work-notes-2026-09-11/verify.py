"""Reproducible coverage/preservation evidence; not semantic approval."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import frontmatter
from build import SiteBuilder, render_work_note

BASE = "60909b2c"
digest = lambda data: hashlib.sha256(data).hexdigest()
mapping = {row["source"]: row for row in json.loads((HERE / "note-review-map.json").read_text())}
rendered = {p["source_stem"]: p for p in SiteBuilder().load_posts()}
records = []
for path in sorted((ROOT / "content/posts").glob("*.md")):
    name = str(path.relative_to(ROOT))
    raw = path.read_bytes()
    old = subprocess.check_output(["git", "show", BASE + ":" + name], cwd=ROOT)
    post = frontmatter.loads(raw.decode())
    if post.get("status") != "published":
        assert raw == old, name
        continue
    stripped = re.sub(rb"^work_note: .*\n", b"", raw, flags=re.M)
    assert stripped == old, name
    note = post["work_note"]
    assert mapping[name]["note"] == note, name
    plain = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", note)
    assert not re.search(r"\b(easy|easier|easily|most|mostly|ever|leverage|leveraging|delve|seamless|unlock|empower|elevate)\b", plain, re.I), name
    data = rendered[path.stem]
    html = (ROOT / "output" / data["url"].strip("/") / "index.html").read_text()
    expected = render_work_note(note)
    assert html.count('class="article-work-note"') == 1, name
    assert expected in html, name
    assert re.search(r'class="article-work-note"[^>]*>\s*<p>' + re.escape(expected) + r'</p>\s*</aside>\s*<div class="post-content">', html), name
    assert data["content"] in html, name
    assert 'href="/static/css/main.css?v=article-work-notes-1"' in html, name
    records.append({"source": name, "url": data["url"], "baseline_sha256": digest(old),
                    "current_sha256": digest(raw), "body_and_old_metadata_unchanged": True,
                    "word_count": len(plain.split()), "note": note, "rendered_note": expected})
assert len(records) == len(mapping) == 67
assert len(set(r["note"] for r in records)) == 67
archive = ROOT / "planning/research/zero-impression-cleanup-2026-09-11/archived-posts"
for path in archive.glob("*.md"):
    name = str(path.relative_to(ROOT))
    assert path.read_bytes() == subprocess.check_output(["git", "show", BASE + ":" + name], cwd=ROOT)
protected = json.loads((archive.parent / "protected-sha256.json").read_text())
for name, expected in protected.items():
    assert digest((ROOT / name).read_bytes()) == expected, name
report = {"baseline": BASE, "published": len(records), "unique_notes": len(records),
          "archived_unchanged": 20, "protected_unchanged": protected,
          "word_range": [min(r["word_count"] for r in records), max(r["word_count"] for r in records)],
          "records": records}
(HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"PASS: 67 unique notes, body/metadata preserved; 20 archives and {len(protected)} protected files unchanged; words {report['word_range']}")
