import unittest

from ingest import read_events
from registry import get_parser
from report import seconds_between
from timeutil import parse_ts


class TimeTest(unittest.TestCase):
    def test_parse_z_suffix(self):
        self.assertEqual(parse_ts("2026-11-23T10:00:00Z").hour, 10)

    def test_parse_offset(self):
        self.assertEqual(parse_ts("2026-11-23T10:00:00+02:00").hour, 8)

    def test_read_events(self):
        events = read_events(["2026-11-23T10:00:00Z deploy\n"])
        self.assertEqual(events[0][1], "deploy")

    def test_seconds_between(self):
        self.assertEqual(seconds_between("2026-11-23T10:00:00Z", "2026-11-23T10:01:30Z"), 90)

    def test_registry(self):
        self.assertEqual(get_parser("timestamp")("2026-11-23T10:00:00Z").minute, 0)


if __name__ == "__main__":
    unittest.main()
