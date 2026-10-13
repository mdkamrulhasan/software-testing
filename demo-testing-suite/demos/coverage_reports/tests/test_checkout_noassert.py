# Week 7 reading, Limitation 1, "Execution Is Not Verification": this
# test also reaches 100% statement and branch coverage, and contains no
# assertions at all. Do not copy it -- it is the anti-pattern.

import pytest
from checkout_app.checkout import subtotal, apply_coupon, shipping_fee, format_receipt

def test_runs_everything():
    for code in ["SAVE10", "FLAT5", "NONE"]:
        apply_coupon(100.0, code)
    shipping_fee(20.0, True)
    shipping_fee(20.0, False)
    format_receipt(1)
    subtotal([(1.0, 1)])
    try:
        subtotal([(1.0, -1)])
    except ValueError:
        pass
