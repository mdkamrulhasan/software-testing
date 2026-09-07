"""Lives in tests/checkout/, so it can see both sample_cart (from the
parent tests/conftest.py) and discounted_cart (from this directory's own
conftest.py) -- but a file back in tests/ cannot see discounted_cart.
Try adding `def test_x(discounted_cart): ...` to ../test_cart.py live to
show the resulting "fixture not found" error.
"""


def test_discounted_cart_has_discount_percent(discounted_cart):
    assert discounted_cart["discount_percent"] == 10
