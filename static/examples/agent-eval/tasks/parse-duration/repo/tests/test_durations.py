import unittest

from durations import format_duration


class FormatTest(unittest.TestCase):
    def test_all_parts(self):
        self.assertEqual(format_duration(5415), "1h30m15s")

    def test_zero(self):
        self.assertEqual(format_duration(0), "0s")


if __name__ == "__main__":
    unittest.main()
