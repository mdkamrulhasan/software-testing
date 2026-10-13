# Week 7 reading, "The Running Example": the deliberately thin first
# suite. One happy-path test per function, and format_receipt() forgotten
# entirely. All three tests pass; coverage shows how little they exercise:
# 74% statement, 66% with --branch, Missing: 8, 16-17, 24, 28.
# (Comments only, no docstring, so the reading's statement counts hold.)

from checkout_app.checkout import subtotal, apply_coupon, shipping_fee


def test_subtotal_two_items():
    assert subtotal([(10.0, 2), (5.0, 1)]) == 25.0


def test_save10_coupon():
    assert apply_coupon(100.0, "SAVE10") == 90.0


def test_member_ships_free():
    assert shipping_fee(20.0, True) == 0.0
