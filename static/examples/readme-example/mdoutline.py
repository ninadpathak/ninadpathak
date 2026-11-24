"""Print the heading outline of a Markdown file."""
import argparse
import re
import sys
from pathlib import Path

__version__ = "0.2.0"

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")


def outline(text, max_level=6):
    """Return (line number, level, title) for each heading outside fenced code blocks.

    A line such as "# install the package" inside a fenced block is a shell comment,
    so the fence state is tracked and those lines are skipped.
    """
    found = []
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = FENCE.match(line)
        if marker:
            kind = marker.group(1)[0]
            if fence is None:
                fence = kind
            elif fence == kind:
                fence = None
            continue
        if fence:
            continue
        heading = HEADING.match(line)
        if heading and len(heading.group(1)) <= max_level:
            found.append((number, len(heading.group(1)), heading.group(2)))
    return found


def render(headings):
    """Format headings as "line  title", indented two spaces per level below the first."""
    return "\n".join(f"{number:>4}  {'  ' * (level - 1)}{title}" for number, level, title in headings)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mdoutline", description=__doc__)
    parser.add_argument("file", help="path to a Markdown file")
    parser.add_argument("--max-level", type=int, default=6, metavar="N",
                        help="deepest heading level to print, 1 to 6 (default: 6)")
    parser.add_argument("--version", action="version", version=f"mdoutline {__version__}")
    args = parser.parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        print(f"mdoutline: no such file: {path}", file=sys.stderr)
        return 1
    headings = outline(path.read_text(encoding="utf-8"), args.max_level)
    if headings:
        print(render(headings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
