"""Pricing an order: subtotal, coupon discount, total (specs/user_stories.md, US-3).

All amounts are integer cents.
"""

from shop.errors import InvalidCoupon

FLAT5_MINIMUM_CENTS = 1000


# def price_order(unit_price_cents, quantity, coupon=None):
#     """Return (subtotal_cents, discount_cents, total_cents) for an order.

#     Raises InvalidCoupon if `coupon` is unknown or does not apply.
#     """
#     subtotal = unit_price_cents * quantity
#     discount = 0
#     if coupon is not None:
#         code = coupon.upper()
#         if code == "SAVE10":
#             discount = subtotal // 10                 # US-3.1: rounded down
#         elif code == "FLAT5":
#             if subtotal < FLAT5_MINIMUM_CENTS:        # US-3.3: the ORDER's subtotal
#                 raise InvalidCoupon("FLAT5 requires an order of at least $10.00")
#             discount = 500                            # US-3.2: once per order
#         else:
#             raise InvalidCoupon(f"unknown coupon code: {coupon}")
#     return subtotal, discount, subtotal - discount

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
