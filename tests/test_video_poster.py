import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location("build_video_poster", "tools/build_video_poster.py")
poster = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poster)


def fake_cwebp(sizes):
    """A subprocess.run stand-in: writes a file whose size depends on (quality, width)
    and records each call's setting."""
    calls = []

    def run(cmd, check):
        quality, width = int(cmd[cmd.index("-q") + 1]), int(cmd[cmd.index("-resize") + 1])
        calls.append((quality, width))
        Path(cmd[cmd.index("-o") + 1]).write_bytes(bytes(sizes(quality, width)))
    return run, calls


class EncodeFallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.png, self.webp = self.tmp / "poster.png", self.tmp / "poster.webp"

    def encode(self, sizes):
        run, calls = fake_cwebp(sizes)
        with mock.patch.object(poster.subprocess, "run", run):
            result = poster.encode(self.png, self.webp, 1080 / 1920)
        return result, calls

    def test_a_poster_that_fits_keeps_full_width_and_quality(self):
        result, calls = self.encode(lambda q, w: 20_000)
        self.assertEqual(result, (85, 1344))
        self.assertEqual(calls, [(85, 1344)])

    def test_quality_steps_down_before_any_downscale(self):
        result, calls = self.encode(lambda q, w: 50_000 if q > 70 else 40_000)
        self.assertEqual(result, (70, 1344))
        self.assertEqual(calls, [(85, 1344), (80, 1344), (75, 1344), (70, 1344)])
        self.assertLessEqual(self.webp.stat().st_size, poster.BUDGET)

    def test_downscales_only_after_every_quality_at_full_width_misses(self):
        result, calls = self.encode(lambda q, w: 30_000 if (w, q) == (1200, 80) else 50_000)
        self.assertEqual(result, (80, 1200))
        self.assertEqual(calls[:6], [(q, 1344) for q in poster.QUALITIES])
        self.assertEqual(calls[6:], [(85, 1200), (80, 1200)])

    def test_never_goes_below_the_legibility_floor(self):
        result, calls = self.encode(lambda q, w: 50_000)
        self.assertEqual(result, (60, 1088))
        self.assertEqual(len(calls), len(poster.WIDTHS) * len(poster.QUALITIES))
        self.assertTrue(all(q >= 60 and w >= 1088 for q, w in calls))
        # The floor keeps the poster above 1.6x the 672-pixel prose column.
        self.assertGreaterEqual(min(poster.WIDTHS), 672 * 1.6)


@unittest.skipUnless(shutil.which("cwebp"), "cwebp not installed")
class BuildPosterTests(unittest.TestCase):
    """Runs the real tool in a scratch site so --check and the printed setting are covered."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        (self.tmp / "content/videos/demo").mkdir(parents=True)
        (self.tmp / "content/videos/demo/video.yaml").write_text(
            "width: 1920\nheight: 1080\nposter: poster.png\nposter_webp: poster.webp\n")
        (self.tmp / "static/videos/demo").mkdir(parents=True)
        self.tool = Path("tools/build_video_poster.py").resolve()

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(self.tool), "demo", *args], cwd=self.tmp,
                              capture_output=True, text=True)

    def write_png(self, noisy):
        # Random noise cannot fit the budget at any setting; a flat frame fits at once.
        code = ("import random,struct,zlib,sys\n"
                "w,h=1920,1080\n"
                f"noisy={noisy}\n"
                "rows=b''.join(b'\\0'+(random.randbytes(w*3) if noisy else bytes([240])*w*3) for _ in range(h))\n"
                "def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d))\n"
                "sys.stdout.buffer.write(b'\\x89PNG\\r\\n\\x1a\\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))"
                "+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))\n")
        png = subprocess.run([sys.executable, "-c", code], capture_output=True, check=True).stdout
        (self.tmp / "static/videos/demo/poster.png").write_bytes(png)

    def test_a_simple_frame_prints_its_setting_and_passes_check(self):
        self.write_png(noisy=False)
        built = self.run_tool()
        self.assertEqual(built.returncode, 0, built.stderr)
        self.assertRegex(built.stdout, r"1344x756, quality 85, \d+ bytes")
        self.assertEqual(self.run_tool("--check").returncode, 0)

    def test_a_frame_that_misses_at_the_floor_fails(self):
        self.write_png(noisy=True)
        built = self.run_tool()
        self.assertEqual(built.returncode, 1)
        self.assertIn("over the 40960-byte budget (at the floor, quality 60)", built.stderr)
        self.assertEqual(self.run_tool("--check").returncode, 1)


if __name__ == "__main__":
    unittest.main()
