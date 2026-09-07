"""Tests for calculate_discounted_price.

Walks the slide order: plain assert, then the assertion-rewriting
failure demo, then pytest.approx, then pytest.raises.
"""

import pytest

from app.pricing.discounts import calculate_discounted_price


def test_ten_percent_discount():
    # "A Test Is Just a Function" slide.
    # See the LIVE DEMO HOOK comment in app/pricing/discounts.py to
    # reproduce the "The Payoff: Assertion Rewriting" slide's failure
    # output using this exact test.
    assert calculate_discounted_price(100, 10) == 90


def test_float_addition():
    # "Comparing Floating-Point Numbers" slide.
    assert 0.1 + 0.2 == pytest.approx(0.3)


def test_invalid_discount_raises_value_error():
    # "Testing for Exceptions: pytest.raises()" slide.
    with pytest.raises(ValueError):
        calculate_discounted_price(100, 150)
