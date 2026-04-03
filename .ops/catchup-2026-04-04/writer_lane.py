#!/usr/bin/env python3

import json
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG = json.loads((SCRIPT_DIR / "assignments.json").read_text())
REPO_ROOT = Path(CONFIG["repo_root"])
STATE_DIR = SCRIPT_DIR / "state"
LOG_DIR = STATE_DIR / "logs"
READY_DIR = STATE_DIR / "draft_ready"
PASS_DIR = STATE_DIR / "passed"
REVISION_DIR = STATE_DIR / "revision_requests"
DONE_DIR = STATE_DIR / "writer_done"


def ensure_state_dirs():
    for path in [LOG_DIR, READY_DIR, PASS_DIR, REVISION_DIR, DONE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def target_file(slug: str) -> Path:
    return REPO_ROOT / "content" / "posts" / f"{slug}.md"


def marker(dir_path: Path, slug: str, suffix: str) -> Path:
    return dir_path / f"{slug}.{suffix}"


def run_codex(prompt: str, slug: str, attempt: str) -> int:
    log_path = LOG_DIR / f"{slug}.{attempt}.log"
    with log_path.open("w", encoding="utf-8") as log_file:
        proc = subprocess.run(
            [
                "codex",
                "exec",
                "-C",
                str(REPO_ROOT),
                "-m",
                "gpt-5.4",
                "--dangerously-bypass-approvals-and-sandbox",
                "-",
            ],
            input=prompt,
            text=True,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return proc.returncode


def build_prompt(assignment: dict, revision_notes: str | None) -> str:
    personal_skill = CONFIG["skill_paths"]["personal_blog_writer"]
    seo_skill = CONFIG["skill_paths"]["seo_blog_writer"]
    file_path = target_file(assignment["slug"])

    prompt = f"""You are a writer working on ninadpathak.com.

Read and follow these skill files before you do anything else:
- {personal_skill}
- {seo_skill}

Assignment:
- Title: {assignment["title"]}
- File: {file_path}
- Publish date: {assignment["date"]}
- Status: published
- Length target: 1500-3500 words

Hard constraints:
- Zero fluff
- Zero em dashes
- Zero contrastive parallelism
- No cliches
- No sentence should ever start with `In`, `This`, `By`, `Finally`, `Most`, or `Ever`
- High specificity only
- No vague statements
- First-person voice throughout
- External links only to official docs, papers, standards, or official company sources
- Internal links to relevant existing ninadpathak.com articles only

Workflow:
1. Research thoroughly before writing. Use official docs, papers, standards, and official company sources. Use shell tools like curl if you need to fetch sources directly.
2. Draft directly into the target file with valid frontmatter.
3. Do a developmental self-edit pass before finishing.
4. Append a short HTML comment at the bottom with:
   - primary keyword
   - sources used
   - research gap identified
   - self-identified risks or weak spots
5. Do not build the site.
6. Do not modify any other article file.

Quality bar:
- Deeply researched
- SEO useful
- Structurally clean
- Natural internal links
- No fake claims
- No placeholder citations
"""

    if revision_notes:
        prompt += f"""

You are revising a previously rejected draft. Address these editorial notes precisely:

{revision_notes}

Keep the same file path and frontmatter. Strengthen research depth where asked.
"""

    return prompt


def wait_for_editor(slug: str):
    ready_marker = marker(READY_DIR, slug, "ready")
    pass_marker = marker(PASS_DIR, slug, "pass")
    revision_marker = marker(REVISION_DIR, slug, "txt")

    while True:
        if pass_marker.exists():
            marker(DONE_DIR, slug, "done").write_text("passed\n", encoding="utf-8")
            return "passed"
        if revision_marker.exists():
            return "revise"
        if not ready_marker.exists() and not pass_marker.exists() and not revision_marker.exists():
            time.sleep(5)
            continue
        time.sleep(5)


def main():
    ensure_state_dirs()

    if len(sys.argv) != 2 or sys.argv[1] not in CONFIG["lanes"]:
        print("usage: writer_lane.py <writer1|writer2|writer3>", file=sys.stderr)
        sys.exit(2)

    lane = sys.argv[1]
    assignments = CONFIG["lanes"][lane]

    for assignment in assignments:
        slug = assignment["slug"]
        pass_marker = marker(PASS_DIR, slug, "pass")
        if pass_marker.exists():
            marker(DONE_DIR, slug, "done").write_text("passed\n", encoding="utf-8")
            continue

        revision_marker = marker(REVISION_DIR, slug, "txt")
        ready_marker = marker(READY_DIR, slug, "ready")

        revision_notes = None
        attempt = 1
        while True:
            if revision_marker.exists():
                revision_notes = revision_marker.read_text(encoding="utf-8")
                revision_marker.unlink()
            elif target_file(slug).exists() and ready_marker.exists():
                result = wait_for_editor(slug)
                if result == "passed":
                    break
                if result == "revise":
                    continue

            returncode = run_codex(build_prompt(assignment, revision_notes), slug, f"attempt{attempt}")
            attempt += 1
            if returncode != 0:
                time.sleep(10)
                continue

            ready_marker.write_text("ready\n", encoding="utf-8")
            result = wait_for_editor(slug)
            if result == "passed":
                break
            revision_notes = None


if __name__ == "__main__":
    main()
