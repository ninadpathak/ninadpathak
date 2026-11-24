import unittest

from app import config
from app.client import fetch


class ClientTest(unittest.TestCase):
    def test_default_timeout_comes_from_config(self):
        self.assertEqual(fetch("https://status.example/api")["timeout"], config.REQUEST_TIMEOUT)

    def test_override(self):
        self.assertEqual(fetch("https://status.example/api", timeout=5)["timeout"], 5)


if __name__ == "__main__":
    unittest.main()
