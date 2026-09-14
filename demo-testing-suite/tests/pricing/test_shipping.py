"""Tests for determine_shipping_cost.

Encodes all three Lecture 3 techniques in one parametrized suite, in the
same order the reading builds them:
  - Equivalence partitioning: one representative value per valid class
    (test_valid_weights).
  - Boundary-value analysis: the exact edges of every class, including
    the 5.0 boundary that exposes the deliberate off-by-one in
    app/pricing/shipping.py (test_valid_weights, xfail case).
  - Negative testing: invalid numeric ranges (test_invalid_weight_raises_value_error)
    and invalid types entirely (test_invalid_type_raises_a_clear_error).
"""

import pytest

from app.pricing.shipping import determine_shipping_cost


# Equivalence partitioning + boundary-value analysis together: one
# representative value per class, plus the exact edges of every class.
@pytest.mark.parametrize(
    "weight_kg, expected_cost",
    [
        # EC1: 0 < weight <= 1
        (0.01, 5.00),
        (0.5, 5.00),
        (1.0, 5.00),
        # EC2: 1 < weight <= 5 (boundary at 5.0 currently FAILS -- see KNOWN BUG)
        (1.01, 10.00),
        (3.0, 10.00),
        pytest.param(
            5.0,
            10.00,
            marks=pytest.mark.xfail(
                reason="known bug -- see app/pricing/shipping.py KNOWN BUG note"
            ),
        ),
        # EC3: 5 < weight <= 20
        (5.01, 20.00),
        (10.0, 20.00),
        (20.0, 20.00),
    ],
)
def test_valid_weights(weight_kg, expected_cost):
    assert determine_shipping_cost(weight_kg) == expected_cost


# Negative testing: invalid numeric ranges (EC4, EC5) and the boundaries
# immediately outside the valid region.
@pytest.mark.parametrize("weight_kg", [-1.0, -0.01, 0.0, 20.01, 25.0])
def test_invalid_weight_raises_value_error(weight_kg):
    with pytest.raises(ValueError):
        determine_shipping_cost(weight_kg)


# Negative testing: invalid types entirely -- these don't fit into any
# equivalence class defined purely in terms of numeric ranges.
@pytest.mark.parametrize("bad_input", [None, "5", [5], {}])
def test_invalid_type_raises_a_clear_error(bad_input):
    with pytest.raises((TypeError, ValueError)):
        determine_shipping_cost(bad_input)
