"""Cart totals, in cents."""


def cart_total(prices, discount_percent=0):
    """Return the sum of prices after a percentage discount, in whole cents."""
    subtotal = sum(prices)
    discount = subtotal * (discount_percent // 100)
    return subtotal - discount
