#!/usr/bin/env python3

import json
import subprocess
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
REPORT_DIR = STATE_DIR / "editor_reports"


def ensure_state_dirs():
    for path in [LOG_DIR, READY_DIR, PASS_DIR, REVISION_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def run_codex(prompt: str, slug: str) -> int:
    log_path = LOG_DIR / f"{slug}.editor.log"
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


def build_prompt(title: str, slug: str) -> str:
    personal_skill = CONFIG["skill_paths"]["personal_blog_writer"]
    seo_skill = CONFIG["skill_paths"]["seo_blog_writer"]
    file_path = REPO_ROOT / "content" / "posts" / f"{slug}.md"
    pass_marker = PASS_DIR / f"{slug}.pass"
    revision_marker = REVISION_DIR / f"{slug}.txt"
    ready_marker = READY_DIR / f"{slug}.ready"
    report_path = REPORT_DIR / f"{slug}.md"

    return f"""You are the editor for a catch-up publishing run on ninadpathak.com.

Read and follow these skill files before you do anything else:
- {personal_skill}
- {seo_skill}

Review this article:
- Title: {title}
- File: {file_path}

Hard constraints to enforce:
- Zero fluff
- Zero em dashes
- Zero contrastive parallelism
- No cliches
- No sentence should start with `In`, `This`, `By`, `Finally`, `Most`, or `Ever`
- High specificity only
- No vague statements
- First-person voice throughout
- External links only to official docs, papers, standards, or official company sources

Decision rule:
- If the article is close to passing, edit the article directly until it passes.
- If the article lacks research depth, weakens claims with poor sourcing, or needs structural rework that the writer should handle, do not rewrite the whole piece yourself. Create a revision request instead.

Required side effects:
1. Write an editorial report to {report_path}.
2. If the article passes after your review, remove {ready_marker} if it exists and write `pass` to {pass_marker}.
3. If the article must be revised by the writer, remove {ready_marker} if it exists and write a precise revision brief to {revision_marker}.

Your report must include:
- pass or reject
- exact issues found
- what you changed, if anything
- whether the article is ready for site build

Do not build the site.
"""


def all_assignments():
    for lane in CONFIG["lanes"].values():
        for assignment in lane:
            yield assignment


def main():
    ensure_state_dirs()
    assignments = list(all_assignments())

    while True:
        remaining = []
        for assignment in assignments:
            slug = assignment["slug"]
            if (PASS_DIR / f"{slug}.pass").exists():
                continue
            remaining.append(assignment)
            ready_marker = READY_DIR / f"{slug}.ready"
            if not ready_marker.exists():
                continue
            run_codex(build_prompt(assignment["title"], slug), slug)

        if not remaining:
            return
        time.sleep(10)


if __name__ == "__main__":
    main()
