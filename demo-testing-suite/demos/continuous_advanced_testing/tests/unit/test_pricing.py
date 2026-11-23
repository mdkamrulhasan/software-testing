"""The developer's own unit tests for price_order(), written while
implementing US-3 -- before the acceptance scenarios existed.

They are reasonable tests, and they all pass with SHOP_COUPONS=per_unit
too: every one orders a single unit, and for a single unit "$5 off the
order" and "$5 off each unit" are the same thing. The developer tested
their own reading of the story. See tests/acceptance/features/coupons.feature.

    SHOP_COUPONS=per_unit pytest tests/unit
"""

import pytest

from shop.errors import InvalidCoupon
from variants import price_order


def test_no_coupon():
    assert price_order(1250, 1) == (1250, 0, 1250)


def test_save10_takes_ten_percent():
    assert price_order(1250, 1, "SAVE10") == (1250, 125, 1125)


def test_save10_rounds_the_discount_down():
    assert price_order(199, 1, "SAVE10") == (199, 19, 180)


def test_flat5_takes_five_dollars():
    assert price_order(1250, 1, "FLAT5") == (1250, 500, 750)


def test_flat5_needs_ten_dollars():
    with pytest.raises(InvalidCoupon, match="at least"):
        price_order(300, 1, "FLAT5")


def test_codes_are_case_insensitive():
    assert price_order(1250, 1, "save10") == price_order(1250, 1, "SAVE10")


def test_unknown_code_is_rejected():
    with pytest.raises(InvalidCoupon, match="unknown coupon code: NOPE"):
        price_order(1250, 1, "NOPE")


def test_quantity_multiplies_the_subtotal():
    subtotal, _, _ = price_order(1250, 3)
    assert subtotal == 3750
