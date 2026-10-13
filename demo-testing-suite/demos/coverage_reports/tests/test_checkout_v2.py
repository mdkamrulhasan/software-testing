# Week 7 reading, "From Report to Tests: Closing the Gaps": every gap in
# the v1 report turned into a behavior-level test with a real assertion.
# 100% statement and branch coverage -- and still not "fully tested":
# no test makes amount >= 50 true, and none sits at the $50 boundary
# (Limitations 2-3; Exercise 4 asks for both).

import pytest
from checkout_app.checkout import (
    subtotal, apply_coupon, shipping_fee, format_receipt,
)


def test_subtotal_two_items():
    assert subtotal([(10.0, 2), (5.0, 1)]) == 25.0


def test_subtotal_rejects_negative_quantity():
    with pytest.raises(ValueError):
        subtotal([(10.0, -1)])


@pytest.mark.parametrize("amount, code, expected", [
    (100.0, "SAVE10", 90.0),
    (100.0, "FLAT5", 95.0),
    (3.0, "FLAT5", 0.0),
    (100.0, "BOGUS", 100.0),
])
def test_apply_coupon(amount, code, expected):
    assert apply_coupon(amount, code) == expected


def test_member_ships_free():
    assert shipping_fee(20.0, True) == 0.0


def test_non_member_small_order_pays_shipping():
    assert shipping_fee(20.0, False) == 7.99


def test_format_receipt():
    assert format_receipt(12.5) == "Total due: $12.50"
