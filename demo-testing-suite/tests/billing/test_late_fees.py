"""pytest-style tests for calculate_late_fee.

Covers two slide moments:
  - "The Problem: One Test Per Case Doesn't Scale" -- the naive,
    one-function-per-case version, kept below as
    test_typical_fee_naive / test_fee_is_capped_naive purely so you can
    show it and then immediately replace it with the parametrized
    version. Feel free to comment these two out once you've made the
    point live.
  - "@pytest.mark.parametrize: Data-Driven Tests" and
    "Documenting Known Bugs with xfail" -- the data-driven replacement.
"""

import pytest

from app.billing.late_fees import calculate_late_fee


# --- "The Problem" slide: one test per case (kept only for contrast) ---
def test_typical_fee_naive():
    assert calculate_late_fee(3) == 4.5


def test_fee_is_capped_naive():
    assert calculate_late_fee(30) == 25.00


# --- "@pytest.mark.parametrize" slide: the data-driven replacement ---
@pytest.mark.parametrize(
    "days_late, expected_fee",
    [
        (0, 0.0),  # no late fee
        (3, 4.5),  # typical case
        (30, 25.00),  # fee should be capped
        (100, 25.00),  # far past the cap, still capped
        pytest.param(
            -4,
            0.0,
            marks=pytest.mark.xfail(
                reason="known bug -- see app/billing/late_fees.py KNOWN BUG note"
            ),
        ),
    ],
)
def test_calculate_late_fee(days_late, expected_fee):
    assert calculate_late_fee(days_late) == expected_fee
