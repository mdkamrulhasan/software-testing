"""Tests for cart_total, using the fixtures defined in
tests/pricing/conftest.py.

"Defining and Using a Fixture" and "Fixtures Can Depend on Other
Fixtures" slides.
"""

import pytest

from app.pricing.cart import cart_total


def test_cart_total(sample_cart):
    assert cart_total(sample_cart) == pytest.approx(54.96)


def test_single_item_total(cart_with_one_item):
    assert cart_total(cart_with_one_item) == pytest.approx(9.99)
