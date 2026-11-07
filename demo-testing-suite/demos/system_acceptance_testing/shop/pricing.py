"""Pricing an order: subtotal, coupon discount, total (specs/user_stories.md, US-3).

All amounts are integer cents.
"""

from shop.errors import InvalidCoupon

FLAT5_MINIMUM_CENTS = 1000


def price_order(unit_price_cents, quantity, coupon=None):
    """Return (subtotal_cents, discount_cents, total_cents) for an order.

    Raises InvalidCoupon if `coupon` is unknown or does not apply.
    """
    subtotal = unit_price_cents * quantity
    discount = 0
    if coupon is not None:
        code = coupon.upper()
        if code == "SAVE10":
            discount = subtotal // 10                 # US-3.1: rounded down
        elif code == "FLAT5":
            if subtotal < FLAT5_MINIMUM_CENTS:        # US-3.3: the ORDER's subtotal
                raise InvalidCoupon("FLAT5 requires an order of at least $10.00")
            discount = 500                            # US-3.2: once per order
        else:
            raise InvalidCoupon(f"unknown coupon code: {coupon}")
    return subtotal, discount, subtotal - discount
