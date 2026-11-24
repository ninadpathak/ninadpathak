import hashlib
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class VendorTest(unittest.TestCase):
    def test_vendored_files_match_checksums(self):
        for line in (ROOT / "vendor" / "CHECKSUMS").read_text().splitlines():
            expected, name = line.split()
            actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, f"{name} was edited")


if __name__ == "__main__":
    unittest.main()
