"""The slide's tests/test_pricing.py, renamed test_cart.py to match this
repo's naming. No import of sample_cart needed -- pytest found it in the
conftest.py in this same directory.
"""

from app.pricing.cart import cart_total


def test_cart_total(sample_cart):
    assert cart_total(sample_cart) == 29.97
