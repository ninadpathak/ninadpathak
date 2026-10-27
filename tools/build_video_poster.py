#!/usr/bin/env python3
"""Write the WebP poster for an article video from its PNG poster.

Usage: python tools/build_video_poster.py <slug> [--check]

The player shows the poster at most 672 CSS pixels wide (the prose column), so the
WebP is drawn at 1344 pixels wide, 2x that column, keeping the PNG's aspect ratio.
Quality 85 keeps the poster well under the 40 KB budget. The PNG stays as the
VideoObject thumbnailUrl. Generating needs cwebp (brew install webp); --check needs
nothing beyond Python and verifies the committed WebP: its header, its width, and
the budget.
"""
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import yaml

WIDTH = 1344
QUALITY = 85
BUDGET = 40 * 1024


def webp_size(data: bytes):
    """Return (width, height) from a WebP file's header, or None if it isn't one."""
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X":
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if chunk == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L" and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def paths(slug: str):
    meta = yaml.safe_load((Path("content/videos") / slug / "video.yaml").read_text(encoding="utf-8"))
    folder = Path("static/videos") / slug
    return meta, folder / meta["poster"], folder / meta["poster_webp"]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    slug = sys.argv[1]
    meta, png, webp = paths(slug)
    height = round(WIDTH * meta["height"] / meta["width"])
    if "--check" not in sys.argv[2:]:
        if not shutil.which("cwebp"):
            print("cwebp not found; install it with: brew install webp", file=sys.stderr)
            return 1
        subprocess.run(["cwebp", "-quiet", "-q", str(QUALITY), "-m", "6", "-resize", str(WIDTH), str(height),
                        str(png), "-o", str(webp)], check=True)
    data = webp.read_bytes() if webp.is_file() else b""
    size = webp_size(data)
    problems = []
    if size != (WIDTH, height):
        problems.append(f"expected a {WIDTH}x{height} WebP, found {size}")
    if len(data) > BUDGET:
        problems.append(f"{len(data)} bytes is over the {BUDGET}-byte budget")
    if problems:
        print(f"{webp}: " + "; ".join(problems), file=sys.stderr)
        return 1
    print(f"{webp}: {size[0]}x{size[1]}, {len(data)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
