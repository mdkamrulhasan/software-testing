"""Pricing an order -- the version that misread US-3.

KNOWN DEFECT (deliberate, for the acceptance testing demo): the
developer priced the order one *unit* at a time, so FLAT5 takes $5 off
every unit instead of the order, and its $10 minimum is checked against
one unit's price instead of the order. Every developer test in
tests/integration/test_pricing.py orders a single unit, where the two
readings agree, so they all pass. The acceptance scenarios, written
from the product owner's examples, do not. See specs/user_stories.md
and tests/acceptance/features/coupons.feature.
"""

from shop.errors import InvalidCoupon

FLAT5_MINIMUM_CENTS = 1000


def price_order(unit_price_cents, quantity, coupon=None):
    """Return (subtotal_cents, discount_cents, total_cents) for an order.

    Raises InvalidCoupon if `coupon` is unknown or does not apply.
    """
    discount_per_unit = 0
    if coupon is not None:
        code = coupon.upper()
        if code == "SAVE10":
            discount_per_unit = unit_price_cents // 10
        elif code == "FLAT5":
            if unit_price_cents < FLAT5_MINIMUM_CENTS:    # KNOWN DEFECT: one unit
                raise InvalidCoupon("FLAT5 requires an order of at least $10.00")
            discount_per_unit = 500                       # KNOWN DEFECT: per unit
        else:
            raise InvalidCoupon(f"unknown coupon code: {coupon}")
    subtotal = unit_price_cents * quantity
    discount = discount_per_unit * quantity
    return subtotal, discount, subtotal - discount
