#!/usr/bin/env python3

import json
import subprocess
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG = json.loads((SCRIPT_DIR / "assignments.json").read_text())
REPO_ROOT = Path(CONFIG["repo_root"])
STATE_DIR = SCRIPT_DIR / "state"
PASS_DIR = STATE_DIR / "passed"
BUILD_DONE = STATE_DIR / "build.done"
BUILD_LOG = STATE_DIR / "logs" / "build.log"


def all_slugs():
    for lane in CONFIG["lanes"].values():
        for assignment in lane:
            yield assignment["slug"]


def main():
    BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)
    slugs = list(all_slugs())

    while True:
        if all((PASS_DIR / f"{slug}.pass").exists() for slug in slugs):
            with BUILD_LOG.open("w", encoding="utf-8") as log_file:
                proc = subprocess.run(
                    ["python3", "build.py"],
                    cwd=REPO_ROOT,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
            BUILD_DONE.write_text(f"build_exit_code={proc.returncode}\n", encoding="utf-8")
            return
        time.sleep(15)


if __name__ == "__main__":
    main()
