import io
import pathlib
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import statuscount

LINE = '203.0.113.7 - - [23/Nov/2026:09:14:02 +0000] "GET / HTTP/1.1" {} 512\n'


class StatusOfTest(unittest.TestCase):
    def test_reads_the_code_after_the_request(self):
        self.assertEqual(statuscount.status_of(LINE.format(404)), 404)

    def test_line_without_a_request_has_no_status(self):
        self.assertIsNone(statuscount.status_of("not a log line\n"))


class CountStatusesTest(unittest.TestCase):
    def test_orders_rows_by_count_then_status_code(self):
        lines = [LINE.format(code) for code in (500, 200, 404, 500, 500, 200)]
        self.assertEqual(statuscount.count_statuses(lines), [(500, 3), (200, 2), (404, 1)])

    def test_min_status_drops_lower_codes(self):
        lines = [LINE.format(code) for code in (200, 301, 404)]
        self.assertEqual(statuscount.count_statuses(lines, 400), [(404, 1)])


class MainTest(unittest.TestCase):
    def test_missing_file_exits_with_status_2(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = statuscount.main(["no-such-file.log"])
        self.assertEqual(code, 2)
        self.assertEqual(err.getvalue(), "statuscount: cannot read no-such-file.log\n")


if __name__ == "__main__":
    unittest.main()
