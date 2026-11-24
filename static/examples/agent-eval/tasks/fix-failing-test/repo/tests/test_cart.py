import unittest

from cart import cart_total


class CartTotalTest(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(cart_total([1000, 500]), 1500)

    def test_ten_percent(self):
        self.assertEqual(cart_total([1000, 500], 10), 1350)

    def test_full_discount(self):
        self.assertEqual(cart_total([1000, 500], 100), 0)


if __name__ == "__main__":
    unittest.main()
