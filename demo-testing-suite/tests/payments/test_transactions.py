"""Control-flow-graph-driven tests for app/payments/transactions.py.

Follows the Week 5 reading (*Control-Flow Graphs and Statement, Branch,
and Path Coverage*):

  - classify_transaction(): one test per entry-to-exit path. There are
    exactly V(G) = 4 paths and no loops, so these four tests give 100%
    statement, branch, and path coverage at once.
  - contains_negative(): the loop makes full path coverage infeasible,
    so the tests follow basis-path testing -- V(G) = 3 independent
    paths -- plus the "zero, one, many" iterations rule of thumb from
    the reading's "A Practical Mental Model" section.

Check the hand-computed numbers against the tool:

    pytest tests/payments/test_transactions.py \
        --cov=app.payments.transactions --cov-branch --cov-report=term-missing
"""

import pytest

from app.payments.transactions import classify_transaction, contains_negative


# One case per path through the CFG, in the order the reading adds them
# in "Statement Coverage: Worked Example".
@pytest.mark.parametrize(
    "amount, is_international, expected",
    [
        pytest.param(-5, False, "invalid", id="amount<0"),
        pytest.param(50, True, "international", id="intl-under-1000"),
        pytest.param(50, False, "domestic", id="domestic"),
        pytest.param(5000, True, "flagged", id="intl-over-1000"),
    ],
)
def test_classify_transaction_every_path(amount, is_international, expected):
    assert classify_transaction(amount, is_international) == expected


# Basis paths for contains_negative (V(G) = 3), plus a "many" case.
@pytest.mark.parametrize(
    "numbers, expected",
    [
        pytest.param([], False, id="zero-iterations"),
        pytest.param([-1], True, id="one-iteration-early-return"),
        pytest.param([1], False, id="one-iteration-loop-exits"),
        pytest.param([3, 7, -2, 9], True, id="many-iterations-negative-late"),
    ],
)
def test_contains_negative_basis_paths(numbers, expected):
    assert contains_negative(numbers) is expected
