#!/usr/bin/env python3
"""Apply the house two-sentence paragraph rule to existing posts.

`build.py` refuses to publish any post whose prose paragraphs run longer than two
sentences. Posts written before that rule landed fail it in bulk, which is why the
April-May article set sat at `status: retired` instead of being reformatted.

This wraps `rule_checker.format_two_sentence_paragraphs`, which is a pure structural
transformation: it regroups existing sentences and never rewrites, adds, or removes
prose. Code fences, HTML blocks, and comments pass through untouched.

    tools/reflow_paragraphs.py content/posts/*.md      # rewrite in place
    tools/reflow_paragraphs.py --check content/posts/*.md   # report only
"""
import argparse
import pathlib
import sys

import frontmatter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from rule_checker import format_two_sentence_paragraphs, paragraph_sentence_violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    parser.add_argument("--check", action="store_true",
                        help="report violations without writing")
    args = parser.parse_args()

    failed = 0
    for path in args.paths:
        post = frontmatter.load(path)
        before = paragraph_sentence_violations(post.content)
        if not before:
            continue

        if args.check:
            print(f"{path}: {len(before)} violation(s)")
            failed += 1
            continue

        post.content = format_two_sentence_paragraphs(post.content)
        after = paragraph_sentence_violations(post.content)
        if after:
            # The formatter could not split these, so a human has to. Report the
            # residue rather than writing a file that will still fail the build.
            print(f"{path}: UNFIXABLE, {len(after)} violation(s) remain")
            for line, count, snippet in after:
                print(f"    line {line}: {count} sentences — {snippet[:90]}")
            failed += 1
            continue

        path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
        print(f"{path}: reflowed {len(before)} paragraph(s)")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
