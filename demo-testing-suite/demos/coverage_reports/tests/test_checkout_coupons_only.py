# Week 7 reading, "Reading the Missing Column": a suite that tests only
# the SAVE10 and FLAT5 coupons. Its report is the reading's arrow example:
# 41%, Missing: 5-10, 16->18, 22-24, 28. Line 18 ran, but never directly
# from line 16 -- no test used an unrecognized coupon code.

from checkout_app.checkout import apply_coupon


def test_save10_coupon():
    assert apply_coupon(100.0, "SAVE10") == 90.0


def test_flat5_coupon():
    assert apply_coupon(100.0, "FLAT5") == 95.0
