"""Statement vs. branch coverage for apply_membership_discount.

The first test alone already reaches 100% statement coverage; the
second is what branch coverage additionally demands (the Week 5
reading's "What Branch Coverage Catches That Statement Coverage
Misses"). demos/coverage_gaps/ reproduces the reading's pytest-cov
report for a suite that has only the first test.
"""

import pytest

from app.pricing.membership import apply_membership_discount


def test_member_gets_ten_percent_off():
    assert apply_membership_discount(100, True) == pytest.approx(90)


def test_non_member_pays_full_price():
    assert apply_membership_discount(100, False) == 100
